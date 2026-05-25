import { useEffect, useRef, useState } from 'react'
import type { AgentEvent, AppPhase, CheckpointData, ReportModel } from './types'
import AgentFeed from './components/AgentFeed'
import CheckpointPanel from './components/CheckpointPanel'
import QueryInput from './components/QueryInput'
import ReportView from './components/ReportView'

const API_BASE = 'https://web-production-e19cc.up.railway.app'

export default function App() {
  const [phase, setPhase] = useState<AppPhase>('idle')
  const [sessionId, setSessionId] = useState<string | null>(null)
  const [events, setEvents] = useState<AgentEvent[]>([])
  const [checkpointData, setCheckpointData] = useState<CheckpointData | null>(null)
  const [finalReport, setFinalReport] = useState<ReportModel | null>(null)
  const [errorMessage, setErrorMessage] = useState<string | null>(null)
  const esRef = useRef<EventSource | null>(null)

  useEffect(() => {
    if (!sessionId) return

    const es = new EventSource(`${API_BASE}/stream/${sessionId}`)
    esRef.current = es

    es.onmessage = (e: MessageEvent) => {
      const evt = JSON.parse(e.data as string) as AgentEvent
      setEvents(prev => [...prev, evt])

      if (evt.status === 'paused') {
        setPhase('paused')
        setCheckpointData((evt.data as CheckpointData) ?? null)
      } else if (evt.status === 'final_report') {
        setFinalReport(evt.data as unknown as ReportModel)
        setPhase('done')
        es.close()
      } else if (evt.status === 'error') {
        setErrorMessage(evt.message)
        setPhase('error')
        es.close()
      }
    }

    es.onerror = () => es.close()

    return () => es.close()
  }, [sessionId])

  const handleSubmit = async (query: string) => {
    esRef.current?.close()
    setEvents([])
    setCheckpointData(null)
    setFinalReport(null)
    setErrorMessage(null)
    setPhase('running')

    const res = await fetch(`${API_BASE}/run`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query }),
    })
    const json = await res.json() as { session_id: string }
    setSessionId(json.session_id)
  }

  const handleResume = async (feedback: string) => {
    if (!sessionId) return
    setPhase('running')
    await fetch(`${API_BASE}/resume/${sessionId}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ feedback }),
    })
  }

  const handleReset = () => {
    esRef.current?.close()
    setPhase('idle')
    setSessionId(null)
    setEvents([])
    setCheckpointData(null)
    setFinalReport(null)
    setErrorMessage(null)
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white border-b border-gray-200 px-6 py-4">
        <div className="max-w-4xl mx-auto flex items-center justify-between">
          <div>
            <h1 className="text-xl font-semibold text-gray-900">Agentic Research Compiler</h1>
            <p className="text-sm text-gray-500">Multi-agent AI research system</p>
          </div>
          {phase !== 'idle' && (
            <button
              onClick={handleReset}
              className="text-sm text-gray-500 hover:text-gray-700 underline"
            >
              New research
            </button>
          )}
        </div>
      </header>

      <main className="max-w-4xl mx-auto px-6 py-8 space-y-6">
        {phase === 'idle' && <QueryInput onSubmit={handleSubmit} />}

        {phase === 'error' && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-4 text-red-700">
            <span className="font-medium">Error: </span>{errorMessage}
          </div>
        )}

        {(phase === 'running' || phase === 'paused' || phase === 'done') && events.length > 0 && (
          <AgentFeed events={events} isRunning={phase === 'running'} />
        )}

        {phase === 'paused' && checkpointData && (
          <CheckpointPanel data={checkpointData} onResume={handleResume} />
        )}

        {phase === 'done' && finalReport && (
          <ReportView report={finalReport} />
        )}
      </main>
    </div>
  )
}
