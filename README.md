# 🤖 Agentic Research Compiler

A production-grade multi-agent AI system that autonomously researches any topic and compiles a structured, cited report.

![Python](https://img.shields.io/badge/Python-3.11+-3776ab?style=flat-square&logo=python)
![React](https://img.shields.io/badge/React-18+-61dafb?style=flat-square&logo=react)
![LangGraph](https://img.shields.io/badge/LangGraph-0.2+-blue?style=flat-square)
![Groq](https://img.shields.io/badge/Groq-llama--3.3--70b-orange?style=flat-square)
![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)

## 📺 Live Demo

**[Coming soon]**

Watch a research query flow through the system:
- User submits: _"Analyze the competitive landscape of AI coding assistants"_
- Orchestrator breaks it into sub-tasks
- Search agent crawls web sources in parallel
- Analyst synthesizes findings with structured Pydantic models
- Human reviews analyst summary at checkpoint, provides feedback
- Writer generates a multi-section report with citations
- Critique agent validates claims against sources, sends back to writer if needed
- Final report delivered with confidence scores per section

---

## 🏗️ Architecture

### The 6-Agent Pipeline

```
Query Input
    ↓
[1] ORCHESTRATOR AGENT
    ├─ Decomposes query into 3-5 researchable sub-tasks
    └─ Output: sub_tasks: List[str]
    ↓
[2] SEARCH AGENT
    ├─ Calls Tavily API with optimized search queries
    ├─ Deduplicates URLs, caps at 10 total results
    └─ Output: raw_search_results: List[SearchResult]
    ↓
[3] ANALYST AGENT
    ├─ Synthesizes search findings using structured output (Pydantic)
    ├─ Identifies contradictions and coverage gaps
    └─ Output: AnalystOutput (key_findings, contradictions, coverage_gaps, sources_used)
    ↓
[4] HUMAN CHECKPOINT ⏸️
    ├─ LangGraph interrupt() pauses the graph
    ├─ User reviews analyst summary, approves or adds feedback
    └─ Resume via Command(resume=feedback)
    ↓
[5] WRITER AGENT
    ├─ Generates full ReportModel with sections
    ├─ Each section: title, content, citations, confidence score
    └─ Output: ReportModel (title, sections, key_takeaways, limitations)
    ↓
[6] CRITIQUE AGENT
    ├─ Validates all claims against source material
    ├─ Checks for hallucinations and unsupported claims
    ├─ If passed=True OR retry_count >= 2: END
    └─ If passed=False AND retry_count < 2: sends back to Writer (max 2 retries)
    ↓
Final Report to User
```

---

## 🎯 Key Patterns Implemented

### 1. **Multi-Agent Orchestration** (Supervisor Pattern)
A central orchestrator decomposes the research task into sub-tasks and coordinates sequential agent execution.

### 2. **Reflection Loop** (Critique-Revise)
The critique agent validates the draft report and sends it back to the writer for revision if needed. Max 2 retries.

### 3. **Human-in-the-Loop** (LangGraph Interrupt)
At the analysis checkpoint, `interrupt(value={...})` pauses execution. User reviews findings and resumes with `Command(resume=feedback)`.

### 4. **Structured Outputs** (Pydantic v2)
All agent outputs are typed with Pydantic models. Uses `llm.with_structured_output()` to force valid JSON.

### 5. **Tool Calling** (Web Search)
The search agent calls Tavily API via LangChain. Results are parsed and deduplicated.

### 6. **Real-Time Streaming** (Server-Sent Events)
FastAPI streams agent events to the frontend via SSE for live status updates.

### 7. **Observability** (LangSmith Tracing)
All LLM calls are traced via LangSmith. State accumulates event metadata for debugging.

### 8. **Evaluation Pipeline** (Golden Set)
`eval_runner.py` validates 10 golden queries against quality criteria.

### 9. **Guardrails** (Input Validation)
`tools/guardrails.py` validates query length, blocks dangerous phrases, detects hallucinations.

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| **LLM** | Groq (llama-3.3-70b-versatile) |
| **Orchestration** | LangGraph 0.2+ |
| **Language Models** | LangChain, langchain-groq |
| **Web Search** | Tavily API |
| **Data Validation** | Pydantic v2 |
| **Backend** | FastAPI |
| **Streaming** | Server-Sent Events |
| **Observability** | LangSmith |
| **Frontend** | React 18 + TypeScript |
| **Build Tool** | Vite |
| **Styling** | Tailwind CSS |

---

## 🚀 How to Run Locally

### Backend Setup

```bash
cd backend
python -m venv venv
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate

pip install -r requirements.txt
```

Configure `.env`:
```
GROQ_API_KEY=gsk_...
TAVILY_API_KEY=tvly-...
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=lsv2_...
LANGCHAIN_PROJECT=agentic-research-compiler
```

Test end-to-end:
```bash
python test_graph.py
```

Start server:
```bash
uvicorn api.main:app --reload
```
Server: `http://localhost:8000`

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```
Frontend: `http://localhost:5173`

### Run Evaluations

```bash
cd backend
python evals/eval_runner.py
```

---

## 📁 Project Structure

```
agentic-research-compiler/
├── backend/
│   ├── agents/               # 6 agent implementations
│   │   ├── orchestrator.py
│   │   ├── search_agent.py
│   │   ├── analyst_agent.py
│   │   ├── writer_agent.py
│   │   └── critique_agent.py
│   ├── graph/
│   │   └── graph.py          # LangGraph state machine
│   ├── schemas/
│   │   └── report.py         # Pydantic models
│   ├── tools/
│   │   ├── tavily_search.py
│   │   └── guardrails.py
│   ├── api/
│   │   └── main.py           # FastAPI endpoints
│   ├── evals/
│   │   └── eval_runner.py    # Golden set evaluation
│   ├── test_graph.py         # End-to-end test
│   └── requirements.txt
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── QueryInput.tsx
│   │   │   ├── AgentFeed.tsx
│   │   │   ├── CheckpointPanel.tsx
│   │   │   └── ReportView.tsx
│   │   └── App.tsx
│   ├── package.json
│   └── vite.config.ts
│
└── README.md
```

---

## 📊 Evaluation Criteria

Each query is evaluated on:
- ✓ Report exists (not None)
- ✓ Has ≥ 2 sections
- ✓ Cites ≥ 3 sources
- ✓ Average section confidence ≥ 0.6
- ✓ Non-empty executive summary

Run `eval_runner.py` after backend setup to see results.

---

## 🎓 Key Concepts for Interviews

- **Multi-agent orchestration**: Decompose complex tasks into sub-tasks, coordinate sequential execution
- **LLM structured outputs**: Use Pydantic v2 + `with_structured_output()` for guaranteed valid schemas
- **Reflection loops**: Critique agent validates and sends back to writer for iterative improvement
- **Human-in-the-loop**: LangGraph `interrupt()` pauses execution; user can review and provide feedback before resuming
- **Real-time streaming**: SSE for live agent event delivery to frontend
- **Observability**: LangSmith tracing for production debugging
- **Guardrails**: Input validation, hallucination detection, rate limiting

---

## 📝 License

MIT

---

**Built as a production example of multi-agent AI systems using LangGraph, LangChain, and Groq.**
