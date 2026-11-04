import os
import re
import time

from crewai import Agent, Crew, LLM, Process, Task
from tools.arxiv_search_tool import search_arxiv


def shorten_papers(papers_data: str, abstract_limit: int = 350) -> str:
    """Shorten abstracts while preserving paper metadata."""
    papers = papers_data.split("\n---\n")
    shortened = []
    for paper in papers:
        match = re.search(r"Abstract:\s*(.*)", paper, re.DOTALL)
        if match:
            original = match.group(1).strip()
            abstract = original[:abstract_limit]
            if len(original) > abstract_limit:
                abstract += "..."
            paper = paper[:match.start()] + "Abstract: " + abstract
        shortened.append(paper.strip())
    return "\n\n---\n\n".join(shortened)


def clean_report(text: str) -> str:
    if not text:
        return text
    cleaned = text.strip()
    cleaned = re.sub(
        r"^\s*(?:Thought:\s*.*?\n+)+", "", cleaned,
        flags=re.IGNORECASE | re.DOTALL,
    )
    cleaned = re.sub(
        r"^\s*#{1,3}\s*Final Answer\s*\n+", "", cleaned,
        flags=re.IGNORECASE,
    )
    cleaned = re.sub(
        r"^\s*Final Answer\s*:?\s*\n+", "", cleaned,
        flags=re.IGNORECASE,
    )
    return cleaned.strip()


def make_llm(model: str, api_key: str, max_tokens: int) -> LLM:
    # GPT-OSS needs enough completion budget for reasoning AND the final answer.
    return LLM(
        model=f"groq/{model}",
        api_key=api_key,
        temperature=0.1,
        max_tokens=max_tokens,
    )


def pause_between_agents(_task_output):
    # Groq applies a rolling TPM limit. Give the window time to clear.
    print("\n⏳ Waiting 65 seconds before the next agent to avoid Groq rate limits...")
    time.sleep(65)


