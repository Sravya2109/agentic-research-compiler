from dotenv import load_dotenv

load_dotenv()

import json
import threading
import time
from uuid import uuid4

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from langgraph.types import Command
from pydantic import BaseModel

from graph.graph import compiled_graph
from schemas.report import AgentEvent
from tools.guardrails import validate_query


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

sessions: dict = {}


class RunRequest(BaseModel):
    query: str


class ResumeRequest(BaseModel):
    feedback: str


def _extract_interrupt_data(chunk: dict) -> dict:
    try:
        interrupts = chunk.get("__interrupt__", ())
        first = interrupts[0] if interrupts else None
        value = first.value if first and hasattr(first, "value") else {}
        return value if isinstance(value, dict) else {}
    except Exception:
        return {}


def _stream_graph(input_val, config: dict, session_id: str) -> bool:
    """
    Stream the graph using update mode, appending trace_log events to the session
    as each node completes. Returns True if the graph paused (interrupt), False if
    it ran to completion.
    """
    for chunk in compiled_graph.stream(input_val, config=config, stream_mode="updates"):
        if "__interrupt__" in chunk:
            interrupt_data = _extract_interrupt_data(chunk)
            state_snapshot = compiled_graph.get_state(config)
            tl = list(state_snapshot.values.get("trace_log", []))
            sessions[session_id]["trace_log"] = tl
            sessions[session_id]["interrupt_data"] = interrupt_data
            sessions[session_id]["paused"] = True
            return True

        for node_name, node_output in chunk.items():
            if node_name.startswith("__"):
                continue
            if isinstance(node_output, dict) and "trace_log" in node_output:
                sessions[session_id]["trace_log"].extend(node_output["trace_log"])

    return False


def run_graph(session_id: str, initial_state: dict, config: dict) -> None:
    try:
        paused = _stream_graph(initial_state, config, session_id)
        if not paused:
            state_snapshot = compiled_graph.get_state(config)
            final_values = state_snapshot.values
            sessions[session_id]["final_report"] = (
                final_values.get("final_report") or final_values.get("draft_report")
            )
            sessions[session_id]["done"] = True
    except Exception as error:
        sessions[session_id]["done"] = True
        sessions[session_id]["error"] = str(error)


def run_graph_resume(session_id: str, feedback: str, config: dict) -> None:
    try:
        _stream_graph(Command(resume=feedback), config, session_id)
        state_snapshot = compiled_graph.get_state(config)
        final_values = state_snapshot.values
        sessions[session_id]["final_report"] = (
            final_values.get("final_report") or final_values.get("draft_report")
        )
        sessions[session_id]["done"] = True
    except Exception as error:
        sessions[session_id]["done"] = True
        sessions[session_id]["error"] = str(error)


@app.post("/run")
def run(request: RunRequest) -> dict:
    is_valid, reason = validate_query(request.query)
    if not is_valid:
        raise HTTPException(status_code=400, detail=reason)

    session_id = str(uuid4())
    config = {"configurable": {"thread_id": session_id}}
    initial_state = {
        "query": request.query,
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

    sessions[session_id] = {
        "config": config,
        "trace_log": [],
        "done": False,
        "paused": False,
        "interrupt_data": {},
        "final_report": None,
        "error": None,
    }

    threading.Thread(
        target=run_graph, args=(session_id, initial_state, config), daemon=True
    ).start()

    return {"session_id": session_id}


@app.get("/stream/{session_id}")
def stream(session_id: str) -> StreamingResponse:
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")

    def event_generator():
        last_index = 0
        checkpoint_sent = False

        while True:
            session = sessions.get(session_id)
            if session is None:
                break

            trace_log = session.get("trace_log", [])
            while last_index < len(trace_log):
                yield f"data: {json.dumps(trace_log[last_index])}\n\n"
                last_index += 1

            if session.get("paused") and not checkpoint_sent:
                checkpoint_event = AgentEvent(
                    agent="human_checkpoint",
                    status="paused",
                    message="Awaiting human review",
                    data=session.get("interrupt_data") or {},
                )
                yield f"data: {json.dumps(checkpoint_event.model_dump())}\n\n"
                checkpoint_sent = True

            if session.get("error"):
                yield f"data: {json.dumps({'agent': 'system', 'status': 'error', 'message': session['error'], 'data': None})}\n\n"
                break

            if session.get("done"):
                final_report = session.get("final_report")
                if final_report is not None:
                    yield f"data: {json.dumps({'agent': 'system', 'status': 'final_report', 'message': 'Final report ready', 'data': final_report})}\n\n"
                break

            time.sleep(0.3)

    return StreamingResponse(event_generator(), media_type="text/event-stream")


@app.post("/resume/{session_id}")
def resume(session_id: str, request: ResumeRequest) -> dict:
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")

    session = sessions[session_id]
    if not session.get("paused"):
        raise HTTPException(status_code=400, detail="Session is not paused at a checkpoint")

    config = session["config"]
    sessions[session_id]["paused"] = False

    threading.Thread(
        target=run_graph_resume,
        args=(session_id, request.feedback, config),
        daemon=True,
    ).start()

    return {"status": "resumed"}


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}
