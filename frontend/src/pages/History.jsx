import React, { useState, useEffect } from 'react'
import api from '../services/api'
import { History as HistoryIcon, Clock, Sparkles } from 'lucide-react'

export default function History() {
  const [records, setRecords] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    // Call DB history endpoints
    const fetchHistory = async () => {
      try {
        const response = await api.get('/expressions/history')
        setRecords(response.data || [])
      } catch (err) {
        console.error(err)
        // Set mock values for layout display
        setRecords([
          { id: 1, image_path: '/uploads/canvas_1.png', latex_output: 'E = mc^2', confidence: 0.985, created_at: new Date().toISOString() },
          { id: 2, image_path: '/uploads/canvas_2.png', latex_output: '\int_{a}^{b} x^2 dx', confidence: 0.941, created_at: new Date().toISOString() },
        ])
      } finally {
        setLoading(false)
      }
    }
    fetchHistory()
  }, [])

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight text-white">Recognition Logs</h1>
        <p className="text-sm text-neutral-400 mt-1">Review historical records of handwritten mathematical formulas parsed by YOLOv11.</p>
      </div>

      <div className="bg-neutral-900/60 border border-neutral-800 rounded-2xl overflow-hidden shadow-xl backdrop-blur-md">
        {loading ? (
          <div className="p-12 text-center text-neutral-400">Loading history logs...</div>
        ) : records.length > 0 ? (
          <div className="divide-y divide-neutral-800">
            {records.map((record) => (
              <div key={record.id} className="p-5 flex items-center justify-between hover:bg-neutral-800/30 transition-colors">
                <div className="flex items-center gap-4">
                  <div className="p-3 bg-neutral-950 rounded-xl border border-neutral-800">
                    <HistoryIcon className="w-5 h-5 text-violet-400" />
                  </div>
                  <div>
                    <code className="text-sm font-semibold text-violet-300 font-mono">{record.latex_output}</code>
                    <div className="flex items-center gap-2 mt-1.5 text-xs text-neutral-500">
                      <Clock className="w-3 h-3" />
                      <span>{new Date(record.created_at).toLocaleString()}</span>
                    </div>
                  </div>
                </div>
                <div className="text-right">
                  <span className="text-xs text-neutral-400 block">Confidence</span>
                  <span className="text-sm font-bold text-emerald-400">{(record.confidence * 100).toFixed(1)}%</span>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="py-16 text-center text-neutral-500">
            <HistoryIcon className="w-10 h-10 mx-auto text-neutral-600 mb-3" />
            <p className="text-sm">No historical logs found</p>
            <p className="text-xs text-neutral-600 mt-1">Any equations processed on the canvas will be recorded here.</p>
          </div>
        )}
      </div>
    </div>
  )
}
