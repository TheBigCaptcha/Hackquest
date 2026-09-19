import { useState } from 'react'

const API = 'http://localhost:8000'

const riskColor = level =>
  ({
    LOW: '#22c55e',
    MEDIUM: '#eab308',
    HIGH: '#f97316',
    CRITICAL: '#ef4444',
    UNASSESSED: '#9ca3af',
  }[level] || '#9ca3af')

export default function App() {
  const [query, setQuery] = useState('')
  const [raw, setRaw] = useState(null)
  const [error, setError] = useState(null)
  const [loading, setLoading] = useState(false)

  const search = async () => {
    if (!query.trim()) return
    setLoading(true)
    setError(null)
    try {
      const res = await fetch(
        `${API}/api/entities/search?query=${encodeURIComponent(query)}`
      )
      if (!res.ok) throw new Error(`Server returned ${res.status}`)
      setRaw(await res.json())
    } catch (e) {
      setError(e.message)
      setRaw(null)
    }
    setLoading(false)
  }

  // Handles both a plain list and an object like { results: [...] }
  const rows = Array.isArray(raw)
    ? raw
    : raw?.results || raw?.items || raw?.entities || []

  return (
    <div style={{ padding: 24, textAlign: 'left', fontFamily: 'sans-serif' }}>
      <h1>Entity Investigation</h1>

      <input
        value={query}
        onChange={e => setQuery(e.target.value)}
        onKeyDown={e => e.key === 'Enter' && search()}
        placeholder="Search entity ID..."
        style={{ padding: 8, marginRight: 8, width: 260 }}
      />
      <button onClick={search} style={{ padding: 8 }}>
        Search
      </button>

      {loading && <p>Loading...</p>}
      {error && <p style={{ color: 'red' }}>Error: {error}</p>}
      {raw && rows.length === 0 && !loading && <p>No results found.</p>}

      {rows.length > 0 && (
        <table style={{ marginTop: 16, borderCollapse: 'collapse' }}>
          <thead>
            <tr>
              <th style={{ padding: 8 }}>Entity ID</th>
              <th style={{ padding: 8 }}>Risk score</th>
              <th style={{ padding: 8 }}>Risk level</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((r, i) => (
              <tr key={i}>
                <td style={{ padding: 8 }}>{r.entity_id}</td>
                <td style={{ padding: 8 }}>{r.risk_score}</td>
                <td style={{ padding: 8 }}>
                  <span
                    style={{
                      background: riskColor(r.risk_level),
                      color: 'white',
                      padding: '2px 10px',
                      borderRadius: 12,
                    }}
                  >
                    {r.risk_level}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}

      {raw && (
        <details style={{ marginTop: 24 }}>
          <summary>Raw API response (for debugging)</summary>
          <pre>{JSON.stringify(raw, null, 2)}</pre>
        </details>
      )}
    </div>
  )
}