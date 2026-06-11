import React, { useEffect, useState } from 'react'
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { AuthProvider } from './context/AuthContext.jsx'
import { ToastProvider } from './context/ToastContext.jsx'
import Home from './pages/Home.jsx'
import Dashboard from './pages/Dashboard.jsx'
import History from './pages/History.jsx'
import About from './pages/About.jsx'
import Login from './pages/Login.jsx'
import Register from './pages/Register.jsx'
import Header from './components/common/Header.jsx'
import Sidebar from './components/common/Sidebar.jsx'
import ErrorBoundary from './components/common/ErrorBoundary.jsx'

function App() {
  const [theme, setTheme] = useState(() => localStorage.getItem('theme') || 'dark')
  const [sidebarOpen, setSidebarOpen] = useState(false)

  useEffect(() => {
    const root = document.documentElement
    root.classList.toggle('dark', theme === 'dark')
    localStorage.setItem('theme', theme)
  }, [theme])

  const toggleTheme = () => {
    setTheme((current) => (current === 'dark' ? 'light' : 'dark'))
  }

  return (
    <BrowserRouter>
      <AuthProvider>
        <ToastProvider>
          <div className="flex h-screen w-screen overflow-hidden bg-slate-50 text-slate-950 transition-colors dark:bg-neutral-950 dark:text-neutral-100">
            <Sidebar isOpen={sidebarOpen} onClose={() => setSidebarOpen(false)} />

            <div className="flex min-w-0 flex-1 flex-col overflow-hidden">
              <Header
                theme={theme}
                onToggleTheme={toggleTheme}
                onOpenSidebar={() => setSidebarOpen(true)}
              />
              <main className="flex-1 overflow-y-auto bg-slate-100 p-4 transition-colors dark:bg-neutral-950 sm:p-6">
                <ErrorBoundary>
                  <Routes>
                    <Route path="/" element={<Navigate to="/predict" replace />} />
                    <Route path="/predict" element={<Home />} />
                    <Route path="/dashboard" element={<Dashboard />} />
                    <Route path="/history" element={<History />} />
                    <Route path="/about" element={<About />} />
                    <Route path="/login" element={<Login />} />
                    <Route path="/register" element={<Register />} />
                    <Route path="*" element={<Navigate to="/predict" replace />} />
                  </Routes>
                </ErrorBoundary>
              </main>
            </div>
          </div>
        </ToastProvider>
      </AuthProvider>
    </BrowserRouter>
  )
}

export default App

