"""Streamlit entry point for SourceCraft."""

from __future__ import annotations

import os

import streamlit as st

from research_assistant.config import Settings
from research_assistant.graph import build_graph, create_initial_state

st.set_page_config(
    page_title="SourceCraft Research",
    page_icon="🔎",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("🔎 SourceCraft Research")
st.caption("A source-aware research brief created by three collaborating AI agents.")

with st.sidebar:
    st.header("Research settings")
    try:
        secret_key = st.secrets.get("GOOGLE_API_KEY", "")
    except FileNotFoundError:
        secret_key = ""
    configured_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY") or secret_key
    api_key = configured_key or st.text_input(
        "Gemini API key",
        type="password",
        help="Used only for this session. Get a key from Google AI Studio.",
    )
    audience = st.selectbox(
        "Audience",
        ["general reader", "high-school student", "university student", "technical professional"],
    )
    depth = st.selectbox(
        "Depth",
        ["concise (about 400 words)", "standard (about 700 words)", "deep (about 1,200 words)"],
        index=1,
    )
    max_sources = st.slider("Search results per round", 3, 10, 6)
    st.divider()
    st.markdown("**Workflow**")
    st.markdown(
        "1. Researcher gathers sources\n"
        "2. Writer creates the brief\n"
        "3. Reviewer approves or routes revisions"
    )

topic = st.text_area(
    "What would you like to research?",
    placeholder="Example: How small language models are changing on-device AI",
    height=100,
    max_chars=500,
)

if st.button("Run research team", type="primary", use_container_width=True):
    if not api_key:
        st.error("Add a Gemini API key in the sidebar or configure GOOGLE_API_KEY.")
    elif len(topic.strip()) < 3:
        st.error("Enter a more specific research topic.")
    else:
        settings = Settings.from_env(api_key=api_key)
        initial_state = create_initial_state(
            topic,
            audience=audience,
            depth=depth,
            max_sources=max_sources,
        )
        status_box = st.status("Starting the research team…", expanded=True)
        final_state = initial_state
        try:
            graph = build_graph(settings)
            labels = {
                "researcher": "Researcher gathered and synthesized web sources",
                "writer": "Writer produced a cited research brief",
                "reviewer": "Reviewer checked evidence, citations, and clarity",
            }
            for event in graph.stream(initial_state):
                for node, update in event.items():
                    final_state = {**final_state, **update}
                    status_box.write(f"✓ {labels.get(node, node.title())}")
            if final_state["status"] == "approved":
                status_box.update(label="Research brief approved", state="complete")
            else:
                status_box.update(label="Research stopped at the safety limit", state="complete")
        except Exception as exc:
            status_box.update(label="Research failed", state="error")
            st.error(f"Could not complete the workflow: {exc}")
        else:
            st.session_state["result"] = final_state

if result := st.session_state.get("result"):
    st.divider()
    metric_cols = st.columns(4)
    metric_cols[0].metric("Status", result["status"].replace("_", " ").title())
    metric_cols[1].metric("Sources", len(result["sources"]))
    metric_cols[2].metric("Research rounds", result["research_rounds"])
    metric_cols[3].metric("Drafts", result["draft_count"])

    report_tab, notes_tab, process_tab = st.tabs(
        ["Research brief", "Research notes", "Review details"]
    )
    with report_tab:
        st.markdown(result["report"])
        st.download_button(
            "Download Markdown",
            result["report"],
            file_name="research-brief.md",
            mime="text/markdown",
        )
    with notes_tab:
        st.markdown(result["research_notes"])
    with process_tab:
        st.write(f"**Final decision:** {result['review_decision']}")
        st.write(f"**Reviewer feedback:** {result['feedback']}")
        st.write("**Collected URLs:**")
        for source in result["sources"]:
            st.markdown(f"- [{source['title']}]({source['url']})")

st.caption(
    "AI-generated research can be wrong. Open and verify important sources before using the brief."
)
