import { useQuery } from '@tanstack/react-query'
import { useNavigate } from 'react-router-dom'
import { Shield, ChevronRight, Wallet, ArrowUpRight, ArrowDownLeft } from 'lucide-react'
import { walletAPI } from '../lib/api'

const formatINR = (amount: number) =>
  new Intl.NumberFormat('en-IN', { style: 'currency', currency: 'INR', maximumFractionDigits: 0 }).format(amount)

export default function WalletsPage() {
  const navigate = useNavigate()

  const { data: wallets, isLoading } = useQuery({
    queryKey: ['wallets'],
    queryFn: () => walletAPI.getAll().then(r => r.data),
  })

  const daily = wallets?.find((w: any) => w.wallet_type === 'DAILY')
  const safety = wallets?.find((w: any) => w.wallet_type === 'SAFETY')

  return (
    <div className="px-5 pb-8 animate-fade-in">
      <h1 className="text-2xl font-bold text-levelly-text mb-1">Your Wallets</h1>
      <p className="text-sm text-gray-500 mb-5">Two wallets. One purpose: financial resilience.</p>

      {/* Daily Wallet */}
      <div className="card-premium mb-4 animate-slide-up">
        <div className="flex items-center justify-between mb-1">
          <div className="flex items-center gap-2">
            <Wallet className="w-4 h-4 text-emerald-300" />
            <span className="text-emerald-200 text-sm font-medium">Daily Wallet</span>
          </div>
          <span className="text-emerald-200/60 text-xs">Your spending money</span>
        </div>
        <div className="text-4xl font-bold text-white mt-2 mb-1">
          {isLoading ? '—' : formatINR(daily?.balance || 0)}
        </div>
        <p className="text-emerald-200/60 text-xs">Available to spend and pay</p>

        <div className="flex gap-2 mt-5">
          <button
            onClick={() => navigate('/pay')}
            className="flex-1 flex items-center justify-center gap-2 bg-white/20 hover:bg-white/30 text-white py-3 rounded-xl text-sm font-semibold border border-white/20 transition-all"
          >
            <ArrowUpRight className="w-4 h-4" /> Make Payment
          </button>
          <button
            onClick={() => navigate('/income')}
            className="flex-1 flex items-center justify-center gap-2 bg-white/20 hover:bg-white/30 text-white py-3 rounded-xl text-sm font-semibold border border-white/20 transition-all"
          >
            <ArrowDownLeft className="w-4 h-4" /> Add Income
          </button>
        </div>
      </div>

      {/* Safety Wallet */}
      <div className="card mb-4">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 bg-emerald-100 rounded-xl flex items-center justify-center">
              <Shield className="w-4 h-4 text-emerald-700" />
            </div>
            <div>
              <p className="font-semibold text-gray-800">Safety Wallet</p>
              <p className="text-xs text-gray-400">Your financial buffer</p>
            </div>
          </div>
          <div className="text-right">
            <p className="text-2xl font-bold text-gray-900">
              {isLoading ? '—' : formatINR(safety?.balance || 0)}
            </p>
            <p className="text-xs text-gray-400">
              Target: {formatINR(safety?.target_amount || 10000)}
            </p>
          </div>
        </div>

        {/* Progress */}
        <div className="mb-4">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm text-gray-600">
              {(safety?.progress_percentage || 0).toFixed(0)}% of your safety target
            </span>
            {safety?.progress_percentage >= 100 && (
              <span className="text-xs text-emerald-600 font-semibold bg-emerald-50 px-2 py-0.5 rounded-full">
                Target Reached! 🎉
              </span>
            )}
          </div>
          <div className="progress-bar">
            <div
              className="progress-fill"
              style={{ width: `${Math.min(100, safety?.progress_percentage || 0)}%` }}
            />
          </div>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-2 gap-3">
          <div className="bg-emerald-50 rounded-xl p-3">
            <p className="text-xs text-gray-500 mb-0.5">Shortfall</p>
            <p className="font-bold text-gray-800">
              {formatINR(safety?.shortfall || 0)}
            </p>
          </div>
          <div className="bg-gray-50 rounded-xl p-3">
            <p className="text-xs text-gray-500 mb-0.5">Surplus</p>
            <p className="font-bold text-gray-800">
              {formatINR(safety?.surplus || 0)}
            </p>
          </div>
        </div>

        {safety?.surplus > 0 && (
          <div className="mt-3 p-3 bg-purple-50 rounded-xl border border-purple-100">
            <p className="text-sm text-purple-700 font-medium">
              ₹{safety.surplus.toLocaleString('en-IN')} available to grow! 🌱
            </p>
            <button
              onClick={() => navigate('/grow')}
              className="text-xs text-purple-600 font-semibold mt-1 flex items-center gap-1"
            >
              View investment suggestions <ChevronRight className="w-3 h-3" />
            </button>
          </div>
        )}
      </div>

      {/* What is Save-at-Pay */}
      <div className="card bg-emerald-900 text-white">
        <p className="font-semibold text-emerald-100 mb-1">💡 What is Save-at-Pay?</p>
        <p className="text-emerald-200 text-sm leading-relaxed">
          Each time you make a payment, LEVELLY suggests adding a small percentage to your Safety Wallet. 
          You choose whether to save — LEVELLY never forces it.
        </p>
        <button
          onClick={() => navigate('/pay')}
          className="mt-3 text-emerald-300 text-sm font-semibold flex items-center gap-1"
        >
          Try a payment <ChevronRight className="w-3 h-3" />
        </button>
      </div>
    </div>
  )
}
