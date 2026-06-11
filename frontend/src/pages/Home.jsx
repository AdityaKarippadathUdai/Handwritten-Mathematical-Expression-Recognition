import React, { useState } from 'react'
import ImageUploader from '../components/Upload/ImageUploader.jsx'
import PredictionResult from '../components/Results/PredictionResult.jsx'
import api from '../services/api'
import { useToast } from '../context/ToastContext.jsx'
import { AlertCircle, ArrowRight, BrainCircuit, CheckCircle2, Loader2, Play, Sparkles } from 'lucide-react'

const workflow = [
  ['Upload image', 'JPG, PNG, or WEBP up to 10 MB'],
  ['Run recognition', 'YOLOv11 detects math symbols'],
  ['Export LaTeX', 'Copy, download, and revisit later'],
]

export default function Home() {
  const [selectedFile, setSelectedFile] = useState(null)
  const [uploadProgress, setUploadProgress] = useState(null)
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const { showToast } = useToast()

  const handleImageSelected = (file) => {
    setSelectedFile(file)
    setResult(null)
    setError('')
    setUploadProgress(null)
  }

  const handlePredict = async () => {
    if (!selectedFile) return

    setLoading(true)
    setError('')
    setResult(null)
    setUploadProgress(0)

    const formData = new FormData()
    formData.append('image', selectedFile)

    try {
      const response = await api.post('/predict', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        // Track actual HTTP upload progress
        onUploadProgress: (progressEvent) => {
          const total = progressEvent.total || selectedFile.size
          const current = progressEvent.loaded
          const percentCompleted = Math.round((current * 100) / total)
          setUploadProgress(percentCompleted)
        },
      })

      const nextResult = {
        latex: response.data.latex || '',
        confidence: response.data.confidence !== undefined ? response.data.confidence : 0.95,
        symbols_detected: response.data.symbols_detected || 0,
        processing_time_ms: response.data.processing_time_ms || 0,
      }
      setResult(nextResult)
      showToast({
        type: 'success',
        title: 'Prediction complete',
        message: nextResult.latex ? 'The equation is ready to render and export.' : 'The model responded without LaTeX output.',
      })
    } catch (err) {
      console.error('Prediction request failed:', err)
      const message = err.response?.data?.detail || 'An error occurred during formula recognition. Please try again.'
      setError(message)
      showToast({ type: 'error', title: 'Prediction failed', message })
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="mx-auto max-w-6xl space-y-6">
      <section className="overflow-hidden rounded-lg border border-slate-200 bg-white shadow-sm dark:border-white/10 dark:bg-neutral-900">
        <div className="grid gap-0 lg:grid-cols-[1.05fr_0.95fr]">
          <div className="p-6 sm:p-8">
            <div className="inline-flex items-center gap-2 rounded-full border border-sky-200 bg-sky-50 px-3 py-1 text-xs font-semibold text-sky-700 dark:border-sky-400/20 dark:bg-sky-400/10 dark:text-sky-300">
              <Sparkles className="h-3.5 w-3.5" />
              Handwriting to LaTeX AI
            </div>
            <h1 className="mt-5 max-w-2xl text-3xl font-semibold tracking-tight text-slate-950 dark:text-white sm:text-4xl">
              Convert handwritten math into publication-ready LaTeX.
            </h1>
            <p className="mt-4 max-w-2xl text-sm leading-6 text-slate-600 dark:text-neutral-400">
              Upload an equation image, send it through the recognition pipeline, then review rendered output, confidence, symbols, and export actions in one workspace.
            </p>
          </div>

          <div className="border-t border-slate-200 bg-slate-50 p-6 dark:border-white/10 dark:bg-white/5 lg:border-l lg:border-t-0">
            <div className="grid gap-3">
              {workflow.map(([title, text], index) => (
                <div key={title} className="flex items-center gap-3 rounded-lg border border-slate-200 bg-white p-3 dark:border-white/10 dark:bg-neutral-950/60">
                  <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-slate-950 text-sm font-bold text-white dark:bg-white dark:text-neutral-950">
                    {index + 1}
                  </div>
                  <div className="min-w-0">
                    <p className="text-sm font-semibold text-slate-950 dark:text-white">{title}</p>
                    <p className="text-xs text-slate-500 dark:text-neutral-500">{text}</p>
                  </div>
                  {index < workflow.length - 1 ? <ArrowRight className="ml-auto hidden h-4 w-4 text-slate-300 sm:block" /> : <CheckCircle2 className="ml-auto h-4 w-4 text-emerald-500" />}
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      <div className="grid grid-cols-1 items-start gap-6 lg:grid-cols-12">
        <div className="space-y-4 lg:col-span-7">
          <section className="rounded-lg border border-slate-200 bg-white p-5 shadow-sm dark:border-white/10 dark:bg-neutral-900 sm:p-6">
            <div className="mb-5 flex items-center justify-between gap-3">
              <div>
                <h2 className="text-sm font-semibold uppercase tracking-wide text-slate-500 dark:text-neutral-400">Input Source</h2>
                <p className="mt-1 text-sm text-slate-600 dark:text-neutral-500">Drop in a clear equation crop for best recognition.</p>
              </div>
              <BrainCircuit className="h-5 w-5 text-sky-500" />
            </div>
            <ImageUploader onImageSelected={handleImageSelected} uploadProgress={uploadProgress} />

            {selectedFile && (
              <button
                onClick={handlePredict}
                disabled={loading}
                className="mt-4 flex w-full items-center justify-center gap-2 rounded-lg bg-slate-950 py-3 text-sm font-semibold text-white shadow-sm transition-colors hover:bg-slate-800 disabled:cursor-not-allowed disabled:bg-slate-300 dark:bg-white dark:text-neutral-950 dark:hover:bg-neutral-200 dark:disabled:bg-white/20 dark:disabled:text-neutral-500"
              >
                {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : <Play className="h-4 w-4" />}
                <span>{loading ? 'Processing Formula...' : 'Run Recognition'}</span>
              </button>
            )}

            {error && (
              <div className="mt-4 flex items-center gap-2.5 rounded-lg border border-rose-200 bg-rose-50 p-4 text-xs text-rose-700 dark:border-rose-500/20 dark:bg-rose-950/30 dark:text-rose-300">
                <AlertCircle className="h-4 w-4 shrink-0" />
                <span>{error}</span>
              </div>
            )}
          </section>
        </div>

        <div className="lg:col-span-5">
          <PredictionResult
            result={result}
            imageFile={selectedFile}
            onRerun={selectedFile ? handlePredict : undefined}
            isRerunning={loading}
          />
        </div>
      </div>
    </div>
  )
}
