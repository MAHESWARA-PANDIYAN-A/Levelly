import { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { Shield, ArrowLeft } from 'lucide-react'
import { authAPI } from '../lib/api'
import { useAuthStore } from '../store/authStore'
import toast from 'react-hot-toast'

export default function RegisterPage() {
  const navigate = useNavigate()
  const { setAuth } = useAuthStore()
  const [form, setForm] = useState({
    full_name: '', email: '', password: '', phone: '', occupation: '', city: ''
  })
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!form.full_name || !form.email || !form.password) {
      toast.error('Please fill required fields')
      return
    }
    setLoading(true)
    try {
      const response = await authAPI.register(form)
      const { access_token, user_id, full_name, role } = response.data
      setAuth({ id: user_id, email: form.email, full_name, role }, access_token)
      toast.success('Account created!')
      navigate('/')
    } catch (err: any) {
      const msg = err.response?.data?.detail?.message || 'Registration failed'
      toast.error(msg)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-dvh bg-gradient-to-br from-emerald-950 via-emerald-900 to-emerald-800 flex flex-col px-6 py-12">
      <button onClick={() => navigate('/login')} className="text-emerald-300 flex items-center gap-1 mb-8 w-fit">
        <ArrowLeft className="w-4 h-4" />
        Back
      </button>

      <div className="flex items-center gap-2 mb-8">
        <Shield className="w-7 h-7 text-emerald-300" />
        <span className="text-2xl font-bold text-white">Create Account</span>
      </div>

      <div className="bg-white/10 backdrop-blur-sm rounded-3xl p-6 border border-white/20">
        <form onSubmit={handleSubmit} className="space-y-4">
          {[
            { key: 'full_name', label: 'Full Name *', placeholder: 'Arjun Kumar', type: 'text' },
            { key: 'email', label: 'Email *', placeholder: 'arjun@example.com', type: 'email' },
            { key: 'password', label: 'Password *', placeholder: '••••••••', type: 'password' },
            { key: 'phone', label: 'Phone', placeholder: '+91 98765 43210', type: 'tel' },
            { key: 'occupation', label: 'Occupation', placeholder: 'Food Delivery Rider', type: 'text' },
            { key: 'city', label: 'City', placeholder: 'Chennai', type: 'text' },
          ].map(({ key, label, placeholder, type }) => (
            <div key={key}>
              <label className="text-emerald-200 text-sm font-medium mb-1.5 block">{label}</label>
              <input
                type={type}
                value={form[key as keyof typeof form]}
                onChange={(e) => setForm({ ...form, [key]: e.target.value })}
                placeholder={placeholder}
                className="w-full bg-white/10 border border-white/20 rounded-xl px-4 py-3 text-white placeholder-emerald-300/50 focus:outline-none focus:border-emerald-400 text-base"
              />
            </div>
          ))}

          <button
            type="submit"
            disabled={loading}
            className="w-full bg-emerald-400 hover:bg-emerald-300 text-emerald-950 font-bold py-4 rounded-2xl mt-2 transition-all disabled:opacity-60"
          >
            {loading ? 'Creating...' : 'Create Account'}
          </button>
        </form>
      </div>

      <p className="mt-6 text-emerald-200/60 text-sm text-center">
        Already have an account?{' '}
        <Link to="/login" className="text-emerald-300 font-semibold">Sign in</Link>
      </p>
    </div>
  )
}
