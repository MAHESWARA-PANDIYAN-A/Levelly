import { useQuery } from '@tanstack/react-query'
import { useNavigate } from 'react-router-dom'
import {
  ShieldCheck,
  ArrowRight,
  Building2,
  Sparkles,
  QrCode,
  HeartHandshake,
} from 'lucide-react'
import { healthAPI, paymentAPI, walletAPI } from '../lib/api'
import { useAuthStore } from '../store/authStore'

const formatINR = (amount: number) =>
  new Intl.NumberFormat('en-IN', { style: 'currency', currency: 'INR', maximumFractionDigits: 0 }).format(amount)

function DistressBanner({ level }: { level: string; signals?: string[] }) {
  if (level === 'LOW') return null

  const config = {
    MODERATE: {
      bg: 'bg-amber-50 border-amber-200/90 text-amber-900',
      icon: '⚠️',
      title: 'Earnings Volatility Detected',
      text: 'Income has dipped recently. Save-at-Pay is automatically tuning savings to protect your cashflow.',
    },
    HIGH: {
      bg: 'bg-orange-50 border-orange-200/90 text-orange-950',
      icon: '📉',
      title: 'Financial Pressure Alert',
      text: 'Recent platform payouts are 37% below your 3-month baseline. Emergency safety reserve is active.',
    },
    SEVERE: {
      bg: 'bg-red-50 border-red-200/90 text-red-950',
      icon: '🔴',
      title: 'Critical Income Shock',
      text: 'Significant income contraction. Levelly Coach and partner liquidity support are available.',
    },
  }[level]

  if (!config) return null

  return (
    <div className={`mx-5 mb-4 p-4 rounded-3xl border ${config.bg} shadow-sm animate-fade-in`}>
      <div className="flex items-start gap-3">
        <span className="text-2xl mt-0.5">{config.icon}</span>
        <div className="flex-1">
          <p className="font-bold text-xs uppercase tracking-wider">{config.title}</p>
          <p className="text-xs mt-1 leading-relaxed">{config.text}</p>
        </div>
      </div>
    </div>
  )
}

