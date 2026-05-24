from dotenv import load_dotenv

load_dotenv()

import os

from langchain_groq import ChatGroq

from schemas.report import AgentEvent, GraphState, ReportModel


def _format_analyst_notes(analyst_notes: dict) -> str:
    key_findings = analyst_notes.get("key_findings", [])[:5]
    contradictions = analyst_notes.get("contradictions", [])
    coverage_gaps = analyst_notes.get("coverage_gaps", [])
    sources_used = analyst_notes.get("sources_used", [])[:5]

    parts = [
        f"Key findings: {key_findings}",
        f"Contradictions: {contradictions}",
        f"Coverage gaps: {coverage_gaps}",
        f"Sources used: {sources_used}",
    ]
    return "\n".join(parts)


def run_writer(state: GraphState) -> dict:
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise RuntimeError("GROQ_API_KEY is not set")

    query = state["query"]
    analyst_notes = state["analyst_notes"] or {}
    human_feedback = state.get("human_feedback")

    client = ChatGroq(
        api_key=api_key,
        model="llama-3.3-70b-versatile",
    )
    structured_client = client.with_structured_output(ReportModel)

    prompt_parts = [
        f"Original query: {query}",
        f"Analyst notes:\n{_format_analyst_notes(analyst_notes)}",
    ]

    if human_feedback:
        prompt_parts.append(
            f"The user has provided this additional direction: {human_feedback}, please incorporate this into the report"
        )

    prompt_parts.append(
        "Write a structured research report with clear sections. Each section must have citations from the source URLs. "
        "Assign a confidence score between 0 and 1 to each section based on how well it is supported by sources. "
        "Include key takeaways and limitations."
    )

    report = structured_client.invoke("\n\n".join(prompt_parts))

    event = AgentEvent(
        agent="writer",
        status="completed",
        message="Draft report written",
        data={"section_count": len(report.sections)},
    )

    return {
        "draft_report": report.model_dump(),
        "trace_log": [event.model_dump()],
    }
