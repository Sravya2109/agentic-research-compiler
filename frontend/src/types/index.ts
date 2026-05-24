export interface AgentEvent {
  agent: string
  status: string
  message: string
  data?: Record<string, unknown> | null
}

export interface ReportSection {
  title: string
  content: string
  citations: string[]
  confidence: number
}

export interface ReportModel {
  title: string
  executive_summary: string
  sections: ReportSection[]
  key_takeaways: string[]
  limitations: string
  total_sources: number
}

export interface AnalystNotes {
  key_findings: string[]
  contradictions: string[]
  coverage_gaps: string[]
  sources_used: string[]
}

export interface CheckpointData {
  summary?: string
  analyst_notes?: AnalystNotes
}

export type AppPhase = 'idle' | 'running' | 'paused' | 'done' | 'error'
