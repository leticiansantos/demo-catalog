import React, { useState, useCallback } from 'react'

const API = '/api'

function formatDate(ms) {
  if (ms == null) return '—'
  try {
    return new Date(ms).toLocaleString('pt-BR')
  } catch {
    return '—'
  }
}

export function DetailPanel({ selectedTable, tableDetail, loading, error }) {
  const [modalOpen, setModalOpen] = useState(false)
  const [requestReason, setRequestReason] = useState('')
  const [requestedBy, setRequestedBy] = useState('')
  const [requestSubmitting, setRequestSubmitting] = useState(false)
  const [requestMessage, setRequestMessage] = useState(null)

  const openRequestModal = useCallback(() => setModalOpen(true), [])
  const closeRequestModal = useCallback(() => {
    setModalOpen(false)
    setRequestMessage(null)
    setRequestReason('')
    setRequestedBy('')
  }, [])

  const submitAccessRequest = useCallback(() => {
    if (!selectedTable) return
    setRequestSubmitting(true)
    setRequestMessage(null)
    fetch(`${API}/access-requests`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        catalog: selectedTable.catalog,
        schema: selectedTable.schema,
        table: selectedTable.table,
        reason: requestReason.trim() || null,
        requested_by: requestedBy.trim() || null,
      }),
    })
      .then((r) => (r.ok ? r.json() : Promise.reject(new Error(r.statusText))))
      .then(() => {
        setRequestMessage({ type: 'success', text: 'Solicitação enviada com sucesso.' })
        setRequestReason('')
        setRequestedBy('')
        setTimeout(closeRequestModal, 1500)
      })
      .catch((e) => setRequestMessage({ type: 'error', text: e.message }))
      .finally(() => setRequestSubmitting(false))
  }, [selectedTable, requestReason, requestedBy, closeRequestModal])
  if (!selectedTable) {
    return (
      <main className="detail-panel">
        <div className="detail-placeholder">
          Clique numa tabela na árvore à esquerda para ver a descrição, colunas, esquema e dono.
        </div>
      </main>
    )
  }

  if (loading) {
    return (
      <main className="detail-panel">
        <div className="detail-placeholder">A carregar…</div>
      </main>
    )
  }

  if (error) {
    return (
      <main className="detail-panel">
        <div className="error">{error}</div>
      </main>
    )
  }

  if (!tableDetail) return null

  const { full_name, name, description, owner, table_type, columns, created_at, updated_at } = tableDetail

  return (
    <main className="detail-panel">
      <div className="detail-header-row">
        <div>
          <h2>{name}</h2>
          <div className="full-name">{full_name}</div>
        </div>
        <button type="button" className="btn-request-access" onClick={openRequestModal}>
          Solicitar acesso ao dado
        </button>
      </div>

      <dl className="detail-meta">
        <div>
          <dt>Dono</dt>
          <dd>{owner || '—'}</dd>
        </div>
        <div>
          <dt>Tipo</dt>
          <dd>{table_type || 'TABLE'}</dd>
        </div>
        <div>
          <dt>Criado em</dt>
          <dd>{formatDate(created_at)}</dd>
        </div>
        <div>
          <dt>Atualizado em</dt>
          <dd>{formatDate(updated_at)}</dd>
        </div>
      </dl>

      {description && (
        <section className="detail-section">
          <h3>Descrição</h3>
          <p>{description}</p>
        </section>
      )}

      <section className="detail-section">
        <h3>Esquema da tabela ({columns?.length ?? 0} colunas)</h3>
        {columns && columns.length > 0 ? (
          <table className="table-schema">
            <thead>
              <tr>
                <th>#</th>
                <th>Coluna</th>
                <th>Tipo</th>
                <th>Nulável</th>
                <th>Descrição</th>
              </tr>
            </thead>
            <tbody>
              {columns.map((col, i) => (
                <tr key={col.name}>
                  <td>{col.position != null ? col.position + 1 : i + 1}</td>
                  <td className="col-name">{col.name}</td>
                  <td>{col.type || '—'}</td>
                  <td>{col.nullable === false ? 'Não' : 'Sim'}</td>
                  <td>{col.comment || '—'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        ) : (
          <p>Sem colunas ou informação não disponível.</p>
        )}
      </section>

      {modalOpen && (
        <div className="modal-overlay" onClick={closeRequestModal} role="dialog" aria-modal="true" aria-labelledby="modal-title">
          <div className="modal-box" onClick={(e) => e.stopPropagation()}>
            <h3 id="modal-title">Solicitar acesso ao dado</h3>
            <p className="modal-table-name">{full_name}</p>
            <label className="modal-label">
              Seu nome ou e-mail (opcional)
              <input
                type="text"
                className="modal-input"
                value={requestedBy}
                onChange={(e) => setRequestedBy(e.target.value)}
                placeholder="Nome ou e-mail"
              />
            </label>
            <label className="modal-label">
              Motivo da solicitação (opcional)
              <textarea
                className="modal-textarea"
                value={requestReason}
                onChange={(e) => setRequestReason(e.target.value)}
                placeholder="Ex.: análise de vendas, relatório mensal..."
                rows={3}
              />
            </label>
            {requestMessage && (
              <p className={requestMessage.type === 'success' ? 'modal-success' : 'modal-error'}>{requestMessage.text}</p>
            )}
            <div className="modal-actions">
              <button type="button" className="btn-secondary" onClick={closeRequestModal}>Cancelar</button>
              <button type="button" className="btn-primary" onClick={submitAccessRequest} disabled={requestSubmitting}>
                {requestSubmitting ? 'A enviar…' : 'Enviar solicitação'}
              </button>
            </div>
          </div>
        </div>
      )}
    </main>
  )
}
