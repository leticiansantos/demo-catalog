import React, { useState, useCallback } from 'react'
import { TreePanel } from './TreePanel'
import { DetailPanel } from './DetailPanel'

const API = '/api'

export default function App() {
  const [selectedTable, setSelectedTable] = useState(null)
  const [tableDetail, setTableDetail] = useState(null)
  const [detailLoading, setDetailLoading] = useState(false)
  const [detailError, setDetailError] = useState(null)

  const fetchTableDetail = useCallback(async (catalog, schema, table) => {
    setSelectedTable({ catalog, schema, table })
    setTableDetail(null)
    setDetailError(null)
    setDetailLoading(true)
    try {
      const res = await fetch(
        `${API}/catalogs/${encodeURIComponent(catalog)}/schemas/${encodeURIComponent(schema)}/tables/${encodeURIComponent(table)}`
      )
      if (!res.ok) throw new Error(await res.text())
      const data = await res.json()
      setTableDetail(data)
    } catch (e) {
      setDetailError(e.message)
    } finally {
      setDetailLoading(false)
    }
  }, [])

  return (
    <div className="app">
      <header className="app-header">
        <a href="https://www.motiva.com.br/" target="_blank" rel="noopener noreferrer" className="app-logo" aria-label="Motiva — Você nos move">
          <img
            src="https://aemassets.grupoccr.com.br/content/dam/sites-modulares/pt/media/images/logos/motiva_logo_only.svg"
            alt="Motiva"
            className="logo-motiva"
          />
        </a>
        <h1>Catalog Browser</h1>
        <span className="badge">Apenas catálogos motiva_*</span>
      </header>
      <div className="app-body">
        <TreePanel onSelectTable={fetchTableDetail} />
        <DetailPanel
          selectedTable={selectedTable}
          tableDetail={tableDetail}
          loading={detailLoading}
          error={detailError}
        />
      </div>
    </div>
  )
}
