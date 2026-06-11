import React, { useEffect, useRef, useState } from 'react'
import { AlertCircle, RefreshCw, UploadCloud, X } from 'lucide-react'

export default function ImageUploader({ onImageSelected, uploadProgress = null }) {
  const [file, setFile] = useState(null)
  const [previewUrl, setPreviewUrl] = useState('')
  const [dimensions, setDimensions] = useState(null)
  const [error, setError] = useState('')
  const [isDragActive, setIsDragActive] = useState(false)
  const fileInputRef = useRef(null)

  useEffect(() => {
    return () => {
      if (previewUrl) {
        URL.revokeObjectURL(previewUrl)
      }
    }
  }, [previewUrl])

  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes'
    const k = 1024
    const sizes = ['Bytes', 'KB', 'MB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return `${parseFloat((bytes / Math.pow(k, i)).toFixed(2))} ${sizes[i]}`
  }

  const processFile = (selectedFile) => {
    setError('')
    setDimensions(null)

    if (!selectedFile) return

    const allowedTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/webp']
    if (!allowedTypes.includes(selectedFile.type)) {
      setError('Unsupported file type. Please upload a JPG, PNG, or WEBP image.')
      return
    }

    const maxSize = 10 * 1024 * 1024
    if (selectedFile.size > maxSize) {
      setError('File is too large. Maximum size is 10 MB.')
      return
    }

    if (previewUrl) {
      URL.revokeObjectURL(previewUrl)
    }

    const objectUrl = URL.createObjectURL(selectedFile)
    setPreviewUrl(objectUrl)
    setFile(selectedFile)

    const img = new Image()
    img.onload = () => {
      setDimensions({ width: img.width, height: img.height })
      onImageSelected(selectedFile)
    }
    img.onerror = () => {
      setError('Failed to load image metadata.')
    }
    img.src = objectUrl
  }

  const handleFileChange = (event) => {
    if (event.target.files && event.target.files.length > 0) {
      processFile(event.target.files[0])
    }
  }

  const handleDragOver = (event) => {
    event.preventDefault()
    setIsDragActive(true)
  }

  const handleDragLeave = (event) => {
    event.preventDefault()
    setIsDragActive(false)
  }

  const handleDrop = (event) => {
    event.preventDefault()
    setIsDragActive(false)
    if (event.dataTransfer.files && event.dataTransfer.files.length > 0) {
      processFile(event.dataTransfer.files[0])
    }
  }

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

  if (!file) {
    return (
      <div className="w-full">
        <div
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
          onClick={() => fileInputRef.current?.click()}
          className={`relative flex min-h-[260px] cursor-pointer flex-col items-center justify-center rounded-lg border-2 border-dashed p-8 text-center transition-all ${
            isDragActive
              ? 'border-sky-400 bg-sky-50 shadow-lg shadow-sky-500/10 dark:bg-sky-400/10'
              : 'border-slate-300 bg-slate-50 hover:border-slate-400 hover:bg-white dark:border-white/10 dark:bg-neutral-950/50 dark:hover:border-white/20 dark:hover:bg-neutral-950'
          }`}
        >
          <input
            type="file"
            ref={fileInputRef}
            onChange={handleFileChange}
            accept=".jpg,.jpeg,.png,.webp"
            className="hidden"
          />

          <div className="mb-4 rounded-lg border border-slate-200 bg-white p-4 text-sky-600 shadow-sm dark:border-white/10 dark:bg-white/5 dark:text-sky-300">
            <UploadCloud className="h-8 w-8" />
          </div>

          <h3 className="mb-1 text-sm font-bold text-slate-950 dark:text-white">
            Drag and drop your image here, or <span className="text-sky-600 dark:text-sky-300">browse</span>
          </h3>
          <p className="max-w-[280px] text-xs text-slate-500 dark:text-neutral-400">
            Supports JPG, JPEG, PNG, and WEBP. Maximum file size is 10 MB.
          </p>

          {error && (
            <div className="absolute bottom-4 left-4 right-4 flex items-center gap-2 rounded-lg border border-rose-200 bg-rose-50 p-3 text-left text-xs text-rose-700 dark:border-rose-500/20 dark:bg-rose-950/40 dark:text-rose-300">
              <AlertCircle className="h-4 w-4 shrink-0" />
              <span>{error}</span>
            </div>
          )}
        </div>
      </div>
    )
  }

  return (
    <div className="w-full">
      <div className="rounded-lg border border-slate-200 bg-slate-50 p-5 shadow-sm dark:border-white/10 dark:bg-neutral-950/50">
        <div className="flex flex-col items-start gap-5 md:flex-row">
          <div className="group relative flex h-32 w-full shrink-0 items-center justify-center overflow-hidden rounded-lg border border-slate-200 bg-white dark:border-white/10 dark:bg-neutral-950 md:w-44">
            <img src={previewUrl} alt="Upload preview" className="h-full w-full object-contain" />
            <button
              onClick={handleRemove}
              className="absolute right-2 top-2 cursor-pointer rounded-lg bg-slate-950/80 p-1.5 text-white shadow-md transition-colors hover:bg-rose-600 dark:bg-neutral-950/80"
              title="Remove image"
            >
              <X className="h-4 w-4" />
            </button>
          </div>

          <div className="min-w-0 flex-1 w-full">
            <div className="flex items-start justify-between">
              <div className="truncate pr-4">
                <h4 className="truncate text-sm font-bold text-slate-950 dark:text-white" title={file.name}>
                  {file.name}
                </h4>
                <p className="mt-1 text-xs text-slate-500 dark:text-neutral-400">
                  Image File ({(file.type.split('/')[1] || '').toUpperCase()})
                </p>
              </div>
              <button
                onClick={handleRemove}
                className="hidden cursor-pointer items-center gap-1.5 rounded-lg border border-slate-200 bg-white px-3 py-1.5 text-xs font-semibold text-slate-600 transition-colors hover:bg-slate-100 dark:border-white/10 dark:bg-white/5 dark:text-neutral-300 dark:hover:bg-white/10 md:flex"
              >
                <X className="h-3.5 w-3.5" />
                <span>Remove</span>
              </button>
            </div>

            <div className="mt-4 grid grid-cols-2 gap-4 border-y border-slate-200 py-3 dark:border-white/10">
              <div>
                <span className="block text-[10px] uppercase tracking-wider text-slate-500 dark:text-neutral-500">File Size</span>
                <span className="mt-0.5 block text-xs font-semibold text-slate-700 dark:text-neutral-200">
                  {formatFileSize(file.size)}
                </span>
              </div>
              <div>
                <span className="block text-[10px] uppercase tracking-wider text-slate-500 dark:text-neutral-500">Dimensions</span>
                <span className="mt-0.5 block text-xs font-semibold text-slate-700 dark:text-neutral-200">
                  {dimensions ? `${dimensions.width} x ${dimensions.height} px` : 'Calculating...'}
                </span>
              </div>
            </div>

            {uploadProgress !== null && (
              <div className="mt-4">
                <div className="mb-1.5 flex items-center justify-between text-xs">
                  <div className="flex items-center gap-1.5 text-slate-500 dark:text-neutral-400">
                    {uploadProgress < 100 ? <RefreshCw className="h-3 w-3 animate-spin text-sky-500" /> : null}
                    <span>{uploadProgress < 100 ? 'Uploading to recognition engine...' : 'Upload complete'}</span>
                  </div>
                  <span className="font-mono font-semibold text-slate-700 dark:text-neutral-300">{uploadProgress}%</span>
                </div>
                <div className="h-1.5 w-full overflow-hidden rounded-full border border-slate-200 bg-slate-200 dark:border-white/10 dark:bg-neutral-900">
                  <div
                    className="h-full rounded-full bg-sky-500 transition-all duration-300 ease-out"
                    style={{ width: `${uploadProgress}%` }}
                  />
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
