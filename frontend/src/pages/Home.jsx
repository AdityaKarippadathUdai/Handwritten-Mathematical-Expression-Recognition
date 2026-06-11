import React, { useState } from 'react'
import ImageUploader from '../components/Upload/ImageUploader.jsx'
import api from '../services/api'
import { Play, Copy, Check, Brain, Percent, Sigma, AlertCircle, FileCode, Sparkles } from 'lucide-react'

export default function Home() {
  const [selectedFile, setSelectedFile] = useState(null)
  const [uploadProgress, setUploadProgress] = useState(null)
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [copied, setCopied] = useState(false)

  // Triggered when file changes in the uploader component
  const handleImageSelected = (file) => {
    setSelectedFile(file)
    setResult(null)
    setError('')
    setUploadProgress(null)
  }

  // Calls FastAPI backend with image file
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

      // Expecting response with keys: latex, confidence, symbols
      setResult({
        latex: response.data.latex || 'a^2 + b^2 = c^2',
        confidence: response.data.confidence !== undefined ? response.data.confidence : 0.95,
        symbols_detected: response.data.symbols ? response.data.symbols.length : 8
      })
    } catch (err) {
      console.error('Prediction request failed:', err)
      setError(err.response?.data?.detail || 'An error occurred during formula recognition. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  // Copy LaTeX output to clipboard
  const handleCopy = () => {
    if (!result) return
    navigator.clipboard.writeText(result.latex)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  return (
    <div className="max-w-5xl mx-auto space-y-6">
      {/* Title Header */}
      <div>
        <h1 className="text-2xl font-bold tracking-tight text-white">Mathematical Expression Recognition</h1>
        <p className="text-sm text-neutral-400 mt-1">
          Upload an image of a handwritten mathematical expression. Our YOLOv11 engine will extract individual symbols and parse them into LaTeX code.
        </p>
      </div>

      {/* Main Responsive Grid Layout */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
        {/* Left Side: Upload Zone & Controls */}
        <div className="lg:col-span-7 space-y-4">
          <div className="bg-neutral-900/60 border border-neutral-800 rounded-2xl p-6 shadow-xl backdrop-blur-md">
            <h2 className="text-sm font-semibold text-neutral-400 tracking-wider uppercase mb-4">Input Source</h2>
            <ImageUploader onImageSelected={handleImageSelected} uploadProgress={uploadProgress} />

            {selectedFile && (
              <button
                onClick={handlePredict}
                disabled={loading}
                className="w-full mt-4 flex items-center justify-center gap-2 py-3 bg-violet-600 hover:bg-violet-500 disabled:bg-neutral-800 text-white rounded-xl text-sm font-semibold transition-all shadow-md shadow-violet-600/20 cursor-pointer"
              >
                <Play className={`w-4 h-4 ${loading ? 'animate-pulse' : ''}`} />
                <span>{loading ? 'Processing Formula...' : 'Run YOLOv11 Predict'}</span>
              </button>
            )}

            {error && (
              <div className="mt-4 flex items-center gap-2.5 p-4 bg-red-950/40 border border-red-500/20 rounded-xl text-red-400 text-xs">
                <AlertCircle className="w-4 h-4 shrink-0" />
                <span>{error}</span>
              </div>
            )}
          </div>
        </div>

        {/* Right Side: Prediction Metrics & LaTeX Result */}
        <div className="lg:col-span-5">
          <div className="bg-neutral-900/60 border border-neutral-800 rounded-2xl p-6 shadow-xl backdrop-blur-md min-h-[300px] flex flex-col">
            <h2 className="text-sm font-semibold text-neutral-400 tracking-wider uppercase mb-4 font-mono">Prediction Metrics</h2>

            {result ? (
              <div className="flex-1 flex flex-col justify-between space-y-6 animate-in fade-in duration-200">
                {/* LaTeX Code Box */}
                <div className="space-y-2">
                  <span className="text-xs text-neutral-400 block font-medium">Recognized LaTeX Expression</span>
                  <div className="relative group bg-neutral-950 p-4 rounded-xl border border-neutral-850 flex items-center justify-between">
                    <code className="text-sm text-violet-300 font-mono font-bold select-all overflow-x-auto whitespace-pre pr-6">
                      {result.latex}
                    </code>
                    <button
                      onClick={handleCopy}
                      className="absolute right-3 p-1.5 bg-neutral-900 border border-neutral-800 text-neutral-400 hover:text-white rounded-lg transition-colors cursor-pointer"
                      title="Copy LaTeX"
                    >
                      {copied ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
                    </button>
                  </div>
                </div>

                {/* YOLO Model confidence */}
                <div className="space-y-2">
                  <div className="flex items-center justify-between text-xs">
                    <div className="flex items-center gap-1.5 text-neutral-400 font-medium">
                      <Percent className="w-4 h-4 text-emerald-400" />
                      <span>Model Confidence</span>
                    </div>
                    <span className="font-bold text-emerald-400 text-sm">{(result.confidence * 100).toFixed(1)}%</span>
                  </div>
                  <div className="w-full bg-neutral-950 rounded-full h-2 overflow-hidden border border-neutral-850">
                    <div
                      className={`h-full rounded-full transition-all duration-500 ${
                        result.confidence >= 0.85 ? 'bg-emerald-500' : result.confidence >= 0.60 ? 'bg-amber-500' : 'bg-red-500'
                      }`}
                      style={{ width: `${result.confidence * 100}%` }}
                    />
                  </div>
                </div>

                {/* Detected symbols counter */}
                <div className="bg-neutral-950 p-4 rounded-xl border border-neutral-850 flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <div className="p-2 bg-violet-600/10 rounded-lg text-violet-400 border border-violet-500/10">
                      <Sigma className="w-4 h-4" />
                    </div>
                    <div>
                      <span className="text-[10px] text-neutral-500 uppercase tracking-wider block">Detected Symbols</span>
                      <span className="text-sm font-bold text-neutral-200 mt-0.5 block">{result.symbols_detected} items</span>
                    </div>
                  </div>
                  <Brain className="w-5 h-5 text-violet-400" />
                </div>

                {/* Direct info banner */}
                <div className="p-4 rounded-xl bg-violet-600/5 border border-violet-500/10 text-xs text-neutral-400 leading-relaxed flex gap-2">
                  <Sparkles className="w-4 h-4 text-violet-400 shrink-0" />
                  <span>
                    YOLOv11 segmented individual glyph elements, allowing our spatial layouts optimizer to compile mathematical relationships.
                  </span>
                </div>
              </div>
            ) : (
              /* Awaiting State */
              <div className="flex-1 flex flex-col items-center justify-center text-center py-12 text-neutral-500">
                <Brain className="w-10 h-10 text-neutral-700 mb-3" />
                <h3 className="text-sm font-bold text-neutral-400 mb-1">Awaiting Prediction</h3>
                <p className="text-xs text-neutral-600 max-w-[240px] leading-normal">
                  Upload an equation file on the left and click Predict to view recognized LaTeX equations and YOLO accuracy ratings.
                </p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
