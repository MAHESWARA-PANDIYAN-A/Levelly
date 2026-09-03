import { useQuery } from '@tanstack/react-query'
import { useNavigate } from 'react-router-dom'
import { Shield, TrendingDown, TrendingUp, ArrowRight } from 'lucide-react'
import { healthAPI, nudgesAPI } from '../lib/api'
import { useAuthStore } from '../store/authStore'

const formatINR = (amount: number) =>
  new Intl.NumberFormat('en-IN', { style: 'currency', currency: 'INR', maximumFractionDigits: 0 }).format(amount)

function SkeletonCard({ height = 'h-32' }: { height?: string }) {
  return <div className={`skeleton ${height} rounded-2xl w-full`} />
}

function DistressBanner({ level }: { level: string; signals?: string[] }) {
  if (level === 'LOW') return null

  const config = {
    MODERATE: {
      bg: 'bg-amber-50 border-amber-200',
      icon: '⚠️',
      title: 'Earnings tracking lower',
      text: 'Your income has dipped recently. Levelly Coach can help you navigate.',
    },
    HIGH: {
      bg: 'bg-orange-50 border-orange-200',
      icon: '📉',
      title: 'Financial pressure detected',
      text: "Your recent earnings are significantly below your usual range. Let's protect your stability.",
    },
    SEVERE: {
      bg: 'bg-red-50 border-red-200',
      icon: '🔴',
      title: 'Immediate attention needed',
      text: 'Your financial situation needs attention. Levelly Coach is ready to help.',
    },
  }[level]

  if (!config) return null

  return (
    <div className={`mx-5 mt-3 p-4 rounded-2xl border ${config.bg} animate-fade-in`}>
      <div className="flex items-start gap-3">
        <span className="text-xl">{config.icon}</span>
        <div className="flex-1">
          <p className="font-semibold text-gray-800 text-sm">{config.title}</p>
          <p className="text-gray-600 text-xs mt-0.5">{config.text}</p>
        </div>
      </div>
    </div>
  )
}

