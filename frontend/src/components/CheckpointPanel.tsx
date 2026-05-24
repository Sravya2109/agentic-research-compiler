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
    <div className="bg-amber-50 border border-amber-200 rounded-xl shadow-sm overflow-hidden">
      <div className="px-6 py-4 border-b border-amber-200 bg-amber-100">
        <h2 className="font-semibold text-amber-900">Human Checkpoint — Review Required</h2>
        <p className="text-sm text-amber-700 mt-0.5">
          The analyst has finished. Review the findings below, then approve or add direction for the writer.
        </p>
      </div>

      <div className="px-6 py-5 space-y-5">
        {notes && notes.key_findings.length > 0 && (
          <section>
            <h3 className="text-sm font-semibold text-gray-800 mb-2">Key Findings</h3>
            <ul className="space-y-1.5">
              {notes.key_findings.map((f, i) => (
                <li key={i} className="flex gap-2 text-sm text-gray-700">
                  <span className="text-amber-600 font-semibold flex-shrink-0">{i + 1}.</span>
                  {f}
                </li>
              ))}
            </ul>
          </section>
        )}

        {notes && notes.contradictions.length > 0 && (
          <section>
            <h3 className="text-sm font-semibold text-gray-800 mb-2">Contradictions Between Sources</h3>
            <ul className="space-y-1">
              {notes.contradictions.map((c, i) => (
                <li key={i} className="text-sm text-gray-600 flex gap-2">
                  <span className="text-orange-500 flex-shrink-0">!</span>
                  {c}
                </li>
              ))}
            </ul>
          </section>
        )}

        {notes && notes.coverage_gaps.length > 0 && (
          <section>
            <h3 className="text-sm font-semibold text-gray-800 mb-2">Coverage Gaps</h3>
            <ul className="space-y-1">
              {notes.coverage_gaps.map((g, i) => (
                <li key={i} className="text-sm text-gray-600 flex gap-2">
                  <span className="text-gray-400 flex-shrink-0">–</span>
                  {g}
                </li>
              ))}
            </ul>
          </section>
        )}

        <section>
          <label className="block text-sm font-semibold text-gray-800 mb-2">
            Additional direction for the writer{' '}
            <span className="font-normal text-gray-500">(optional)</span>
          </label>
          <textarea
            value={feedback}
            onChange={e => setFeedback(e.target.value)}
            placeholder="e.g. Focus more on open-source alternatives. Add a section on pricing models."
            rows={3}
            className="w-full px-3 py-2 border border-amber-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-amber-500 bg-white resize-none"
            disabled={isLoading}
          />
        </section>

        <button
          onClick={handleApprove}
          disabled={isLoading}
          className="w-full bg-amber-600 hover:bg-amber-700 disabled:bg-amber-300 disabled:cursor-not-allowed text-white font-medium py-3 rounded-lg text-sm transition-colors"
        >
          {isLoading ? 'Resuming...' : 'Approve & Generate Report'}
        </button>
      </div>
    </div>
  )
}
