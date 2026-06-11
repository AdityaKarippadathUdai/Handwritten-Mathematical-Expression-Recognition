import React from 'react'
import { AlertTriangle, RefreshCw } from 'lucide-react'

export default class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props)
    this.state = { hasError: false }
  }

  static getDerivedStateFromError() {
    return { hasError: true }
  }

  componentDidCatch(error, info) {
    console.error('UI boundary caught an error:', error, info)
  }

  handleReset = () => {
    this.setState({ hasError: false })
  }

  render() {
    if (!this.state.hasError) {
      return this.props.children
    }

    return (
      <div className="flex min-h-[520px] items-center justify-center p-6">
        <div className="w-full max-w-lg rounded-lg border border-rose-200 bg-white p-6 text-center shadow-2xl shadow-slate-900/10 dark:border-rose-500/20 dark:bg-neutral-900">
          <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-lg border border-rose-200 bg-rose-50 text-rose-500 dark:border-rose-500/30 dark:bg-rose-500/10 dark:text-rose-300">
            <AlertTriangle className="h-6 w-6" />
          </div>
          <h1 className="mt-5 text-xl font-semibold text-slate-950 dark:text-white">Something went wrong</h1>
          <p className="mt-2 text-sm leading-6 text-slate-600 dark:text-neutral-400">
            The interface hit an unexpected state. Reset this view and try the action again.
          </p>
          <button
            type="button"
            onClick={this.handleReset}
            className="mt-5 inline-flex items-center gap-2 rounded-lg bg-slate-950 px-4 py-2 text-sm font-semibold text-white transition-colors hover:bg-slate-800 dark:bg-white dark:text-neutral-950 dark:hover:bg-neutral-200"
          >
            <RefreshCw className="h-4 w-4" />
            <span>Reset view</span>
          </button>
        </div>
      </div>
    )
  }
}