def run_research(
    topic: str,
    max_papers: int = 2,
    year_from: str | None = None,
):
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise RuntimeError(
            "GROQ_API_KEY is missing. Add it to your .env file and restart Streamlit."
        )

    model_name = os.getenv("GROQ_MODEL", "openai/gpt-oss-20b").strip()

    # Limit source volume, not the model's reasoning budget.
    paper_count = max(1, min(int(max_papers), 2))
    papers_data = search_arxiv(
        query=topic,
        max_results=paper_count,
        year_from=year_from,
    )
    if not papers_data or papers_data.startswith("No arXiv papers found"):
        raise RuntimeError(
            "No arXiv papers were returned. Try a broader research topic."
        )

    papers_data = shorten_papers(papers_data, abstract_limit=350)
    year_instruction = (
        f"Publication preference: {year_from} onward."
        if year_from else "Consider any publication year."
    )

    # Do not use tiny output caps with GPT-OSS: reasoning tokens also consume budget.
    discovery_llm = make_llm(model_name, api_key, 1400)
    literature_llm = make_llm(model_name, api_key, 1600)
    gap_llm = make_llm(model_name, api_key, 1200)
    summary_llm = make_llm(model_name, api_key, 1400)
    report_llm = make_llm(model_name, api_key, 2200)

    discovery_agent = Agent(
        role="Research Paper Discovery Specialist",
        goal="Accurately organize the supplied arXiv paper records.",
        backstory=(
            "You are an academic research librarian. Preserve the supplied "
            "bibliographic details exactly and never invent metadata."
        ),
        llm=discovery_llm, verbose=False,
        allow_delegation=False, max_iter=1,
    )
    literature_agent = Agent(
        role="Literature Review Analyst",
        goal="Compare research papers using only supplied abstracts and metadata.",
        backstory=(
            "You are an academic researcher. Distinguish what the abstracts "
            "actually say from assumptions; do not claim full-text access."
        ),
        llm=literature_llm, verbose=False,
        allow_delegation=False, max_iter=1,
    )
    gap_agent = Agent(
        role="Research Gap Analyst",
        goal="Identify cautious and evidence-based research gaps.",
        backstory=(
            "You distinguish author-stated limitations from your own "
            "inferences and avoid overgeneralizing from a small sample."
        ),
        llm=gap_llm, verbose=False,
        allow_delegation=False, max_iter=1,
    )
    summarizer_agent = Agent(
        role="Research Paper Summarizer",
        goal="Summarize each selected paper accurately.",
        backstory=(
            "You explain academic papers clearly and use only information "
            "supported by the supplied abstracts and metadata."
        ),
        llm=summary_llm, verbose=False,
        allow_delegation=False, max_iter=1,
    )
    report_agent = Agent(
        role="Academic Report Writer",
        goal="Produce a complete, concise academic research report.",
        backstory=(
            "You are an academic technical writer. Include every requested "
            "section and never invent facts or references."
        ),
        llm=report_llm, verbose=False,
        allow_delegation=False, max_iter=1,
    )

    discovery_task = Task(
        description=(
            f"Research topic: {topic}\n{year_instruction}\n\n"
            "These records came directly from the arXiv API. List each paper "
            "with exact title, authors, publication date, arXiv ID and URL. "
            "Add one brief abstract summary per paper. Do not invent details.\n\n"
            f"{papers_data}"
        ),
        expected_output=(
            "A complete numbered source list preserving all supplied metadata "
            "and one brief abstract summary per paper."
        ),
        agent=discovery_agent,
        callback=pause_between_agents,
    )

    literature_task = Task(
        description=(
            f"Write a comparative literature review for: {topic}\n"
            "For each selected paper, explain its objective, approach and "
            "contribution in a short paragraph. Mention limitations only if "
            "supported by the supplied abstract. Cite arXiv IDs. "
            "Do not claim full-text access. Aim for 180-250 words."
        ),
        expected_output="A concise comparative literature review citing each arXiv ID.",
        agent=literature_agent,
        context=[discovery_task],
        callback=pause_between_agents,
    )

    gap_task = Task(
        description=(
            f"Analyze research gaps for: {topic}\n"
            "Use only the literature review. Identify up to two possible gaps "
            "and up to two future research questions. Label each as "
            "'author-stated limitation' or 'inference'. Cite arXiv IDs. "
            "Keep the answer near 120-160 words."
        ),
        expected_output="Up to two evidence-based gaps and two research questions.",
        agent=gap_agent,
        context=[literature_task],
        callback=pause_between_agents,
    )

    summary_task = Task(
        description=(
            f"Summarize the selected papers for: {topic}\n"
            "For each paper, give its objective, approach and relevance in "
            "two or three concise sentences. Use only the discovery results "
            "and abstracts. Keep the whole answer under 180 words."
        ),
        expected_output="A concise labelled summary for every selected paper.",
        agent=summarizer_agent,
        context=[discovery_task],
        callback=pause_between_agents,
    )

    report_task = Task(
        description=(
            f"Write the final academic research assistance report on: {topic}\n\n"
            "Include all nine sections, using concise Markdown and no table:\n"
            "1. Introduction.\n"
            f"2. Research Scope and Search Method: arXiv API, query topic, "
            f"{paper_count} retrieved records, and abstract-based scope.\n"
            "3. Selected Research Papers: actual titles and arXiv IDs.\n"
            "4. Comparative Literature Review.\n"
            "5. Research Gaps.\n"
            "6. Future Research Questions.\n"
            "7. Paper Summaries.\n"
            "8. Conclusion.\n"
            "9. References: exact supplied titles, authors, arXiv IDs and URLs.\n\n"
            "State clearly that this is a preliminary review based on arXiv "
            "metadata and shortened abstracts, not full-text review. Use only "
            "the previous agents' evidence. Do not invent facts or references. "
            "Return only the report."
        ),
        expected_output=(
            "A complete Markdown report with all nine sections and accurate references."
        ),
        agent=report_agent,
        context=[literature_task, gap_task, summary_task],
    )

    crew = Crew(
        agents=[
            discovery_agent,
            literature_agent,
            gap_agent,
            summarizer_agent,
            report_agent,
        ],
        tasks=[
            discovery_task,
            literature_task,
            gap_task,
            summary_task,
            report_task,
        ],
        process=Process.sequential,
        verbose=True,
    )

    try:
        result = crew.kickoff(
            inputs={"topic": topic, "max_papers": paper_count}
        )
    except Exception as exc:
        message = str(exc)
        if "None or empty" in message or "Invalid response from LLM" in message:
            raise RuntimeError(
                "Groq returned an empty response to one of the agents. "
                "Wait 2 minutes and retry once. If it repeats, run the "
                "Groq connection test from the troubleshooting instructions. "
                f"Original error: {message}"
            ) from exc
        raise

    if hasattr(result, "raw") and isinstance(result.raw, str):
        cleaned = clean_report(result.raw)
        try:
            result.raw = cleaned
        except Exception:
            object.__setattr__(result, "raw", cleaned)

    return result