export default function HomePage() {
  const navigate = useNavigate()
  const { user } = useAuthStore()
  const firstName = user?.full_name?.split(' ')[0] || 'there'

  const { data: dashboard } = useQuery({
    queryKey: ['dashboard'],
    queryFn: () => healthAPI.dashboard().then(r => r.data),
    refetchInterval: 60000,
  })

  const { data: linkedAccount } = useQuery({
    queryKey: ['linked-account'],
    queryFn: () => paymentAPI.getLinkedAccount().then(r => r.data),
  })

  const { data: safetyWallet } = useQuery({
    queryKey: ['safety-wallet'],
    queryFn: () => walletAPI.getSafety().then(r => r.data),
  })

  const { data: recentPayments } = useQuery({
    queryKey: ['recent-payments'],
    queryFn: () => paymentAPI.recent(5).then(r => r.data),
  })

  const distressLevel = dashboard?.distress?.level || 'LOW'
  const safetyBalance = safetyWallet?.balance ?? dashboard?.safety_wallet?.balance ?? 8200
  const safetyTarget = safetyWallet?.target_amount ?? dashboard?.safety_wallet?.target ?? 10000
  const safetyProgress = Math.min(100, (safetyBalance / (safetyTarget || 1)) * 100)
  const resilienceScore = dashboard?.resilience?.score ?? 58
  const resilienceLabel = dashboard?.resilience?.label ?? 'at_risk'

  return (
    <div className="animate-fade-in pb-10">
      {/* Greeting Header */}
      <div className="px-5 pt-1 pb-3 flex items-center justify-between">
        <div>
          <p className="text-xs text-slate-400 font-medium">
            {new Date().toLocaleDateString('en-IN', { weekday: 'short', month: 'short', day: 'numeric' })}
          </p>
          <h1 className="text-xl font-black text-slate-900 tracking-tight">
            Hi, {firstName} 👋
          </h1>
          <p className="text-[11px] text-slate-500 font-medium">
            {user?.occupation || 'Food Delivery Rider'} • {user?.city || 'Chennai'}
          </p>
        </div>

        <button
          onClick={() => navigate('/coach')}
          className="flex items-center gap-1.5 bg-emerald-50 hover:bg-emerald-100 text-emerald-800 border border-emerald-200/80 px-3 py-1.5 rounded-full text-xs font-bold transition shadow-sm"
        >
          <HeartHandshake className="w-3.5 h-3.5 text-emerald-600" />
          <span>Coach</span>
        </button>
      </div>

      {/* Distress Alert Banner if in High/Severe */}
      <DistressBanner level={distressLevel} signals={dashboard?.distress?.signals} />

      {/* DIRECT BANK & LEVELLY PAY CARD (New Model Core) */}
      <div className="mx-5 mb-4">
        <div className="relative overflow-hidden rounded-3xl bg-gradient-to-br from-slate-900 via-slate-950 to-emerald-950 p-5 text-white shadow-xl shadow-slate-950/20 border border-emerald-800/30">
          <div className="absolute top-0 right-0 -mt-6 -mr-6 w-36 h-36 bg-emerald-500/10 rounded-full blur-xl pointer-events-none" />

          <div className="relative z-10">
            {/* Header / Source */}
            <div className="flex items-center justify-between text-xs text-slate-300 mb-3">
              <div className="flex items-center gap-2">
                <Building2 className="w-4 h-4 text-emerald-400" />
                <span className="font-semibold text-white">
                  {linkedAccount?.bank_name || 'HDFC Bank'} ({linkedAccount?.account_mask || '****4821'})
                </span>
              </div>
              <span className="text-[10px] font-bold bg-emerald-900/60 text-emerald-300 border border-emerald-700/50 px-2 py-0.5 rounded-full">
                Direct UPI Ready
              </span>
            </div>

            {/* UPI Identifier & Architecture Note */}
            <div className="mb-4">
              <p className="text-[11px] text-emerald-300/80 font-mono">
                {linkedAccount?.upi_id || 'arjun@upi'}
              </p>
              <p className="text-xs text-slate-300 mt-1">
                Spend directly from your bank. Zero preloading required.
              </p>
            </div>

            {/* LEVELLY Pay Instant Launch Button */}
            <button
              id="btn-levelly-pay"
              onClick={() => navigate('/pay')}
              className="w-full py-3.5 bg-gradient-to-r from-emerald-500 to-teal-400 hover:from-emerald-400 hover:to-teal-300 text-slate-950 font-black rounded-2xl text-xs transition shadow-lg shadow-emerald-500/20 flex items-center justify-center gap-2 active:scale-[0.98]"
            >
              <QrCode className="w-4 h-4" /> Scan & Pay with LEVELLY Pay
            </button>
          </div>
        </div>
      </div>

      {/* SAFETY WALLET RESILIENCE CARD */}
      <div className="mx-5 mb-4">
        <div
          onClick={() => navigate('/safety')}
          className="cursor-pointer bg-white rounded-3xl p-5 border border-slate-200/80 shadow-sm hover:shadow-md transition active:scale-[0.99]"
        >
          <div className="flex items-center justify-between mb-3">
            <div className="flex items-center gap-2.5">
              <div className="w-8 h-8 rounded-xl bg-emerald-50 text-emerald-700 flex items-center justify-center">
                <ShieldCheck className="w-5 h-5" />
              </div>
              <div>
                <p className="text-xs font-bold text-slate-900">Safety Wallet</p>
                <p className="text-[10px] text-slate-400">Emergency Shock Reserve</p>
              </div>
            </div>
            <ArrowRight className="w-4 h-4 text-slate-400" />
          </div>

          <div className="flex items-baseline justify-between mb-2">
            <div>
              <span className="text-2xl font-black text-slate-900">{formatINR(safetyBalance)}</span>
              <span className="text-xs text-slate-400 font-medium ml-1">/ {formatINR(safetyTarget)}</span>
            </div>
            <span className="text-xs font-extrabold text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded-full">
              {safetyProgress.toFixed(0)}% Buffer
            </span>
          </div>

          {/* Progress Bar */}
          <div className="h-2 bg-slate-100 rounded-full overflow-hidden mb-2">
            <div
              className="h-full bg-gradient-to-r from-emerald-500 to-teal-400 rounded-full transition-all duration-700"
              style={{ width: `${safetyProgress}%` }}
            />
          </div>

          <div className="flex items-center justify-between text-[11px] text-slate-500">
            <span>
              {safetyProgress < 100
                ? `${formatINR(Math.max(0, safetyTarget - safetyBalance))} to target`
                : 'Target achieved! 🎉'}
            </span>
            <span className="text-emerald-700 font-semibold flex items-center gap-1">
              <Sparkles className="w-3 h-3" /> Auto-grows on UPI spends
            </span>
          </div>
        </div>
      </div>

      {/* FINANCIAL RESILIENCE SCORE & HEALTH */}
      <div className="mx-5 mb-4">
        <div
          onClick={() => navigate('/analytics')}
          className="cursor-pointer bg-white rounded-3xl p-5 border border-slate-200/80 shadow-sm flex items-center justify-between"
        >
          <div>
            <p className="text-[11px] text-slate-400 font-bold uppercase tracking-wider">Financial Resilience Score</p>
            <div className="flex items-baseline gap-2 mt-1">
              <span className="text-3xl font-black text-slate-900">{resilienceScore.toFixed(0)}</span>
              <span className="text-xs text-slate-400 font-semibold">/ 100</span>
              <span
                className={`text-[10px] font-bold px-2 py-0.5 rounded-full capitalize ${
                  resilienceLabel === 'stable'
                    ? 'bg-emerald-50 text-emerald-700'
                    : resilienceLabel === 'moderate'
                    ? 'bg-amber-50 text-amber-700'
                    : 'bg-orange-50 text-orange-700'
                }`}
              >
                {resilienceLabel.replace('_', ' ')}
              </span>
            </div>
            <p className="text-[11px] text-slate-500 mt-1">
              Adaptive buffer safeguards against irregular gig income
            </p>
          </div>

          <div className="w-14 h-14 relative flex items-center justify-center">
            <svg viewBox="0 0 40 40" className="w-full h-full -rotate-90">
              <circle cx="20" cy="20" r="16" fill="none" stroke="#F1F5F9" strokeWidth="4" />
              <circle
                cx="20"
                cy="20"
                r="16"
                fill="none"
                stroke="#10B981"
                strokeWidth="4"
                strokeDasharray={`${(resilienceScore / 100) * 100.5} 100.5`}
                strokeLinecap="round"
              />
            </svg>
            <span className="absolute text-[11px] font-black text-slate-800">
              {resilienceScore.toFixed(0)}%
            </span>
          </div>
        </div>
      </div>

      {/* RECENT LEVELLY PAY ACTIVITY */}
      <div className="mx-5">
        <div className="flex items-center justify-between mb-2.5">
          <h2 className="text-xs font-bold text-slate-800 uppercase tracking-wider">
            Recent Payments & Savings
          </h2>
          <button
            onClick={() => navigate('/transactions')}
            className="text-[11px] font-bold text-emerald-700 hover:underline"
          >
            History
          </button>
        </div>

        <div className="bg-white rounded-3xl border border-slate-200/80 shadow-sm divide-y divide-slate-100 overflow-hidden">
          {recentPayments && recentPayments.length > 0 ? (
            recentPayments.map((p: any) => (
              <div key={p.id} className="p-3.5 flex items-center justify-between hover:bg-slate-50/70 transition">
                <div className="flex items-center gap-3">
                  <div className="w-9 h-9 rounded-xl bg-slate-100 flex items-center justify-center text-slate-700 font-bold text-xs">
                    {p.merchant_name?.slice(0, 2).toUpperCase() || 'TX'}
                  </div>
                  <div>
                    <p className="text-xs font-bold text-slate-900">{p.merchant_name}</p>
                    <p className="text-[10px] text-slate-400 capitalize">
                      {p.category} • UPI Direct
                    </p>
                  </div>
                </div>

                <div className="text-right">
                  <p className="text-xs font-black text-slate-900">-{formatINR(p.amount)}</p>
                  {p.save_amount > 0 && (
                    <span className="text-[10px] font-bold text-emerald-700 bg-emerald-50 px-1.5 py-0.5 rounded">
                      +{formatINR(p.save_amount)} saved
                    </span>
                  )}
                </div>
              </div>
            ))
          ) : (
            <div className="p-5 text-center text-xs text-slate-400">
              No recent payments. Make your first payment with LEVELLY Pay!
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
