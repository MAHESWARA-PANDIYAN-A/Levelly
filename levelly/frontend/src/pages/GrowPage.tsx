import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useNavigate } from 'react-router-dom'
import { Shield, TrendingUp, ChevronRight, Pause, Sparkles, RefreshCw, CheckCircle2 } from 'lucide-react'
import { investmentAPI } from '../lib/api'
import toast from 'react-hot-toast'

const formatINR = (amount: number) =>
  new Intl.NumberFormat('en-IN', { style: 'currency', currency: 'INR', maximumFractionDigits: 0 }).format(amount)


export default function GrowPage() {
  const navigate = useNavigate()
  const queryClient = useQueryClient()

  const { data: suggestions, isLoading } = useQuery({
    queryKey: ['suggestions'],
    queryFn: () => investmentAPI.suggestions().then(r => r.data),
  })

  const { data: status } = useQuery({
    queryKey: ['invest-status'],
    queryFn: () => investmentAPI.status().then(r => r.data),
  })

  const toggleSurplusMutation = useMutation({
    mutationFn: () => investmentAPI.toggleDemoSurplus(),
    onSuccess: (res) => {
      toast.success(res.data.message)
      queryClient.invalidateQueries({ queryKey: ['suggestions'] })
      queryClient.invalidateQueries({ queryKey: ['invest-status'] })
      queryClient.invalidateQueries({ queryKey: ['wallets'] })
      queryClient.invalidateQueries({ queryKey: ['profile'] })
      queryClient.invalidateQueries({ queryKey: ['distress'] })
    },
    onError: (err: any) => {
      toast.error(err.response?.data?.detail?.message || 'Failed to toggle demo surplus')
    },
  })

  const isPaused = suggestions?.paused ?? status?.is_paused
  const isSurplusMode = (status?.safety_surplus || 0) > 0

  return (
    <div className="px-5 pb-8 animate-fade-in">
      <div className="flex items-center justify-between mb-1">
        <h1 className="text-2xl font-bold text-levelly-text">Grow</h1>
        <button
          onClick={() => toggleSurplusMutation.mutate()}
          disabled={toggleSurplusMutation.isPending}
          className={`flex items-center gap-1.5 px-3 py-1.5 text-xs font-semibold rounded-full border transition-all shadow-sm ${
            isSurplusMode
              ? 'bg-amber-50 text-amber-800 border-amber-300 hover:bg-amber-100'
              : 'bg-emerald-50 text-emerald-800 border-emerald-300 hover:bg-emerald-100'
          }`}
          title="Toggle between State A (₹10.5k Surplus) and State B (₹8.2k Paused)"
        >
          {toggleSurplusMutation.isPending ? (
            <RefreshCw className="w-3.5 h-3.5 animate-spin" />
          ) : (
            <Sparkles className="w-3.5 h-3.5 text-emerald-600" />
          )}
          {isSurplusMode ? 'Simulate State B (₹8.2k Paused)' : 'Simulate State A (₹10.5k Surplus)'}
        </button>
      </div>
      <p className="text-sm text-gray-500 mb-5">Invest your surplus safely and responsibly.</p>

      {/* Safety Wallet Status */}
      <div className="card mb-4 shadow-sm border border-gray-100">
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center gap-2">
            <Shield className="w-4 h-4 text-emerald-600" />
            <p className="text-sm font-semibold text-gray-700">Safety Wallet Status</p>
          </div>
          {isSurplusMode ? (
            <span className="flex items-center gap-1 text-xs font-semibold px-2 py-0.5 rounded-full bg-emerald-100 text-emerald-800">
              <CheckCircle2 className="w-3 h-3" /> Target Met
            </span>
          ) : (
            <span className="text-xs font-semibold px-2 py-0.5 rounded-full bg-amber-100 text-amber-800">
              Building Buffer
            </span>
          )}
        </div>
        <div className="flex justify-between text-sm mb-2">
          <span className="text-gray-500">Safety Wallet</span>
          <span className="font-bold text-gray-900">{formatINR(status?.safety_balance || 10500)}</span>
        </div>
        <div className="flex justify-between text-sm mb-2">
          <span className="text-gray-500">Safety Target</span>
          <span className="font-medium text-gray-700">{formatINR(status?.safety_target || 10000)}</span>
        </div>
        {(status?.safety_surplus || 0) > 0 && (
          <div className="flex justify-between text-sm mb-3">
            <span className="text-gray-500">Potential Surplus</span>
            <span className="font-bold text-emerald-700">{formatINR(status?.safety_surplus || 500)}</span>
          </div>
        )}
        {status?.safety_surplus > 0 ? (
          <div className="p-3 bg-emerald-50 rounded-xl border border-emerald-200">
            <p className="text-sm font-semibold text-emerald-800">
              Your safety target is currently covered.
            </p>
            <p className="text-xs text-emerald-600 mt-0.5">
              Explore options for your surplus.
            </p>
          </div>
        ) : (
          <div className="p-3 bg-gray-50 rounded-xl border border-gray-100">
            <p className="text-sm text-gray-600 font-medium">
              {formatINR(Math.abs(status?.safety_surplus || 0))} more needed before active investing
            </p>
            <p className="text-xs text-gray-400 mt-0.5">
              Levelly guards your liquidity so you never lock up money you need for daily expenses.
            </p>
          </div>
        )}
      </div>

      {/* Paused banner if applicable (Section 24 & 27) */}
      {isPaused && (
        <div className="card border-2 border-orange-200 bg-orange-50 mb-4 shadow-sm p-4">
          <div className="flex items-center gap-2 mb-2">
            <Pause className="w-5 h-5 text-orange-600" />
            <p className="font-semibold text-orange-800">Investment suggestions paused</p>
          </div>
          <p className="text-orange-700 text-sm leading-relaxed">
            {status?.pause_reason || 'Investment suggestions are paused because your current financial position prioritizes liquidity.'}
          </p>
          <div className="flex items-center gap-4 mt-3">
            <button
              onClick={() => navigate('/coach')}
              className="text-xs font-semibold text-orange-800 underline"
            >
              Talk to Levelly Coach
            </button>
            <button
              onClick={() => toggleSurplusMutation.mutate()}
              className="text-xs font-semibold bg-orange-600 text-white px-3 py-1.5 rounded-lg hover:bg-orange-700 transition-colors shadow-xs"
            >
              ⚡ Test Live Surplus Flow
            </button>
          </div>
        </div>
      )}

      {/* Investment Products Section — ONLY visible when healthy (Section 21 & 24) */}
      {!isPaused && (
        <div>
          <div className="flex items-center justify-between mb-2">
            <h2 className="section-header mb-0">Recommended Investment Options</h2>
            <span className="text-[11px] font-semibold text-emerald-700 bg-emerald-100 px-2 py-0.5 rounded-full">
              Surplus Ready
            </span>
          </div>
          <p className="text-xs text-gray-500 mb-3">
            Explore options for your surplus based on your safety reserve.
          </p>

          {isLoading ? (
            <div className="space-y-3">
              <div className="skeleton h-24 rounded-2xl" />
              <div className="skeleton h-24 rounded-2xl" />
            </div>
          ) : (Array.isArray(suggestions) ? suggestions : (suggestions?.suggestions || [])).length === 0 ? (
            <div className="card text-center text-gray-500 py-8">
              <TrendingUp className="w-10 h-10 text-gray-300 mx-auto mb-2" />
              <p className="font-medium">No investments available</p>
            </div>
          ) : (
            <div className="space-y-3.5">
              {(Array.isArray(suggestions) ? suggestions : (suggestions?.suggestions || [])).map((s: any) => (
                <div
                  key={s.product_id}
                  className="card p-4 transition-all border border-gray-200 bg-white hover:border-emerald-300 hover:shadow-md"
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-1">
                        <h3 className="font-bold text-gray-900 text-base">{s.name}</h3>
                        <span className="text-[10px] font-semibold bg-slate-100 text-slate-700 px-2 py-0.5 rounded-full">
                          {s.type?.replace(/_/g, ' ')}
                        </span>
                      </div>
                      <p className="text-xs text-gray-500 mb-2">{s.issuer}</p>
                      <p className="text-xs text-gray-700 leading-relaxed font-medium mb-2">
                        {s.suitable_for || s.description}
                      </p>
                      {s.reason && (
                        <p className="text-xs text-emerald-700 bg-emerald-50 p-2 rounded-lg border border-emerald-100 leading-relaxed mb-2">
                          💡 {s.reason}
                        </p>
                      )}
                    </div>
                  </div>

                  <div className="grid grid-cols-2 sm:grid-cols-3 gap-2 my-2.5 text-xs">
                    <div className="p-2 bg-gray-50 rounded-lg">
                      <span className="text-[10px] text-gray-400 block font-medium uppercase">Risk Level</span>
                      <span className={`font-semibold ${s.risk_level === 'LOW' ? 'text-green-700' : 'text-amber-700'}`}>
                        {s.risk_level}
                      </span>
                    </div>
                    <div className="p-2 bg-gray-50 rounded-lg">
                      <span className="text-[10px] text-gray-400 block font-medium uppercase">Liquidity</span>
                      <span className="font-semibold text-gray-800 line-clamp-1">{s.liquidity}</span>
                    </div>
                    <div className="p-2 bg-gray-50 rounded-lg col-span-2 sm:col-span-1">
                      <span className="text-[10px] text-gray-400 block font-medium uppercase">Holding Period</span>
                      <span className="font-semibold text-gray-800 line-clamp-1">{s.holding_period}</span>
                    </div>
                  </div>

                  <div className="flex items-center justify-between pt-3 border-t border-gray-100">
                    <div>
                      <span className="text-[10px] text-gray-400 block">Min Amount</span>
                      <span className="text-xs font-bold text-gray-800">{formatINR(s.min_investment)}</span>
                    </div>
                    <button
                      onClick={() => navigate(`/grow/invest/${s.product_id}`)}
                      className="px-4 py-2 bg-emerald-600 hover:bg-emerald-700 active:scale-98 text-white text-xs font-bold rounded-xl transition flex items-center gap-1.5 shadow-sm"
                    >
                      View Details <ChevronRight className="w-3.5 h-3.5" />
                    </button>
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

