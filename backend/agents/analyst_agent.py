from dotenv import load_dotenv

load_dotenv()

import os

from langchain_groq import ChatGroq

from schemas.report import AgentEvent, AnalystOutput, GraphState


def _format_search_results(raw_search_results: list[dict]) -> str:
    formatted_sources: list[str] = []

    for index, result in enumerate(raw_search_results[:8], start=1):
        title = result.get("title", "")
        url = result.get("url", "")
        snippet = result.get("snippet", "")[:200]
        formatted_sources.append(
            f"Source {index}: {title}\nURL: {url}\nSnippet: {snippet}"
        )

    return "\n\n".join(formatted_sources)


def run_analyst(state: GraphState) -> dict:
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise RuntimeError("GROQ_API_KEY is not set")

    query = state["query"]
    raw_search_results = state["raw_search_results"]
    search_results_text = _format_search_results(raw_search_results)

    client = ChatGroq(
        api_key=api_key,
        model="llama-3.3-70b-versatile",
    )
    structured_client = client.with_structured_output(AnalystOutput)

    prompt = (
        "You are a research analyst. Here is the original query and all the search results. "
        "Extract key findings with source references, note any contradictions between sources, "
        "identify coverage gaps, and list the URLs you used.\n\n"
        f"Original query: {query}\n\n"
        f"Search results:\n{search_results_text}"
    )

    analyst_output = structured_client.invoke(prompt)

    event = AgentEvent(
        agent="analyst",
        status="completed",
        message="Analysis complete",
        data={"findings_count": len(analyst_output.key_findings)},
    )

    return {
        "analyst_notes": analyst_output.model_dump(),
        "trace_log": [event.model_dump()],
    }
