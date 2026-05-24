from dotenv import load_dotenv

load_dotenv()

import json
import os
from pathlib import Path

from langgraph.types import Command

from graph.graph import compiled_graph

AGENT_LABELS = {
    "orchestrator": "Orchestrator",
    "search_agent": "Search Agent",
    "analyst": "Analyst",
    "human_checkpoint": "Human Checkpoint",
    "writer": "Writer",
    "critique": "Critique",
}


def _validate_required_env() -> bool:
    missing = [k for k in ("GROQ_API_KEY", "TAVILY_API_KEY") if not os.getenv(k)]
    if not missing:
        return True
    env_path = Path(__file__).resolve().parent / ".env"
    print("Cannot run graph: missing required environment variables.")
    print("Missing:", ", ".join(missing))
    print(f"Set them in: {env_path}")
    return False


def _stream_phase(input_val, config: dict) -> dict | None:
    """
    Stream the graph in update mode. Prints each agent event as it arrives.
    Returns the interrupt value dict if the graph pauses, else None.
    """
    for chunk in compiled_graph.stream(input_val, config=config, stream_mode="updates"):
        if "__interrupt__" in chunk:
            interrupts = chunk["__interrupt__"]
            first = interrupts[0] if interrupts else None
            value = first.value if first and hasattr(first, "value") else {}
            return value if isinstance(value, dict) else {}

        for node_name, node_output in chunk.items():
            if node_name.startswith("__"):
                continue
            label = AGENT_LABELS.get(node_name, node_name)
            if isinstance(node_output, dict):
                for evt in node_output.get("trace_log", []):
                    print(f"  [{label}] {evt.get('status')} — {evt.get('message')}")

    return None


def test_run() -> None:
    if not _validate_required_env():
        return

    initial_state = {
        "query": "Analyze the competitive landscape of AI coding assistants",
        "sub_tasks": [],
        "raw_search_results": [],
        "analyst_notes": None,
        "human_feedback": None,
        "draft_report": None,
        "critique_result": None,
        "retry_count": 0,
        "final_report": None,
        "trace_log": [],
    }
    config = {"configurable": {"thread_id": "test-001"}}

    # ── Phase 1: run until human checkpoint ───────────────────────────────────
    print("=" * 60)
    print("PHASE 1: Running until human checkpoint")
    print("=" * 60)

    interrupt_value = _stream_phase(initial_state, config)

    if interrupt_value is None:
        print("ERROR: Graph ran to completion without pausing. Check human_checkpoint node.")
        return

    print("\nGraph paused at human_checkpoint.")
    if interrupt_value:
        print("Interrupt value:")
        print(json.dumps(interrupt_value, indent=2, default=str))

    state_snapshot = compiled_graph.get_state(config)
    analyst_notes = state_snapshot.values.get("analyst_notes") or {}
    findings = analyst_notes.get("key_findings", [])
    if findings:
        print("\nAnalyst key findings:")
        for i, finding in enumerate(findings, start=1):
            print(f"  {i}. {finding}")

    # ── Phase 2: resume with feedback ─────────────────────────────────────────
    print("\n" + "=" * 60)
    print("PHASE 2: Resuming with feedback")
    print("=" * 60)

    extra_interrupt = _stream_phase(
        Command(resume="focus on pricing and market share"),
        config,
    )
    if extra_interrupt is not None:
        print(f"Unexpected second interrupt: {extra_interrupt}")

    # Pull final state from checkpointer and print summary
    final_snapshot = compiled_graph.get_state(config)
    final_values = final_snapshot.values

    print("\nAll agent events (accumulated):")
    for evt in final_values.get("trace_log", []):
        label = AGENT_LABELS.get(evt.get("agent", ""), evt.get("agent", ""))
        print(f"  [{label}] {evt.get('status')} — {evt.get('message')}")

    final_report = final_values.get("final_report") or final_values.get("draft_report")
    if final_report:
        print(f"\nFINAL REPORT TITLE:\n  {final_report.get('title')}")
        print(f"\nEXECUTIVE SUMMARY:\n  {final_report.get('executive_summary', '')}")
    else:
        print("\nNo final report found in state.")


if __name__ == "__main__":
    test_run()
