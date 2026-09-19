import { useState } from 'react'

const API = 'http://127.0.0.1:8000'

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
  const [selected, setSelected] = useState(null)
  const [detail, setDetail] = useState(null)
  const [detailError, setDetailError] = useState(null)

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

  const openDetail = async id => {
    setSelected(id)
    setDetail(null)
    setDetailError(null)
    try {
      const res = await fetch(
        `${API}/api/transactions/${encodeURIComponent(id)}`
      )
      if (!res.ok) throw new Error(`Server returned ${res.status}`)
      setDetail(await res.json())
    } catch (e) {
      setDetailError(e.message)
    }
  }

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

      <div style={{ display: 'flex', gap: 32, alignItems: 'flex-start' }}>
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
                <tr
                  key={i}
                  onClick={() => openDetail(r.entity_id)}
                  style={{
                    cursor: 'pointer',
                    background:
                      selected === r.entity_id ? '#33363d' : 'transparent',
                  }}
                >
                  <td style={{ padding: 8 }}>{r.entity_id}</td>
                  <td style={{ padding: 8 }}>{r.risk_score ?? '—'}</td>
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

        {selected && (
          <div style={{ marginTop: 16, minWidth: 300 }}>
            <h2>{selected}</h2>
            {!detail && !detailError && <p>Loading details...</p>}
            {detailError && (
              <p style={{ color: 'red' }}>Error: {detailError}</p>
            )}
            {detail && (
  <div style={{ lineHeight: 1.9 }}>
    <div>
      <b>Status:</b>{' '}
      <span
        style={{
          background: detail.is_suspicious ? '#ef4444' : '#22c55e',
          color: 'white',
          padding: '2px 10px',
          borderRadius: 12,
        }}
      >
        {detail.is_suspicious ? 'Suspicious' : 'Not flagged'}
      </span>
    </div>
    <div><b>From:</b> {detail.source_entity ?? '—'}</div>
    <div><b>To:</b> {detail.target_entity ?? '—'}</div>
    <div><b>Amount:</b> {detail.amount ?? '—'}</div>
    <div><b>Time:</b> {detail.timestamp ?? '—'}</div>
    <div><b>Reason:</b> {detail.flag_reason ?? 'None'}</div>
  </div>
)}
          </div>
        )}
      </div>
    </div>
  )
}