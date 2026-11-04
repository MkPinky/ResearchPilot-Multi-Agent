
import os
from pathlib import Path
from datetime import datetime

import streamlit as st
from dotenv import load_dotenv


# ==================================================
# ENVIRONMENT CONFIGURATION
# ==================================================

# Load local .env file
load_dotenv()

# Load Streamlit Cloud secrets
try:
    if "GROQ_API_KEY" in st.secrets:
        os.environ.setdefault(
            "GROQ_API_KEY",
            st.secrets["GROQ_API_KEY"]
        )

    if "GROQ_MODEL" in st.secrets:
        os.environ.setdefault(
            "GROQ_MODEL",
            st.secrets["GROQ_MODEL"]
        )

except Exception:
    pass


# ==================================================
# PAGE CONFIGURATION
# ==================================================

st.set_page_config(
    page_title="ResearchPilot | Multi-Agent Research Assistant",
    page_icon="📚",
    layout="wide",
)


# ==================================================
# CUSTOM CSS
# ==================================================

st.markdown("""
<style>

@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@500;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
}

.stApp {
    background: #f5f7fb;
    color: #18263b;
}

.block-container {
    max-width: 1200px;
    padding-top: 2rem;
    padding-bottom: 3rem;
}

/* HERO SECTION */

.hero {
    background: linear-gradient(
        115deg,
        #14243b,
        #234a78 70%,
        #3868d8
    );
    padding: 38px 42px;
    border-radius: 22px;
    color: white;
    margin-bottom: 30px;
    box-shadow: 0 12px 30px rgba(20, 36, 59, 0.12);
}

.hero h1 {
    font-family: 'Manrope', sans-serif;
    color: #ffffff;
    font-size: 2.6rem;
    font-weight: 800;
    letter-spacing: -0.04em;
    margin: 0;
    padding: 0;
}

.hero p {
    color: #dbe6f8;
    max-width: 760px;
    font-size: 1rem;
    margin-top: 12px;
    line-height: 1.7;
}

.eyebrow {
    color: #9db8ff;
    font-size: 0.72rem;
    letter-spacing: 0.16em;
    font-weight: 800;
    text-transform: uppercase;
    margin-bottom: 12px;
}

/* INFORMATION PANEL */

.panel {
    background: #ffffff;
    border: 1px solid #e5eaf2;
    border-radius: 16px;
    padding: 24px;
    margin-top: 10px;
    box-shadow: 0 5px 18px rgba(20, 36, 59, 0.04);
}

.panel-item {
    margin-bottom: 20px;
}

.panel-item:last-child {
    margin-bottom: 0;
}

.panel-title {
    color: #234a78;
    font-size: 1rem;
    font-weight: 700;
}

.small-muted {
    color: #718096;
    font-size: 0.88rem;
    line-height: 1.5;
}

/* SIDEBAR */

[data-testid="stSidebar"] {
    background: #ffffff;
}

[data-testid="stSidebar"] h1 {
    color: #14243b;
    font-family: 'Manrope', sans-serif;
    font-weight: 800;
}

/* BUTTONS */

div[data-testid="stButton"] button {
    border-radius: 11px;
    font-weight: 700;
    min-height: 46px;
}

/* INPUTS */

.stTextArea textarea {
    border-radius: 12px;
}

.stSelectbox div[data-baseweb="select"] {
    border-radius: 10px;
}

/* REPORT */

.report-container {
    background: #ffffff;
    border: 1px solid #e5eaf2;
    border-radius: 16px;
    padding: 24px;
}

</style>
""", unsafe_allow_html=True)


# ==================================================
# HERO SECTION
# ==================================================

st.markdown("""
<div class="hero">
<div class="eyebrow">CREWAI · MULTI-AGENT RESEARCH WORKSPACE</div>
<h1>ResearchPilot</h1>
<p>Discover research papers, compare findings, identify research gaps and generate a structured literature review with a collaborative team of AI agents.</p>
</div>
""", unsafe_allow_html=True)


# ==================================================
# SIDEBAR
# ==================================================

with st.sidebar:

    st.title("📚 ResearchPilot")

    st.caption("Multi-Agent Research Paper Assistant")

    st.markdown("---")

    st.markdown("**🤖 Agent Team**")

    agents = [
        "🔍 Paper Discovery Agent",
        "📖 Literature Review Agent",
        "🎯 Research Gap Agent",
        "📝 Paper Summarizer Agent",
        "📑 Report Writer Agent",
    ]

    for agent in agents:
        st.markdown(agent)

    st.markdown("---")

    st.markdown("**Technology Stack**")

    st.caption("Python · Streamlit")
    st.caption("CrewAI · Groq")
    st.caption("arXiv Research API")

    st.markdown("---")

    st.caption("Sources: arXiv metadata and abstracts")
    st.caption("LLM: Groq · Orchestration: CrewAI")


