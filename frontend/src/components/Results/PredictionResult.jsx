import React, { useEffect, useMemo, useState } from 'react'
import katex from 'katex'
import 'katex/dist/katex.min.css'
import Skeleton from '../common/Skeleton.jsx'
import { useToast } from '../../context/ToastContext.jsx'
import {
  Check,
  Clipboard,
  Clock3,
  Download,
  FileCode2,
  Image as ImageIcon,
  Percent,
  RefreshCw,
  Sigma,
} from 'lucide-react'

export default function PredictionResult({
  result,
  imageFile = null,
  imageUrl = '',
  onRerun,
  isRerunning = false,
}) {
  const [copied, setCopied] = useState(false)
  const [previewUrl, setPreviewUrl] = useState(imageUrl)
  const { showToast } = useToast()

  useEffect(() => {
    if (!imageFile) {
      setPreviewUrl(imageUrl)
      return undefined
    }

    const objectUrl = URL.createObjectURL(imageFile)
    setPreviewUrl(objectUrl)

    return () => URL.revokeObjectURL(objectUrl)
  }, [imageFile, imageUrl])

  const latex = result?.latex || ''
  const confidence = Number(result?.confidence || 0)
  const processingTime = Number(result?.processing_time_ms || 0)
  const symbolsDetected = Number(result?.symbols_detected || 0)

  const renderedEquation = useMemo(() => {
    if (!latex) return ''
    return katex.renderToString(latex, {
      displayMode: true,
      throwOnError: false,
      strict: false,
    })
  }, [latex])

  const handleCopy = async () => {
    if (!latex) return
    await navigator.clipboard.writeText(latex)
    setCopied(true)
    showToast({ type: 'success', title: 'LaTeX copied', message: 'The generated expression is on your clipboard.' })
    window.setTimeout(() => setCopied(false), 1800)
  }

  const handleDownload = () => {
    if (!latex) return

    const blob = new Blob([latex], { type: 'text/plain;charset=utf-8' })
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = 'prediction.tex'
    document.body.appendChild(link)
    link.click()
    link.remove()
    URL.revokeObjectURL(url)
    showToast({ type: 'success', title: 'LaTeX downloaded', message: 'Saved as prediction.tex.' })
  }

  if (isRerunning && !result) {
    return (
      <section className="rounded-lg border border-slate-200 bg-white p-5 shadow-sm dark:border-white/10 dark:bg-neutral-900">
        <div className="flex items-center justify-between">
          <Skeleton className="h-4 w-36" />
          <RefreshCw className="h-4 w-4 animate-spin text-sky-500" />
        </div>
        <Skeleton className="mt-5 h-40 w-full" />
        <div className="mt-5 space-y-3">
          <Skeleton className="h-11 w-full" />
          <Skeleton className="h-24 w-full" />
          <div className="grid grid-cols-3 gap-3">
            <Skeleton className="h-20" />
            <Skeleton className="h-20" />
            <Skeleton className="h-20" />
          </div>
        </div>
      </section>
    )
  }

  if (!result) {
    return (
      <section className="flex min-h-[360px] flex-col items-center justify-center rounded-lg border border-slate-200 bg-white p-8 text-center shadow-sm dark:border-white/10 dark:bg-neutral-900">
        <FileCode2 className="h-10 w-10 text-slate-300 dark:text-neutral-700" />
        <h2 className="mt-4 text-sm font-semibold text-slate-800 dark:text-neutral-300">No prediction yet</h2>
        <p className="mt-2 max-w-xs text-xs leading-5 text-slate-500 dark:text-neutral-500">
          Upload an equation image and run prediction to view the rendered result, metrics, and LaTeX actions.
        </p>
      </section>
    )
  }

  return (
    <section className="overflow-hidden rounded-lg border border-slate-200 bg-white shadow-sm dark:border-white/10 dark:bg-neutral-900">
      <div className="grid grid-cols-1 xl:grid-cols-[minmax(220px,0.9fr)_minmax(0,1.35fr)]">
        <div className="border-b border-slate-200 bg-slate-50 p-4 dark:border-white/10 dark:bg-neutral-950/50 xl:border-b-0 xl:border-r">
          <div className="flex items-center justify-between gap-3">
            <h2 className="text-sm font-semibold text-slate-800 dark:text-neutral-200">Uploaded Image</h2>
            <ImageIcon className="h-4 w-4 text-slate-400 dark:text-neutral-500" />
          </div>
          <div className="mt-4 flex aspect-[4/3] items-center justify-center overflow-hidden rounded-lg border border-slate-200 bg-white dark:border-white/10 dark:bg-neutral-950">
            {previewUrl ? (
              <img src={previewUrl} alt="Uploaded equation" className="h-full w-full object-contain" />
            ) : (
              <span className="text-xs text-slate-400 dark:text-neutral-600">Image preview unavailable</span>
            )}
          </div>
        </div>

        <div className="p-4 sm:p-5 space-y-5">
          <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
            <div className="min-w-0">
              <p className="text-xs font-medium uppercase tracking-wide text-slate-500 dark:text-neutral-500">Generated LaTeX</p>
              <code className="mt-2 block overflow-x-auto rounded-lg border border-slate-200 bg-slate-50 px-3 py-3 text-sm font-semibold text-sky-700 dark:border-white/10 dark:bg-neutral-950 dark:text-sky-300">
                {latex}
              </code>
            </div>
            <div className="flex shrink-0 items-center gap-2">
              <button
                type="button"
                onClick={handleCopy}
                className="inline-flex h-9 w-9 items-center justify-center rounded-lg border border-slate-200 bg-white text-slate-600 transition-colors hover:border-sky-300 hover:text-sky-600 dark:border-white/10 dark:bg-white/5 dark:text-neutral-300 dark:hover:border-sky-500/50 dark:hover:text-sky-300"
                title="Copy LaTeX"
              >
                {copied ? <Check className="h-4 w-4 text-emerald-400" /> : <Clipboard className="h-4 w-4" />}
              </button>
              <button
                type="button"
                onClick={handleDownload}
                className="inline-flex h-9 w-9 items-center justify-center rounded-lg border border-slate-200 bg-white text-slate-600 transition-colors hover:border-sky-300 hover:text-sky-600 dark:border-white/10 dark:bg-white/5 dark:text-neutral-300 dark:hover:border-sky-500/50 dark:hover:text-sky-300"
                title="Download LaTeX"
              >
                <Download className="h-4 w-4" />
              </button>
              <button
                type="button"
                onClick={onRerun}
                disabled={!onRerun || isRerunning}
                className="inline-flex h-9 w-9 items-center justify-center rounded-lg border border-slate-200 bg-white text-slate-600 transition-colors hover:border-sky-300 hover:text-sky-600 disabled:cursor-not-allowed disabled:opacity-50 dark:border-white/10 dark:bg-white/5 dark:text-neutral-300 dark:hover:border-sky-500/50 dark:hover:text-sky-300"
                title="Re-run prediction"
              >
                <RefreshCw className={`h-4 w-4 ${isRerunning ? 'animate-spin' : ''}`} />
              </button>
            </div>
          </div>

          <div>
            <p className="text-xs font-medium uppercase tracking-wide text-slate-500 dark:text-neutral-500">Rendered Equation</p>
            <div
              className="mt-2 min-h-24 overflow-x-auto rounded-lg border border-slate-200 bg-white px-4 py-5 text-neutral-950 dark:border-white/10"
              dangerouslySetInnerHTML={{ __html: renderedEquation }}
            />
          </div>

          <div className="grid grid-cols-1 gap-3 sm:grid-cols-3">
            <Metric
              icon={<Percent className="h-4 w-4 text-emerald-400" />}
              label="Confidence"
              value={`${(confidence * 100).toFixed(1)}%`}
            />
            <Metric
              icon={<Clock3 className="h-4 w-4 text-amber-300" />}
              label="Processing Time"
              value={`${processingTime} ms`}
            />
            <Metric
              icon={<Sigma className="h-4 w-4 text-sky-300" />}
              label="Detected Symbols"
              value={symbolsDetected}
            />
          </div>
        </div>
      </div>
    </section>
  )
}

function Metric({ icon, label, value }) {
  return (
    <div className="rounded-lg border border-slate-200 bg-slate-50 p-4 dark:border-white/10 dark:bg-neutral-950/50">
      <div className="flex items-center gap-2 text-xs font-medium uppercase tracking-wide text-slate-500 dark:text-neutral-500">
        {icon}
        <span>{label}</span>
      </div>
      <div className="mt-2 text-lg font-semibold text-slate-950 dark:text-neutral-100">{value}</div>
    </div>
  )
}
