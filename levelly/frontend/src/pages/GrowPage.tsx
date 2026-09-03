import { useQuery } from '@tanstack/react-query'
import { useNavigate } from 'react-router-dom'
import { Shield, TrendingUp, ChevronRight, Pause } from 'lucide-react'
import { investmentAPI } from '../lib/api'

const formatINR = (amount: number) =>
  new Intl.NumberFormat('en-IN', { style: 'currency', currency: 'INR', maximumFractionDigits: 0 }).format(amount)

const riskColors: Record<string, string> = {
  LOW: 'bg-green-100 text-green-700',
  MODERATE: 'bg-amber-100 text-amber-700',
  HIGH: 'bg-red-100 text-red-700',
}

export default function GrowPage() {
  const navigate = useNavigate()

  const { data: suggestions, isLoading } = useQuery({
    queryKey: ['suggestions'],
    queryFn: () => investmentAPI.suggestions().then(r => r.data),
  })

  const { data: status } = useQuery({
    queryKey: ['invest-status'],
    queryFn: () => investmentAPI.status().then(r => r.data),
  })

  const isPaused = suggestions?.paused || status?.is_paused

  return (
    <div className="px-5 pb-8 animate-fade-in">
      <h1 className="text-2xl font-bold text-levelly-text mb-1">Grow</h1>
      <p className="text-sm text-gray-500 mb-5">Invest your surplus safely and responsibly.</p>

      {/* Safety Wallet Status */}
      <div className="card mb-4">
        <div className="flex items-center gap-2 mb-3">
          <Shield className="w-4 h-4 text-emerald-600" />
          <p className="text-sm font-semibold text-gray-700">Safety Wallet Status</p>
        </div>
        <div className="flex justify-between text-sm mb-2">
          <span className="text-gray-500">Balance</span>
          <span className="font-bold">{formatINR(status?.safety_balance || 0)}</span>
        </div>
        <div className="flex justify-between text-sm mb-3">
          <span className="text-gray-500">Target</span>
          <span className="font-medium">{formatINR(status?.safety_target || 10000)}</span>
        </div>
        {status?.safety_surplus > 0 ? (
          <div className="p-3 bg-emerald-50 rounded-xl border border-emerald-200">
            <p className="text-sm font-semibold text-emerald-700">
              🎉 Surplus: {formatINR(status.safety_surplus)}
            </p>
            <p className="text-xs text-emerald-600 mt-0.5">
              Up to {formatINR(status.available_for_investment)} available for investment
            </p>
          </div>
        ) : (
          <div className="p-3 bg-gray-50 rounded-xl">
            <p className="text-sm text-gray-600">
              {formatINR(Math.abs(status?.safety_surplus || 0))} more needed before investing
            </p>
          </div>
        )}
      </div>

      {/* Paused state */}
      {isPaused && (
        <div className="card border-2 border-orange-200 bg-orange-50 mb-4">
          <div className="flex items-center gap-2 mb-2">
            <Pause className="w-5 h-5 text-orange-600" />
            <p className="font-semibold text-orange-800">Investment Suggestions Paused</p>
          </div>
          <p className="text-orange-700 text-sm">
            {suggestions?.pause_reason || status?.pause_reason}
          </p>
          <button
            onClick={() => navigate('/coach')}
            className="mt-3 text-sm font-semibold text-orange-700 underline"
          >
            Talk to Levelly Coach
          </button>
        </div>
      )}

      {/* Suggestions */}
      {!isPaused && (
        <div>
          <p className="section-header">Investment Options</p>
          {isLoading ? (
            <div className="space-y-3">
              <div className="skeleton h-24 rounded-2xl" />
              <div className="skeleton h-24 rounded-2xl" />
            </div>
          ) : suggestions?.suggestions?.length === 0 ? (
            <div className="card text-center text-gray-500">
              <TrendingUp className="w-10 h-10 text-gray-300 mx-auto mb-2" />
              <p>No suggestions available</p>
            </div>
          ) : (
            <div className="space-y-3">
              {suggestions?.suggestions?.map((s: any) => (
                <div
                  key={s.product_id}
                  onClick={() => navigate(`/grow/invest/${s.product_id}`)}
                  className="card cursor-pointer hover:shadow-card-hover transition-all active:scale-98"
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-1">
                        <p className="font-semibold text-gray-800">{s.name}</p>
                      </div>
                      <p className="text-xs text-gray-500 mb-2">{s.issuer}</p>
                      <p className="text-xs text-gray-600 leading-relaxed">{s.reason}</p>
                    </div>
                    <ChevronRight className="w-5 h-5 text-gray-400 ml-2 flex-shrink-0" />
                  </div>
                  <div className="flex gap-2 mt-3">
                    <span className={`px-2 py-0.5 rounded-full text-xs font-semibold ${riskColors[s.risk_level]}`}>
                      {s.risk_level} Risk
                    </span>
                    <span className="px-2 py-0.5 rounded-full text-xs font-semibold bg-gray-100 text-gray-600">
                      {s.liquidity}
                    </span>
                    <span className="px-2 py-0.5 rounded-full text-xs font-semibold bg-blue-100 text-blue-600">
                      Min {formatINR(s.min_investment)}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Disclaimer */}
      <div className="mt-5 p-4 bg-gray-100 rounded-2xl">
        <p className="text-xs text-gray-500 leading-relaxed">
          <strong>Important:</strong> These are illustrative product categories, not specific investment advice. 
          Investments are subject to market risks. Past performance does not guarantee future returns. 
          LEVELLY is not a SEBI-registered investment advisor. Consult a qualified financial advisor for investment decisions.
        </p>
      </div>
    </div>
  )
}
