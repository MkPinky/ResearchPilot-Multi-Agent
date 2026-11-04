import xml.etree.ElementTree as ET
from typing import Type

import requests
from pydantic import BaseModel, Field
from crewai.tools import BaseTool


ARXIV_API_URL = "https://export.arxiv.org/api/query"


def search_arxiv(
    query: str,
    max_results: int = 5,
    year_from: str | None = None,
) -> str:
    """Search arXiv directly using Python, without an LLM tool call."""

    search_query = f"all:{query}"

    if year_from:
        search_query += (
            f" AND submittedDate:[{year_from}01010000 TO 999912312359]"
        )

    params = {
        "search_query": search_query,
        "start": 0,
        "max_results": max_results,
        "sortBy": "relevance",
        "sortOrder": "descending",
    }

    try:
        response = requests.get(
            ARXIV_API_URL,
            params=params,
            timeout=30,
            headers={"User-Agent": "ResearchPilotStudentProject/1.0"},
        )
        response.raise_for_status()

        root = ET.fromstring(response.text)

        ns = {"atom": "http://www.w3.org/2005/Atom"}
        entries = root.findall("atom:entry", ns)

        if not entries:
            return f"No arXiv papers found for: {query}"

        results = []

        for index, entry in enumerate(entries, start=1):
            title = " ".join(
                entry.findtext("atom:title", default="", namespaces=ns).split()
            )

            abstract = " ".join(
                entry.findtext("atom:summary", default="", namespaces=ns).split()
            )

            published = entry.findtext(
                "atom:published", default="", namespaces=ns
            )

            paper_url = entry.findtext(
                "atom:id", default="", namespaces=ns
            )

            authors = [
                author.findtext(
                    "atom:name", default="", namespaces=ns
                )
                for author in entry.findall("atom:author", ns)
            ]

            arxiv_id = paper_url.rstrip("/").rsplit("/", 1)[-1]

            results.append(
                f"PAPER {index}\n"
                f"Title: {title}\n"
                f"Authors: {', '.join(authors)}\n"
                f"Published: {published[:10]}\n"
                f"arXiv ID: {arxiv_id}\n"
                f"URL: {paper_url}\n"
                f"Abstract: {abstract}\n"
            )

        return "\n---\n".join(results)

    except requests.RequestException as exc:
        raise RuntimeError(f"arXiv API request failed: {exc}") from exc

    except ET.ParseError as exc:
        raise RuntimeError(f"Could not parse arXiv response: {exc}") from exc


class ArxivSearchInput(BaseModel):
    query: str = Field(
        ...,
        description="Research topic or keywords to search on arXiv.",
    )
    max_results: int = Field(
        5,
        ge=1,
        le=10,
        description="Maximum number of papers to return.",
    )


class ArxivSearchTool(BaseTool):
    name: str = "arXiv Research Paper Search"

    description: str = (
        "Search arXiv for scholarly research papers and retrieve "
        "their titles, authors, publication dates, IDs, URLs and abstracts."
    )

    args_schema: Type[BaseModel] = ArxivSearchInput

    def _run(self, query: str, max_results: int = 5) -> str:
        return search_arxiv(query, max_results)