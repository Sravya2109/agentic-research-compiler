import { useState } from 'react'
import type { CheckpointData } from '../types'

interface Props {
  data: CheckpointData
  onResume: (feedback: string) => Promise<void>
}

export default function CheckpointPanel({ data, onResume }: Props) {
  const [feedback, setFeedback] = useState('')
  const [isLoading, setIsLoading] = useState(false)

  const notes = data.analyst_notes

  const handleApprove = async () => {
    setIsLoading(true)
    await onResume(feedback.trim() || 'Approved. Proceed with the report.')
    setIsLoading(false)
  }

  return (
    <div className="bg-gradient-to-br from-amber-50 to-orange-50 border border-amber-200 rounded-xl shadow-md hover:shadow-lg transition-shadow duration-300 overflow-hidden">
      <div className="px-6 py-5 border-b border-amber-200 bg-gradient-to-r from-amber-100 to-orange-100">
        <h2 className="font-bold text-lg text-amber-900 flex items-center gap-2">
          <span>👤</span> Human Checkpoint — Review Required
        </h2>
        <p className="text-sm text-amber-700 mt-1">
          The analyst has finished. Review the findings below, then approve or add direction for the writer.
        </p>
      </div>

      <div className="px-6 py-6 space-y-6">
        {notes && notes.key_findings.length > 0 && (
          <section>
            <h3 className="text-sm font-bold text-gray-900 mb-3 flex items-center gap-2">
              <span>⭐</span> Key Findings
            </h3>
            <ul className="space-y-2">
              {notes.key_findings.map((f, i) => (
                <li key={i} className="flex gap-3 text-sm text-gray-700 bg-white/50 p-3 rounded-lg border border-amber-100">
                  <span className="text-amber-600 font-bold flex-shrink-0 w-6">{i + 1}.</span>
                  <span>{f}</span>
                </li>
              ))}
            </ul>
          </section>
        )}

        {notes && notes.contradictions.length > 0 && (
          <section>
            <h3 className="text-sm font-bold text-gray-900 mb-3 flex items-center gap-2">
              <span>⚡</span> Contradictions Between Sources
            </h3>
            <ul className="space-y-2">
              {notes.contradictions.map((c, i) => (
                <li key={i} className="text-sm text-gray-700 flex gap-3 bg-white/50 p-3 rounded-lg border border-orange-100">
                  <span className="text-orange-500 font-bold flex-shrink-0">!</span>
                  <span>{c}</span>
                </li>
              ))}
            </ul>
          </section>
        )}

        {notes && notes.coverage_gaps.length > 0 && (
          <section>
            <h3 className="text-sm font-bold text-gray-900 mb-3 flex items-center gap-2">
              <span>🔲</span> Coverage Gaps
            </h3>
            <ul className="space-y-2">
              {notes.coverage_gaps.map((g, i) => (
                <li key={i} className="text-sm text-gray-700 flex gap-3 bg-white/50 p-3 rounded-lg border border-gray-100">
                  <span className="text-gray-400 font-bold flex-shrink-0">–</span>
                  <span>{g}</span>
                </li>
              ))}
            </ul>
          </section>
        )}

        <section>
          <label className="block text-sm font-bold text-gray-900 mb-2 flex items-center gap-2">
            <span>💬</span> Additional direction for the writer{' '}
            <span className="font-normal text-gray-500">(optional)</span>
          </label>
          <textarea
            value={feedback}
            onChange={e => setFeedback(e.target.value)}
            placeholder="e.g. Focus more on open-source alternatives. Add a section on pricing models."
            rows={3}
            className="w-full px-4 py-3 border border-amber-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-amber-500 bg-white resize-none transition-all duration-200 hover:border-amber-400"
            disabled={isLoading}
          />
        </section>

        <button
          onClick={handleApprove}
          disabled={isLoading}
          className="w-full bg-gradient-to-r from-amber-600 to-orange-600 hover:from-amber-700 hover:to-orange-700 disabled:from-amber-300 disabled:to-orange-300 disabled:cursor-not-allowed text-white font-semibold py-3 rounded-lg text-sm transition-all duration-200 transform hover:scale-105 active:scale-95 shadow-md"
        >
          {isLoading ? '⏳ Resuming...' : '✓ Approve & Generate Report'}
        </button>
      </div>
    </div>
  )
}
