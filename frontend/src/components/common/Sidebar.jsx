import React from 'react'
import { NavLink } from 'react-router-dom'
import { SquarePen, History, Sigma } from 'lucide-react'

export default function Sidebar() {
  return (
    <aside className="w-64 border-r border-neutral-800 bg-neutral-950 flex flex-col h-full shrink-0">
      <div className="h-16 flex items-center gap-3 px-6 border-b border-neutral-800">
        <div className="p-1.5 bg-violet-600 rounded-lg text-white shadow-md shadow-violet-600/30">
          <Sigma className="w-6 h-6" />
        </div>
        <span className="font-bold text-lg tracking-tight text-white bg-clip-text">
          HMER Workspace
        </span>
      </div>

      <nav className="flex-1 p-4 space-y-1.5">
        <NavLink
          to="/dashboard"
          className={({ isActive }) =>
            `flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-medium transition-all ${
              isActive
                ? 'bg-neutral-800/80 text-violet-400 border-l-4 border-violet-500 shadow-sm'
                : 'text-neutral-400 hover:text-white hover:bg-neutral-900'
            }`
          }
        >
          <SquarePen className="w-5 h-5" />
          <span>Canvas Studio</span>
        </NavLink>

        <NavLink
          to="/history"
          className={({ isActive }) =>
            `flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-medium transition-all ${
              isActive
                ? 'bg-neutral-800/80 text-violet-400 border-l-4 border-violet-500 shadow-sm'
                : 'text-neutral-400 hover:text-white hover:bg-neutral-900'
            }`
          }
        >
          <History className="w-5 h-5" />
          <span>Formula Logs</span>
        </NavLink>
      </nav>
    </aside>
  )
}
