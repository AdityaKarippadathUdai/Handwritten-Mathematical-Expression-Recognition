import React, { useEffect, useMemo, useState } from 'react'
import katex from 'katex'
import 'katex/dist/katex.min.css'
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
  }

  if (!result) {
    return (
      <section className="min-h-[360px] rounded-lg border border-neutral-800 bg-neutral-950/50 p-8 flex flex-col items-center justify-center text-center">
        <FileCode2 className="h-10 w-10 text-neutral-700" />
        <h2 className="mt-4 text-sm font-semibold text-neutral-300">No prediction yet</h2>
        <p className="mt-2 max-w-xs text-xs leading-5 text-neutral-500">
          Upload an equation image and run prediction to view the rendered result, metrics, and LaTeX actions.
        </p>
      </section>
    )
  }

  return (
    <section className="rounded-lg border border-neutral-800 bg-neutral-950/50 overflow-hidden">
      <div className="grid grid-cols-1 xl:grid-cols-[minmax(220px,0.9fr)_minmax(0,1.35fr)]">
        <div className="border-b border-neutral-800 bg-neutral-900/40 p-4 xl:border-b-0 xl:border-r">
          <div className="flex items-center justify-between gap-3">
            <h2 className="text-sm font-semibold text-neutral-200">Uploaded Image</h2>
            <ImageIcon className="h-4 w-4 text-neutral-500" />
          </div>
          <div className="mt-4 aspect-[4/3] rounded-lg border border-neutral-800 bg-neutral-950 flex items-center justify-center overflow-hidden">
            {previewUrl ? (
              <img src={previewUrl} alt="Uploaded equation" className="h-full w-full object-contain" />
            ) : (
              <span className="text-xs text-neutral-600">Image preview unavailable</span>
            )}
          </div>
        </div>

        <div className="p-4 sm:p-5 space-y-5">
          <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
            <div className="min-w-0">
              <p className="text-xs font-medium uppercase tracking-wide text-neutral-500">Generated LaTeX</p>
              <code className="mt-2 block rounded-lg border border-neutral-800 bg-neutral-900 px-3 py-3 text-sm font-semibold text-sky-300 overflow-x-auto">
                {latex}
              </code>
            </div>
            <div className="flex shrink-0 items-center gap-2">
              <button
                type="button"
                onClick={handleCopy}
                className="inline-flex h-9 w-9 items-center justify-center rounded-lg border border-neutral-800 bg-neutral-900 text-neutral-300 hover:border-sky-500/50 hover:text-sky-300 transition-colors"
                title="Copy LaTeX"
              >
                {copied ? <Check className="h-4 w-4 text-emerald-400" /> : <Clipboard className="h-4 w-4" />}
              </button>
              <button
                type="button"
                onClick={handleDownload}
                className="inline-flex h-9 w-9 items-center justify-center rounded-lg border border-neutral-800 bg-neutral-900 text-neutral-300 hover:border-sky-500/50 hover:text-sky-300 transition-colors"
                title="Download LaTeX"
              >
                <Download className="h-4 w-4" />
              </button>
              <button
                type="button"
                onClick={onRerun}
                disabled={!onRerun || isRerunning}
                className="inline-flex h-9 w-9 items-center justify-center rounded-lg border border-neutral-800 bg-neutral-900 text-neutral-300 hover:border-sky-500/50 hover:text-sky-300 disabled:cursor-not-allowed disabled:opacity-50 transition-colors"
                title="Re-run prediction"
              >
                <RefreshCw className={`h-4 w-4 ${isRerunning ? 'animate-spin' : ''}`} />
              </button>
            </div>
          </div>

          <div>
            <p className="text-xs font-medium uppercase tracking-wide text-neutral-500">Rendered Equation</p>
            <div
              className="mt-2 min-h-24 rounded-lg border border-neutral-800 bg-white px-4 py-5 text-neutral-950 overflow-x-auto"
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
    <div className="rounded-lg border border-neutral-800 bg-neutral-900 p-4">
      <div className="flex items-center gap-2 text-xs font-medium uppercase tracking-wide text-neutral-500">
        {icon}
        <span>{label}</span>
      </div>
      <div className="mt-2 text-lg font-semibold text-neutral-100">{value}</div>
    </div>
  )
}
