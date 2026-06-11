import React, { createContext, useCallback, useContext, useMemo, useState } from 'react'
import { AlertCircle, CheckCircle2, Info, X } from 'lucide-react'

const ToastContext = createContext(null)

const icons = {
  success: CheckCircle2,
  error: AlertCircle,
  info: Info,
}

export function ToastProvider({ children }) {
  const [toasts, setToasts] = useState([])

  const dismiss = useCallback((id) => {
    setToasts((current) => current.filter((toast) => toast.id !== id))
  }, [])

  const showToast = useCallback((toast) => {
    const id = crypto.randomUUID()
    const nextToast = {
      id,
      type: toast.type || 'info',
      title: toast.title,
      message: toast.message,
    }

    setToasts((current) => [nextToast, ...current].slice(0, 4))
    window.setTimeout(() => dismiss(id), toast.duration || 4200)
  }, [dismiss])

  const value = useMemo(() => ({ showToast, dismiss }), [showToast, dismiss])

  return (
    <ToastContext.Provider value={value}>
      {children}
      <div className="pointer-events-none fixed right-4 top-4 z-50 flex w-[calc(100vw-2rem)] max-w-sm flex-col gap-3">
        {toasts.map((toast) => {
          const Icon = icons[toast.type] || Info
          return (
            <div
              key={toast.id}
              className="pointer-events-auto rounded-lg border border-slate-200 bg-white/95 p-4 text-slate-900 shadow-2xl shadow-slate-900/10 backdrop-blur-xl dark:border-white/10 dark:bg-neutral-900/95 dark:text-neutral-100"
            >
              <div className="flex gap-3">
                <Icon className={`mt-0.5 h-4 w-4 shrink-0 ${
                  toast.type === 'success'
                    ? 'text-emerald-500'
                    : toast.type === 'error'
                      ? 'text-rose-500'
                      : 'text-sky-500'
                }`} />
                <div className="min-w-0 flex-1">
                  <p className="text-sm font-semibold">{toast.title}</p>
                  {toast.message ? (
                    <p className="mt-1 text-sm leading-5 text-slate-500 dark:text-neutral-400">{toast.message}</p>
                  ) : null}
                </div>
                <button
                  type="button"
                  onClick={() => dismiss(toast.id)}
                  className="flex h-7 w-7 items-center justify-center rounded-lg text-slate-400 transition-colors hover:bg-slate-100 hover:text-slate-700 dark:hover:bg-white/10 dark:hover:text-white"
                  title="Dismiss notification"
                >
                  <X className="h-4 w-4" />
                </button>
              </div>
            </div>
          )
        })}
      </div>
    </ToastContext.Provider>
  )
}

export function useToast() {
  const context = useContext(ToastContext)
  if (!context) {
    throw new Error('useToast must be used within ToastProvider')
  }
  return context
}
