import type { ReportModel, ReportSection } from '../types'

function ConfidenceBar({ value }: { value: number }) {
  const pct = Math.round(value * 100)
  const color = pct >= 75 ? 'bg-green-500' : pct >= 50 ? 'bg-yellow-500' : 'bg-red-400'
  return (
    <div className="flex items-center gap-2">
      <div className="flex-1 h-1.5 bg-gray-200 rounded-full overflow-hidden">
        <div className={`h-full rounded-full transition-all ${color}`} style={{ width: `${pct}%` }} />
      </div>
      <span className="text-xs text-gray-500 w-8 text-right tabular-nums">{pct}%</span>
    </div>
  )
}

function SectionCard({ section }: { section: ReportSection }) {
  return (
    <div className="border border-gray-200 rounded-lg p-5 space-y-3">
      <div className="flex items-start justify-between gap-4">
        <h3 className="font-semibold text-gray-900 leading-snug">{section.title}</h3>
        <div className="w-28 flex-shrink-0 pt-1">
          <ConfidenceBar value={section.confidence} />
        </div>
      </div>
      <p className="text-sm text-gray-700 leading-relaxed">{section.content}</p>
      {section.citations.length > 0 && (
        <div>
          <p className="text-xs font-medium text-gray-500 mb-1.5">Sources</p>
          <ul className="space-y-1">
            {section.citations.map((url, i) => (
              <li key={i}>
                <a
                  href={url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-xs text-blue-600 hover:underline break-all"
                >
                  {url}
                </a>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  )
}

function downloadMarkdown(report: ReportModel) {
  const lines: string[] = [`# ${report.title}`, '', '## Executive Summary', '', report.executive_summary, '']

  for (const s of report.sections) {
    lines.push(`## ${s.title}`, '', s.content, '')
    if (s.citations.length > 0) {
      lines.push('**Sources:**')
      s.citations.forEach((url, i) => lines.push(`${i + 1}. ${url}`))
      lines.push('')
    }
    lines.push(`*Confidence: ${Math.round(s.confidence * 100)}%*`, '')
  }

  lines.push('## Key Takeaways', '')
  report.key_takeaways.forEach((t, i) => lines.push(`${i + 1}. ${t}`))
  lines.push('', '## Limitations', '', report.limitations)

  const blob = new Blob([lines.join('\n')], { type: 'text/markdown' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = 'research-report.md'
  a.click()
  URL.revokeObjectURL(url)
}

interface Props {
  report: ReportModel
}

export default function ReportView({ report }: Props) {
  return (
    <div className="bg-white rounded-xl border border-gray-200 shadow-sm overflow-hidden">
      <div className="px-6 py-5 border-b border-gray-100 flex items-start justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold text-gray-900 leading-tight">{report.title}</h2>
          <p className="text-sm text-gray-500 mt-1">
            {report.total_sources} sources &middot; {report.sections.length} sections
          </p>
        </div>
        <button
          onClick={() => downloadMarkdown(report)}
          className="flex-shrink-0 text-sm text-blue-600 hover:text-blue-700 border border-blue-200 hover:border-blue-300 px-3 py-1.5 rounded-lg transition-colors"
        >
          Download .md
        </button>
      </div>

      <div className="px-6 py-5 space-y-7">
        <section>
          <h3 className="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-2">
            Executive Summary
          </h3>
          <p className="text-gray-800 leading-relaxed">{report.executive_summary}</p>
        </section>

        <section>
          <h3 className="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-3">
            Sections
          </h3>
          <div className="space-y-3">
            {report.sections.map((s, i) => (
              <SectionCard key={i} section={s} />
            ))}
          </div>
        </section>

        <section>
          <h3 className="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-2">
            Key Takeaways
          </h3>
          <ul className="space-y-1.5">
            {report.key_takeaways.map((t, i) => (
              <li key={i} className="flex gap-2 text-sm text-gray-700">
                <span className="text-blue-600 font-semibold flex-shrink-0">{i + 1}.</span>
                {t}
              </li>
            ))}
          </ul>
        </section>

        <section>
          <h3 className="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-2">
            Limitations
          </h3>
          <p className="text-sm text-gray-600 leading-relaxed">{report.limitations}</p>
        </section>
      </div>
    </div>
  )
}
