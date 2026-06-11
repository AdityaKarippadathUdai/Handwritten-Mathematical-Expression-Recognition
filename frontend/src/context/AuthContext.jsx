import React, { createContext, useContext, useState, useEffect } from 'react'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)
  const [token, setToken] = useState(() => localStorage.getItem('token') || null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (token) {
      localStorage.setItem('token', token)
      // Mock parsing JWT payload/user email
      setUser({ email: 'user@example.com' })
    } else {
      localStorage.removeItem('token')
      setUser(null)
    }
    setLoading(false)
  }, [token])

  const login = async (email, password) => {
    // In a real application, make a POST request to /api/v1/auth/login
    setToken('mock-jwt-token')
    setUser({ email })
    return true
  }

  const logout = () => {
    setToken(null)
  }

  const value = {
    user,
    token,
    loading,
    login,
    logout
  }

  return (
    <AuthContext.Provider value={value}>
      {!loading && children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}
