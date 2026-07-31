"""SQLite commission catalogue: build, and read.

The catalogue is a database rather than Python literals for two reasons. It is
the thing a salesperson would actually maintain, and it gives the LLM a closed
world to choose from - the proposal step can only return an option that exists
here, which is what stops a model inventing a finish or a price.
"""

from __future__ import annotations

import sqlite3
from collections.abc import Iterable
from functools import lru_cache
from pathlib import Path
from typing import Any

from lca.config import get_settings
from lca.data import knowledge, seed

SCHEMA = """
DROP TABLE IF EXISTS models;
DROP TABLE IF EXISTS paints;
DROP TABLE IF EXISTS leathers;
DROP TABLE IF EXISTS veneers;
DROP TABLE IF EXISTS wheels;
DROP TABLE IF EXISTS options;
DROP TABLE IF EXISTS availability;
DROP TABLE IF EXISTS regions;
DROP TABLE IF EXISTS constraints;
DROP TABLE IF EXISTS knowledge;

CREATE TABLE models (
    name TEXT PRIMARY KEY,
    tier TEXT NOT NULL,
    body TEXT NOT NULL,
    powertrain TEXT NOT NULL,
    base_price_eur INTEGER NOT NULL,
    positioning TEXT NOT NULL
);
CREATE TABLE paints (
    name TEXT PRIMARY KEY,
    family TEXT NOT NULL,
    finish TEXT NOT NULL,
    price_eur INTEGER NOT NULL,
    extra_lead_weeks INTEGER NOT NULL,
    keywords TEXT NOT NULL
);
CREATE TABLE leathers (
    name TEXT PRIMARY KEY,
    family TEXT NOT NULL,
    price_eur INTEGER NOT NULL,
    vegan INTEGER NOT NULL,
    keywords TEXT NOT NULL
);
CREATE TABLE veneers (
    name TEXT PRIMARY KEY,
    price_eur INTEGER NOT NULL,
    sustainable INTEGER NOT NULL,
    keywords TEXT NOT NULL
);
CREATE TABLE wheels (
    name TEXT PRIMARY KEY,
    size_inch INTEGER NOT NULL,
    price_eur INTEGER NOT NULL,
    use_case TEXT NOT NULL,
    keywords TEXT NOT NULL
);
CREATE TABLE options (
    name TEXT PRIMARY KEY,
    category TEXT NOT NULL,
    price_eur INTEGER NOT NULL,
    keywords TEXT NOT NULL,
    description TEXT NOT NULL
);
CREATE TABLE availability (
    model TEXT NOT NULL,
    region TEXT NOT NULL,
    status TEXT NOT NULL,
    lead_min_months INTEGER NOT NULL,
    lead_max_months INTEGER NOT NULL,
    PRIMARY KEY (model, region)
);
CREATE TABLE regions (
    name TEXT PRIMARY KEY,
    uplift_factor REAL NOT NULL,
    note TEXT NOT NULL
);
CREATE TABLE constraints (
    rule TEXT PRIMARY KEY,
    severity TEXT NOT NULL
);
CREATE TABLE knowledge (
    title TEXT PRIMARY KEY,
    category TEXT NOT NULL,
    content TEXT NOT NULL,
    keywords TEXT NOT NULL
);
"""

_INSERTS: tuple[tuple[str, int, Iterable[tuple[Any, ...]]], ...] = (
    ("models", 6, seed.MODELS),
    ("paints", 6, seed.PAINTS),
    ("leathers", 5, seed.LEATHERS),
    ("veneers", 4, seed.VENEERS),
    ("wheels", 5, seed.WHEELS),
    ("options", 5, seed.OPTIONS),
    ("availability", 5, seed.AVAILABILITY),
    ("regions", 3, seed.REGIONS),
    ("constraints", 2, seed.CONSTRAINTS),
    ("knowledge", 4, knowledge.KNOWLEDGE),
)


