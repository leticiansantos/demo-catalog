import React, { useState, useEffect } from 'react'

const API = '/api'

function formatDate(iso) {
  if (!iso) return '—'
  try {
    return new Date(iso).toLocaleString('pt-BR')
  } catch {
    return '—'
  }
}

export function AdminPage() {
  const [requests, setRequests] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  const load = () => {
    setLoading(true)
    setError(null)
    fetch(`${API}/access-requests`)
      .then((r) => {
        if (r.ok) return r.json()
        if (r.status === 404) return Promise.reject(new Error('A rota de solicitações não foi encontrada. Faça um novo deploy da aplicação para atualizar o backend.'))
        return Promise.reject(new Error(r.statusText || `Erro ${r.status}`))
      })
      .then((data) => setRequests(Array.isArray(data) ? data : []))
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false))
  }

  useEffect(() => load(), [])

  if (loading) return <div className="admin-page"><div className="loading">A carregar solicitações…</div></div>
  if (error) return <div className="admin-page"><div className="error">{error}</div></div>

  return (
    <div className="admin-page">
      <h2>Solicitações de acesso ao dado</h2>
      <p className="admin-desc">Listagem para administradores. Todas as solicitações feitas pelos usuários.</p>
      <button type="button" className="btn-refresh" onClick={load}>Atualizar</button>
      {requests.length === 0 ? (
        <div className="admin-empty-state">
          <div className="admin-empty-icon" aria-hidden>📋</div>
          <p className="admin-empty-title">Nenhuma solicitação de acesso</p>
          <p className="admin-empty-desc">Quando um usuário clicar em &quot;Solicitar acesso ao dado&quot; numa tabela, a solicitação aparecerá aqui.</p>
        </div>
      ) : (
        <div className="admin-table-wrap">
          <table className="admin-table">
            <thead>
              <tr>
                <th>Data</th>
                <th>Catálogo</th>
                <th>Schema</th>
                <th>Tabela</th>
                <th>Solicitante</th>
                <th>Motivo</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              {requests.map((r) => (
                <tr key={r.id}>
                  <td>{formatDate(r.created_at)}</td>
                  <td>{r.catalog}</td>
                  <td>{r.schema}</td>
                  <td className="col-name">{r.table}</td>
                  <td>{r.requested_by || '—'}</td>
                  <td>{r.reason || '—'}</td>
                  <td><span className={`status status-${r.status || 'pending'}`}>{r.status || 'pending'}</span></td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}
