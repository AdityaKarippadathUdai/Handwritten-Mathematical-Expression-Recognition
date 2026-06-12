import React, { useState } from 'react'
import Canvas from '../components/canvas/Canvas.jsx'
import api from '../services/api'
import { Sparkles, FileCode, CheckCircle, Percent } from 'lucide-react'

export default function Dashboard() {
  const [latex, setLatex] = useState('')
  const [confidence, setConfidence] = useState(0)
  const [loading, setLoading] = useState(false)

  const handleRecognize = async (imageBlob) => {
    setLoading(true)
    setLatex('')
    setConfidence(0)
    try {
      const formData = new FormData()
      formData.append('image', imageBlob, 'canvas.png')
      const response = await api.post('/expressions/recognize', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      })
      
      setLatex(response.data.latex || '')
      setConfidence(response.data.confidence || 0)
    } catch (err) {
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="space-y-6 max-w-5xl mx-auto">
      <div>
        <h1 className="text-2xl font-bold tracking-tight text-white">Equation Recognition Hub</h1>
        <p className="text-sm text-neutral-400 mt-1">
          Draw mathematical expressions manually, send them to Pix2Tex OCR, and render structured LaTeX syntax.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Drawing Workspace */}
        <div className="lg:col-span-2">
          <Canvas onRecognize={handleRecognize} loading={loading} />
        </div>

        {/* Results Metadata */}
        <div className="space-y-6">
          <div className="bg-neutral-900/60 border border-neutral-800 rounded-2xl p-6 shadow-xl backdrop-blur-md">
            <h3 className="text-sm font-semibold text-neutral-400 tracking-wider uppercase mb-4">Recognition Output</h3>

            {latex ? (
              <div className="space-y-4">
                <div className="bg-neutral-950 p-4 rounded-xl border border-neutral-800 flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <FileCode className="w-5 h-5 text-violet-400" />
                    <div>
                      <span className="text-xs text-neutral-400 block">LaTeX Format</span>
                      <code className="text-sm text-violet-300 font-mono font-semibold">{latex}</code>
                    </div>
                  </div>
                </div>

                <div className="bg-neutral-950 p-4 rounded-xl border border-neutral-800 flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <Percent className="w-5 h-5 text-emerald-400" />
                    <div>
                      <span className="text-xs text-neutral-400 block">OCR Confidence</span>
                      <span className="text-sm text-emerald-400 font-semibold">{(confidence * 100).toFixed(1)}%</span>
                    </div>
                  </div>
                  <CheckCircle className="w-5 h-5 text-emerald-500" />
                </div>

                <div className="p-4 rounded-xl bg-violet-600/10 border border-violet-500/20 text-xs text-neutral-300 leading-relaxed flex gap-2">
                  <Sparkles className="w-4 h-4 text-violet-400 shrink-0" />
                  <span>
                    Copy LaTeX code and paste it directly into your math documents, markdown reports, or MathJax engine scripts.
                  </span>
                </div>
              </div>
            ) : (
              <div className="py-12 text-center text-neutral-500">
                <FileCode className="w-8 h-8 mx-auto text-neutral-600 mb-2" />
                <p className="text-sm">No expressions analyzed yet</p>
                <p className="text-xs text-neutral-600 mt-1">Draw an equation and press recognize.</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
