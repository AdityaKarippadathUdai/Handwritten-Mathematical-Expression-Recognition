import React from 'react'
import { useAuth } from '../../context/AuthContext'
import { Bell, LogOut, Menu, Moon, Search, Sun, User as UserIcon } from 'lucide-react'

export default function Header({ theme, onToggleTheme, onOpenSidebar }) {
  const { user, logout } = useAuth()

  return (
    <header className="z-20 flex h-16 items-center justify-between border-b border-slate-200 bg-white/85 px-4 backdrop-blur-xl dark:border-white/10 dark:bg-neutral-950/80 sm:px-6">
      <div className="flex min-w-0 items-center gap-3">
        <button
          type="button"
          onClick={onOpenSidebar}
          className="flex h-10 w-10 items-center justify-center rounded-lg border border-slate-200 bg-white text-slate-600 transition-colors hover:bg-slate-50 dark:border-white/10 dark:bg-white/5 dark:text-neutral-300 dark:hover:bg-white/10 lg:hidden"
          title="Open navigation"
        >
          <Menu className="h-5 w-5" />
        </button>
        <div className="hidden h-10 w-full max-w-sm items-center gap-2 rounded-lg border border-slate-200 bg-slate-50 px-3 text-sm text-slate-500 dark:border-white/10 dark:bg-white/5 dark:text-neutral-400 md:flex">
          <Search className="h-4 w-4" />
          <span className="truncate">Search predictions, LaTeX, history</span>
        </div>
      </div>

      <div className="flex items-center gap-2 sm:gap-3">
        <span className="hidden rounded-full border border-sky-200 bg-sky-50 px-2.5 py-1 text-xs font-semibold text-sky-700 dark:border-sky-400/20 dark:bg-sky-400/10 dark:text-sky-300 sm:inline-flex">
          v1.0.0
        </span>
        <button
          type="button"
          className="flex h-10 w-10 items-center justify-center rounded-lg border border-slate-200 bg-white text-slate-600 transition-colors hover:bg-slate-50 dark:border-white/10 dark:bg-white/5 dark:text-neutral-300 dark:hover:bg-white/10"
          title="Notifications"
        >
          <Bell className="h-4 w-4" />
        </button>
        <button
          type="button"
          onClick={onToggleTheme}
          className="flex h-10 w-10 items-center justify-center rounded-lg border border-slate-200 bg-white text-slate-600 transition-colors hover:bg-slate-50 dark:border-white/10 dark:bg-white/5 dark:text-neutral-300 dark:hover:bg-white/10"
          title="Toggle dark mode"
        >
          {theme === 'dark' ? <Sun className="h-4 w-4" /> : <Moon className="h-4 w-4" />}
        </button>

        {user ? (
          <div className="flex items-center gap-3">
            <div className="hidden items-center gap-2 rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm text-slate-600 dark:border-white/10 dark:bg-white/5 dark:text-neutral-300 sm:flex">
              <UserIcon className="h-4 w-4 text-slate-400 dark:text-neutral-400" />
              <span className="max-w-40 truncate">{user.email}</span>
            </div>
            <button
              onClick={logout}
              className="flex h-10 w-10 items-center justify-center rounded-lg border border-slate-200 bg-white text-slate-500 transition-colors hover:border-rose-200 hover:text-rose-500 dark:border-white/10 dark:bg-white/5 dark:text-neutral-300 dark:hover:border-rose-400/30 dark:hover:text-rose-300"
              title="Logout"
            >
              <LogOut className="h-4 w-4" />
            </button>
          </div>
        ) : (
          <a
            href="/login"
            className="rounded-lg bg-slate-950 px-3 py-2 text-sm font-semibold text-white transition-colors hover:bg-slate-800 dark:bg-white dark:text-neutral-950 dark:hover:bg-neutral-200"
          >
            Sign In
          </a>
        )}
      </div>
    </header>
  )
}
