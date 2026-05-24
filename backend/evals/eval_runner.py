from dotenv import load_dotenv

load_dotenv()

import os
from pathlib import Path
from uuid import uuid4

from langgraph.types import Command

from graph.graph import compiled_graph

GOLDEN_QUERIES = [
    "Analyze the competitive landscape of AI coding assistants",
    "What are the latest trends in large language model research",
    "Compare the top vector databases for production AI applications",
    "What is the current state of autonomous vehicle technology",
    "Analyze the open source LLM ecosystem in 2025",
    "What are the best practices for deploying machine learning models in production",
    "Compare cloud providers AWS vs Azure vs GCP for AI workloads",
    "What is the current state of AI regulation globally",
    "Analyze the generative AI startup funding landscape",
    "What are the emerging trends in AI agents and multi-agent systems",
]


def _validate_env() -> bool:
    missing = [k for k in ("GROQ_API_KEY", "TAVILY_API_KEY") if not os.getenv(k)]
    if not missing:
        return True
    env_path = Path(__file__).resolve().parent.parent / ".env"
    print("Missing env vars:", ", ".join(missing))
    print(f"Set them in: {env_path}")
    return False


def _run_query(query: str) -> dict | None:
    """
    Run the graph for a single query, automatically resuming at the human checkpoint.
    Returns the final state if successful, None if there was an error.
    """
    session_id = str(uuid4())
    config = {"configurable": {"thread_id": session_id}}
    initial_state = {
        "query": query,
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

    try:
        hit_interrupt = False

        for chunk in compiled_graph.stream(initial_state, config=config, stream_mode="updates"):
            if "__interrupt__" in chunk:
                hit_interrupt = True
                break

        if hit_interrupt:
            for chunk in compiled_graph.stream(
                Command(resume="approved, proceed as planned"),
                config=config,
                stream_mode="updates",
            ):
                if "__interrupt__" in chunk:
                    break

        state_snapshot = compiled_graph.get_state(config)
        return state_snapshot.values

    except Exception as e:
        print(f"    ERROR: {e}")
        return None


def _check_quality(final_values: dict) -> tuple[bool, str]:
    """
    Check if the final output meets quality criteria.
    Returns (passed: bool, reason: str)
    """
    final_report = final_values.get("final_report") or final_values.get("draft_report")

    if final_report is None:
        return False, "No final report generated"

    sections = final_report.get("sections", [])
    if len(sections) < 2:
        return False, f"Only {len(sections)} section(s), need >= 2"

    total_sources = final_report.get("total_sources", 0)
    if total_sources < 3:
        return False, f"Only {total_sources} source(s), need >= 3"

    executive_summary = final_report.get("executive_summary", "").strip()
    if not executive_summary:
        return False, "Empty executive summary"

    if sections:
        confidences = [s.get("confidence", 0) for s in sections if isinstance(s, dict)]
        avg_confidence = sum(confidences) / len(confidences) if confidences else 0
        if avg_confidence < 0.6:
            return False, f"Average confidence {avg_confidence:.2f}, need >= 0.6"

    return True, "All checks passed"


def eval_runner() -> None:
    if not _validate_env():
        return

    print("=" * 70)
    print("EVAL RUNNER: Testing 10 golden queries")
    print("=" * 70)

    passed = 0
    failed = 0

    for i, query in enumerate(GOLDEN_QUERIES, start=1):
        print(f"\n[{i}/10] {query}")

        final_values = _run_query(query)

        if final_values is None:
            print("  ✗ FAIL: Graph execution failed")
            failed += 1
            continue

        is_pass, reason = _check_quality(final_values)

        if is_pass:
            print(f"  ✓ PASS: {reason}")
            passed += 1
        else:
            print(f"  ✗ FAIL: {reason}")
            failed += 1

    print("\n" + "=" * 70)
    print(f"FINAL SCORE: {passed}/{len(GOLDEN_QUERIES)} passed")
    print("=" * 70)


if __name__ == "__main__":
    eval_runner()
