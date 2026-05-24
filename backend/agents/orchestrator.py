from dotenv import load_dotenv

load_dotenv()

import json
import os

from langchain_groq import ChatGroq

from schemas.report import AgentEvent, GraphState


def run_orchestrator(state: GraphState) -> dict:
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise RuntimeError("GROQ_API_KEY is not set")

    client = ChatGroq(
        api_key=api_key,
        model="llama-3.3-70b-versatile",
    )

    query = state["query"]
    prompt = (
        "decompose the query into 3-5 specific researchable sub-tasks, "
        "return them as a JSON array of strings, nothing else\n\n"
        f"Query: {query}"
    )

    response = client.invoke(prompt)
    content = response.content
    if isinstance(content, list):
        content = "".join(
            block.get("text", "") if isinstance(block, dict) else str(block)
            for block in content
        )

    sub_tasks = json.loads(content)

    event = AgentEvent(
        agent="orchestrator",
        status="completed",
        message="Query decomposed into sub-tasks",
        data={"sub_tasks": sub_tasks},
    )

    return {
        "sub_tasks": sub_tasks,
        "trace_log": [event.model_dump()],
    }
