import { useState } from 'react'

interface Props {
  onSubmit: (query: string) => Promise<void>
}

export default function QueryInput({ onSubmit }: Props) {
  const [query, setQuery] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    const trimmed = query.trim()
    if (trimmed.length < 10) {
      setError('Query must be at least 10 characters.')
      return
    }
    setError(null)
    setIsLoading(true)
    try {
      await onSubmit(trimmed)
    } catch {
      setError('Failed to start research. Is the backend running?')
      setIsLoading(false)
    }
  }

  return (
    <div className="bg-white rounded-xl border border-gray-200 p-8 shadow-sm">
      <h2 className="text-lg font-semibold text-gray-900 mb-1">What would you like to research?</h2>
      <p className="text-sm text-gray-500 mb-6">
        A team of AI agents will search the web, analyze findings, and compile a cited report.
      </p>
      <form onSubmit={handleSubmit} className="space-y-4">
        <textarea
          value={query}
          onChange={e => setQuery(e.target.value)}
          placeholder="e.g. Analyze the competitive landscape of AI coding assistants in 2025"
          rows={4}
          className="w-full px-4 py-3 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
          disabled={isLoading}
        />
        {error && <p className="text-sm text-red-600">{error}</p>}
        <button
          type="submit"
          disabled={isLoading || query.trim().length < 10}
          className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-blue-300 disabled:cursor-not-allowed text-white font-medium py-3 rounded-lg text-sm transition-colors"
        >
          {isLoading ? 'Starting research...' : 'Start Research'}
        </button>
      </form>
    </div>
  )
}
