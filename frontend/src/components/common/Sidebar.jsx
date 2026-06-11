import React from 'react'
import { NavLink } from 'react-router-dom'
import { History, Info, Sigma, UploadCloud, X, Zap } from 'lucide-react'

const navItems = [
  { to: '/', label: 'Home', icon: UploadCloud },
  { to: '/history', label: 'History', icon: History },
  { to: '/about', label: 'About', icon: Info },
]

export default function Sidebar({ isOpen = false, onClose }) {
  return (
    <>
      <div
        className={`fixed inset-0 z-30 bg-slate-950/60 backdrop-blur-sm transition-opacity lg:hidden ${
          isOpen ? 'opacity-100' : 'pointer-events-none opacity-0'
        }`}
        onClick={onClose}
      />
      <aside className={`fixed inset-y-0 left-0 z-40 flex h-full w-72 shrink-0 flex-col border-r border-white/10 bg-slate-950 text-white transition-transform shadow-2xl shadow-slate-950/40 lg:static lg:z-auto lg:w-64 lg:translate-x-0 ${
        isOpen ? 'translate-x-0' : '-translate-x-full'
      }`}>
        <div className="flex h-16 items-center justify-between border-b border-white/10 px-5">
          <div className="flex min-w-0 items-center gap-3">
            <div className="flex h-11 w-11 items-center justify-center rounded-3xl bg-sky-400 text-slate-950 shadow-lg shadow-sky-500/20">
              <Sigma className="h-6 w-6" />
            </div>
            <div className="min-w-0">
              <span className="block truncate text-base font-semibold tracking-tight text-white">
                Formula AI
              </span>
              <span className="block text-xs text-slate-400">Math recognition suite</span>
            </div>
          </div>
          <button
            type="button"
            onClick={onClose}
            className="flex h-9 w-9 items-center justify-center rounded-xl bg-white/5 text-slate-200 transition hover:bg-white/10 lg:hidden"
            title="Close navigation"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        <nav className="flex-1 px-4 py-5">
          {navItems.map((item) => {
            const Icon = item.icon
            return (
              <NavLink
                key={item.to}
                to={item.to}
                onClick={onClose}
                className={({ isActive }) =>
                  `flex items-center gap-3 rounded-3xl px-4 py-3 text-sm font-semibold transition ${
                    isActive
                      ? 'bg-white/10 text-white shadow-sm'
                      : 'text-slate-300 hover:bg-white/5 hover:text-white'
                  }`
                }
              >
                <Icon className="h-5 w-5" />
                <span>{item.label}</span>
              </NavLink>
            )
          })}
        </nav>

        <div className="mx-4 mb-4 rounded-3xl border border-white/10 bg-white/5 p-4 text-sm text-slate-300">
          <div className="flex items-center gap-2 font-semibold text-sky-200">
            <Zap className="h-4 w-4" />
            AI-ready workflow
          </div>
          <p className="mt-2 text-xs leading-5 text-slate-400">
            Upload, recognize, render, and revisit equations from one focused workspace.
          </p>
        </div>
      </aside>
    </>
  )
}
