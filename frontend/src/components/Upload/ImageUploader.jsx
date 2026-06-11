import React, { useState, useEffect, useRef } from 'react'
import { UploadCloud, X, Image as ImageIcon, AlertCircle, RefreshCw } from 'lucide-react'

export default function ImageUploader({ onImageSelected, uploadProgress = null }) {
  const [file, setFile] = useState(null)
  const [previewUrl, setPreviewUrl] = useState('')
  const [dimensions, setDimensions] = useState(null)
  const [error, setError] = useState('')
  const [isDragActive, setIsDragActive] = useState(false)
  const fileInputRef = useRef(null)

  // Clean up object URLs to prevent memory leaks
  useEffect(() => {
    return () => {
      if (previewUrl) {
        URL.revokeObjectURL(previewUrl)
      }
    }
  }, [previewUrl])

  // Helper to format file sizes
  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes'
    const k = 1024
    const sizes = ['Bytes', 'KB', 'MB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
  }

  // Validate and process the file
  const processFile = (selectedFile) => {
    setError('')
    setDimensions(null)

    if (!selectedFile) return

    // Validate type (jpg, jpeg, png, webp)
    const allowedTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/webp']
    if (!allowedTypes.includes(selectedFile.type)) {
      setError('Unsupported file type. Please upload a JPG, PNG, or WEBP image.')
      return
    }

    // Validate size (max 10 MB = 10 * 1024 * 1024 bytes)
    const maxSize = 10 * 1024 * 1024
    if (selectedFile.size > maxSize) {
      setError('File is too large. Maximum size is 10 MB.')
      return
    }

    // Generate preview URL
    const objectUrl = URL.createObjectURL(selectedFile)
    setPreviewUrl(objectUrl)
    setFile(selectedFile)

    // Calculate dimensions
    const img = new Image()
    img.onload = () => {
      setDimensions({ width: img.width, height: img.height })
      // Callback to parent container
      onImageSelected(selectedFile)
    }
    img.onerror = () => {
      setError('Failed to load image metadata.')
    }
    img.src = objectUrl
  }

  // File selection handlers
  const handleFileChange = (e) => {
    if (e.target.files && e.target.files.length > 0) {
      processFile(e.target.files[0])
    }
  }

  // Drag and drop event handlers
  const handleDragOver = (e) => {
    e.preventDefault()
    setIsDragActive(true)
  }

  const handleDragLeave = (e) => {
    e.preventDefault()
    setIsDragActive(false)
  }

  const handleDrop = (e) => {
    e.preventDefault()
    setIsDragActive(false)
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      processFile(e.dataTransfer.files[0])
    }
  }

  // Remove selected image
  const handleRemove = () => {
    setFile(null)
    setDimensions(null)
    setError('')
    if (previewUrl) {
      URL.revokeObjectURL(previewUrl)
      setPreviewUrl('')
    }
    if (fileInputRef.current) {
      fileInputRef.current.value = ''
    }
    onImageSelected(null)
  }

  return (
    <div className="w-full">
      {/* Upload Zone */}
      {!file ? (
        <div
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
          onClick={() => fileInputRef.current?.click()}
          className={`relative flex flex-col items-center justify-center border-2 border-dashed rounded-2xl p-8 text-center cursor-pointer transition-all min-h-[260px] ${
            isDragActive
              ? 'border-violet-500 bg-violet-600/10 shadow-lg shadow-violet-500/5'
              : 'border-neutral-800 hover:border-neutral-700 bg-neutral-950/40 hover:bg-neutral-900/30'
          }`}
        >
          <input
            type="file"
            ref={fileInputRef}
            onChange={handleFileChange}
            accept=".jpg,.jpeg,.png,.webp"
            className="hidden"
          />

          <div className="p-4 bg-neutral-900/80 border border-neutral-800 rounded-2xl text-violet-400 mb-4 shadow-sm">
            <UploadCloud className="w-8 h-8" />
          </div>

          <h3 className="text-sm font-bold text-white mb-1">
            Drag and drop your image here, or <span className="text-violet-400 hover:text-violet-300">browse</span>
          </h3>
          <p className="text-xs text-neutral-400 max-w-[280px]">
            Supports JPG, JPEG, PNG, and WEBP. Maximum file size is 10 MB.
          </p>

          {error && (
            <div className="absolute bottom-4 left-4 right-4 flex items-center gap-2 p-3 bg-red-950/40 border border-red-500/20 rounded-xl text-red-400 text-xs text-left animate-in fade-in duration-200">
              <AlertCircle className="w-4 h-4 shrink-0" />
              <span>{error}</span>
            </div>
          )}
        </div>
      ) : (
        /* Preview / Detail Card */
        <div className="bg-neutral-950/40 border border-neutral-800 rounded-2xl p-5 shadow-xl animate-in fade-in zoom-in-95 duration-200">
          <div className="flex flex-col md:flex-row gap-5 items-start">
            {/* Image Preview Window */}
            <div className="relative group rounded-xl overflow-hidden border border-neutral-800 bg-neutral-900 w-full md:w-44 h-32 flex items-center justify-center shrink-0">
              <img
                src={previewUrl}
                alt="Upload preview"
                className="w-full h-full object-contain"
              />
              <button
                onClick={handleRemove}
                className="absolute top-2 right-2 p-1.5 bg-neutral-950/80 hover:bg-red-600/90 text-neutral-300 hover:text-white rounded-lg transition-colors cursor-pointer shadow-md"
                title="Remove image"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            {/* Metadata & Progress Details */}
            <div className="flex-1 min-w-0 w-full">
              <div className="flex items-start justify-between">
                <div className="truncate pr-4">
                  <h4 className="text-sm font-bold text-white truncate" title={file.name}>
                    {file.name}
                  </h4>
                  <p className="text-xs text-neutral-400 mt-1">
                    Image File ({(file.type.split('/')[1] || '').toUpperCase()})
                  </p>
                </div>
                <button
                  onClick={handleRemove}
                  className="hidden md:flex items-center gap-1.5 px-3 py-1.5 border border-neutral-800 hover:bg-neutral-800 rounded-xl text-xs font-semibold text-neutral-300 hover:text-white transition-colors cursor-pointer"
                >
                  <X className="w-3.5 h-3.5" />
                  <span>Remove</span>
                </button>
              </div>

              {/* Attributes Checklist */}
              <div className="grid grid-cols-2 gap-4 mt-4 py-3 border-t border-b border-neutral-850">
                <div>
                  <span className="text-[10px] text-neutral-500 uppercase tracking-wider block">File Size</span>
                  <span className="text-xs font-semibold text-neutral-200 mt-0.5 block">
                    {formatFileSize(file.size)}
                  </span>
                </div>
                <div>
                  <span className="text-[10px] text-neutral-500 uppercase tracking-wider block">Dimensions</span>
                  <span className="text-xs font-semibold text-neutral-200 mt-0.5 block">
                    {dimensions ? `${dimensions.width} × ${dimensions.height} px` : 'Calculating...'}
                  </span>
                </div>
              </div>

              {/* Progress Loading Indicator */}
              {uploadProgress !== null && (
                <div className="mt-4">
                  <div className="flex items-center justify-between text-xs mb-1.5">
                    <div className="flex items-center gap-1.5 text-neutral-400">
                      {uploadProgress < 100 ? (
                        <RefreshCw className="w-3 h-3 animate-spin text-violet-400" />
                      ) : null}
                      <span>{uploadProgress < 100 ? 'Uploading to YOLOv11...' : 'Complete!'}</span>
                    </div>
                    <span className="font-mono text-neutral-300 font-semibold">{uploadProgress}%</span>
                  </div>
                  <div className="w-full bg-neutral-900 rounded-full h-1.5 overflow-hidden border border-neutral-800">
                    <div
                      className="bg-gradient-to-r from-violet-600 to-indigo-500 h-full rounded-full transition-all duration-300 ease-out"
                      style={{ width: `${uploadProgress}%` }}
                    />
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
