import React from 'react'
import { NavLink } from 'react-router-dom'
import { History, Info, Sigma, UploadCloud, X, Zap } from 'lucide-react'

const navItems = [
  { to: '/predict', label: 'Home', icon: UploadCloud },
  { to: '/history', label: 'History', icon: History },
  { to: '/about', label: 'About', icon: Info },
]

export default function Sidebar({ isOpen = false, onClose }) {
  return (
    <>
      <div
        className={`fixed inset-0 z-30 bg-slate-950/40 backdrop-blur-sm transition-opacity lg:hidden ${
          isOpen ? 'opacity-100' : 'pointer-events-none opacity-0'
        }`}
        onClick={onClose}
      />
      <aside className={`fixed inset-y-0 left-0 z-40 flex h-full w-72 shrink-0 flex-col border-r border-slate-200 bg-white transition-transform dark:border-white/10 dark:bg-neutral-950 lg:static lg:z-auto lg:w-64 lg:translate-x-0 ${
        isOpen ? 'translate-x-0' : '-translate-x-full'
      }`}>
        <div className="flex h-16 items-center justify-between border-b border-slate-200 px-5 dark:border-white/10">
          <div className="flex min-w-0 items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-slate-950 text-white shadow-lg shadow-slate-950/20 dark:bg-white dark:text-neutral-950 dark:shadow-white/10">
              <Sigma className="h-6 w-6" />
            </div>
            <div className="min-w-0">
              <span className="block truncate text-base font-bold tracking-tight text-slate-950 dark:text-white">
                Formula AI
              </span>
              <span className="block text-xs font-medium text-slate-500 dark:text-neutral-500">Recognition suite</span>
            </div>
          </div>
          <button
            type="button"
            onClick={onClose}
            className="flex h-9 w-9 items-center justify-center rounded-lg text-slate-500 transition-colors hover:bg-slate-100 dark:text-neutral-400 dark:hover:bg-white/10 lg:hidden"
            title="Close navigation"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        <nav className="flex-1 space-y-1.5 p-4">
          {navItems.map((item) => {
            const Icon = item.icon
            return (
              <NavLink
                key={item.to}
                to={item.to}
                onClick={onClose}
                className={({ isActive }) =>
                  `flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-semibold transition-all ${
                    isActive
                      ? 'bg-slate-950 text-white shadow-sm dark:bg-white dark:text-neutral-950'
                      : 'text-slate-600 hover:bg-slate-100 hover:text-slate-950 dark:text-neutral-400 dark:hover:bg-white/10 dark:hover:text-white'
                  }`
                }
              >
                <Icon className="h-5 w-5" />
                <span>{item.label}</span>
              </NavLink>
            )
          })}
        </nav>

        <div className="m-4 rounded-lg border border-slate-200 bg-slate-50 p-4 dark:border-white/10 dark:bg-white/5">
          <div className="flex items-center gap-2 text-sm font-semibold text-slate-950 dark:text-white">
            <Zap className="h-4 w-4 text-amber-500" />
            <span>AI-ready workflow</span>
          </div>
          <p className="mt-2 text-xs leading-5 text-slate-500 dark:text-neutral-400">
            Upload, recognize, render, and revisit equations from one focused workspace.
          </p>
        </div>
      </aside>
    </>
  )
}