export default function HomePage() {
  const navigate = useNavigate()
  const { user } = useAuthStore()
  const firstName = user?.full_name?.split(' ')[0] || 'there'

  const { data: dashboard, isLoading } = useQuery({
    queryKey: ['dashboard'],
    queryFn: () => healthAPI.dashboard().then(r => r.data),
    refetchInterval: 60000,
  })

  const { data: nudgesData } = useQuery({
    queryKey: ['nudges'],
    queryFn: () => nudgesAPI.get().then(r => r.data),
    refetchInterval: 60000,
  })

  const nudges = nudgesData?.nudges || []
  const distressLevel = dashboard?.distress?.level || 'LOW'

  return (
    <div className="animate-fade-in pb-8">
      {/* Admin quick switch banner */}
      {user?.role === 'admin' && (
        <div className="mx-5 my-2 p-3 bg-slate-900 text-white rounded-xl flex items-center justify-between text-xs shadow-sm">
          <div className="flex items-center gap-2">
            <Shield className="w-4 h-4 text-emerald-400 flex-shrink-0" />
            <span>Logged in as <strong>Administrator</strong></span>
          </div>
          <button
            onClick={() => navigate('/admin')}
            className="bg-emerald-600 hover:bg-emerald-500 text-white px-2.5 py-1 rounded-lg text-xs font-bold transition flex items-center gap-1"
          >
            Admin Portal <ArrowRight className="w-3 h-3" />
          </button>
        </div>
      )}

      {/* Greeting */}
      <div className="px-5 pb-2">
        <p className="text-sm text-gray-500 mt-1">
          {new Date().toLocaleDateString('en-IN', { weekday: 'long', month: 'long', day: 'numeric' })}
        </p>
        <h1 className="text-2xl font-bold text-levelly-text">
          Hey, {firstName} 👋
        </h1>
        <p className="text-sm text-gray-500 mt-0.5">
          {user?.occupation || 'Your financial dashboard'}
        </p>
      </div>

      {/* Distress banner */}
      {dashboard && <DistressBanner level={distressLevel} signals={dashboard.distress?.signals || []} />}

      {/* Daily Wallet Card */}
      <div className="mx-5 mt-4">
        {isLoading ? (
          <SkeletonCard height="h-36" />
        ) : (
          <div className="card-premium animate-slide-up">
            <div className="flex items-center justify-between mb-1">
              <span className="text-emerald-200 text-sm font-medium">Daily Wallet</span>
              <div className="flex items-center gap-1 bg-white/10 rounded-full px-2 py-0.5">
                <div className="w-1.5 h-1.5 bg-emerald-300 rounded-full animate-pulse" />
                <span className="text-emerald-200 text-xs">Live</span>
              </div>
            </div>
            <div className="text-4xl font-bold text-white mt-1 text-rupee">
              {formatINR(dashboard?.daily_wallet?.balance || 0)}
            </div>
            <p className="text-emerald-200/60 text-xs mt-1">Available to spend</p>

            <div className="flex gap-2 mt-4">
              <button
                id="btn-make-payment"
                onClick={() => navigate('/pay')}
                className="flex-1 bg-white/20 hover:bg-white/30 text-white font-semibold py-2.5 rounded-xl text-sm transition-all border border-white/20"
              >
                Make Payment
              </button>
              <button
                onClick={() => navigate('/income')}
                className="flex-1 bg-white/20 hover:bg-white/30 text-white font-semibold py-2.5 rounded-xl text-sm transition-all border border-white/20"
              >
                Add Income
              </button>
            </div>
          </div>
        )}
      </div>

      {/* Safety Wallet */}
      <div className="mx-5 mt-3">
        {isLoading ? (
          <SkeletonCard height="h-28" />
        ) : (
          <div
            className="card cursor-pointer hover:shadow-card-hover transition-shadow"
            onClick={() => navigate('/wallets')}
          >
            <div className="flex items-center justify-between mb-2">
              <div className="flex items-center gap-2">
                <Shield className="w-4 h-4 text-emerald-600" />
                <span className="text-sm font-semibold text-gray-700">Safety Wallet</span>
              </div>
              <ArrowRight className="w-4 h-4 text-gray-400" />
            </div>

            <div className="flex items-end justify-between mb-3">
              <div>
                <span className="text-2xl font-bold text-gray-900">
                  {formatINR(dashboard?.safety_wallet?.balance || 0)}
                </span>
                <span className="text-gray-400 text-sm ml-1">
                  / {formatINR(dashboard?.safety_wallet?.target || 10000)}
                </span>
              </div>
              <span className="text-sm font-bold text-emerald-600">
                {(dashboard?.safety_wallet?.progress || 0).toFixed(0)}%
              </span>
            </div>

            <div className="progress-bar">
              <div
                className="progress-fill"
                style={{ width: `${Math.min(100, dashboard?.safety_wallet?.progress || 0)}%` }}
              />
            </div>

            {(dashboard?.safety_wallet?.progress || 0) < 100 && (
              <p className="text-xs text-gray-500 mt-2">
                {formatINR(Math.max(0, (dashboard?.safety_wallet?.target || 10000) - (dashboard?.safety_wallet?.balance || 0)))} more to reach your target
              </p>
            )}
          </div>
        )}
      </div>

      {/* LEVELLY Financial Resilience Score */}
      <div className="mx-5 mt-3">
        {isLoading ? (
          <SkeletonCard height="h-24" />
        ) : (
          <div className="card cursor-pointer" onClick={() => navigate('/analytics')}>
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-500 font-medium">Financial Resilience Score</p>
                <p className="text-xs text-gray-400 mt-0.5">LEVELLY's measure of your financial health</p>
                <div className="flex items-center gap-2 mt-2">
                  <span className="text-3xl font-bold text-gray-900">
                    {(dashboard?.resilience?.score || 0).toFixed(0)}
                  </span>
                  <span className="text-gray-400 text-sm">/100</span>
                  <span className={`text-xs px-2 py-0.5 rounded-full font-medium capitalize
                    ${dashboard?.resilience?.label === 'stable' ? 'bg-green-100 text-green-700' : ''}
                    ${dashboard?.resilience?.label === 'moderate' ? 'bg-amber-100 text-amber-700' : ''}
                    ${dashboard?.resilience?.label === 'at_risk' ? 'bg-orange-100 text-orange-700' : ''}
                    ${dashboard?.resilience?.label === 'critical' ? 'bg-red-100 text-red-700' : ''}
                  `}>
                    {(dashboard?.resilience?.label || 'stable').replace('_', ' ')}
                  </span>
                </div>
              </div>
              <div className="w-16 h-16 flex items-center justify-center">
                <svg viewBox="0 0 64 64" className="w-full h-full -rotate-90">
                  <circle cx="32" cy="32" r="26" fill="none" stroke="#f0fdf4" strokeWidth="8" />
                  <circle
                    cx="32" cy="32" r="26"
                    fill="none"
                    stroke={
                      (dashboard?.resilience?.score || 0) >= 75 ? '#059669' :
                      (dashboard?.resilience?.score || 0) >= 55 ? '#d97706' :
                      (dashboard?.resilience?.score || 0) >= 35 ? '#ea580c' : '#dc2626'
                    }
                    strokeWidth="8"
                    strokeDasharray={`${((dashboard?.resilience?.score || 0) / 100) * 163} 163`}
                    strokeLinecap="round"
                    style={{ transition: 'stroke-dasharray 1s ease-out' }}
                  />
                </svg>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Income Section */}
      <div className="mx-5 mt-3">
        {isLoading ? (
          <SkeletonCard height="h-24" />
        ) : (
          <div className="card cursor-pointer" onClick={() => navigate('/income')}>
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-500">Recent Income Pace</p>
                <p className="text-xl font-bold text-gray-900 mt-1">
                  {formatINR(dashboard?.income?.recent_pace || 0)}<span className="text-sm text-gray-400 font-normal">/month</span>
                </p>
                <p className="text-xs text-gray-400 mt-0.5">
                  Usual: {formatINR(dashboard?.income?.historical_avg || 0)}/month
                </p>
              </div>
              <div className="flex flex-col items-end gap-1">
                {dashboard?.income?.trend === 'declining' ? (
                  <TrendingDown className="w-6 h-6 text-orange-500" />
                ) : (
                  <TrendingUp className="w-6 h-6 text-emerald-600" />
                )}
                <span className={`text-xs font-semibold capitalize px-2 py-0.5 rounded-full
                  ${dashboard?.income?.trend === 'declining' ? 'text-orange-600 bg-orange-50' : 'text-emerald-600 bg-emerald-50'}
                `}>
                  {dashboard?.income?.trend || 'stable'}
                </span>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Nudges */}
      {nudges.length > 0 && (
        <div className="mx-5 mt-4">
          <p className="section-header">What LEVELLY sees</p>
          <div className="space-y-2">
            {nudges.slice(0, 2).map((nudge: any, i: number) => (
              <div
                key={i}
                onClick={() => nudge.cta_url && navigate(nudge.cta_url)}
                className={`p-3.5 rounded-2xl cursor-pointer border transition-all
                  ${nudge.priority === 'high' ? 'bg-orange-50 border-orange-200' : 'bg-white border-gray-100'}
                `}
              >
                <div className="flex items-center justify-between">
                  <p className="text-sm text-gray-700 flex-1">{nudge.message}</p>
                  <ArrowRight className="w-4 h-4 text-gray-400 ml-2 flex-shrink-0" />
                </div>
                {nudge.cta && (
                  <p className={`text-xs font-semibold mt-1.5
                    ${nudge.priority === 'high' ? 'text-orange-600' : 'text-emerald-600'}
                  `}>
                    {nudge.cta} →
                  </p>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Quick Actions */}
      <div className="mx-5 mt-5">
        <p className="section-header">Quick Actions</p>
        <div className="grid grid-cols-2 gap-3">
          {[
            {
              id: 'qa-pay',
              icon: '💳',
              label: 'Make Payment',
              sub: 'Save as you pay',
              to: '/pay',
              color: 'bg-emerald-50',
            },
            {
              id: 'qa-coach',
              icon: '🤝',
              label: 'Levelly Coach',
              sub: 'Get guidance',
              to: '/coach',
              color: 'bg-blue-50',
            },
            {
              id: 'qa-grow',
              icon: '📈',
              label: 'Grow Surplus',
              sub: 'Smart investments',
              to: '/grow',
              color: 'bg-purple-50',
            },
            {
              id: 'qa-credit',
              icon: '🏦',
              label: 'Need Credit?',
              sub: 'Responsible lending',
              to: '/credit',
              color: 'bg-yellow-50',
            },
          ].map(({ id, icon, label, sub, to, color }) => (
            <button
              key={id}
              id={id}
              onClick={() => navigate(to)}
              className={`${color} rounded-2xl p-4 text-left hover:shadow-card transition-all active:scale-98`}
            >
              <span className="text-2xl">{icon}</span>
              <p className="font-semibold text-gray-800 text-sm mt-2">{label}</p>
              <p className="text-gray-500 text-xs">{sub}</p>
            </button>
          ))}
        </div>
      </div>
    </div>
  )
}