def build_database(db_path: Path) -> dict[str, int]:
    """Create the catalogue from the seed module. Destructive and idempotent."""
    db_path.parent.mkdir(parents=True, exist_ok=True)
    counts: dict[str, int] = {}
    with sqlite3.connect(db_path) as conn:
        conn.executescript(SCHEMA)
        for table, width, rows in _INSERTS:
            placeholders = ",".join("?" * width)
            payload = list(rows)
            conn.executemany(f"INSERT INTO {table} VALUES ({placeholders})", payload)
            counts[table] = len(payload)
        conn.commit()
    return counts


class CatalogRepository:
    """Read-only access to the commission catalogue."""

    def __init__(self, db_path: Path):
        self.db_path = db_path
        if not db_path.exists():
            build_database(db_path)

    def _rows(self, sql: str, params: tuple[Any, ...] = ()) -> list[dict[str, Any]]:
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            return [dict(row) for row in conn.execute(sql, params)]

    def _row(self, sql: str, params: tuple[Any, ...] = ()) -> dict[str, Any] | None:
        rows = self._rows(sql, params)
        return rows[0] if rows else None

    # -- catalogue listings -------------------------------------------------
    def models(self) -> list[dict[str, Any]]:
        return self._rows("SELECT * FROM models ORDER BY base_price_eur DESC")

    def model(self, name: str) -> dict[str, Any] | None:
        return self._row("SELECT * FROM models WHERE name = ?", (name,))

    def paints(self) -> list[dict[str, Any]]:
        return self._rows("SELECT * FROM paints ORDER BY name")

    def leathers(self) -> list[dict[str, Any]]:
        return self._rows("SELECT * FROM leathers ORDER BY name")

    def veneers(self) -> list[dict[str, Any]]:
        return self._rows("SELECT * FROM veneers ORDER BY name")

    def wheels(self) -> list[dict[str, Any]]:
        return self._rows("SELECT * FROM wheels ORDER BY size_inch")

    def options(self, category: str | None = None) -> list[dict[str, Any]]:
        if category:
            return self._rows("SELECT * FROM options WHERE category = ? ORDER BY name", (category,))
        return self._rows("SELECT * FROM options ORDER BY category, name")

    def constraints(self) -> list[dict[str, Any]]:
        return self._rows("SELECT * FROM constraints")

    def knowledge(self) -> list[dict[str, Any]]:
        """Every retrievable passage. This is the system's only knowledge source."""
        return self._rows("SELECT * FROM knowledge ORDER BY category, title")

    # -- lookups ------------------------------------------------------------
    def availability(self, model: str, region: str) -> dict[str, Any] | None:
        return self._row(
            "SELECT * FROM availability WHERE model = ? AND region = ?", (model, region)
        )

    def region(self, name: str) -> dict[str, Any] | None:
        return self._row("SELECT * FROM regions WHERE name = ?", (name,))

    def price_of(self, table: str, name: str) -> int:
        """Price of a named catalogue item, or 0 when it is not in the catalogue.

        Callers should validate membership separately: a silent 0 here means
        "no surcharge", never "this option is fine".
        """
        if table not in {"paints", "leathers", "veneers", "wheels", "options"}:
            raise ValueError(f"Unknown catalogue table: {table}")
        row = self._row(f"SELECT price_eur FROM {table} WHERE name = ?", (name,))
        return int(row["price_eur"]) if row else 0

    def names(self, table: str) -> list[str]:
        if table not in {"models", "paints", "leathers", "veneers", "wheels", "options"}:
            raise ValueError(f"Unknown catalogue table: {table}")
        return [row["name"] for row in self._rows(f"SELECT name FROM {table} ORDER BY name")]

    def counts(self) -> dict[str, int]:
        tables = ("models", "paints", "leathers", "veneers", "wheels", "options")
        return {
            table: int(self._rows(f"SELECT COUNT(*) AS n FROM {table}")[0]["n"])
            for table in tables
        }


@lru_cache
def get_repository() -> CatalogRepository:
    """Process-wide catalogue handle, built on first use if the file is absent."""
    return CatalogRepository(get_settings().db_path)
