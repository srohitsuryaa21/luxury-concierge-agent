from __future__ import annotations

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import streamlit as st

from lca.agent import LuxuryConciergeAgent
from lca.config import get_settings

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

        .prompt-grid {
            display: grid;
            grid-template-columns: repeat(3, minmax(0, 1fr));
            gap: 10px;
            margin: 12px 0 18px;
        }

        .prompt-card {
            border: 1px solid var(--lca-border);
            background: rgba(255, 255, 255, 0.74);
            border-radius: 8px;
            padding: 13px 14px;
            min-height: 112px;
        }

        .prompt-card strong {
            display: block;
            margin-bottom: 7px;
            color: #101828;
            font-size: 0.95rem;
        }

        .prompt-card span {
            color: #667085;
            font-size: 0.90rem;
            line-height: 1.38;
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

        .thinking-panel {
            border: 1px solid rgba(26, 115, 232, 0.18);
            background: linear-gradient(135deg, rgba(26, 115, 232, 0.08), rgba(15, 157, 138, 0.07));
            border-radius: 8px;
            padding: 16px 18px;
            margin: 12px 0;
        }

        .thinking-title {
            font-weight: 760;
            color: #101828;
            margin-bottom: 8px;
        }

        .thinking-line {
            color: #475467;
            margin: 4px 0;
            font-size: 0.94rem;
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

        @media (max-width: 860px) {
            .brand-row {
                align-items: flex-start;
                flex-direction: column;
            }
            .prompt-grid,
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
    settings = get_settings()
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
                    Local model: {settings.ollama_model if settings.model_provider == "ollama" else settings.model_provider}
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


def render_prompt_cards() -> None:
    st.markdown(
        """
        <div class="prompt-grid">
            <div class="prompt-card">
                <strong>Family commission</strong>
                <span>Dubai client, mountain trips, warm handcrafted cabin, rear-seat comfort, 10-month timeline.</span>
            </div>
            <div class="prompt-card">
                <strong>Electric grand tourer</strong>
                <span>London client wants quiet electric luxury, sustainable materials, modern cabin, discreet exterior.</span>
            </div>
            <div class="prompt-card">
                <strong>Formal chauffeur brief</strong>
                <span>Black flagship presence, rear privacy, ceremonial use, calm cabin, high-touch sales handoff.</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_brief(result: dict) -> None:
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


def render_sidebar() -> None:
    settings = get_settings()
    st.sidebar.subheader("Run Mode")
    st.sidebar.write(f"Provider: `{settings.model_provider}`")
    st.sidebar.write(f"Model: `{settings.ollama_model if settings.model_provider == 'ollama' else settings.openai_model}`")
    st.sidebar.write(f"Retriever: `{settings.retriever_backend}`")

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


def run_agent_with_progress(prompt: str) -> dict:
    agent = get_agent()
    progress = st.progress(0, text="Understanding the client brief")
    status_box = st.empty()
    status_box.markdown(
        """
        <div class="thinking-panel">
            <div class="thinking-title">Crafting the recommendation</div>
            <div class="thinking-line">Reading intent, region, timeline, and cabin preferences...</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    time.sleep(0.25)
    progress.progress(22, text="Retrieving product knowledge")
    time.sleep(0.25)
    progress.progress(48, text="Calling configuration and availability tools")
    time.sleep(0.25)
    progress.progress(72, text="Preparing the sales-ready summary")
    result = agent.invoke(prompt, memory=st.session_state.messages[:-1])
    progress.progress(100, text="Recommendation ready")
    time.sleep(0.25)
    progress.empty()
    status_box.empty()
    return result


apply_theme()
render_header()
render_sidebar()

if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": "Describe the client, region, usage, cabin mood, timeline, and budget.",
        }
    ]

if len(st.session_state.messages) == 1:
    render_prompt_cards()

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        if message["role"] == "assistant" and message.get("result"):
            render_brief(message["result"])
        st.markdown(message["content"])

prompt = st.chat_input("Describe the client brief, preferences, region, timeline, and budget...")

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        result = run_agent_with_progress(prompt)
        response = result["response"]
        render_brief(result)
        st.markdown(response)

    st.session_state.last_result = result
    st.session_state.messages.append(
        {"role": "assistant", "content": response, "result": result}
    )
    st.rerun()
