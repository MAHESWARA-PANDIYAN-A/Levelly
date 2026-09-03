import { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { Eye, EyeOff, Shield } from 'lucide-react'
import { authAPI } from '../lib/api'
import { useAuthStore } from '../store/authStore'
import toast from 'react-hot-toast'

export default function LoginPage() {
  const navigate = useNavigate()
  const { setAuth } = useAuthStore()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [showPassword, setShowPassword] = useState(false)
  const [loading, setLoading] = useState(false)

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!email || !password) {
      toast.error('Please enter email and password')
      return
    }
    setLoading(true)
    try {
      const response = await authAPI.login(email, password)
      const { access_token, user_id, full_name, role } = response.data
      setAuth({ id: user_id, email, full_name, role }, access_token)
      toast.success(`Welcome back, ${full_name.split(' ')[0]}!`)
      if (role === 'admin') {
        navigate('/admin')
      } else {
        navigate('/')
      }
    } catch (err: any) {
      const msg = err.response?.data?.detail?.message || 'Login failed. Check your credentials.'
      toast.error(msg)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-dvh bg-gradient-to-br from-emerald-950 via-emerald-900 to-emerald-800 flex flex-col">
      {/* Hero */}
      <div className="flex-1 flex flex-col items-center justify-center px-6 py-12">
        <div className="flex flex-col items-center mb-10">
          <div className="w-16 h-16 bg-white/10 rounded-2xl flex items-center justify-center mb-4 backdrop-blur-sm border border-white/20">
            <Shield className="w-8 h-8 text-emerald-300" />
          </div>
          <h1 className="text-3xl font-bold text-white mb-1">LEVELLY</h1>
          <p className="text-emerald-200 text-sm text-center max-w-xs">
            Your income changes.<br />Your financial safety should adapt.
          </p>
        </div>

        <div className="w-full max-w-sm bg-white/10 backdrop-blur-sm rounded-3xl p-6 border border-white/20">
          <h2 className="text-xl font-bold text-white mb-6">Sign in</h2>

          <form onSubmit={handleLogin} className="space-y-4">
            <div>
              <label className="text-emerald-200 text-sm font-medium mb-1.5 block">Email</label>
              <input
                id="email"
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="arjun@levelly.app"
                className="w-full bg-white/10 border border-white/20 rounded-xl px-4 py-3 text-white placeholder-emerald-300/50 focus:outline-none focus:border-emerald-400 focus:ring-2 focus:ring-emerald-400/20 text-base"
                autoComplete="email"
              />
            </div>

            <div>
              <label className="text-emerald-200 text-sm font-medium mb-1.5 block">Password</label>
              <div className="relative">
                <input
                  id="password"
                  type={showPassword ? 'text' : 'password'}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="••••••••"
                  className="w-full bg-white/10 border border-white/20 rounded-xl px-4 py-3 text-white placeholder-emerald-300/50 focus:outline-none focus:border-emerald-400 focus:ring-2 focus:ring-emerald-400/20 text-base pr-12"
                  autoComplete="current-password"
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-emerald-300/70"
                >
                  {showPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
                </button>
              </div>
            </div>

            <button
              type="submit"
              disabled={loading}
              id="btn-login"
              className="w-full bg-emerald-400 hover:bg-emerald-300 text-emerald-950 font-bold py-4 rounded-2xl mt-2 transition-all disabled:opacity-60 disabled:cursor-not-allowed active:scale-98"
            >
              {loading ? 'Signing in...' : 'Sign in'}
            </button>
          </form>

          {/* Demo hint */}
          <div className="mt-4 p-3 bg-white/5 rounded-xl border border-white/10 space-y-2">
            <p className="text-emerald-200/70 text-xs text-center font-medium">Quick Demo Logins (Click to fill):</p>
            <div className="flex gap-2">
              <button
                type="button"
                onClick={() => {
                  setEmail('arjun@levelly.app')
                  setPassword('Levelly@123')
                }}
                className="flex-1 py-1.5 px-2 bg-emerald-500/20 hover:bg-emerald-500/30 text-emerald-200 border border-emerald-400/30 rounded-lg text-xs font-medium transition active:scale-[0.98]"
              >
                👤 User (Arjun)
              </button>
              <button
                type="button"
                onClick={() => {
                  setEmail('admin@levelly.app')
                  setPassword('Admin@Levelly123')
                }}
                className="flex-1 py-1.5 px-2 bg-emerald-300/20 hover:bg-emerald-300/30 text-emerald-100 border border-emerald-300/40 rounded-lg text-xs font-medium transition active:scale-[0.98]"
              >
                🛡️ Admin (Ops)
              </button>
            </div>
          </div>
        </div>

        <p className="mt-6 text-emerald-200/60 text-sm">
          New to LEVELLY?{' '}
          <Link to="/register" className="text-emerald-300 font-semibold">
            Create account
          </Link>
        </p>
      </div>

      <div className="px-6 pb-10 text-center">
        <p className="text-emerald-300/40 text-xs">
          Understand your income. Build your safety. Grow when you're ready.
        </p>
      </div>
    </div>
  )
}
