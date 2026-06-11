import React, { useState } from 'react'
import ImageUploader from '../components/Upload/ImageUploader.jsx'
import PredictionResult from '../components/Results/PredictionResult.jsx'
import api from '../services/api'
import { Play, AlertCircle } from 'lucide-react'

export default function Home() {
  const [selectedFile, setSelectedFile] = useState(null)
  const [uploadProgress, setUploadProgress] = useState(null)
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

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

      setResult({
        latex: response.data.latex || '',
        confidence: response.data.confidence !== undefined ? response.data.confidence : 0.95,
        symbols_detected: response.data.symbols_detected || 0,
        processing_time_ms: response.data.processing_time_ms || 0,
      })
    } catch (err) {
      console.error('Prediction request failed:', err)
      setError(err.response?.data?.detail || 'An error occurred during formula recognition. Please try again.')
    } finally {
      setLoading(false)
    }
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

        {/* Right Side: Prediction Result */}
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
