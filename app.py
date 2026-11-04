import os
from pathlib import Path
from datetime import datetime

import streamlit as st
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(
    page_title="ResearchPilot | Multi-Agent Research Assistant",
    page_icon="📚",
    layout="wide",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@500;600;700;800&display=swap');
html, body, [class*="css"] {font-family:'DM Sans',sans-serif;}
.stApp {background:#f5f7fb;color:#18263b;}
.block-container {max-width:1120px;padding-top:2rem;padding-bottom:3rem;}
.hero {background:linear-gradient(115deg,#14243b,#234a78 70%,#3868d8);padding:34px 38px;border-radius:22px;color:white;margin-bottom:24px;}
.hero h1 {font-family:Manrope,sans-serif;color:white;font-size:2.35rem;letter-spacing:-.04em;margin:0;}
.hero p {color:#dbe6f8;max-width:760px;margin:10px 0 0;line-height:1.6;}
.eyebrow {color:#9db8ff;font-size:.72rem;letter-spacing:.16em;font-weight:800;text-transform:uppercase;margin-bottom:10px;}
.panel {background:white;border:1px solid #e5eaf2;border-radius:16px;padding:18px 20px;margin:10px 0;}
.small-muted {color:#718096;font-size:.88rem;}
.agent-pill {display:inline-block;background:#edf2ff;color:#315bd6;border-radius:999px;padding:6px 11px;margin:4px;font-size:.78rem;font-weight:700;}
div[data-testid="stButton"] button {border-radius:11px;font-weight:700;}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="hero">
  <div class="eyebrow">CREWAI · MULTI-AGENT RESEARCH WORKSPACE</div>
  <h1>ResearchPilot</h1>
  <p>Discover research papers, compare findings, identify research gaps and generate a structured literature review with a collaborative team of AI agents.</p>
</div>
""", unsafe_allow_html=True)

with st.sidebar:
    st.title("ResearchPilot")
    st.caption("Multi-Agent Research Paper Assistant")
    st.markdown("---")
    st.markdown("**Agent team**")
    for name in [
        "Paper Discovery Agent",
        "Literature Review Agent",
        "Research Gap Agent",
        "Paper Summarizer Agent",
        "Report Writer Agent",
    ]:
        st.markdown(f"• {name}")
    st.markdown("---")
    st.caption("Sources: arXiv metadata and abstracts")
    st.caption("LLM: Groq · Orchestration: CrewAI")

left, right = st.columns([1.35, 0.85], gap="large")
with left:
    st.subheader("Start a research investigation")
    topic = st.text_area(
        "Research topic",
        placeholder="Example: Explainable AI for medical image diagnosis",
        height=105,
    )
    col1, col2 = st.columns(2)
    with col1:
        max_papers = st.slider("Papers to discover", min_value=3, max_value=10, value=5)
    with col2:
        year_from = st.selectbox("Publication period", ["Any year", "Since 2020", "Since 2022", "Since 2024"])
    run = st.button("🚀 Start multi-agent research", type="primary", use_container_width=True)

with right:
    st.subheader("What the agents deliver")
    st.markdown("""
    <div class="panel">
      <b>01 · Discovery</b><br><span class="small-muted">Find relevant papers and bibliographic details.</span><br><br>
      <b>02 · Literature review</b><br><span class="small-muted">Compare methods, datasets and findings.</span><br><br>
      <b>03 · Research gaps</b><br><span class="small-muted">Highlight limitations and open questions.</span><br><br>
      <b>04 · Summaries</b><br><span class="small-muted">Explain key papers in accessible language.</span><br><br>
      <b>05 · Final report</b><br><span class="small-muted">Create a structured research assistance report.</span>
    </div>
    """, unsafe_allow_html=True)

if run:
    if not topic.strip():
        st.warning("Enter a research topic first.")
        st.stop()
    if not os.getenv("GROQ_API_KEY"):
        st.error("GROQ_API_KEY is missing. Add it to your .env file and restart the app.")
        st.stop()

    date_filter = {
        "Any year": None,
        "Since 2020": "2020",
        "Since 2022": "2022",
        "Since 2024": "2024",
    }[year_from]

    st.markdown("---")
    st.subheader("Research in progress")
    status = st.status("Preparing the CrewAI research team…", expanded=True)
    try:
        from research_crew import run_research
        status.write("Connecting to arXiv and initializing five specialized agents.")
        result = run_research(topic=topic.strip(), max_papers=max_papers, year_from=date_filter)
        status.update(label="Research workflow completed", state="complete", expanded=False)

        output_text = str(result)
        output_dir = Path("outputs")
        output_dir.mkdir(exist_ok=True)
        stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_path = output_dir / f"research_report_{stamp}.md"
        report_path.write_text(output_text, encoding="utf-8")

        st.success("All five agents have completed their tasks.")
        st.markdown("### Research report")
        st.markdown(output_text)
        st.download_button(
            "⬇️ Download research report (.md)",
            data=output_text,
            file_name=report_path.name,
            mime="text/markdown",
        )
        st.caption(f"Saved locally to: {report_path}")
    except Exception as exc:
        status.update(label="Research workflow failed", state="error")
        st.error(f"Could not complete the research workflow: {exc}")
        st.info("Check your Groq API key, internet connection and terminal logs.")
