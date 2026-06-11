import React from 'react'
import { useAuth } from '../../context/AuthContext'
import { LogOut, User as UserIcon } from 'lucide-react'

export default function Header() {
  const { user, logout } = useAuth()

  return (
    <header className="h-16 border-b border-neutral-800 bg-neutral-950 flex items-center justify-between px-6 z-10">
      <div className="flex items-center gap-2">
        <span className="text-xs font-semibold px-2.5 py-1 bg-violet-500/20 text-violet-400 rounded-full border border-violet-500/30">
          v1.0.0
        </span>
      </div>
      <div className="flex items-center gap-4">
        {user ? (
          <div className="flex items-center gap-3">
            <div className="flex items-center gap-2 text-sm text-neutral-300">
              <UserIcon className="w-4 h-4 text-neutral-400" />
              <span>{user.email}</span>
            </div>
            <button
              onClick={logout}
              className="p-2 text-neutral-400 hover:text-red-400 hover:bg-neutral-800/50 rounded-lg transition-colors cursor-pointer"
              title="Logout"
            >
              <LogOut className="w-4 h-4" />
            </button>
          </div>
        ) : (
          <a
            href="/login"
            className="text-sm font-medium text-violet-400 hover:text-violet-300 transition-colors"
          >
            Sign In
          </a>
        )}
      </div>
    </header>
  )
}
