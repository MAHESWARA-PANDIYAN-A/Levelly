import { useAuthStore } from '../store/authStore'
import { useNavigate } from 'react-router-dom'
import { LogOut, Shield, ChevronRight, User, MessageCircle, TrendingUp, BarChart2 } from 'lucide-react'
import toast from 'react-hot-toast'

export default function ProfilePage() {
  const { user, clearAuth } = useAuthStore()
  const navigate = useNavigate()

  const handleLogout = () => {
    clearAuth()
    toast.success('Logged out')
    navigate('/login')
  }

  const menuItems = [
    { icon: BarChart2, label: 'Analytics', to: '/analytics' },
    { icon: TrendingUp, label: 'Transactions', to: '/transactions' },
    { icon: Shield, label: 'Wallets & Safety', to: '/wallets' },
    { icon: MessageCircle, label: 'Levelly Coach', to: '/coach' },
  ]

  return (
    <div className="px-5 pb-8 animate-fade-in">
      {/* User card */}
      <div className="card-premium mb-5">
        <div className="flex items-center gap-4">
          <div className="w-14 h-14 bg-white/20 rounded-2xl flex items-center justify-center">
            <User className="w-7 h-7 text-white" />
          </div>
          <div>
            <p className="text-xl font-bold text-white">{user?.full_name}</p>
            <p className="text-emerald-200 text-sm">{user?.email}</p>
            {user?.occupation && (
              <p className="text-emerald-300 text-xs mt-0.5">{user.occupation}</p>
            )}
          </div>
        </div>
      </div>

      {/* Menu */}
      <div className="card mb-4 divide-y divide-gray-50">
        {menuItems.map(({ icon: Icon, label, to }) => (
          <button
            key={to}
            onClick={() => navigate(to)}
            className="flex items-center justify-between w-full py-3 first:pt-0 last:pb-0"
          >
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 bg-gray-50 rounded-xl flex items-center justify-center">
                <Icon className="w-4 h-4 text-gray-600" />
              </div>
              <span className="text-sm font-medium text-gray-700">{label}</span>
            </div>
            <ChevronRight className="w-4 h-4 text-gray-400" />
          </button>
        ))}
      </div>

      {/* App info */}
      <div className="card mb-4 bg-gray-50">
        <p className="text-xs font-semibold text-gray-500 mb-2">ABOUT LEVELLY</p>
        <p className="text-xs text-gray-500 leading-relaxed">
          LEVELLY is a financial resilience platform for gig and informal workers. 
          We help you understand your income, build your safety buffer, grow when ready, and borrow responsibly.
        </p>
        <div className="mt-3 pt-3 border-t border-gray-200">
          <p className="text-xs text-gray-400">
            Financial Resilience Score is LEVELLY's internal measure — not a government or credit bureau score.
          </p>
        </div>
      </div>

      <button
        id="btn-logout"
        onClick={handleLogout}
        className="w-full flex items-center justify-center gap-2 py-4 text-red-600 font-semibold bg-red-50 rounded-2xl hover:bg-red-100 transition-all"
      >
        <LogOut className="w-4 h-4" />
        Sign Out
      </button>
    </div>
  )
}
