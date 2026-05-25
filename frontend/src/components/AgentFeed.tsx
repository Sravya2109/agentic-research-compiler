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

const AGENT_ICONS: Record<string, string> = {
  orchestrator: '🎼',
  search_agent: '🔍',
  analyst: '📊',
  human_checkpoint: '👤',
  writer: '✍️',
  critique: '🔍',
  system: '⚙️',
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
    <div className="bg-white rounded-xl border border-gray-200 shadow-md hover:shadow-lg transition-shadow duration-300 overflow-hidden">
      <div className="px-6 py-4 border-b border-gray-100 flex items-center justify-between bg-gradient-to-r from-blue-50 to-transparent">
        <h2 className="font-semibold text-gray-900 flex items-center gap-2">
          <span>🤖</span> Agent Activity
        </h2>
        {isRunning && (
          <span className="flex items-center gap-1.5 text-xs text-blue-600 font-medium">
            <span className="w-2 h-2 bg-blue-600 rounded-full animate-pulse" />
            Running
          </span>
        )}
      </div>
      <ul className="divide-y divide-gray-100">
        {events.map((evt, i) => {
          const detail = eventDetail(evt)
          const icon = AGENT_ICONS[evt.agent] ?? '•'
          return (
            <li key={i} className="px-6 py-4 flex items-start gap-4 hover:bg-blue-50/30 transition-colors duration-200">
              <div className="flex flex-col items-center gap-1 mt-0.5">
                <span className="text-lg">{icon}</span>
                <span
                  className={`w-2 h-2 rounded-full ${STATUS_DOT[evt.status] ?? 'bg-gray-400'}`}
                />
              </div>
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2 flex-wrap">
                  <span className="text-sm font-semibold text-gray-800">
                    {AGENT_LABELS[evt.agent] ?? evt.agent}
                  </span>
                  <span
                    className={`text-xs px-2 py-1 rounded-full font-medium ${STATUS_BADGE[evt.status] ?? 'bg-gray-100 text-gray-600'}`}
                  >
                    {evt.status}
                  </span>
                </div>
                <p className="text-sm text-gray-700 mt-1">{evt.message}</p>
                {detail && <p className="text-xs text-gray-400 mt-1 flex items-center gap-1">ℹ️ {detail}</p>}
              </div>
            </li>
          )
        })}
        {isRunning && (
          <li className="px-6 py-4 flex items-center gap-4 text-sm text-gray-400 bg-blue-50/20">
            <span className="flex items-center gap-2">
              <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" />
              Processing...
            </span>
          </li>
        )}
      </ul>
    </div>
  )
}
