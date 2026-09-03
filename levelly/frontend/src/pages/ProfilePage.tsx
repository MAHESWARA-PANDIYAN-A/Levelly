import { useAuthStore } from '../store/authStore'
import { useNavigate } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import {
  LogOut,
  ShieldCheck,
  ChevronRight,
  MessageCircle,
  TrendingUp,
  BarChart2,
  Building2,
  Lock,
  CreditCard,
  CheckCircle2,
} from 'lucide-react'
import { paymentAPI } from '../lib/api'
import toast from 'react-hot-toast'

export default function ProfilePage() {
  const { user, clearAuth } = useAuthStore()
  const navigate = useNavigate()

  const { data: linkedAccount } = useQuery({
    queryKey: ['linked-account'],
    queryFn: () => paymentAPI.getLinkedAccount().then(r => r.data),
  })

  const handleLogout = () => {
    clearAuth()
    toast.success('Signed out')
    navigate('/login')
  }

  const menuItems = [
    { icon: ShieldCheck, label: 'Safety Wallet & Resilience', to: '/safety' },
    { icon: BarChart2, label: 'Income & Expense Analytics', to: '/analytics' },
    { icon: TrendingUp, label: 'Transaction Timeline', to: '/transactions' },
    { icon: MessageCircle, label: 'Levelly Coach', to: '/coach' },
    { icon: CreditCard, label: 'Credit & Safety Buffer', to: '/credit' },
  ]

  return (
    <div className="px-5 pb-12 animate-fade-in">
      {/* Profile Card */}
      <div className="relative overflow-hidden rounded-3xl bg-gradient-to-br from-slate-900 via-slate-950 to-emerald-950 p-6 text-white border border-emerald-800/30 shadow-xl mb-5">
        <div className="flex items-center gap-4">
          <div className="w-14 h-14 bg-emerald-500/20 border border-emerald-500/40 rounded-2xl flex items-center justify-center text-emerald-400 font-black text-xl shadow-inner">
            {user?.full_name ? user.full_name[0].toUpperCase() : 'A'}
          </div>
          <div>
            <p className="text-lg font-black text-white">{user?.full_name}</p>
            <p className="text-xs text-emerald-300/90 font-medium">{user?.email}</p>
            <div className="flex items-center gap-2 mt-1">
              <span className="text-[10px] font-bold bg-white/10 px-2 py-0.5 rounded-full text-slate-200">
                {user?.occupation || 'Delivery Partner'}
              </span>
              <span className="text-[10px] font-bold bg-emerald-500/20 text-emerald-300 px-2 py-0.5 rounded-full">
                {user?.city || 'Chennai'}
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Linked Bank & UPI Account Card */}
      <div className="bg-white rounded-3xl p-5 border border-slate-200/80 shadow-sm mb-5">
        <div className="flex items-center justify-between mb-3">
          <p className="text-xs font-bold text-slate-800 uppercase tracking-wider flex items-center gap-1.5">
            <Building2 className="w-4 h-4 text-emerald-700" /> Linked Payment Account
          </p>
          <span className="flex items-center gap-1 text-[10px] font-bold text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded-full border border-emerald-200">
            <CheckCircle2 className="w-3 h-3" /> Connected
          </span>
        </div>

        <div className="bg-slate-50 rounded-2xl p-3.5 border border-slate-100 flex items-center justify-between mb-3">
          <div>
            <p className="text-xs font-bold text-slate-900">
              {linkedAccount?.bank_name || 'HDFC Bank'} ({linkedAccount?.account_mask || '****4821'})
            </p>
            <p className="text-[11px] font-mono text-emerald-700 font-semibold mt-0.5">
              {linkedAccount?.upi_id || 'arjun@upi'}
            </p>
            <p className="text-[10px] text-slate-400">Primary direct payment & savings source</p>
          </div>
        </div>

        <div className="flex items-center gap-2 text-[11px] text-slate-500">
          <Lock className="w-3.5 h-3.5 text-slate-400 shrink-0" />
          <span>LEVELLY never stores your UPI PIN, passwords, or OTPs.</span>
        </div>
      </div>

      {/* Navigation Menu */}
      <div className="bg-white rounded-3xl border border-slate-200/80 shadow-sm mb-5 divide-y divide-slate-100 overflow-hidden">
        {menuItems.map(({ icon: Icon, label, to }) => (
          <button
            key={to}
            onClick={() => navigate(to)}
            className="flex items-center justify-between w-full p-4 hover:bg-slate-50/80 transition"
          >
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 bg-slate-50 text-slate-700 rounded-xl flex items-center justify-center">
                <Icon className="w-4 h-4 text-slate-700" />
              </div>
              <span className="text-xs font-bold text-slate-800">{label}</span>
            </div>
            <ChevronRight className="w-4 h-4 text-slate-400" />
          </button>
        ))}
      </div>

      {/* Regulatory & Safety Disclosure */}
      <div className="bg-slate-50 rounded-2xl p-4 border border-slate-200/80 mb-5">
        <p className="text-[10px] font-bold text-slate-600 uppercase tracking-wider mb-1.5">
          FINANCIAL RESILIENCE GUARANTEE
        </p>
        <p className="text-[11px] text-slate-500 leading-relaxed">
          LEVELLY is designed to cushion irregular income flows for gig workers. All Save-at-Pay micro-savings are held securely in your designated Safety Wallet reserve.
        </p>
      </div>

      {/* Logout */}
      <button
        id="btn-logout"
        onClick={handleLogout}
        className="w-full flex items-center justify-center gap-2 py-3.5 text-red-600 font-bold bg-red-50 hover:bg-red-100 rounded-2xl text-xs transition active:scale-[0.98]"
      >
        <LogOut className="w-4 h-4" />
        Sign Out
      </button>
    </div>
  )
}
