from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import streamlit as st

from lca.agent import LuxuryConciergeAgent
from lca.config import get_settings
from lca.llm import get_usage, provider_status

# session_state.messages holds chat turns; assistant turns additionally carry
# the full agent result dict under "result". Typed loosely on purpose since
# values are a mix of str (role/content) and dict (result).
ChatMessage = dict[str, Any]

st.set_page_config(page_title="Luxury Concierge Agent", page_icon="LCA", layout="wide")


@st.cache_resource
def get_agent() -> LuxuryConciergeAgent:
    return LuxuryConciergeAgent()


def apply_theme() -> None:
    st.markdown(
        """
        <style>
        :root {
            --lca-bg: #f7f8fb;
            --lca-surface: rgba(255, 255, 255, 0.86);
            --lca-border: rgba(32, 37, 52, 0.10);
            --lca-text: #111827;
            --lca-muted: #667085;
            --lca-blue: #1a73e8;
            --lca-teal: #0f9d8a;
            --lca-gold: #b7791f;
        }

        .stApp {
            background:
                radial-gradient(circle at 12% 0%, rgba(26, 115, 232, 0.13), transparent 34%),
                radial-gradient(circle at 90% 4%, rgba(15, 157, 138, 0.12), transparent 30%),
                linear-gradient(180deg, #fbfcff 0%, var(--lca-bg) 42%, #eef2f7 100%);
            color: var(--lca-text);
        }

        .block-container {
            max-width: 1180px;
            padding-top: 1.4rem;
            padding-bottom: 3rem;
        }

        [data-testid="stSidebar"] {
            background: rgba(255, 255, 255, 0.72);
            border-right: 1px solid var(--lca-border);
        }

        .hero {
            padding: 22px 0 16px;
            border-bottom: 1px solid var(--lca-border);
            margin-bottom: 18px;
        }

        .brand-row {
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 18px;
        }

        .brand-lockup {
            display: flex;
            align-items: center;
            gap: 14px;
        }

        .brand-mark {
            width: 42px;
            height: 42px;
            border-radius: 12px;
            display: grid;
            place-items: center;
            color: white;
            font-weight: 760;
            background: linear-gradient(135deg, #1a73e8 0%, #0f9d8a 100%);
            box-shadow: 0 10px 28px rgba(26, 115, 232, 0.22);
        }

        .eyebrow {
            color: var(--lca-muted);
            font-size: 0.82rem;
            font-weight: 650;
            letter-spacing: 0.02em;
            text-transform: uppercase;
            margin-bottom: 4px;
        }

        .hero h1 {
            font-size: clamp(2rem, 4.5vw, 4.2rem);
            line-height: 1.02;
            margin: 0;
            letter-spacing: 0;
            font-weight: 760;
        }

        .hero-copy {
            max-width: 720px;
            color: #475467;
            font-size: 1.05rem;
            margin: 14px 0 0;
        }

        .status-pill {
            display: inline-flex;
            align-items: center;
            gap: 8px;
            padding: 8px 12px;
            border: 1px solid var(--lca-border);
            border-radius: 999px;
            background: rgba(255, 255, 255, 0.78);
            color: #344054;
            font-size: 0.88rem;
            white-space: nowrap;
        }

        .pulse {
            width: 8px;
            height: 8px;
            border-radius: 999px;
            background: #12b76a;
            box-shadow: 0 0 0 0 rgba(18, 183, 106, 0.50);
            animation: pulse 1.7s infinite;
        }

        @keyframes pulse {
            70% { box-shadow: 0 0 0 10px rgba(18, 183, 106, 0); }
            100% { box-shadow: 0 0 0 0 rgba(18, 183, 106, 0); }
        }

        .brief-grid {
            display: grid;
            grid-template-columns: repeat(4, minmax(0, 1fr));
            gap: 10px;
            margin: 0 0 16px;
        }

        .brief-tile {
            border: 1px solid var(--lca-border);
            background: rgba(255, 255, 255, 0.78);
            border-radius: 8px;
            padding: 12px 14px;
        }

        .brief-label {
            color: var(--lca-muted);
            font-size: 0.78rem;
            font-weight: 650;
            text-transform: uppercase;
            margin-bottom: 5px;
        }

        .brief-value {
            color: #101828;
            font-size: 1rem;
            font-weight: 720;
            overflow-wrap: anywhere;
        }

div[data-testid="stChatMessage"] {
            background: rgba(255, 255, 255, 0.70);
            border: 1px solid var(--lca-border);
            border-radius: 8px;
            box-shadow: 0 12px 30px rgba(16, 24, 40, 0.04);
        }

        div[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) {
            background: rgba(255, 255, 255, 0.88);
        }

        .stChatInput {
            border-top: 1px solid rgba(32, 37, 52, 0.08);
        }

        .stButton > button {
            border-radius: 8px;
        }

        @media (prefers-color-scheme: dark) {
            :root {
                --lca-bg: #0b0d12;
                --lca-surface: rgba(255, 255, 255, 0.04);
                --lca-border: rgba(255, 255, 255, 0.10);
                --lca-text: #e6e8ee;
                --lca-muted: #94a0b4;
            }

            .stApp {
                background:
                    radial-gradient(circle at 12% 0%, rgba(26, 115, 232, 0.16), transparent 34%),
                    radial-gradient(circle at 90% 4%, rgba(15, 157, 138, 0.14), transparent 30%),
                    linear-gradient(180deg, #0b0d12 0%, #0e1117 42%, #0b0d12 100%);
                color: var(--lca-text);
            }

            [data-testid="stSidebar"] {
                background: rgba(255, 255, 255, 0.03);
            }

            .status-pill,
            .brief-tile {
                background: rgba(255, 255, 255, 0.05);
            }

            .hero h1,
            .brief-value,
            .status-pill {
                color: var(--lca-text);
            }

            div[data-testid="stChatMessage"] {
                background: rgba(255, 255, 255, 0.04);
            }

            div[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) {
                background: rgba(255, 255, 255, 0.07);
            }
        }

        @media (max-width: 860px) {
            .brand-row {
                align-items: flex-start;
                flex-direction: column;
            }
            .brief-grid {
                grid-template-columns: 1fr;
            }
            .status-pill {
                white-space: normal;
            }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_header() -> None:
    status = provider_status()
    st.markdown(
        f"""
        <section class="hero">
            <div class="brand-row">
                <div class="brand-lockup">
                    <div class="brand-mark">LCA</div>
                    <div>
                        <div class="eyebrow">Agentic luxury sales assistant</div>
                        <h1>Luxury Concierge Agent</h1>
                    </div>
                </div>
                <div class="status-pill">
                    <span class="pulse"></span>
                    {"Model: " + str(status["model"]) if status["ready"] else "MODEL NOT CONNECTED"}
                </div>
            </div>
            <p class="hero-copy">
                Turn a client brief into a sales-ready bespoke configuration with retrieval,
                tool calls, availability, and pricing in one guided conversation.
            </p>
        </section>
        """,
        unsafe_allow_html=True,
    )


SAMPLE_BRIEFS = [
    (
        "Family commission",
        "Dubai client, mountain trips, warm handcrafted cabin, rear-seat comfort, 10-month timeline.",
    ),
    (
        "Electric grand tourer",
        "London client wants quiet electric luxury, sustainable materials, modern cabin, discreet exterior.",
    ),
    (
        "Formal chauffeur brief",
        "Black flagship presence, rear privacy, ceremonial use, calm cabin, high-touch sales handoff.",
    ),
]


def render_prompt_cards() -> str | None:
    """Clickable sample-brief cards. Returns the picked brief text, if any."""
    st.caption("Try a sample brief")
    picked = None
    columns = st.columns(3)
    for column, (title, description) in zip(columns, SAMPLE_BRIEFS):
        with column, st.container(border=True):
            st.markdown(f"**{title}**")
            st.caption(description)
            if st.button("Use this brief", key=f"sample_{title}", use_container_width=True):
                picked = description
    return picked


def render_brief(result: dict[str, Any]) -> None:
    config = result.get("configuration", {})
    price = result.get("price", {})
    availability = result.get("availability", {})
    options = result.get("complementary_options", {}).get("recommended_options", [])
    option_count = len(options)
    total = price.get("estimated_total")
    total_text = f"EUR {total:,}" if isinstance(total, int) else "Pending"
    st.markdown(
        f"""
        <div class="brief-grid">
            <div class="brief-tile">
                <div class="brief-label">Model</div>
                <div class="brief-value">{config.get("model", "Pending")}</div>
            </div>
            <div class="brief-tile">
                <div class="brief-label">Region</div>
                <div class="brief-value">{availability.get("region", "Pending")}</div>
            </div>
            <div class="brief-tile">
                <div class="brief-label">Estimate</div>
                <div class="brief-value">{total_text}</div>
            </div>
            <div class="brief-tile">
                <div class="brief-label">Options</div>
                <div class="brief-value">{option_count} suggested</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    budget = result.get("budget_eur")
    if budget:
        fit = price.get("budget_fit")
        if fit == "over_budget":
            st.caption(f"Stated budget EUR {budget:,} — estimate is above budget.")
        elif fit == "fits":
            st.caption(f"Stated budget EUR {budget:,} — estimate fits.")


def render_sidebar() -> None:
    settings = get_settings()
    if st.sidebar.button("New conversation", use_container_width=True):
        st.session_state.clear()
        st.rerun()
    st.sidebar.divider()
    st.sidebar.subheader("Run Mode")
    status = provider_status()
    st.sidebar.write(f"Provider: `{status['provider']}`")
    st.sidebar.write(f"Model: `{status['model']}`")
    st.sidebar.write(f"Retriever: `{settings.retriever_backend}`")
    if status["ready"]:
        st.sidebar.success("Model connected", icon=":material/check_circle:")
    else:
        st.sidebar.error(status["detail"], icon=":material/error:")

    # Usage meter. Failures are shown next to calls on purpose: the agent falls
    # back to deterministic rules when the model is unreachable, so without this
    # a broken key looks exactly like a working demo.
    usage = get_usage()
    st.sidebar.divider()
    st.sidebar.subheader("Model Usage")
    left, right = st.sidebar.columns(2)
    left.metric("Calls", usage.calls)
    right.metric("Failures", usage.failures)
    left.metric("Prompt tok", f"{usage.prompt_tokens:,}")
    right.metric("Output tok", f"{usage.completion_tokens:,}")
    st.sidebar.caption(f"Total tokens this session: {usage.total_tokens:,}")
    if usage.calls and usage.failures == usage.calls:
        st.sidebar.warning("Every model call failed - answers are rule-based only.")
    if usage.last_error:
        st.sidebar.caption("Last model error")
        st.sidebar.code(usage.last_error, language=None)

    if "last_result" in st.session_state:
        result = st.session_state.last_result
        st.sidebar.divider()
        st.sidebar.subheader("Agent Trace")
        with st.sidebar.expander("Configuration", expanded=True):
            st.json(result.get("configuration", {}))
        with st.sidebar.expander("Availability"):
            st.json(result.get("availability", {}))
        with st.sidebar.expander("Price"):
            st.json(result.get("price", {}))
        with st.sidebar.expander("Retrieved Knowledge"):
            st.json(result.get("context", []))


def run_agent(prompt: str) -> dict[str, Any]:
    """Run the deterministic pipeline. No artificial delays: retrieval, tool
    calls, pricing, and availability are all local computation and typically
    finish in well under a second."""
    agent = get_agent()
    with st.status("Reading the brief and pricing the configuration...", expanded=False) as status:
        result = agent.invoke(prompt, memory=st.session_state.messages[:-1])
        status.update(label="Recommendation ready", state="complete")
    return result


apply_theme()
render_header()
render_sidebar()

if "messages" not in st.session_state:
    initial_messages: list[ChatMessage] = [
        {
            "role": "assistant",
            "content": "Describe the client, region, usage, cabin mood, timeline, and budget.",
        }
    ]
    st.session_state.messages = initial_messages

if len(st.session_state.messages) == 1:
    picked_brief = render_prompt_cards()
    if picked_brief:
        st.session_state.pending_prompt = picked_brief

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        if message["role"] == "assistant" and message.get("result"):
            render_brief(message["result"])
        st.markdown(message["content"])

typed_prompt = st.chat_input("Describe the client brief, preferences, region, timeline, and budget...")
prompt = typed_prompt or st.session_state.pop("pending_prompt", None)

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        result = run_agent(prompt)
        render_brief(result)
        agent = get_agent()
        response = st.write_stream(agent.stream_response(result))

    st.session_state.last_result = result
    st.session_state.messages.append(
        {"role": "assistant", "content": response, "result": result}
    )
    st.rerun()
