from dotenv import load_dotenv

load_dotenv()

from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, StateGraph
from langgraph.types import Command, interrupt

from agents import run_analyst, run_critique, run_orchestrator, run_search_agent, run_writer
from schemas.report import AgentEvent, GraphState


def human_checkpoint(state: GraphState) -> dict:
    analyst_notes = state.get("analyst_notes") or {}
    key_findings = analyst_notes.get("key_findings", [])

    if key_findings:
        summary_lines = [f"{index}. {finding}" for index, finding in enumerate(key_findings, start=1)]
        summary = "Key findings:\n" + "\n".join(summary_lines)
    else:
        summary = "Key findings: None provided."

    human_feedback = interrupt(value={"summary": summary, "analyst_notes": analyst_notes})

    event = AgentEvent(
        agent="human_checkpoint",
        status="completed",
        message="Human feedback received",
    )

    return {
        "human_feedback": human_feedback,
        "trace_log": [event.model_dump()],
    }


def should_revise(state: GraphState) -> str:
    critique_result = state.get("critique_result") or {}
    retry_count = state.get("retry_count", 0)

    if critique_result.get("passed") is True:
        return "end"

    if retry_count >= 2:
        return "end"

    return "writer"


workflow = StateGraph(GraphState)

workflow.add_node("orchestrator", run_orchestrator)
workflow.add_node("search_agent", run_search_agent)
workflow.add_node("analyst", run_analyst)
workflow.add_node("human_checkpoint", human_checkpoint)
workflow.add_node("writer", run_writer)
workflow.add_node("critique", run_critique)

workflow.add_edge("orchestrator", "search_agent")
workflow.add_edge("search_agent", "analyst")
workflow.add_edge("analyst", "human_checkpoint")
workflow.add_edge("human_checkpoint", "writer")
workflow.add_edge("writer", "critique")

workflow.add_conditional_edges(
    "critique",
    should_revise,
    {
        "end": END,
        "writer": "writer",
    },
)

workflow.set_entry_point("orchestrator")

compiled_graph = workflow.compile(checkpointer=MemorySaver())
