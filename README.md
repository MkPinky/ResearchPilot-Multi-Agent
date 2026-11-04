# ResearchPilot — CrewAI Multi-Agent Research Paper Assistant

A student project that uses five collaborating CrewAI agents to discover papers, synthesize literature, identify research gaps, summarize papers and write a Markdown report.

## Software and versions

- Python 3.11 recommended (CrewAI supports Python >=3.10 and <3.14).
- PyCharm Community/Professional or VS Code.
- Groq API key for LLM inference.
- Internet access for arXiv search and package installation.

CrewAI version is pinned in `requirements.txt` to reduce dependency drift.

## Agents

1. **Paper Discovery Agent** — searches the arXiv API and collects metadata and abstracts.
2. **Literature Review Agent** — compares research objectives, methods, findings and limitations.
3. **Research Gap Agent** — identifies stated limitations and cautious inferred opportunities.
4. **Paper Summarizer Agent** — summarizes selected papers.
5. **Report Writer Agent** — creates the final Markdown report.

## Project structure

```text
Research_Paper_Multi_Agent/
├── app.py
├── research_crew.py
├── tools/
│   ├── __init__.py
│   └── arxiv_search_tool.py
├── requirements.txt
├── .env.example
├── .gitignore
├── run_windows.bat
├── README.md
└── outputs/
```

## Setup on Windows / PyCharm

1. Extract the ZIP.
2. Open the extracted `Research_Paper_Multi_Agent` folder in PyCharm.
3. Open PyCharm Terminal in the project root.
4. Create and activate a Python 3.11 virtual environment:

```powershell
py -3.11 -m venv .venv
.venv\Scripts\Activate.ps1
```

5. Install dependencies:

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

6. Copy `.env.example` to `.env`.
7. Open `.env` and add your Groq API key:

```env
GROQ_API_KEY=your_actual_groq_api_key
GROQ_MODEL=openai/gpt-oss-20b
```

Get or manage the key at https://console.groq.com/. Never paste the key into chat or commit `.env` to GitHub.

8. Start the app:

```powershell
streamlit run app.py
```

Open the local URL shown by Streamlit, usually http://localhost:8501.

### Easier Windows option

You can double-click `run_windows.bat`. It creates the virtual environment, installs dependencies, creates `.env` from the example if needed, and launches Streamlit. If it creates `.env`, add your key and run the batch file again.

## How to use

1. Enter a research topic, e.g. `Explainable AI for medical image diagnosis`.
2. Choose how many papers to discover.
3. Choose a publication period.
4. Click **Start multi-agent research**.
5. Wait while the five agents work sequentially.
6. Review the generated report and download it as Markdown.

## Data and academic limitations

- Paper discovery uses the public arXiv API. It does not search every journal or publisher database.
- The initial literature synthesis is based on metadata and abstracts returned by arXiv. The agents are instructed not to claim that they read full papers.
- Research gaps are suggestions, not proof of novelty. Verify them through a wider systematic literature search.
- AI-generated summaries can contain errors. Check the original paper before citing it.
- Groq model availability, quotas and rate limits depend on your account and can change.

## Troubleshooting

**`GROQ_API_KEY is missing`** — check that `.env` exists in the project root and contains the key without extra quotes or spaces around `=`. Restart Streamlit after editing it.

**Model not available** — check the current model ID available in your Groq account and update `GROQ_MODEL` in `.env`. The app prepends the `groq/` provider prefix for CrewAI.

**Package installation fails** — confirm Python is 3.11, activate `.venv`, then run `pip install -r requirements.txt` again. If Windows reports a build-tool error, share the exact terminal error before changing package versions.

**No papers found** — try a broader topic with fewer specialized phrases. Search results depend on arXiv coverage and query wording.

## Sample topics

- Explainable AI for medical image diagnosis
- Federated learning for healthcare data privacy
- Deep learning for crop disease detection
- Large language models in education
- Cybersecurity threat detection using machine learning

## Sample evaluation checks

1. Does each discovered paper include a real arXiv URL and ID?
2. Are literature review claims traceable to the supplied abstracts?
3. Are explicit author limitations separated from inferred research gaps?
4. Does the report state that it is an abstract-based preliminary review?
5. Can the generated Markdown report be downloaded?

## License and use

Educational prototype. Verify paper metadata and all claims against original publications before academic use.
