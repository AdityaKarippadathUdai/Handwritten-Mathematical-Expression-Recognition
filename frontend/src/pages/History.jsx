import React, { useEffect, useMemo, useState } from 'react'
import katex from 'katex'
import 'katex/dist/katex.min.css'
import api from '../services/api'
import {
  ChevronLeft,
  ChevronRight,
  Clock,
  History as HistoryIcon,
  Search,
  Trash2,
} from 'lucide-react'

const PAGE_SIZE = 8

export default function History() {
  const [records, setRecords] = useState([])
  const [search, setSearch] = useState('')
  const [page, setPage] = useState(1)
  const [totalPages, setTotalPages] = useState(1)
  const [total, setTotal] = useState(0)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [deletingId, setDeletingId] = useState(null)

  const query = useMemo(() => search.trim(), [search])

  useEffect(() => {
    const timer = window.setTimeout(() => {
      fetchHistory()
    }, 250)

    return () => window.clearTimeout(timer)
  }, [query, page])

  useEffect(() => {
    setPage(1)
  }, [query])

  const fetchHistory = async () => {
    setLoading(true)
    setError('')

    try {
      const response = await api.get('/history', {
        params: {
          search: query,
          page,
          page_size: PAGE_SIZE,
        },
      })
      setRecords(response.data.items || [])
      setTotal(response.data.total || 0)
      setTotalPages(response.data.total_pages || 1)
    } catch (err) {
      console.error(err)
      setError(err.response?.data?.detail || 'Unable to load equation history.')
    } finally {
      setLoading(false)
    }
  }

  const handleDelete = async (id) => {
    setDeletingId(id)
    setError('')

    try {
      await api.delete(`/history/${id}`)
      const remainingOnPage = records.length - 1
      if (remainingOnPage === 0 && page > 1) {
        setPage((current) => current - 1)
      } else {
        await fetchHistory()
      }
    } catch (err) {
      console.error(err)
      setError(err.response?.data?.detail || 'Unable to delete history item.')
    } finally {
      setDeletingId(null)
    }
  }

  return (
    <div className="max-w-6xl mx-auto space-y-5">
      <div className="flex flex-col gap-4 lg:flex-row lg:items-end lg:justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-white">Equation History</h1>
          <p className="text-sm text-neutral-400 mt-1">
            Browse saved predictions, inspect generated LaTeX, and remove records you no longer need.
          </p>
        </div>

        <div className="relative w-full lg:w-80">
          <Search className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-neutral-500" />
          <input
            value={search}
            onChange={(event) => setSearch(event.target.value)}
            placeholder="Search LaTeX or image path"
            className="h-10 w-full rounded-lg border border-neutral-800 bg-neutral-950 pl-9 pr-3 text-sm text-neutral-100 outline-none transition-colors placeholder:text-neutral-600 focus:border-sky-500/60"
          />
        </div>
      </div>

      {error && (
        <div className="rounded-lg border border-red-500/20 bg-red-950/30 px-4 py-3 text-sm text-red-300">
          {error}
        </div>
      )}

      <section className="rounded-lg border border-neutral-800 bg-neutral-950/50 overflow-hidden">
        <div className="flex items-center justify-between border-b border-neutral-800 px-4 py-3">
          <div className="flex items-center gap-2 text-sm font-semibold text-neutral-200">
            <HistoryIcon className="h-4 w-4 text-sky-300" />
            <span>{total} saved predictions</span>
          </div>
          <span className="text-xs text-neutral-500">Page {page} of {totalPages}</span>
        </div>

        {loading ? (
          <div className="p-12 text-center text-sm text-neutral-500">Loading history...</div>
        ) : records.length > 0 ? (
          <div className="divide-y divide-neutral-800">
            {records.map((record) => (
              <HistoryRow
                key={record.id}
                record={record}
                deleting={deletingId === record.id}
                onDelete={() => handleDelete(record.id)}
              />
            ))}
          </div>
        ) : (
          <div className="py-16 text-center text-neutral-500">
            <HistoryIcon className="w-10 h-10 mx-auto text-neutral-700 mb-3" />
            <p className="text-sm font-medium text-neutral-400">No history records found</p>
            <p className="text-xs text-neutral-600 mt-1">Successful image predictions will appear here.</p>
          </div>
        )}
      </section>

      <div className="flex items-center justify-between">
        <button
          type="button"
          onClick={() => setPage((current) => Math.max(1, current - 1))}
          disabled={page <= 1 || loading}
          className="inline-flex items-center gap-2 rounded-lg border border-neutral-800 bg-neutral-950 px-3 py-2 text-sm font-medium text-neutral-300 transition-colors hover:border-sky-500/50 hover:text-sky-300 disabled:cursor-not-allowed disabled:opacity-50"
        >
          <ChevronLeft className="h-4 w-4" />
          <span>Previous</span>
        </button>

        <button
          type="button"
          onClick={() => setPage((current) => Math.min(totalPages, current + 1))}
          disabled={page >= totalPages || loading}
          className="inline-flex items-center gap-2 rounded-lg border border-neutral-800 bg-neutral-950 px-3 py-2 text-sm font-medium text-neutral-300 transition-colors hover:border-sky-500/50 hover:text-sky-300 disabled:cursor-not-allowed disabled:opacity-50"
        >
          <span>Next</span>
          <ChevronRight className="h-4 w-4" />
        </button>
      </div>
    </div>
  )
}

function HistoryRow({ record, deleting, onDelete }) {
  const renderedEquation = useMemo(() => {
    return katex.renderToString(record.latex_output || '', {
      displayMode: false,
      throwOnError: false,
      strict: false,
    })
  }, [record.latex_output])

  return (
    <article className="grid grid-cols-1 gap-4 p-4 transition-colors hover:bg-neutral-900/50 lg:grid-cols-[88px_minmax(0,1fr)_auto] lg:items-center">
      <div className="h-20 w-full overflow-hidden rounded-lg border border-neutral-800 bg-neutral-900 lg:w-20">
        {record.image_path ? (
          <img src={record.image_path} alt="Prediction input" className="h-full w-full object-contain" />
        ) : null}
      </div>

      <div className="min-w-0 space-y-3">
        <div className="overflow-x-auto rounded-lg border border-neutral-800 bg-white px-3 py-2 text-neutral-950">
          <span dangerouslySetInnerHTML={{ __html: renderedEquation }} />
        </div>
        <code className="block overflow-x-auto whitespace-pre rounded-lg bg-neutral-900 px-3 py-2 text-xs font-semibold text-sky-300">
          {record.latex_output}
        </code>
        <div className="flex flex-wrap items-center gap-x-4 gap-y-1 text-xs text-neutral-500">
          <span className="flex items-center gap-1.5">
            <Clock className="h-3.5 w-3.5" />
            {new Date(record.created_at).toLocaleString()}
          </span>
          <span>Confidence {(Number(record.confidence || 0) * 100).toFixed(1)}%</span>
        </div>
      </div>

      <button
        type="button"
        onClick={onDelete}
        disabled={deleting}
        className="inline-flex h-9 w-9 items-center justify-center rounded-lg border border-neutral-800 bg-neutral-900 text-neutral-400 transition-colors hover:border-red-500/50 hover:text-red-300 disabled:cursor-not-allowed disabled:opacity-50"
        title="Delete history item"
      >
        <Trash2 className="h-4 w-4" />
      </button>
    </article>
  )
}
