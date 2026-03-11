import React from 'react'

function formatDate(ms) {
  if (ms == null) return '—'
  try {
    return new Date(ms).toLocaleString('pt-BR')
  } catch {
    return '—'
  }
}

export function DetailPanel({ selectedTable, tableDetail, loading, error }) {
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
      <h2>{name}</h2>
      <div className="full-name">{full_name}</div>

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
    </main>
  )
}
