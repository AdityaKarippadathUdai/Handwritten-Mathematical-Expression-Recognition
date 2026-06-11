import React from 'react'
import { Link } from 'react-router-dom'
import { useAuth } from '../../context/AuthContext'
import { Bell, LogOut, Menu, Moon, Search, Sun, User as UserIcon } from 'lucide-react'

export default function Header({ theme, onToggleTheme, onOpenSidebar }) {
  const { user, logout } = useAuth()

  return (
    <header className="z-20 flex h-16 items-center justify-between border-b border-white/10 bg-slate-950/90 px-4 backdrop-blur-xl dark:bg-[#020617]/90 sm:px-6">
      <div className="flex min-w-0 items-center gap-3">
        <button
          type="button"
          onClick={onOpenSidebar}
          className="flex h-10 w-10 items-center justify-center rounded-xl border border-white/10 bg-slate-900 text-slate-200 transition-colors hover:border-slate-300 hover:bg-slate-800 lg:hidden"
          title="Open navigation"
        >
          <Menu className="h-5 w-5" />
        </button>

        <Link
          to="/"
          className="hidden items-center gap-2 rounded-2xl border border-slate-800 bg-white/5 px-3 py-2 text-sm font-semibold tracking-tight text-white transition hover:border-slate-500 lg:flex"
        >
          <span className="inline-flex h-9 w-9 items-center justify-center rounded-2xl bg-slate-800 text-sky-300">AI</span>
          <span>Formula AI</span>
        </Link>

        <div className="hidden h-10 min-w-[260px] items-center gap-2 rounded-2xl border border-slate-800 bg-slate-900/70 px-3 text-sm text-slate-400 md:flex">
          <Search className="h-4 w-4" />
          <span className="truncate">Search history, predictions, LaTeX</span>
        </div>
      </div>

      <div className="flex items-center gap-2 sm:gap-3">
        <span className="hidden rounded-full border border-sky-300/30 bg-sky-300/10 px-2.5 py-1 text-xs font-semibold text-sky-200 sm:inline-flex">
          v1.0.0
        </span>
        <button
          type="button"
          className="flex h-10 w-10 items-center justify-center rounded-xl border border-white/10 bg-slate-900 text-slate-200 transition hover:border-slate-300"
          title="Notifications"
        >
          <Bell className="h-4 w-4" />
        </button>
        <button
          type="button"
          onClick={onToggleTheme}
          className="flex h-10 w-10 items-center justify-center rounded-xl border border-white/10 bg-slate-900 text-slate-200 transition hover:border-slate-300"
          title="Toggle dark mode"
        >
          {theme === 'dark' ? <Sun className="h-4 w-4" /> : <Moon className="h-4 w-4" />}
        </button>

        {user ? (
          <div className="flex items-center gap-3">
            <div className="hidden items-center gap-2 rounded-2xl border border-white/10 bg-slate-900/75 px-3 py-2 text-sm text-slate-200 sm:inline-flex">
              <UserIcon className="h-4 w-4 text-slate-400" />
              <span className="max-w-40 truncate">{user.email}</span>
            </div>
            <button
              onClick={logout}
              className="flex h-10 w-10 items-center justify-center rounded-xl border border-white/10 bg-slate-900 text-slate-200 transition hover:border-red-300 hover:text-red-300"
              title="Logout"
            >
              <LogOut className="h-4 w-4" />
            </button>
          </div>
        ) : (
          <Link
            to="/login"
            className="rounded-2xl bg-slate-100 px-3 py-2 text-sm font-semibold text-slate-950 transition hover:bg-slate-200"
          >
            Sign in
          </Link>
        )}
      </div>
    </header>
  )
}
