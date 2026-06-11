import React from 'react'
import { useCanvas } from '../../hooks/useCanvas'
import { Trash2, Send, Sliders } from 'lucide-react'

export default function Canvas({ onRecognize, loading }) {
  const {
    canvasRef,
    brushWidth,
    setBrushWidth,
    startDrawing,
    draw,
    stopDrawing,
    clearCanvas,
  } = useCanvas()

  const handleRecognize = () => {
    const canvas = canvasRef.current
    if (!canvas) return
    canvas.toBlob((blob) => {
      if (blob) {
        onRecognize(blob)
      }
    }, 'image/png')
  }

  return (
    <div className="bg-neutral-900/60 border border-neutral-800 rounded-2xl p-6 shadow-xl backdrop-blur-md">
      <div className="flex items-center justify-between mb-4">
        <div>
          <h2 className="text-lg font-bold text-white">Drawing Canvas</h2>
          <p className="text-xs text-neutral-400">Write mathematical symbols clearly inside the box.</p>
        </div>
        <div className="flex items-center gap-4 bg-neutral-950/40 px-3 py-1.5 rounded-xl border border-neutral-800">
          <div className="flex items-center gap-2 text-xs text-neutral-400">
            <Sliders className="w-3.5 h-3.5" />
            <span>Brush Width:</span>
          </div>
          <input
            type="range"
            min="2"
            max="12"
            value={brushWidth}
            onChange={(e) => setBrushWidth(parseInt(e.target.value))}
            className="w-24 h-1.5 bg-neutral-800 rounded-lg appearance-none cursor-pointer accent-violet-500"
          />
          <span className="text-xs font-mono text-neutral-300 w-4">{brushWidth}px</span>
        </div>
      </div>

      <div className="relative border-2 border-dashed border-neutral-800 hover:border-neutral-700 bg-neutral-950 rounded-xl overflow-hidden transition-colors">
        <canvas
          ref={canvasRef}
          width={700}
          height={380}
          onMouseDown={startDrawing}
          onMouseMove={draw}
          onMouseUp={stopDrawing}
          onMouseLeave={stopDrawing}
          className="w-full block bg-white cursor-crosshair"
        />
      </div>

      <div className="flex items-center justify-end gap-3 mt-4">
        <button
          onClick={clearCanvas}
          className="flex items-center gap-2 px-4 py-2.5 rounded-xl text-sm font-medium border border-neutral-800 hover:bg-neutral-800 text-neutral-300 transition-colors cursor-pointer"
        >
          <Trash2 className="w-4 h-4 text-neutral-400" />
          <span>Clear Canvas</span>
        </button>
        <button
          onClick={handleRecognize}
          disabled={loading}
          className="flex items-center gap-2 px-5 py-2.5 bg-violet-600 hover:bg-violet-500 disabled:bg-neutral-800 text-white rounded-xl text-sm font-semibold transition-all shadow-md shadow-violet-600/20 cursor-pointer"
        >
          <Send className="w-4 h-4" />
          <span>{loading ? 'Analyzing...' : 'Recognize Equation'}</span>
        </button>
      </div>
    </div>
  )
}