# ==================================================
# MAIN LAYOUT
# ==================================================

left, right = st.columns(
    [1.35, 0.85],
    gap="large"
)


# ==================================================
# RESEARCH INPUT
# ==================================================

with left:

    st.subheader("Start a Research Investigation")

    st.write(
        "Enter your research topic and configure the paper discovery settings."
    )

    topic = st.text_area(
        "Research Topic",
        placeholder="Example: Explainable AI for medical image diagnosis",
        height=110,
    )

    col1, col2 = st.columns(2)

    with col1:

        max_papers = st.slider(
            "Papers to discover",
            min_value=3,
            max_value=10,
            value=5,
        )

    with col2:

        year_from = st.selectbox(
            "Publication period",
            [
                "Any year",
                "Since 2020",
                "Since 2022",
                "Since 2024",
            ],
        )

    st.markdown("")

    run = st.button(
        "🚀 Start Multi-Agent Research",
        type="primary",
        use_container_width=True,
    )


# ==================================================
# AGENT INFORMATION PANEL
# ==================================================

with right:

    st.subheader("What the Agents Deliver")

    st.markdown("""
<div class="panel">

<div class="panel-item">
<div class="panel-title">01 · Discovery</div>
<div class="small-muted">Find relevant research papers and bibliographic details.</div>
</div>

<div class="panel-item">
<div class="panel-title">02 · Literature Review</div>
<div class="small-muted">Compare research methods, datasets and findings.</div>
</div>

<div class="panel-item">
<div class="panel-title">03 · Research Gaps</div>
<div class="small-muted">Identify limitations and potential research opportunities.</div>
</div>

<div class="panel-item">
<div class="panel-title">04 · Paper Summaries</div>
<div class="small-muted">Explain important research papers in accessible language.</div>
</div>

<div class="panel-item">
<div class="panel-title">05 · Final Report</div>
<div class="small-muted">Generate a structured academic research assistance report.</div>
</div>

</div>
""", unsafe_allow_html=True)


# ==================================================
# RUN RESEARCH WORKFLOW
# ==================================================

if run:

    # Validate research topic
    if not topic.strip():

        st.warning("Please enter a research topic first.")

        st.stop()

    # Validate Groq API key
    if not os.getenv("GROQ_API_KEY"):

        st.error(
            "GROQ_API_KEY is missing. "
            "Configure it in your local .env file "
            "or Streamlit Cloud Secrets."
        )

        st.stop()

    # Publication year filter
    date_filter = {
        "Any year": None,
        "Since 2020": "2020",
        "Since 2022": "2022",
        "Since 2024": "2024",
    }[year_from]

    st.markdown("---")

    st.subheader("Research in Progress")

    status = st.status(
        "Preparing the CrewAI research team...",
        expanded=True,
    )

    try:

        from research_crew import run_research

        status.write(
            "Connecting to arXiv and initializing five specialized agents."
        )

        # Execute five-agent research workflow
        result = run_research(
            topic=topic.strip(),
            max_papers=max_papers,
            year_from=date_filter,
        )

        status.update(
            label="Research workflow completed",
            state="complete",
            expanded=False,
        )

        # Convert result into Markdown
        output_text = str(result)

        # Create output directory
        output_dir = Path("outputs")
        output_dir.mkdir(exist_ok=True)

        # Generate report filename
        stamp = datetime.now().strftime(
            "%Y%m%d_%H%M%S"
        )

        report_path = (
            output_dir /
            f"research_report_{stamp}.md"
        )

        # Save report
        report_path.write_text(
            output_text,
            encoding="utf-8",
        )

        st.success(
            "All five agents have completed their tasks!"
        )

        # Display final research report
        st.markdown("---")
        st.subheader("📑 Research Report")

        st.markdown(
            output_text
        )

        # Download Markdown report
        st.download_button(
            label="⬇️ Download Research Report (.md)",
            data=output_text,
            file_name=report_path.name,
            mime="text/markdown",
            use_container_width=True,
        )

        st.caption(
            f"Report saved to: {report_path}"
        )

    except Exception as exc:

        status.update(
            label="Research workflow failed",
            state="error",
        )

        st.error(
            f"Could not complete the research workflow: {exc}"
        )

        st.info(
            "Check your Groq API key, internet connection "
            "and application logs."
        )


# ==================================================
# FOOTER
# ==================================================

st.markdown("---")

st.markdown(
    """
    <div style="text-align:center; color:#718096; padding:12px;">
        <b>ResearchPilot</b> · AI-Powered Multi-Agent Research Assistant<br>
        <span style="font-size:12px;">
        Built with Python, Streamlit, CrewAI and Groq
        </span>
    </div>
    """,
    unsafe_allow_html=True,
)
