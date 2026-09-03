import { useState } from 'react'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { useNavigate } from 'react-router-dom'
import { ArrowLeft, Shield } from 'lucide-react'
import { paymentAPI } from '../lib/api'
import toast from 'react-hot-toast'

const CATEGORIES = [
  { key: 'food', label: 'Food & Groceries', emoji: '🍛' },
  { key: 'fuel', label: 'Fuel', emoji: '⛽' },
  { key: 'education', label: 'Education', emoji: '📚' },
  { key: 'entertainment', label: 'Entertainment', emoji: '🎬' },
  { key: 'shopping', label: 'Shopping', emoji: '🛒' },
  { key: 'family', label: 'Family', emoji: '👨‍👩‍👧' },
  { key: 'healthcare', label: 'Healthcare', emoji: '🏥' },
  { key: 'rent', label: 'Rent', emoji: '🏠' },
  { key: 'bills', label: 'Bills', emoji: '📄' },
  { key: 'other', label: 'Other', emoji: '💳' },
]

type Step = 'input' | 'preview' | 'confirm' | 'success'

export default function PaymentPage() {
  const navigate = useNavigate()
  const queryClient = useQueryClient()

  const [step, setStep] = useState<Step>('input')
  const [amount, setAmount] = useState('')
  const [category, setCategory] = useState('food')
  const [description, setDescription] = useState('')
  const [preview, setPreview] = useState<any>(null)
  const [saveConsent, setSaveConsent] = useState<boolean | null>(null)
  const [result, setResult] = useState<any>(null)

  const previewMutation = useMutation({
    mutationFn: () => paymentAPI.preview(parseFloat(amount), category),
    onSuccess: (res) => {
      setPreview(res.data)
      setSaveConsent(null)
      setStep('preview')
    },
    onError: () => toast.error('Could not load payment preview'),
  })

  const confirmMutation = useMutation({
    mutationFn: () =>
      paymentAPI.confirm({
        amount: parseFloat(amount),
        category,
        save_consent: saveConsent === true,
        description,
      }),
    onSuccess: (res) => {
      setResult(res.data)
      setStep('success')
      queryClient.invalidateQueries({ queryKey: ['dashboard'] })
      queryClient.invalidateQueries({ queryKey: ['wallets'] })
    },
    onError: (err: any) => {
      const msg = err.response?.data?.detail?.message || 'Payment failed'
      toast.error(msg)
    },
  })

  if (step === 'success' && result) {
    return (
      <div className="min-h-dvh bg-levelly-bg flex flex-col px-5 pt-12 animate-fade-in">
        <div className="flex-1 flex flex-col items-center justify-center text-center">
          <div className="w-20 h-20 bg-emerald-100 rounded-full flex items-center justify-center mb-5 animate-bounce-soft">
            <span className="text-4xl">✅</span>
          </div>
          <h2 className="text-2xl font-bold text-gray-900 mb-2">Payment Done</h2>
          <p className="text-gray-500 mb-6">
            ₹{result.payment_amount?.toLocaleString('en-IN')} for {category}
          </p>

          {result.save_amount > 0 && (
            <div className="w-full max-w-sm bg-emerald-50 border border-emerald-200 rounded-2xl p-5 mb-6">
              <div className="text-3xl mb-2">🐷</div>
              <p className="font-semibold text-emerald-800">Save-at-Pay Complete!</p>
              <p className="text-emerald-600 text-2xl font-bold mt-1">
                +₹{result.save_amount?.toLocaleString('en-IN')}
              </p>
              <p className="text-emerald-600 text-sm mt-1">
                Added to Safety Wallet
              </p>
              <div className="mt-3">
                <p className="text-xs text-emerald-700">
                  Safety Wallet: {result.safety_wallet_progress?.toFixed(0)}% of target
                </p>
                <div className="progress-bar mt-1">
                  <div className="progress-fill" style={{ width: `${result.safety_wallet_progress}%` }} />
                </div>
              </div>
            </div>
          )}

          <div className="w-full max-w-sm bg-white rounded-2xl p-4 mb-6 shadow-card">
            <div className="flex justify-between text-sm mb-1">
              <span className="text-gray-500">Daily Wallet</span>
              <span className="font-semibold">₹{result.daily_wallet_balance?.toLocaleString('en-IN')}</span>
            </div>
            {result.save_amount > 0 && (
              <div className="flex justify-between text-sm">
                <span className="text-gray-500">Safety Wallet</span>
                <span className="font-semibold text-emerald-600">₹{result.safety_wallet_balance?.toLocaleString('en-IN')}</span>
              </div>
            )}
          </div>

          <button
            onClick={() => { setStep('input'); setAmount(''); setSaveConsent(null); setPreview(null) }}
            className="btn-primary max-w-sm"
          >
            Make Another Payment
          </button>
          <button onClick={() => navigate('/')} className="btn-ghost max-w-sm mt-2">
            Back to Home
          </button>
        </div>
      </div>
    )
  }

  if (step === 'preview' && preview) {
    const saveSuggested = preview.save_suggestion_available && preview.suggested_save_amount > 0

    return (
      <div className="min-h-dvh bg-levelly-bg px-5 pt-12 animate-fade-in">
        <button onClick={() => setStep('input')} className="flex items-center gap-2 text-gray-600 mb-5">
          <ArrowLeft className="w-4 h-4" /> Back
        </button>

        <h2 className="text-xl font-bold text-gray-900 mb-5">Payment Preview</h2>

        {/* Payment amount */}
        <div className="card mb-4">
          <div className="flex justify-between items-center">
            <span className="text-gray-500">Payment Amount</span>
            <span className="text-2xl font-bold">₹{parseFloat(amount).toLocaleString('en-IN')}</span>
          </div>
          <div className="flex justify-between items-center mt-2">
            <span className="text-gray-500">Category</span>
            <span className="text-gray-700 capitalize">{category}</span>
          </div>
        </div>

        {/* Save-at-Pay suggestion */}
        {saveSuggested ? (
          <div className="mb-4">
            <div className="bg-emerald-50 border-2 border-emerald-200 rounded-2xl p-5">
              <div className="flex items-center gap-2 mb-3">
                <span className="text-2xl">🐷</span>
                <div>
                  <p className="font-bold text-emerald-800">Save-at-Pay Suggestion</p>
                  <p className="text-xs text-emerald-600">{preview.suggested_percentage}% of payment</p>
                </div>
              </div>

              <div className="flex items-end justify-between mb-4">
                <div>
                  <p className="text-xs text-emerald-600">Suggested save amount</p>
                  <p className="text-3xl font-bold text-emerald-700">
                    +₹{preview.suggested_save_amount?.toLocaleString('en-IN')}
                  </p>
                </div>
                <div className="text-right">
                  <p className="text-xs text-gray-500">Safety Wallet</p>
                  <p className="text-sm font-bold text-gray-700">
                    ₹{(preview.safety_wallet_balance + preview.suggested_save_amount).toLocaleString('en-IN')}
                  </p>
                  <p className="text-xs text-gray-400">after saving</p>
                </div>
              </div>

              <p className="text-xs text-emerald-600 mb-3">
                You choose whether to save. LEVELLY never forces it.
              </p>

              <div className="grid grid-cols-2 gap-3">
                <button
                  id="btn-save-yes"
                  onClick={() => { setSaveConsent(true); setStep('confirm') }}
                  className="bg-emerald-600 hover:bg-emerald-700 text-white font-bold py-3.5 rounded-xl text-sm transition-all"
                >
                  Yes, Save ₹{preview.suggested_save_amount?.toLocaleString('en-IN')}
                </button>
                <button
                  id="btn-save-no"
                  onClick={() => { setSaveConsent(false); setStep('confirm') }}
                  className="bg-white border-2 border-gray-200 text-gray-600 font-semibold py-3.5 rounded-xl text-sm transition-all"
                >
                  Pay Without Saving
                </button>
              </div>
            </div>
          </div>
        ) : (
          <div className="card mb-4 bg-gray-50">
            <p className="text-gray-600 text-sm text-center">
              {preview.distress_level_applied !== 'LOW'
                ? 'Save-at-Pay paused — LEVELLY is protecting your liquidity during financial pressure.'
                : 'No save suggestion for this category.'}
            </p>
            <button
              onClick={() => { setSaveConsent(false); setStep('confirm') }}
              className="btn-primary mt-3"
            >
              Proceed with Payment
            </button>
          </div>
        )}
      </div>
    )
  }

  if (step === 'confirm') {
    const finalSaveAmount = saveConsent && preview ? preview.suggested_save_amount : 0
    const totalDebit = parseFloat(amount) + finalSaveAmount

    return (
      <div className="min-h-dvh bg-levelly-bg px-5 pt-12 animate-fade-in">
        <button onClick={() => setStep('preview')} className="flex items-center gap-2 text-gray-600 mb-5">
          <ArrowLeft className="w-4 h-4" /> Back
        </button>
        <h2 className="text-xl font-bold mb-5">Confirm Payment</h2>

        <div className="card mb-4">
          <div className="space-y-3">
            {[
              { label: 'Payment', value: `₹${parseFloat(amount).toLocaleString('en-IN')}` },
              saveConsent && { label: 'Save-at-Pay', value: `+₹${finalSaveAmount?.toLocaleString('en-IN')}` },
              { label: 'Category', value: category },
            ].filter(Boolean).map((row: any, i) => (
              <div key={i} className="flex justify-between">
                <span className="text-gray-500">{row.label}</span>
                <span className={`font-semibold ${row.label === 'Save-at-Pay' ? 'text-emerald-600' : 'text-gray-900'}`}>
                  {row.value}
                </span>
              </div>
            ))}
            <div className="border-t pt-3 flex justify-between">
              <span className="font-semibold text-gray-700">Total from Daily Wallet</span>
              <span className="font-bold text-gray-900 text-lg">₹{totalDebit.toLocaleString('en-IN')}</span>
            </div>
          </div>
        </div>

        {saveConsent && (
          <div className="mb-4 p-3 bg-emerald-50 rounded-xl border border-emerald-200 flex items-center gap-2">
            <Shield className="w-4 h-4 text-emerald-600" />
            <p className="text-sm text-emerald-700">
              ₹{finalSaveAmount?.toLocaleString('en-IN')} will be added to your Safety Wallet
            </p>
          </div>
        )}

        <button
          id="btn-confirm-payment"
          onClick={() => confirmMutation.mutate()}
          disabled={confirmMutation.isPending}
          className="btn-primary"
        >
          {confirmMutation.isPending ? 'Processing...' : 'Confirm Payment'}
        </button>
        <button onClick={() => navigate('/')} className="btn-ghost mt-2">
          Cancel
        </button>
      </div>
    )
  }

  // Input step
  return (
    <div className="min-h-dvh bg-levelly-bg px-5 pt-12 animate-fade-in">
      <button onClick={() => navigate(-1)} className="flex items-center gap-2 text-gray-600 mb-5">
        <ArrowLeft className="w-4 h-4" /> Back
      </button>
      <h1 className="text-2xl font-bold text-gray-900 mb-1">Make Payment</h1>
      <p className="text-gray-500 text-sm mb-6">Save-at-Pay: build your Safety Wallet as you pay</p>

      {/* Amount input */}
      <div className="card mb-4">
        <label className="text-sm font-medium text-gray-600 mb-2 block">Payment Amount (₹)</label>
        <div className="flex items-center gap-2">
          <span className="text-3xl font-bold text-gray-400">₹</span>
          <input
            id="payment-amount"
            type="number"
            value={amount}
            onChange={(e) => setAmount(e.target.value)}
            placeholder="0"
            min="1"
            className="flex-1 text-4xl font-bold text-gray-900 focus:outline-none bg-transparent"
          />
        </div>
        {/* Quick amounts */}
        <div className="flex gap-2 mt-3">
          {[100, 200, 500, 1000].map((v) => (
            <button
              key={v}
              onClick={() => setAmount(String(v))}
              className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-all
                ${amount === String(v) ? 'bg-emerald-600 text-white' : 'bg-gray-100 text-gray-600 hover:bg-gray-200'}
              `}
            >
              ₹{v}
            </button>
          ))}
        </div>
      </div>

      {/* Category */}
      <div className="card mb-4">
        <p className="text-sm font-medium text-gray-600 mb-3">Category</p>
        <div className="grid grid-cols-2 gap-2">
          {CATEGORIES.map(({ key, label, emoji }) => (
            <button
              key={key}
              onClick={() => setCategory(key)}
              className={`flex items-center gap-2 p-3 rounded-xl text-left transition-all
                ${category === key ? 'bg-emerald-600 text-white' : 'bg-gray-50 hover:bg-gray-100 text-gray-700'}
              `}
            >
              <span>{emoji}</span>
              <span className="text-sm font-medium">{label}</span>
            </button>
          ))}
        </div>
      </div>

      {/* Description */}
      <div className="card mb-6">
        <label className="text-sm font-medium text-gray-600 mb-2 block">Description (optional)</label>
        <input
          type="text"
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          placeholder="e.g., Lunch, Petrol, Monthly rent"
          className="input-field"
        />
      </div>

      <button
        id="btn-preview-payment"
        onClick={() => {
          if (!amount || parseFloat(amount) <= 0) {
            toast.error('Enter a valid amount')
            return
          }
          previewMutation.mutate()
        }}
        disabled={previewMutation.isPending}
        className="btn-primary"
      >
        {previewMutation.isPending ? 'Loading...' : 'Preview with Save Suggestion →'}
      </button>
    </div>
  )
}
