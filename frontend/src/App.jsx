import React, { useEffect, useState } from 'react'
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { AuthProvider } from './context/AuthContext.jsx'
import { ToastProvider } from './context/ToastContext.jsx'
import Home from './pages/Home.jsx'
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
          <div className="flex min-h-screen w-screen overflow-hidden bg-slate-950 text-white transition-colors dark:bg-[#04080f] dark:text-neutral-100">
            <Sidebar isOpen={sidebarOpen} onClose={() => setSidebarOpen(false)} />

            <div className="flex min-w-0 flex-1 flex-col overflow-hidden">
              <Header
                theme={theme}
                onToggleTheme={toggleTheme}
                onOpenSidebar={() => setSidebarOpen(true)}
              />
              <main className="flex-1 overflow-y-auto bg-[radial-gradient(circle_at_top,_rgba(56,189,248,0.16),_transparent_35%),linear-gradient(180deg,_rgba(15,23,42,0.95),_rgba(15,23,42,0.99))] px-4 py-5 transition-colors sm:px-6 sm:py-6">
                <ErrorBoundary>
                  <Routes>
                    <Route path="/" element={<Home />} />
                    <Route path="/history" element={<History />} />
                    <Route path="/about" element={<About />} />
                    <Route path="/login" element={<Login />} />
                    <Route path="/register" element={<Register />} />
                    <Route path="*" element={<Navigate to="/" replace />} />
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

