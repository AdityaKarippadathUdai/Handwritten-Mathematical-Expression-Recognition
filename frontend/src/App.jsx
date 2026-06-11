import React from 'react'
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { AuthProvider } from './context/AuthContext.jsx'
import Home from './pages/Home.jsx'
import Dashboard from './pages/Dashboard.jsx'
import History from './pages/History.jsx'
import Login from './pages/Login.jsx'
import Register from './pages/Register.jsx'
import Header from './components/common/Header.jsx'
import Sidebar from './components/common/Sidebar.jsx'

function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <div className="flex h-screen w-screen bg-neutral-950 text-neutral-100 font-sans overflow-hidden">
          {/* Side navigation */}
          <Sidebar />

          {/* Main workspace area */}
          <div className="flex-1 flex flex-col overflow-hidden">
            <Header />
            <main className="flex-1 overflow-y-auto p-6 bg-neutral-900">
              <Routes>
                <Route path="/" element={<Navigate to="/predict" replace />} />
                <Route path="/predict" element={<Home />} />
                <Route path="/dashboard" element={<Dashboard />} />
                <Route path="/history" element={<History />} />
                <Route path="/login" element={<Login />} />
                <Route path="/register" element={<Register />} />
                <Route path="*" element={<Navigate to="/predict" replace />} />
              </Routes>
            </main>
          </div>
        </div>
      </AuthProvider>
    </BrowserRouter>
  )
}

export default App

