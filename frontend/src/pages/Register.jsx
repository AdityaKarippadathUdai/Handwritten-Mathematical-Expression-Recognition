import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { UserPlus } from 'lucide-react'

export default function Register() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const navigate = useNavigate()

  const handleSubmit = (e) => {
    e.preventDefault()
    // Simulated registration
    navigate('/login')
  }

  return (
    <div className="max-w-md mx-auto mt-12 bg-neutral-900 border border-neutral-800 p-8 rounded-2xl shadow-xl">
      <h2 className="text-xl font-bold text-white flex items-center gap-2">
        <UserPlus className="w-5 h-5 text-violet-400" />
        <span>Create Account</span>
      </h2>
      <form onSubmit={handleSubmit} className="space-y-4 mt-6">
        <div>
          <label className="text-xs text-neutral-400 block mb-1.5">Email Address</label>
          <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            className="w-full bg-neutral-950 border border-neutral-800 rounded-xl px-4 py-2.5 text-sm text-white focus:outline-none focus:border-violet-500"
            placeholder="name@example.com"
            required
          />
        </div>
        <div>
          <label className="text-xs text-neutral-400 block mb-1.5">Password</label>
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="w-full bg-neutral-950 border border-neutral-800 rounded-xl px-4 py-2.5 text-sm text-white focus:outline-none focus:border-violet-500"
            placeholder="••••••••"
            required
          />
        </div>
        <button
          type="submit"
          className="w-full bg-violet-600 hover:bg-violet-500 py-3 rounded-xl text-sm font-semibold transition-colors cursor-pointer"
        >
          Sign Up
        </button>
      </form>
    </div>
  )
}
