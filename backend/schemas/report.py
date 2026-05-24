from typing import Annotated, TypedDict
import operator

from pydantic import BaseModel, Field


class SearchResult(BaseModel):
    url: str
    title: str
    snippet: str
    published_date: str | None = None


class AnalystOutput(BaseModel):
    key_findings: list[str]
    contradictions: list[str]
    coverage_gaps: list[str]
    sources_used: list[str]


class ReportSection(BaseModel):
    title: str
    content: str
    citations: list[str]
    confidence: float = Field(ge=0, le=1)


class ReportModel(BaseModel):
    title: str
    executive_summary: str
    sections: list[ReportSection]
    key_takeaways: list[str]
    limitations: str
    total_sources: int


class CritiqueOutput(BaseModel):
    passed: bool
    issues: list[str]
    feedback: str
    hallucination_flags: list[str]


class AgentEvent(BaseModel):
    agent: str
    status: str
    message: str
    data: dict | None = None


class GraphState(TypedDict):
    query: str
    sub_tasks: list[str]
    raw_search_results: list[dict]
    analyst_notes: dict | None
    human_feedback: str | None
    draft_report: dict | None
    critique_result: dict | None
    retry_count: int
    final_report: dict | None
    trace_log: Annotated[list[dict], operator.add]
