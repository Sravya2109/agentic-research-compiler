import type { AgentEvent } from '../types'

const AGENT_LABELS: Record<string, string> = {
  orchestrator: 'Orchestrator',
  search_agent: 'Search Agent',
  analyst: 'Analyst',
  human_checkpoint: 'Human Checkpoint',
  writer: 'Writer',
  critique: 'Critique',
  system: 'System',
}

const STATUS_BADGE: Record<string, string> = {
  completed: 'bg-green-100 text-green-800',
  paused: 'bg-yellow-100 text-yellow-800',
  revision_needed: 'bg-orange-100 text-orange-800',
  final_report: 'bg-blue-100 text-blue-800',
  error: 'bg-red-100 text-red-800',
}

const STATUS_DOT: Record<string, string> = {
  completed: 'bg-green-500',
  paused: 'bg-yellow-500',
  revision_needed: 'bg-orange-500',
  final_report: 'bg-blue-500',
  error: 'bg-red-500',
}

interface Props {
  events: AgentEvent[]
  isRunning: boolean
}

function eventDetail(evt: AgentEvent): string | null {
  if (!evt.data || typeof evt.data !== 'object') return null
  if ('source_count' in evt.data) return `${evt.data.source_count as number} sources collected`
  if ('findings_count' in evt.data) return `${evt.data.findings_count as number} key findings extracted`
  if ('section_count' in evt.data) return `${evt.data.section_count as number} sections written`
  if ('issues_count' in evt.data) return `${evt.data.issues_count as number} issues found`
  if ('sub_tasks' in evt.data && Array.isArray(evt.data.sub_tasks))
    return `${(evt.data.sub_tasks as unknown[]).length} sub-tasks created`
  return null
}

export default function AgentFeed({ events, isRunning }: Props) {
  return (
    <div className="bg-white rounded-xl border border-gray-200 shadow-sm overflow-hidden">
      <div className="px-6 py-4 border-b border-gray-100 flex items-center justify-between">
        <h2 className="font-semibold text-gray-900">Agent Activity</h2>
        {isRunning && (
          <span className="flex items-center gap-1.5 text-xs text-blue-600 font-medium">
            <span className="w-1.5 h-1.5 bg-blue-600 rounded-full animate-pulse" />
            Running
          </span>
        )}
      </div>
      <ul className="divide-y divide-gray-50">
        {events.map((evt, i) => {
          const detail = eventDetail(evt)
          return (
            <li key={i} className="px-6 py-3 flex items-start gap-4">
              <span
                className={`mt-1 w-2 h-2 rounded-full flex-shrink-0 ${STATUS_DOT[evt.status] ?? 'bg-gray-400'}`}
              />
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2 flex-wrap">
                  <span className="text-xs font-medium text-gray-800">
                    {AGENT_LABELS[evt.agent] ?? evt.agent}
                  </span>
                  <span
                    className={`text-xs px-1.5 py-0.5 rounded font-medium ${STATUS_BADGE[evt.status] ?? 'bg-gray-100 text-gray-600'}`}
                  >
                    {evt.status}
                  </span>
                </div>
                <p className="text-sm text-gray-600 mt-0.5">{evt.message}</p>
                {detail && <p className="text-xs text-gray-400 mt-0.5">{detail}</p>}
              </div>
            </li>
          )
        })}
        {isRunning && (
          <li className="px-6 py-3 flex items-center gap-4 text-sm text-gray-400">
            <span className="w-2 h-2 bg-gray-300 rounded-full animate-pulse flex-shrink-0" />
            Processing...
          </li>
        )}
      </ul>
    </div>
  )
}
