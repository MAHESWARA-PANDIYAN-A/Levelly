import { useState } from 'react'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { useNavigate } from 'react-router-dom'
import { ArrowLeft, AlertTriangle, Shield, TrendingDown } from 'lucide-react'
import { expenseAPI } from '../lib/api'
import toast from 'react-hot-toast'

const formatINR = (amount: number) =>
  new Intl.NumberFormat('en-IN', { style: 'currency', currency: 'INR', maximumFractionDigits: 0 }).format(amount)

type Step = 'input' | 'preview' | 'confirm' | 'success'

export default function LargeExpensePage() {
  const navigate = useNavigate()
  const queryClient = useQueryClient()

  const [step, setStep] = useState<Step>('input')
  const [amount, setAmount] = useState('')
  const [purpose, setPurpose] = useState('')
  const [preview, setPreview] = useState<any>(null)
  const [result, setResult] = useState<any>(null)

  const previewMutation = useMutation({
    mutationFn: () => expenseAPI.largePreview(parseFloat(amount), purpose),
    onSuccess: (res) => {
      setPreview(res.data)
      setStep('preview')
    },
    onError: () => toast.error('Could not load expense preview'),
  })

  const confirmMutation = useMutation({
    mutationFn: () => expenseAPI.largeConfirm(parseFloat(amount), purpose, true),
    onSuccess: (res) => {
      setResult(res.data)
      setStep('success')
      queryClient.invalidateQueries({ queryKey: ['dashboard'] })
      queryClient.invalidateQueries({ queryKey: ['wallets'] })
    },
    onError: (err: any) => {
      toast.error(err.response?.data?.detail?.message || 'Expense failed')
    },
  })

  if (step === 'success' && result) {
    return (
      <div className="px-5 pt-12 pb-8 text-center animate-fade-in">
        <div className="w-20 h-20 bg-orange-100 rounded-full flex items-center justify-center mx-auto mb-5">
          <Shield className="w-10 h-10 text-orange-500" />
        </div>
        <h2 className="text-2xl font-bold mb-2">Expense Recorded</h2>
        <p className="text-gray-500 mb-6">{formatINR(parseFloat(amount))} used from Safety Wallet</p>
        <div className="card mb-4 text-left">
          <div className="space-y-2 text-sm">
            <div className="flex justify-between">
              <span className="text-gray-500">Safety Wallet Balance</span>
              <span className="font-bold">{formatINR(result.safety_wallet_balance)}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-500">Safety Progress</span>
              <span className="font-bold">{(result.safety_wallet_progress || 0).toFixed(0)}%</span>
            </div>
          </div>
        </div>
        <button onClick={() => navigate('/coach')} className="btn-primary mb-2">
          Talk to Levelly Coach
        </button>
        <button onClick={() => navigate('/')} className="btn-ghost">Back to Home</button>
      </div>
    )
  }

  if (step === 'preview' && preview) {
    const riskColors = ({
      critical: 'border-red-300 bg-red-50',
      high: 'border-orange-300 bg-orange-50',
      moderate: 'border-amber-200 bg-amber-50',
      low: 'border-gray-200 bg-gray-50',
    } as Record<string, string>)[preview.risk_level] || 'border-gray-200 bg-gray-50'

    return (
      <div className="px-5 pt-12 pb-8 animate-fade-in">
        <button onClick={() => setStep('input')} className="flex items-center gap-2 text-gray-600 mb-5">
          <ArrowLeft className="w-4 h-4" /> Back
        </button>
        <h2 className="text-xl font-bold mb-5">Impact Analysis</h2>

        {/* Piggy bank impact visualization */}
        <div className={`card border-2 ${riskColors} mb-4`}>
          <div className="text-center mb-4">
            <div className="text-5xl mb-3 animate-piggy-wobble">🐷</div>
            <p className="text-sm font-medium text-gray-500">Safety Wallet Impact</p>
            <div className="flex items-center justify-center gap-3 mt-2">
              <div className="text-center">
                <p className="text-xs text-gray-400">Before</p>
                <p className="font-bold text-gray-700">{formatINR(preview.safety_wallet_balance)}</p>
              </div>
              <TrendingDown className="w-5 h-5 text-red-400" />
              <div className="text-center">
                <p className="text-xs text-gray-400">After</p>
                <p className="font-bold text-red-600">{formatINR(preview.remaining_safety_balance)}</p>
              </div>
            </div>
          </div>

          {/* Progress comparison */}
          <div className="space-y-2 mb-4">
            <div>
              <div className="flex justify-between text-xs mb-1">
                <span className="text-gray-500">Current safety</span>
                <span className="font-medium">{(preview.saving_wallet_progress || 0).toFixed(0)}%</span>
              </div>
              <div className="progress-bar">
                <div className="progress-fill bg-emerald-500"
                  style={{ width: `${Math.min(100, (preview.safety_wallet_balance / preview.safety_wallet_target) * 100)}%` }} />
              </div>
            </div>
            <div>
              <div className="flex justify-between text-xs mb-1">
                <span className="text-gray-500">After expense</span>
                <span className="font-medium text-red-600">{(preview.remaining_safety_progress || 0).toFixed(0)}%</span>
              </div>
              <div className="progress-bar">
                <div className="h-full rounded-full transition-all duration-700 ease-out bg-red-400"
                  style={{ width: `${Math.min(100, preview.remaining_safety_progress || 0)}%` }} />
              </div>
            </div>
          </div>

          <div className={`rounded-xl p-3 text-sm font-medium
            ${preview.risk_level === 'critical' || preview.risk_level === 'high' ? 'bg-red-100 text-red-700' : 'bg-amber-100 text-amber-700'}
          `}>
            {preview.risk_message}
          </div>
        </div>

        {/* Stats */}
        <div className="card mb-4">
          <div className="grid grid-cols-2 gap-4 text-sm">
            <div className="text-center p-3 bg-gray-50 rounded-xl">
              <p className="text-gray-500 text-xs">Using</p>
              <p className="font-bold text-lg">{preview.savings_usage_percentage?.toFixed(0)}%</p>
              <p className="text-xs text-gray-400">of Safety Wallet</p>
            </div>
            <div className="text-center p-3 bg-gray-50 rounded-xl">
              <p className="text-gray-500 text-xs">Remaining</p>
              <p className="font-bold text-lg">{formatINR(preview.remaining_safety_balance)}</p>
              <p className="text-xs text-gray-400">in Safety Wallet</p>
            </div>
          </div>
        </div>

        {preview.insufficient_savings ? (
          <div className="card border border-red-200 bg-red-50 mb-4">
            <div className="flex items-center gap-2 mb-2">
              <AlertTriangle className="w-4 h-4 text-red-600" />
              <p className="font-semibold text-red-700 text-sm">Insufficient Safety Wallet funds</p>
            </div>
            <p className="text-xs text-red-600">
              You need {formatINR(preview.shortfall)} more in your Safety Wallet.
              {preview.partner_credit_available && ' Consider using credit instead.'}
            </p>
            {preview.partner_credit_available && (
              <button onClick={() => navigate('/credit')} className="mt-3 text-sm font-semibold text-red-600 underline">
                Check credit options →
              </button>
            )}
          </div>
        ) : (
          <>
            {(preview.risk_level === 'critical' || preview.risk_level === 'high') && (
              <div className="card border-orange-200 bg-orange-50 mb-4">
                <div className="flex items-start gap-2">
                  <AlertTriangle className="w-4 h-4 text-orange-600 mt-0.5 flex-shrink-0" />
                  <p className="text-sm text-orange-700">
                    This will significantly reduce your safety buffer. Make sure this expense is urgent.
                    Levelly Coach can suggest alternatives.
                  </p>
                </div>
                <button onClick={() => navigate('/coach')} className="mt-2 text-sm font-semibold text-orange-700 underline">
                  Talk to Levelly Coach first →
                </button>
              </div>
            )}
            <button
              id="btn-confirm-large-expense"
              onClick={() => setStep('confirm')}
              className={preview.risk_level === 'critical' ? 'btn-danger' : 'btn-primary'}
            >
              Proceed with Expense →
            </button>
          </>
        )}
        <button onClick={() => navigate('/')} className="btn-ghost mt-2">Cancel — Go Back</button>
      </div>
    )
  }

  if (step === 'confirm') {
    return (
      <div className="px-5 pt-12 pb-8 animate-fade-in">
        <button onClick={() => setStep('preview')} className="flex items-center gap-2 text-gray-600 mb-5">
          <ArrowLeft className="w-4 h-4" /> Back
        </button>
        <h2 className="text-xl font-bold mb-5">Final Confirmation</h2>

        <div className="card mb-4">
          <div className="space-y-3 text-sm">
            <div className="flex justify-between">
              <span className="text-gray-500">Amount</span>
              <span className="font-bold text-lg">{formatINR(parseFloat(amount))}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-500">Purpose</span>
              <span className="font-medium text-right max-w-[60%]">{purpose}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-500">Source</span>
              <span className="font-medium text-orange-600">Safety Wallet</span>
            </div>
          </div>
        </div>

        <div className="p-4 bg-amber-50 border border-amber-200 rounded-2xl mb-5">
          <p className="text-sm text-amber-800 font-medium">
            By confirming, {formatINR(parseFloat(amount))} will be withdrawn from your Safety Wallet.
            This cannot be undone. Your safety buffer will reduce.
          </p>
        </div>

        <button
          id="btn-final-confirm-expense"
          onClick={() => confirmMutation.mutate()}
          disabled={confirmMutation.isPending}
          className="btn-danger mb-2"
        >
          {confirmMutation.isPending ? 'Processing...' : `Yes, Use ${formatINR(parseFloat(amount))} from Safety Wallet`}
        </button>
        <button onClick={() => navigate('/')} className="btn-ghost">Cancel</button>
      </div>
    )
  }

  return (
    <div className="px-5 pt-12 pb-8 animate-fade-in">
      <button onClick={() => navigate(-1)} className="flex items-center gap-2 text-gray-600 mb-5">
        <ArrowLeft className="w-4 h-4" /> Back
      </button>
      <h1 className="text-2xl font-bold mb-1">Large Expense</h1>
      <p className="text-sm text-gray-500 mb-6">See the impact before using your Safety Wallet</p>

      <div className="card mb-4">
        <label className="text-sm font-medium text-gray-600 block mb-2">Amount needed (₹)</label>
        <div className="flex items-center gap-2">
          <span className="text-3xl font-bold text-gray-400">₹</span>
          <input
            id="large-expense-amount"
            type="number"
            value={amount}
            onChange={(e) => setAmount(e.target.value)}
            placeholder="0"
            className="flex-1 text-4xl font-bold text-gray-900 focus:outline-none bg-transparent"
          />
        </div>
        <div className="flex gap-2 mt-3">
          {[2000, 5000, 10000, 15000].map((v) => (
            <button key={v} onClick={() => setAmount(String(v))}
              className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-all
                ${amount === String(v) ? 'bg-emerald-600 text-white' : 'bg-gray-100 text-gray-600'}`}>
              ₹{v >= 1000 ? `${v / 1000}k` : v}
            </button>
          ))}
        </div>
      </div>

      <div className="card mb-6">
        <label className="text-sm font-medium text-gray-600 block mb-2">Purpose</label>
        <input
          type="text"
          value={purpose}
          onChange={(e) => setPurpose(e.target.value)}
          placeholder="e.g., Vehicle repair, Medical emergency"
          className="input-field"
        />
      </div>

      <button
        id="btn-preview-large-expense"
        onClick={() => {
          if (!amount || parseFloat(amount) <= 0) { toast.error('Enter a valid amount'); return }
          if (!purpose.trim()) { toast.error('Describe the purpose'); return }
          previewMutation.mutate()
        }}
        disabled={previewMutation.isPending}
        className="btn-primary"
      >
        {previewMutation.isPending ? 'Analysing...' : 'See Impact on Safety Wallet →'}
      </button>
    </div>
  )
}
