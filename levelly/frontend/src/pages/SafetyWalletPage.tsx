import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useNavigate } from 'react-router-dom'
import {
  ShieldCheck,
  ArrowUpRight,
  Plus,
  Sparkles,
  CheckCircle2,
  AlertCircle,
  HelpCircle,
  Building2,
  Lock,
} from 'lucide-react'
import { walletAPI, paymentAPI, transactionAPI } from '../lib/api'
import toast from 'react-hot-toast'

const formatINR = (amount: number) =>
  new Intl.NumberFormat('en-IN', { style: 'currency', currency: 'INR', maximumFractionDigits: 0 }).format(amount)

export default function SafetyWalletPage() {
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const [showTargetModal, setShowTargetModal] = useState(false)
  const [newTarget, setNewTarget] = useState('')
  const [depositAmount, setDepositAmount] = useState('')
  const [showDepositModal, setShowDepositModal] = useState(false)

  const { data: safety, isLoading } = useQuery({
    queryKey: ['safety-wallet'],
    queryFn: () => walletAPI.getSafety().then(r => r.data),
  })

  const { data: linkedAccount } = useQuery({
    queryKey: ['linked-account'],
    queryFn: () => paymentAPI.getLinkedAccount().then(r => r.data),
  })

  const { data: transactionsData } = useQuery({
    queryKey: ['savings-txns'],
    queryFn: () => transactionAPI.getAll(10, 0, 'savings').then(r => r.data),
  })

  const targetMutation = useMutation({
    mutationFn: (target: number) => walletAPI.updateTarget(target),
    onSuccess: () => {
      toast.success('Safety target updated successfully!')
      queryClient.invalidateQueries({ queryKey: ['safety-wallet'] })
      queryClient.invalidateQueries({ queryKey: ['wallets'] })
      setShowTargetModal(false)
    },
    onError: (err: any) => {
      toast.error(err.response?.data?.detail || 'Failed to update target')
    },
  })

  const depositMutation = useMutation({
    mutationFn: (amount: number) => walletAPI.depositSafety(amount),
    onSuccess: () => {
      toast.success(`Added ₹${depositAmount} to Safety Wallet!`)
      queryClient.invalidateQueries({ queryKey: ['safety-wallet'] })
      queryClient.invalidateQueries({ queryKey: ['wallets'] })
      queryClient.invalidateQueries({ queryKey: ['savings-txns'] })
      setShowDepositModal(false)
      setDepositAmount('')
    },
    onError: (err: any) => {
      toast.error(err.response?.data?.detail || 'Deposit failed')
    },
  })

  const balance = safety?.balance || 0
  const target = safety?.target_amount || 10000
  const progress = Math.min(100, safety?.progress_percentage || 0)
  const shortfall = safety?.shortfall || 0
  const surplus = safety?.surplus || 0
  const isTargetMet = progress >= 100

  return (
    <div className="px-5 pb-10 animate-fade-in">
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <div>
          <h1 className="text-2xl font-black text-slate-900 tracking-tight">Safety Wallet</h1>
          <p className="text-xs text-slate-500 font-medium">Your personal shock-absorbing financial reserve</p>
        </div>
        <div className="flex items-center gap-1.5 bg-emerald-50 border border-emerald-200/60 px-2.5 py-1 rounded-full">
          <ShieldCheck className="w-3.5 h-3.5 text-emerald-700" />
          <span className="text-[11px] font-bold text-emerald-800">Protected Reserve</span>
        </div>
      </div>

      {/* Main Hero Card */}
      <div className="relative overflow-hidden rounded-3xl bg-gradient-to-br from-emerald-900 via-teal-950 to-slate-950 p-6 text-white shadow-xl shadow-emerald-950/20 border border-emerald-700/30 mb-5">
        <div className="absolute top-0 right-0 -mt-8 -mr-8 w-44 h-44 bg-emerald-500/10 rounded-full blur-2xl pointer-events-none" />
        <div className="absolute bottom-0 left-0 -mb-8 -ml-8 w-36 h-36 bg-teal-500/10 rounded-full blur-xl pointer-events-none" />

        <div className="relative z-10">
          <div className="flex items-center justify-between text-xs text-emerald-200/80 mb-2 font-medium">
            <span className="flex items-center gap-1.5">
              <Lock className="w-3 h-3 text-emerald-400" /> Managed Resilience Reserve
            </span>
            <button
              onClick={() => {
                setNewTarget(target.toString())
                setShowTargetModal(true)
              }}
              className="text-[11px] text-emerald-300 hover:text-white underline underline-offset-2 transition"
            >
              Edit Target
            </button>
          </div>

          <div className="text-4xl font-extrabold tracking-tight text-white mb-2">
            {isLoading ? '—' : formatINR(balance)}
          </div>

          {/* Progress towards target */}
          <div className="mt-4 mb-4">
            <div className="flex items-center justify-between text-xs font-semibold mb-1.5">
              <span className="text-emerald-200">{progress.toFixed(0)}% of buffer target</span>
              <span className="text-slate-300 font-normal">Target: {formatINR(target)}</span>
            </div>
            <div className="h-2.5 bg-slate-800/80 rounded-full overflow-hidden p-0.5 border border-emerald-500/20">
              <div
                className="h-full bg-gradient-to-r from-emerald-400 to-teal-300 rounded-full transition-all duration-700 ease-out"
                style={{ width: `${progress}%` }}
              />
            </div>
          </div>

          {/* Status Indicator */}
          <div className="flex items-center justify-between pt-3 border-t border-emerald-800/40 text-xs">
            {isTargetMet ? (
              <div className="flex items-center gap-1.5 text-emerald-300 font-semibold">
                <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                <span>Buffer Target Achieved! Surplus: {formatINR(surplus)}</span>
              </div>
            ) : (
              <div className="flex items-center gap-1.5 text-amber-200 font-medium">
                <AlertCircle className="w-4 h-4 text-amber-300" />
                <span>Shortfall: {formatINR(shortfall)} to full security</span>
              </div>
            )}
          </div>

          {/* Quick Actions */}
          <div className="flex gap-2.5 mt-5">
            <button
              onClick={() => setShowDepositModal(true)}
              className="flex-1 flex items-center justify-center gap-2 bg-emerald-500 hover:bg-emerald-400 text-slate-950 py-3 rounded-2xl text-xs font-bold transition shadow-md shadow-emerald-500/20 active:scale-[0.98]"
            >
              <Plus className="w-4 h-4" /> Boost Reserve
            </button>
            <button
              onClick={() => navigate('/pay')}
              className="flex-1 flex items-center justify-center gap-2 bg-white/10 hover:bg-white/20 text-white py-3 rounded-2xl text-xs font-semibold border border-white/20 transition active:scale-[0.98]"
            >
              <ArrowUpRight className="w-4 h-4" /> Pay & Save
            </button>
          </div>
        </div>
      </div>

      {/* Linked Bank Source Box */}
      <div className="bg-white rounded-2xl p-4 border border-slate-200/80 shadow-sm mb-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-slate-100 flex items-center justify-center text-slate-700">
              <Building2 className="w-5 h-5" />
            </div>
            <div>
              <p className="text-xs text-slate-500 font-medium">Funding Bank Account</p>
              <p className="text-sm font-bold text-slate-900">
                {linkedAccount?.bank_name || 'HDFC Bank'} {linkedAccount?.account_mask || '****4821'}
              </p>
              <p className="text-[11px] text-emerald-600 font-semibold">{linkedAccount?.upi_id || 'arjun@upi'}</p>
            </div>
          </div>
          <span className="bg-emerald-50 text-emerald-700 text-[10px] font-bold px-2 py-1 rounded-full border border-emerald-200">
            Active
          </span>
        </div>
        <div className="mt-3 pt-3 border-t border-slate-100 flex items-center justify-between text-xs text-slate-600">
          <span>Smart Save-at-Pay</span>
          <span className="font-semibold text-emerald-700 flex items-center gap-1">
            <Sparkles className="w-3.5 h-3.5" /> Auto-Adds on UPI spends
          </span>
        </div>
      </div>

      {/* Growth Transition Suggestion */}
      {isTargetMet ? (
        <div className="bg-gradient-to-r from-teal-50 to-emerald-50 border border-emerald-200 rounded-2xl p-4 mb-4 flex items-center justify-between">
          <div>
            <p className="text-xs font-bold text-emerald-900 flex items-center gap-1">
              <Sparkles className="w-3.5 h-3.5 text-emerald-600" /> Surplus Available for Growth
            </p>
            <p className="text-[11px] text-emerald-700 mt-0.5">
              You have {formatINR(surplus)} above your target. Put it in liquid mutual funds!
            </p>
          </div>
          <button
            onClick={() => navigate('/grow')}
            className="bg-emerald-700 text-white text-xs font-bold px-3 py-2 rounded-xl shrink-0 hover:bg-emerald-800 transition"
          >
            Explore Grow →
          </button>
        </div>
      ) : (
        <div className="bg-slate-50 border border-slate-200/80 rounded-2xl p-3.5 mb-4 text-xs text-slate-600 flex items-start gap-2.5">
          <HelpCircle className="w-4 h-4 text-slate-400 shrink-0 mt-0.5" />
          <p>
            <span className="font-semibold text-slate-800">How Safety Wallet builds:</span> Every time you make a UPI payment with LEVELLY Pay, micro-savings (0-15%) are deposited straight here from your bank.
          </p>
        </div>
      )}

      {/* Recent Savings Activity */}
      <div className="mb-6">
        <div className="flex items-center justify-between mb-3">
          <h2 className="text-sm font-bold text-slate-800 uppercase tracking-wider">Savings Activity</h2>
          <button
            onClick={() => navigate('/transactions')}
            className="text-xs text-emerald-700 font-semibold hover:underline"
          >
            See All
          </button>
        </div>

        <div className="bg-white rounded-2xl border border-slate-200/80 shadow-sm divide-y divide-slate-100 overflow-hidden">
          {transactionsData?.transactions && transactionsData.transactions.length > 0 ? (
            transactionsData.transactions.slice(0, 5).map((t: any) => (
              <div key={t.id} className="p-3.5 flex items-center justify-between hover:bg-slate-50/60 transition">
                <div className="flex items-center gap-3">
                  <div className="w-8 h-8 rounded-xl bg-emerald-50 text-emerald-700 flex items-center justify-center">
                    <ShieldCheck className="w-4 h-4" />
                  </div>
                  <div>
                    <p className="text-xs font-bold text-slate-900">{t.description}</p>
                    <p className="text-[10px] text-slate-400">
                      {new Date(t.date).toLocaleDateString('en-IN', { day: 'numeric', month: 'short' })}
                    </p>
                  </div>
                </div>
                <span className="text-xs font-extrabold text-emerald-700">
                  +{formatINR(t.amount)}
                </span>
              </div>
            ))
          ) : (
            <div className="p-6 text-center text-xs text-slate-400">
              No recent savings deposits. Make a payment with Save-at-Pay to start building!
            </div>
          )}
        </div>
      </div>

      {/* Target Update Modal */}
      {showTargetModal && (
        <div className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-5">
          <div className="bg-white w-full max-w-sm rounded-3xl p-6 shadow-2xl border border-slate-100 animate-scale-up">
            <h3 className="text-lg font-bold text-slate-900 mb-1">Set Safety Target</h3>
            <p className="text-xs text-slate-500 mb-4">
              Recommended: 1-2 months of living expenses (₹8,000 - ₹15,000)
            </p>

            <div className="relative mb-4">
              <span className="absolute left-4 top-3.5 text-slate-400 font-bold">₹</span>
              <input
                type="number"
                value={newTarget}
                onChange={(e) => setNewTarget(e.target.value)}
                placeholder="10000"
                className="w-full pl-9 pr-4 py-3 bg-slate-50 border border-slate-200 rounded-xl text-slate-900 font-bold text-lg focus:outline-none focus:border-emerald-600 focus:bg-white transition"
              />
            </div>

            <div className="flex gap-2">
              <button
                onClick={() => setShowTargetModal(false)}
                className="flex-1 py-3 bg-slate-100 hover:bg-slate-200 text-slate-700 font-bold rounded-xl text-xs transition"
              >
                Cancel
              </button>
              <button
                onClick={() => {
                  const val = parseFloat(newTarget)
                  if (!val || val < 1000) {
                    toast.error('Target must be at least ₹1,000')
                    return
                  }
                  targetMutation.mutate(val)
                }}
                disabled={targetMutation.isPending}
                className="flex-1 py-3 bg-emerald-700 hover:bg-emerald-800 text-white font-bold rounded-xl text-xs transition disabled:opacity-50"
              >
                {targetMutation.isPending ? 'Saving...' : 'Save Target'}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Boost / Deposit Modal */}
      {showDepositModal && (
        <div className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-5">
          <div className="bg-white w-full max-w-sm rounded-3xl p-6 shadow-2xl border border-slate-100 animate-scale-up">
            <h3 className="text-lg font-bold text-slate-900 mb-1">Boost Safety Reserve</h3>
            <p className="text-xs text-slate-500 mb-4">
              Transfer funds directly from {linkedAccount?.bank_name || 'HDFC Bank'} into your Safety Wallet.
            </p>

            <div className="relative mb-3">
              <span className="absolute left-4 top-3.5 text-slate-400 font-bold">₹</span>
              <input
                type="number"
                value={depositAmount}
                onChange={(e) => setDepositAmount(e.target.value)}
                placeholder="500"
                className="w-full pl-9 pr-4 py-3 bg-slate-50 border border-slate-200 rounded-xl text-slate-900 font-bold text-lg focus:outline-none focus:border-emerald-600 focus:bg-white transition"
              />
            </div>

            <div className="flex gap-2 mb-4">
              {[200, 500, 1000, 2000].map((preset) => (
                <button
                  key={preset}
                  onClick={() => setDepositAmount(preset.toString())}
                  className="flex-1 py-1.5 bg-slate-100 hover:bg-emerald-50 hover:text-emerald-700 text-slate-700 text-xs font-semibold rounded-lg transition"
                >
                  +{preset}
                </button>
              ))}
            </div>

            <div className="flex gap-2">
              <button
                onClick={() => setShowDepositModal(false)}
                className="flex-1 py-3 bg-slate-100 hover:bg-slate-200 text-slate-700 font-bold rounded-xl text-xs transition"
              >
                Cancel
              </button>
              <button
                onClick={() => {
                  const val = parseFloat(depositAmount)
                  if (!val || val <= 0) {
                    toast.error('Enter a valid amount')
                    return
                  }
                  depositMutation.mutate(val)
                }}
                disabled={depositMutation.isPending}
                className="flex-1 py-3 bg-emerald-700 hover:bg-emerald-800 text-white font-bold rounded-xl text-xs transition disabled:opacity-50"
              >
                {depositMutation.isPending ? 'Processing...' : 'Confirm Deposit'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
