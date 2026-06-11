import React, { useEffect, useMemo, useState } from 'react'
import katex from 'katex'
import 'katex/dist/katex.min.css'
import api from '../services/api'
import Skeleton from '../components/common/Skeleton.jsx'
import { useToast } from '../context/ToastContext.jsx'
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
  const { showToast } = useToast()

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
      const message = err.response?.data?.detail || 'Unable to load equation history.'
      setError(message)
      showToast({ type: 'error', title: 'History unavailable', message })
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
      showToast({ type: 'success', title: 'History item deleted', message: 'The saved prediction was removed.' })
    } catch (err) {
      console.error(err)
      const message = err.response?.data?.detail || 'Unable to delete history item.'
      setError(message)
      showToast({ type: 'error', title: 'Delete failed', message })
    } finally {
      setDeletingId(null)
    }
  }

  return (
    <div className="mx-auto max-w-6xl space-y-5">
      <div className="flex flex-col gap-4 lg:flex-row lg:items-end lg:justify-between">
        <div>
          <h1 className="text-3xl font-semibold tracking-tight text-white">Equation History</h1>
          <p className="mt-1 text-sm text-slate-400">
            Browse saved predictions, inspect generated LaTeX, and clear records you no longer need.
          </p>
        </div>

        <div className="relative w-full lg:w-80">
          <Search className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-500" />
          <input
            value={search}
            onChange={(event) => setSearch(event.target.value)}
            placeholder="Search LaTeX or image path"
            className="h-11 w-full rounded-2xl border border-slate-800 bg-slate-950/90 pl-11 pr-3 text-sm text-slate-100 outline-none transition focus:border-sky-400/70 focus:ring-1 focus:ring-sky-400/30"
          />
        </div>
      </div>

      {error && (
        <div className="rounded-3xl border border-rose-500/20 bg-rose-950/30 px-4 py-3 text-sm text-rose-200">
          {error}
        </div>
      )}

      <section className="rounded-3xl border border-slate-800 bg-slate-950/80 shadow-2xl shadow-slate-950/20 overflow-hidden">
        <div className="flex items-center justify-between border-b border-slate-800 px-4 py-3">
          <div className="flex items-center gap-2 text-sm font-semibold text-slate-100">
            <HistoryIcon className="h-4 w-4 text-sky-300" />
            <span>{total} saved predictions</span>
          </div>
          <span className="text-xs text-slate-500">Page {page} of {totalPages}</span>
        </div>

        {loading ? (
          <HistorySkeleton />
        ) : records.length > 0 ? (
          <div className="divide-y divide-slate-800">
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
          <div className="py-16 text-center text-slate-400">
            <HistoryIcon className="mx-auto mb-3 h-10 w-10 text-slate-500" />
            <p className="text-sm font-semibold text-slate-100">No history records found</p>
            <p className="mt-1 text-xs text-slate-500">Successful image predictions will appear here.</p>
          </div>
        )}
      </section>

      <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <button
          type="button"
          onClick={() => setPage((current) => Math.max(1, current - 1))}
          disabled={page <= 1 || loading}
          className="inline-flex items-center gap-2 rounded-2xl border border-slate-800 bg-slate-950 px-4 py-2 text-sm font-medium text-slate-100 transition hover:border-sky-400 hover:text-sky-300 disabled:cursor-not-allowed disabled:opacity-50"
        >
          <ChevronLeft className="h-4 w-4" />
          <span>Previous</span>
        </button>

        <button
          type="button"
          onClick={() => setPage((current) => Math.min(totalPages, current + 1))}
          disabled={page >= totalPages || loading}
          className="inline-flex items-center gap-2 rounded-2xl border border-slate-800 bg-slate-950 px-4 py-2 text-sm font-medium text-slate-100 transition hover:border-sky-400 hover:text-sky-300 disabled:cursor-not-allowed disabled:opacity-50"
        >
          <span>Next</span>
          <ChevronRight className="h-4 w-4" />
        </button>
      </div>
    </div>
  )
}

function HistorySkeleton() {
  return (
    <div className="divide-y divide-slate-800">
      {Array.from({ length: 5 }).map((_, index) => (
        <div key={index} className="grid grid-cols-1 gap-4 p-4 lg:grid-cols-[88px_minmax(0,1fr)_auto] lg:items-center">
          <Skeleton className="h-20 w-full rounded-3xl bg-slate-800/70" />
          <div className="space-y-3">
            <Skeleton className="h-11 w-full rounded-3xl bg-slate-800/70" />
            <Skeleton className="h-9 w-3/4 rounded-3xl bg-slate-800/70" />
            <Skeleton className="h-4 w-56 rounded-3xl bg-slate-800/70" />
          </div>
          <Skeleton className="h-9 w-9 rounded-3xl bg-slate-800/70" />
        </div>
      ))}
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
    <article className="grid grid-cols-1 gap-4 p-4 transition-colors hover:bg-slate-900/70 lg:grid-cols-[88px_minmax(0,1fr)_auto] lg:items-center">
      <div className="h-20 w-full overflow-hidden rounded-3xl border border-slate-800 bg-slate-950 lg:w-20">
        {record.image_path ? (
          <img src={record.image_path} alt="Prediction input" className="h-full w-full object-contain" />
        ) : null}
      </div>

      <div className="min-w-0 space-y-3">
        <div className="overflow-x-auto rounded-3xl border border-slate-800 bg-slate-950 px-3 py-2 text-slate-100">
          <span dangerouslySetInnerHTML={{ __html: renderedEquation }} />
        </div>
        <code className="block overflow-x-auto whitespace-pre rounded-3xl bg-slate-900 px-3 py-2 text-xs font-semibold text-sky-300">
          {record.latex_output}
        </code>
        <div className="flex flex-wrap items-center gap-x-4 gap-y-1 text-xs text-slate-500">
          <span className="flex items-center gap-1.5 text-slate-400">
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
        className="inline-flex h-10 w-10 items-center justify-center rounded-3xl border border-slate-800 bg-slate-950 text-slate-300 transition hover:border-rose-500 hover:text-rose-300 disabled:cursor-not-allowed disabled:opacity-50"
        title="Delete history item"
      >
        <Trash2 className="h-4 w-4" />
      </button>
    </article>
  )
}
