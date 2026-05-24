from dotenv import load_dotenv

load_dotenv()

from schemas.report import AgentEvent, GraphState
from tools.tavily_search import build_search_queries, run_search


def run_search_agent(state: GraphState) -> dict:
    query = state["query"]
    sub_tasks = state["sub_tasks"]

    search_queries = build_search_queries(query, sub_tasks)
    search_results = run_search(search_queries)
    result_dicts = [result.model_dump() for result in search_results]

    event = AgentEvent(
        agent="search_agent",
        status="completed",
        message=f"Found {len(result_dicts)} sources",
        data={"source_count": len(result_dicts)},
    )

    return {
        "raw_search_results": result_dicts,
        "trace_log": [event.model_dump()],
    }
