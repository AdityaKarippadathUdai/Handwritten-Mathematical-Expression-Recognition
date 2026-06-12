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
  const ocrTime = Number(result?.ocr_time_ms || 0)
  const preprocessingTime = Number(result?.preprocessing_time_ms || 0)
  const predictionId = result?.prediction_id || ''
  const createdAt = result?.created_at ? new Date(result.created_at).toLocaleString() : ''

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
      <section className="rounded-3xl border border-slate-800 bg-slate-950/80 p-6 shadow-2xl shadow-slate-950/20">
        <div className="flex items-center justify-between gap-3">
          <Skeleton className="h-4 w-36 rounded-full bg-slate-800/70" />
          <RefreshCw className="h-4 w-4 animate-spin text-sky-400" />
        </div>
        <Skeleton className="mt-6 h-52 rounded-3xl bg-slate-800/70" />
        <div className="mt-6 space-y-4">
          <Skeleton className="h-12 rounded-3xl bg-slate-800/70" />
          <Skeleton className="h-24 rounded-3xl bg-slate-800/70" />
          <div className="grid gap-3 sm:grid-cols-3">
            <Skeleton className="h-20 rounded-3xl bg-slate-800/70" />
            <Skeleton className="h-20 rounded-3xl bg-slate-800/70" />
            <Skeleton className="h-20 rounded-3xl bg-slate-800/70" />
          </div>
        </div>
      </section>
    )
  }

  if (!result) {
    return (
      <section className="flex min-h-[360px] flex-col items-center justify-center rounded-3xl border border-slate-800 bg-slate-950/80 p-8 text-center shadow-2xl shadow-slate-950/20">
        <FileCode2 className="h-10 w-10 text-slate-500" />
        <h2 className="mt-4 text-sm font-semibold text-slate-100">No prediction yet</h2>
        <p className="mt-2 max-w-xs text-xs leading-5 text-slate-400">
          Upload an equation image and run prediction to view the rendered result, metrics, and LaTeX actions.
        </p>
      </section>
    )
  }

  return (
    <section className="overflow-hidden rounded-3xl border border-slate-800 bg-slate-950/80 shadow-2xl shadow-slate-950/20">
      <div className="grid grid-cols-1 xl:grid-cols-[minmax(220px,0.9fr)_minmax(0,1.35fr)]">
        <div className="border-b border-slate-800 bg-slate-900/80 p-4 xl:border-b-0 xl:border-r">
          <div className="flex items-center justify-between gap-3">
            <h2 className="text-sm font-semibold text-slate-100">Uploaded Image</h2>
            <ImageIcon className="h-4 w-4 text-slate-500" />
          </div>
          <div className="mt-4 aspect-[4/3] overflow-hidden rounded-3xl border border-slate-800 bg-slate-950 flex items-center justify-center">
            {previewUrl ? (
              <img src={previewUrl} alt="Uploaded equation" className="h-full w-full object-contain" />
            ) : (
              <span className="text-xs text-slate-500">Image preview unavailable</span>
            )}
          </div>
        </div>

        <div className="p-4 sm:p-5 space-y-5">
          <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
            <div className="min-w-0">
              <p className="text-xs font-medium uppercase tracking-wide text-slate-400">Generated LaTeX</p>
              <code className="mt-2 block overflow-x-auto rounded-3xl border border-slate-800 bg-slate-950 px-3 py-3 text-sm font-semibold text-sky-300">
                {latex}
              </code>
            </div>
            <div className="flex shrink-0 items-center gap-2">
              <button
                type="button"
                onClick={handleCopy}
                className="inline-flex h-9 w-9 items-center justify-center rounded-2xl border border-slate-800 bg-slate-900 text-slate-200 hover:border-sky-400 hover:text-sky-300 transition"
                title="Copy LaTeX"
              >
                {copied ? <Check className="h-4 w-4 text-emerald-400" /> : <Clipboard className="h-4 w-4" />}
              </button>
              <button
                type="button"
                onClick={handleDownload}
                className="inline-flex h-9 w-9 items-center justify-center rounded-2xl border border-slate-800 bg-slate-900 text-slate-200 hover:border-sky-400 hover:text-sky-300 transition"
                title="Download LaTeX"
              >
                <Download className="h-4 w-4" />
              </button>
              <button
                type="button"
                onClick={onRerun}
                disabled={!onRerun || isRerunning}
                className="inline-flex h-9 w-9 items-center justify-center rounded-2xl border border-slate-800 bg-slate-900 text-slate-200 hover:border-sky-400 hover:text-sky-300 disabled:cursor-not-allowed disabled:opacity-50 transition"
                title="Re-run prediction"
              >
                <RefreshCw className={`h-4 w-4 ${isRerunning ? 'animate-spin' : ''}`} />
              </button>
            </div>
          </div>

          <div>
            <p className="text-xs font-medium uppercase tracking-wide text-slate-400">Rendered Equation</p>
            <div
              className="mt-2 min-h-24 overflow-x-auto rounded-3xl border border-slate-800 bg-white px-4 py-5 text-slate-950"
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
              label="Total Time"
              value={`${processingTime} ms`}
            />
            <Metric
              icon={<Sigma className="h-4 w-4 text-sky-300" />}
              label="Pix2Tex OCR"
              value={`${ocrTime} ms`}
            />
          </div>
          <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
            <Metric
              icon={<Clock3 className="h-4 w-4 text-slate-300" />}
              label="Preprocessing"
              value={`${preprocessingTime} ms`}
            />
            <Metric
              icon={<FileCode2 className="h-4 w-4 text-slate-300" />}
              label="Prediction ID"
              value={predictionId ? predictionId.slice(0, 8) : 'Pending'}
            />
          </div>
          {createdAt && (
            <p className="text-xs text-slate-500">Created {createdAt}</p>
          )}
        </div>
      </div>
    </section>
  )
}

function Metric({ icon, label, value }) {
  return (
    <div className="rounded-3xl border border-slate-800 bg-slate-950 p-4">
      <div className="flex items-center gap-2 text-xs font-medium uppercase tracking-wide text-slate-400">
        {icon}
        <span>{label}</span>
      </div>
      <div className="mt-2 text-lg font-semibold text-slate-100">{value}</div>
    </div>
  )
}
