import React, { useState, useEffect, useCallback } from 'react'

const API = '/api'

function CatalogNode({ name, comment, onSelectTable }) {
  const [expanded, setExpanded] = useState(false)
  const [schemas, setSchemas] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const load = useCallback(() => {
    setLoading(true)
    setError(null)
    fetch(`${API}/catalogs/${encodeURIComponent(name)}/schemas`)
      .then((r) => (r.ok ? r.json() : Promise.reject(new Error(r.statusText))))
      .then((data) => {
        setSchemas(data.schemas || [])
        setExpanded(true)
      })
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false))
  }, [name])

  const toggle = () => {
    if (schemas === null && !loading) load()
    else setExpanded((e) => !e)
  }

  return (
    <div className="tree-node">
      <div
        className={`tree-item ${expanded ? 'expanded' : ''}`}
        onClick={toggle}
        role="button"
        aria-expanded={expanded}
      >
        <span className="chevron">▶</span>
        <span className="icon">📁</span>
        <span className="name" title={comment || name}>{name}</span>
      </div>
      {loading && <div className="loading">A carregar…</div>}
      {error && <div className="error">{error}</div>}
      {expanded && schemas && schemas.length > 0 && (
        <div className="tree-children">
          {schemas.map((s) => (
            <SchemaNode
              key={`${name}.${s.name}`}
              catalogName={name}
              schemaName={s.name}
              schemaComment={s.comment}
              onSelectTable={onSelectTable}
            />
          ))}
        </div>
      )}
    </div>
  )
}

function SchemaNode({ catalogName, schemaName, schemaComment, onSelectTable }) {
  const [expanded, setExpanded] = useState(false)
  const [tables, setTables] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const load = useCallback(() => {
    setLoading(true)
    setError(null)
    fetch(
      `${API}/catalogs/${encodeURIComponent(catalogName)}/schemas/${encodeURIComponent(schemaName)}/tables`
    )
      .then((r) => (r.ok ? r.json() : Promise.reject(new Error(r.statusText))))
      .then((data) => {
        setTables(data.tables || [])
        setExpanded(true)
      })
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false))
  }, [catalogName, schemaName])

  const toggle = () => {
    if (tables === null && !loading) load()
    else setExpanded((e) => !e)
  }

  return (
    <div className="tree-node">
      <div
        className={`tree-item ${expanded ? 'expanded' : ''}`}
        onClick={toggle}
        role="button"
        aria-expanded={expanded}
      >
        <span className="chevron">▶</span>
        <span className="icon">📂</span>
        <span className="name" title={schemaComment || schemaName}>{schemaName}</span>
      </div>
      {loading && <div className="loading">A carregar…</div>}
      {error && <div className="error">{error}</div>}
      {expanded && tables && tables.length > 0 && (
        <div className="tree-children">
          {tables.map((t) => (
            <div
              key={t.full_name}
              className="tree-item"
              onClick={() => onSelectTable(catalogName, schemaName, t.name)}
              role="button"
            >
              <span className="chevron" style={{ visibility: 'hidden' }}>▶</span>
              <span className="icon">📄</span>
              <span className="name" title={t.comment || t.name}>{t.name}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

export function TreePanel({ onSelectTable }) {
  const [catalogs, setCatalogs] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    fetch(`${API}/catalogs`)
      .then((r) => (r.ok ? r.json() : Promise.reject(new Error(r.statusText))))
      .then((data) => setCatalogs(data.catalogs || []))
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false))
  }, [])

  if (loading) return <div className="tree-panel"><div className="loading">A carregar catálogos…</div></div>
  if (error) return <div className="tree-panel"><div className="error">{error}</div></div>

  return (
    <aside className="tree-panel">
      {catalogs.length === 0 ? (
        <div className="loading">Nenhum catálogo motiva_* encontrado.</div>
      ) : (
        catalogs.map((c) => (
          <CatalogNode
            key={c.name}
            name={c.name}
            comment={c.comment}
            onSelectTable={onSelectTable}
          />
        ))
      )}
    </aside>
  )
}
