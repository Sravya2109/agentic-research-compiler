from dotenv import load_dotenv

load_dotenv()

import os

from langchain_groq import ChatGroq

from schemas.report import AgentEvent, CritiqueOutput, GraphState


def _format_draft_report(draft_report: dict) -> str:
    title = draft_report.get("title", "")
    executive_summary = draft_report.get("executive_summary", "")
    sections = draft_report.get("sections", [])
    key_takeaways = draft_report.get("key_takeaways", [])
    limitations = draft_report.get("limitations", "")
    total_sources = draft_report.get("total_sources", 0)

    section_texts: list[str] = []
    for index, section in enumerate(sections, start=1):
        section_texts.append(
            "\n".join(
                [
                    f"Section {index}: {section.get('title', '')}",
                    f"Content: {section.get('content', '')}",
                    f"Citations: {section.get('citations', [])}",
                    f"Confidence: {section.get('confidence', '')}",
                ]
            )
        )

    return "\n\n".join(
        [
            f"Title: {title}",
            f"Executive summary: {executive_summary}",
            "Sections:",
            *section_texts,
            f"Key takeaways: {key_takeaways}",
            f"Limitations: {limitations}",
            f"Total sources: {total_sources}",
        ]
    )


def _format_source_material(raw_search_results: list[dict]) -> str:
    source_texts: list[str] = []

    for index, result in enumerate(raw_search_results, start=1):
        source_texts.append(
            "\n".join(
                [
                    f"Source {index}:",
                    f"URL: {result.get('url', '')}",
                    f"Title: {result.get('title', '')}",
                    f"Snippet: {result.get('snippet', '')}",
                ]
            )
        )

    return "\n\n".join(source_texts)


def run_critique(state: GraphState) -> dict:
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise RuntimeError("GROQ_API_KEY is not set")

    draft_report = state["draft_report"] or {}
    raw_search_results = state["raw_search_results"]
    retry_count = state["retry_count"]

    client = ChatGroq(
        api_key=api_key,
        model="llama-3.3-70b-versatile",
    )
    structured_client = client.with_structured_output(CritiqueOutput)

    prompt = (
        "You are a strict research editor. Check if every claim in the report is supported by the provided sources. "
        "Flag any hallucinations or unsupported claims. Check if all sections have proper citations. Check if confidence scores are justified. "
        "Return passed=True only if the report meets high quality standards. Otherwise return passed=False with specific issues and actionable feedback for the writer.\n\n"
        f"Draft report:\n{_format_draft_report(draft_report)}\n\n"
        f"Source material:\n{_format_source_material(raw_search_results)}\n\n"
        f"Retry count: {retry_count}"
    )

    critique = structured_client.invoke(prompt)

    event = AgentEvent(
        agent="critique",
        status="completed" if critique.passed else "revision_needed",
        message="Report approved" if critique.passed else "Revision requested",
        data={"passed": critique.passed, "issues_count": len(critique.issues)},
    )

    return {
        "critique_result": critique.model_dump(),
        "retry_count": retry_count + 1,
        "trace_log": [event.model_dump()],
    }
