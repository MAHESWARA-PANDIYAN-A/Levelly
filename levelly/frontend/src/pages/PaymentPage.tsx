import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useNavigate } from 'react-router-dom'
import {
  ArrowLeft,
  QrCode,
  Building2,
  Sparkles,
  ChevronRight,
  CheckCircle2,
  AlertTriangle,
  CreditCard,
  Zap,
  RefreshCw,
} from 'lucide-react'
import { paymentAPI } from '../lib/api'
import toast from 'react-hot-toast'

const CATEGORIES = [
  { key: 'food', label: 'Food & Grocery', emoji: '🍛' },
  { key: 'fuel', label: 'Fuel Station', emoji: '⛽' },
  { key: 'vehicle', label: 'Vehicle Repair', emoji: '🔧' },
  { key: 'healthcare', label: 'Healthcare & Meds', emoji: '🏥' },
  { key: 'education', label: 'Education', emoji: '📚' },
  { key: 'entertainment', label: 'Entertainment', emoji: '🎬' },
  { key: 'shopping', label: 'Shopping', emoji: '🛒' },
  { key: 'bills', label: 'Bills & Utilities', emoji: '📄' },
  { key: 'other', label: 'Other Spends', emoji: '💳' },
]

type Step = 'scan_or_select' | 'amount_input' | 'preview' | 'success'

const formatINR = (amount: number) =>
  new Intl.NumberFormat('en-IN', { style: 'currency', currency: 'INR', maximumFractionDigits: 0 }).format(amount)

export default function PaymentPage() {
  const navigate = useNavigate()
  const queryClient = useQueryClient()

  const [step, setStep] = useState<Step>('scan_or_select')
  const [selectedMerchant, setSelectedMerchant] = useState<any>(null)
  const [amount, setAmount] = useState('')
  const [category, setCategory] = useState('food')
  const [description, setDescription] = useState('')
  const [qrCodeInput, setQrCodeInput] = useState('')
  const [showQRScannerModal, setShowQRScannerModal] = useState(false)
  const [saveConsent, setSaveConsent] = useState(true)
  const [preview, setPreview] = useState<any>(null)
  const [result, setResult] = useState<any>(null)
  const [animatingCoin, setAnimatingCoin] = useState(false)

  // Fetch Linked Bank/UPI Account
  const { data: linkedAccount } = useQuery({
    queryKey: ['linked-account'],
    queryFn: () => paymentAPI.getLinkedAccount().then(r => r.data),
  })

  // Fetch Verified Merchants
  const { data: merchants } = useQuery({
    queryKey: ['verified-merchants'],
    queryFn: () => paymentAPI.getMerchants().then(r => r.data),
  })

  // Scan QR mutation
  const scanMutation = useMutation({
    mutationFn: (payload: string) => paymentAPI.scanQR(payload),
    onSuccess: (res) => {
      setSelectedMerchant(res.data.merchant)
      setCategory(res.data.default_category || 'food')
      setShowQRScannerModal(false)
      setStep('amount_input')
      toast.success(`Merchant verified: ${res.data.merchant.name}`)
    },
    onError: () => toast.error('Could not parse QR code. Selected demo merchant instead.'),
  })

  // Preview mutation (backend authoritative calculation)
  const previewMutation = useMutation({
    mutationFn: () =>
      paymentAPI.preview({
        merchant_id: selectedMerchant?.id,
        merchant_name: selectedMerchant?.name,
        merchant_upi_id: selectedMerchant?.upi_id,
        amount: parseFloat(amount),
        category,
      }),
    onSuccess: (res) => {
      setPreview(res.data)
      setStep('preview')
    },
    onError: (err: any) => {
      const msg = err.response?.data?.detail?.message || 'Failed to calculate payment preview'
      toast.error(msg)
    },
  })

  // Confirm UPI payment mutation
  const confirmMutation = useMutation({
    mutationFn: () =>
      paymentAPI.confirm({
        merchant_id: selectedMerchant?.id,
        merchant_name: selectedMerchant?.name,
        merchant_upi_id: selectedMerchant?.upi_id,
        amount: parseFloat(amount),
        category,
        save_consent: saveConsent,
        suggested_save_amount: preview?.suggested_save_amount,
        description: description || `Payment to ${selectedMerchant?.name || 'Merchant'}`,
        idempotency_key: `IDEMP_${Date.now()}`,
      }),
    onSuccess: (res) => {
      setResult(res.data)
      setAnimatingCoin(true)
      setTimeout(() => {
        setAnimatingCoin(false)
        setStep('success')
        queryClient.invalidateQueries({ queryKey: ['safety-wallet'] })
        queryClient.invalidateQueries({ queryKey: ['wallets'] })
        queryClient.invalidateQueries({ queryKey: ['dashboard'] })
        queryClient.invalidateQueries({ queryKey: ['recent-payments'] })
      }, 700)
    },
    onError: (err: any) => {
      const msg = err.response?.data?.detail?.message || 'UPI Payment execution failed'
      toast.error(msg)
    },
  })

  const handleSelectMerchant = (m: any) => {
    setSelectedMerchant(m)
    setCategory(m.normalized_category || 'food')
    setStep('amount_input')
  }

  const handleTriggerPreview = () => {
    const val = parseFloat(amount)
    if (!val || val <= 0) {
      toast.error('Please enter a valid amount')
      return
    }
    previewMutation.mutate()
  }

  // ============================================================
  // STEP 4: SUCCESS RECEIPT
  // ============================================================
  if (step === 'success' && result) {
    const isSaveAdded = result.save_amount > 0
    return (
      <div className="px-5 pt-4 pb-12 animate-fade-in">
        <div className="flex flex-col items-center justify-center text-center">
          {/* Animated Success Badge */}
          <div className="w-20 h-20 bg-emerald-100 rounded-full flex items-center justify-center mb-4 border-4 border-emerald-50 shadow-inner">
            <CheckCircle2 className="w-10 h-10 text-emerald-600 animate-scale-up" />
          </div>

          <h1 className="text-2xl font-black text-slate-900 tracking-tight mb-1">
            Payment Successful!
          </h1>
          <p className="text-xs text-slate-500 font-medium mb-5">
            Paid directly via {linkedAccount?.bank_name || 'HDFC Bank'} ({linkedAccount?.upi_id || 'arjun@upi'})
          </p>

          {/* Amount Box */}
          <div className="w-full max-w-sm bg-gradient-to-br from-slate-900 via-slate-950 to-emerald-950 rounded-3xl p-6 text-white border border-emerald-800/30 shadow-xl mb-4 text-left">
            <div className="flex items-center justify-between text-xs text-slate-400 mb-2">
              <span>Merchant Settled</span>
              <span className="font-mono text-[10px] text-emerald-400">{result.provider_transaction_id}</span>
            </div>
            <div className="text-3xl font-black tracking-tight text-white mb-1">
              {formatINR(result.merchant_amount)}
            </div>
            <div className="text-xs text-emerald-200/80 font-medium">
              To: <span className="text-white font-bold">{result.merchant?.name || selectedMerchant?.name}</span>
            </div>

            {/* Save-at-Pay Breakdown */}
            {isSaveAdded ? (
              <div className="mt-4 pt-4 border-t border-slate-800/80 bg-emerald-950/40 -mx-6 -mb-6 p-6 rounded-b-3xl">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <span className="text-xl">🐷</span>
                    <div>
                      <p className="text-xs font-bold text-emerald-300">Save-at-Pay Boost</p>
                      <p className="text-[10px] text-emerald-400/80">Credited to Safety Wallet</p>
                    </div>
                  </div>
                  <span className="text-lg font-black text-emerald-300">
                    +{formatINR(result.save_amount)}
                  </span>
                </div>
                <div className="mt-3">
                  <div className="flex justify-between text-[11px] text-emerald-200/70 mb-1">
                    <span>New Safety Reserve</span>
                    <span className="font-bold text-white">{formatINR(result.safety_wallet_balance)}</span>
                  </div>
                  <div className="h-2 bg-slate-800 rounded-full overflow-hidden">
                    <div
                      className="h-full bg-emerald-400 rounded-full transition-all duration-700"
                      style={{ width: `${Math.min(100, result.safety_wallet_progress || 0)}%` }}
                    />
                  </div>
                </div>
              </div>
            ) : (
              <div className="mt-4 pt-3 border-t border-slate-800/80 text-[11px] text-slate-400">
                Save-at-Pay skipped for this payment.
              </div>
            )}
          </div>

          {/* Action Buttons */}
          <div className="w-full max-w-sm space-y-2.5">
            <button
              onClick={() => {
                setStep('scan_or_select')
                setAmount('')
                setSelectedMerchant(null)
                setPreview(null)
                setResult(null)
              }}
              className="w-full py-3.5 bg-emerald-700 hover:bg-emerald-800 text-white font-bold rounded-2xl text-xs transition shadow-md shadow-emerald-700/20 active:scale-[0.98]"
            >
              Make Another Payment
            </button>
            <button
              onClick={() => navigate('/safety')}
              className="w-full py-3.5 bg-white hover:bg-slate-50 text-slate-800 font-bold rounded-2xl text-xs border border-slate-200 transition active:scale-[0.98]"
            >
              View Safety Wallet
            </button>
            <button
              onClick={() => navigate('/')}
              className="w-full py-2 text-xs font-semibold text-slate-400 hover:text-slate-600 transition"
            >
              Return Home
            </button>
          </div>
        </div>
      </div>
    )
  }

  // ============================================================
  // STEP 3: AUTHORITATIVE PREVIEW & CONSENT
  // ============================================================
  if (step === 'preview' && preview) {
    const suggestedSave = preview.suggested_save_amount || 0
    const totalWithSave = preview.total_if_save || preview.amount
    const isLarge = preview.is_large_expense

    return (
      <div className="px-5 pt-2 pb-12 animate-fade-in">
        {/* Back header */}
        <div className="flex items-center gap-3 mb-4">
          <button
            onClick={() => setStep('amount_input')}
            className="p-2 rounded-xl bg-white border border-slate-200 text-slate-700 hover:bg-slate-50 transition"
          >
            <ArrowLeft className="w-4 h-4" />
          </button>
          <div>
            <h1 className="text-xl font-black text-slate-900">Confirm Payment</h1>
            <p className="text-xs text-slate-500 font-medium">Review amount & smart savings contribution</p>
          </div>
        </div>

        {/* Large Expense / Shock Buffer Warning if applicable */}
        {isLarge && (
          <div className="bg-amber-50 border border-amber-200 rounded-2xl p-4 mb-4 flex items-start gap-3">
            <AlertTriangle className="w-5 h-5 text-amber-600 shrink-0 mt-0.5" />
            <div>
              <p className="text-xs font-bold text-amber-900">Safety Buffer Check</p>
              <p className="text-[11px] text-amber-800 mt-0.5 leading-relaxed">
                This ₹{preview.amount.toLocaleString('en-IN')} payment equals {preview.buffer_impact_pct}% of your Safety Wallet reserve.
                We recommend checking if this is an essential expense.
              </p>
            </div>
          </div>
        )}

        {/* Merchant & Account Summary Card */}
        <div className="bg-white rounded-3xl p-5 border border-slate-200/80 shadow-sm mb-4">
          <div className="flex items-center justify-between pb-3 border-b border-slate-100">
            <div>
              <p className="text-[11px] text-slate-400 font-medium">Paying Merchant</p>
              <p className="text-base font-bold text-slate-900">{preview.merchant.name}</p>
              <p className="text-xs text-slate-500">{preview.merchant.upi_id}</p>
            </div>
            <div className="text-right">
              <span className="text-xs font-bold bg-slate-100 text-slate-700 px-2.5 py-1 rounded-full uppercase tracking-wider">
                {preview.category}
              </span>
            </div>
          </div>

          <div className="pt-3 flex items-center justify-between text-xs">
            <div className="flex items-center gap-2 text-slate-600">
              <Building2 className="w-4 h-4 text-emerald-700" />
              <span>{linkedAccount?.bank_name || 'HDFC Bank'} ({linkedAccount?.account_mask || '****4821'})</span>
            </div>
            <span className="text-emerald-700 font-bold">UPI Direct</span>
          </div>
        </div>

        {/* Smart Save-at-Pay Interactive Box */}
        <div className="relative overflow-hidden rounded-3xl bg-gradient-to-br from-emerald-900 via-teal-950 to-slate-950 p-5 text-white border border-emerald-700/30 shadow-lg mb-5">
          <div className="flex items-center justify-between mb-3">
            <div className="flex items-center gap-2">
              <span className="text-2xl animate-piggy-wobble">🐷</span>
              <div>
                <p className="text-sm font-black text-white flex items-center gap-1">
                  Smart Save-at-Pay
                  <span className="bg-emerald-400/20 text-emerald-300 text-[10px] px-2 py-0.5 rounded-full font-bold">
                    +{preview.suggested_percentage}%
                  </span>
                </p>
                <p className="text-[10px] text-emerald-200/70">Autonomous financial buffer growth</p>
              </div>
            </div>

            {/* Consent Toggle */}
            <button
              onClick={() => setSaveConsent(!saveConsent)}
              className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors focus:outline-none ${
                saveConsent ? 'bg-emerald-500' : 'bg-slate-700'
              }`}
            >
              <span
                className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                  saveConsent ? 'translate-x-6' : 'translate-x-1'
                }`}
              />
            </button>
          </div>

          <p className="text-xs text-emerald-100/90 leading-relaxed mb-4">
            {saveConsent
              ? `Round up this spend with ₹${suggestedSave} saved directly into your Safety Wallet.`
              : 'Save-at-Pay turned off. Only merchant charge will be processed.'}
          </p>

          {/* Breakdown Table */}
          <div className="bg-black/30 rounded-2xl p-3.5 space-y-2 text-xs border border-white/10">
            <div className="flex justify-between text-slate-300">
              <span>Merchant bill:</span>
              <span className="font-semibold text-white">{formatINR(preview.amount)}</span>
            </div>
            <div className="flex justify-between text-emerald-300">
              <span className="flex items-center gap-1">
                <Sparkles className="w-3.5 h-3.5" /> Safety Reserve deposit:
              </span>
              <span className="font-bold">
                {saveConsent ? `+${formatINR(suggestedSave)}` : '₹0'}
              </span>
            </div>
            <div className="pt-2 border-t border-white/10 flex justify-between font-bold text-sm text-white">
              <span>Total Bank Impact:</span>
              <span className="text-emerald-400">
                {formatINR(saveConsent ? totalWithSave : preview.amount)}
              </span>
            </div>
          </div>
        </div>

        {/* Safety Wallet Impact Card */}
        <div className="bg-white rounded-2xl p-4 border border-slate-200/80 shadow-sm mb-6">
          <div className="flex items-center justify-between text-xs mb-1.5 font-semibold">
            <span className="text-slate-600">Safety Wallet Goal</span>
            <span className="text-emerald-700">
              {formatINR(preview.safety_wallet_balance + (saveConsent ? suggestedSave : 0))} / {formatINR(preview.safety_wallet_target)}
            </span>
          </div>
          <div className="h-2 bg-slate-100 rounded-full overflow-hidden">
            <div
              className="h-full bg-gradient-to-r from-emerald-500 to-teal-400 rounded-full transition-all duration-500"
              style={{
                width: `${Math.min(
                  100,
                  ((preview.safety_wallet_balance + (saveConsent ? suggestedSave : 0)) / preview.safety_wallet_target) * 100
                )}%`,
              }}
            />
          </div>
        </div>

        {/* Action Button */}
        <button
          onClick={() => confirmMutation.mutate()}
          disabled={confirmMutation.isPending || animatingCoin}
          className="w-full py-4 bg-emerald-700 hover:bg-emerald-800 text-white font-extrabold rounded-2xl text-sm transition shadow-lg shadow-emerald-700/20 active:scale-[0.98] disabled:opacity-60 flex items-center justify-center gap-2"
        >
          {confirmMutation.isPending || animatingCoin ? (
            <>
              <RefreshCw className="w-4 h-4 animate-spin" /> Processing UPI Payment...
            </>
          ) : (
            <>
              Authorize Payment ({formatINR(saveConsent ? totalWithSave : preview.amount)}) →
            </>
          )}
        </button>
      </div>
    )
  }

  // ============================================================
  // STEP 2: AMOUNT & CATEGORY INPUT
  // ============================================================
  if (step === 'amount_input' && selectedMerchant) {
    return (
      <div className="px-5 pt-2 pb-12 animate-fade-in">
        <div className="flex items-center gap-3 mb-4">
          <button
            onClick={() => setStep('scan_or_select')}
            className="p-2 rounded-xl bg-white border border-slate-200 text-slate-700 hover:bg-slate-50 transition"
          >
            <ArrowLeft className="w-4 h-4" />
          </button>
          <div>
            <h1 className="text-xl font-black text-slate-900">Enter Payment Amount</h1>
            <p className="text-xs text-slate-500 font-medium">To {selectedMerchant.name}</p>
          </div>
        </div>

        {/* Selected Merchant Banner */}
        <div className="bg-white rounded-2xl p-4 border border-slate-200/80 shadow-sm mb-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-emerald-50 text-emerald-700 flex items-center justify-center font-bold text-sm">
              {selectedMerchant.name.slice(0, 2).toUpperCase()}
            </div>
            <div>
              <p className="text-sm font-bold text-slate-900">{selectedMerchant.name}</p>
              <p className="text-xs text-slate-400">{selectedMerchant.upi_id}</p>
            </div>
          </div>
          <span className="text-[10px] font-bold bg-emerald-50 text-emerald-700 border border-emerald-200 px-2 py-0.5 rounded-full">
            Verified
          </span>
        </div>

        {/* Amount Input */}
        <div className="bg-white rounded-3xl p-6 border border-slate-200/80 shadow-sm mb-5 text-center">
          <p className="text-xs text-slate-400 font-medium mb-2">Payment Amount (INR)</p>
          <div className="relative inline-flex items-center justify-center mb-4">
            <span className="text-3xl font-bold text-slate-400 mr-1">₹</span>
            <input
              type="number"
              value={amount}
              onChange={(e) => setAmount(e.target.value)}
              placeholder="0"
              autoFocus
              className="text-4xl font-black text-slate-900 w-44 text-center focus:outline-none bg-transparent"
            />
          </div>

          {/* Quick preset chips */}
          <div className="flex justify-center gap-2">
            {[100, 250, 500, 1000, 2000].map((preset) => (
              <button
                key={preset}
                type="button"
                onClick={() => setAmount(preset.toString())}
                className="px-3 py-1.5 bg-slate-100 hover:bg-emerald-50 hover:text-emerald-700 text-slate-700 text-xs font-semibold rounded-xl transition"
              >
                ₹{preset}
              </button>
            ))}
          </div>
        </div>

        {/* Category Selection */}
        <div className="mb-6">
          <p className="text-xs font-bold text-slate-700 uppercase tracking-wider mb-2.5">
            Select Spending Category
          </p>
          <div className="grid grid-cols-3 gap-2">
            {CATEGORIES.map((c) => (
              <button
                key={c.key}
                type="button"
                onClick={() => setCategory(c.key)}
                className={`p-2.5 rounded-2xl border text-left transition flex flex-col items-center text-center gap-1 ${
                  category === c.key
                    ? 'border-emerald-600 bg-emerald-50/70 text-emerald-900 shadow-sm ring-1 ring-emerald-600'
                    : 'border-slate-200 bg-white text-slate-700 hover:bg-slate-50'
                }`}
              >
                <span className="text-xl">{c.emoji}</span>
                <span className="text-[11px] font-bold leading-tight">{c.label}</span>
              </button>
            ))}
          </div>
        </div>

        {/* Note / Description */}
        <div className="mb-6">
          <input
            type="text"
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            placeholder="Add a payment note (optional)"
            className="w-full px-4 py-3 bg-white border border-slate-200 rounded-2xl text-xs text-slate-800 placeholder-slate-400 focus:outline-none focus:border-emerald-600"
          />
        </div>

        {/* Continue Button */}
        <button
          onClick={handleTriggerPreview}
          disabled={previewMutation.isPending || !amount || parseFloat(amount) <= 0}
          className="w-full py-4 bg-emerald-700 hover:bg-emerald-800 text-white font-extrabold rounded-2xl text-sm transition shadow-lg shadow-emerald-700/20 active:scale-[0.98] disabled:opacity-50 flex items-center justify-center gap-2"
        >
          {previewMutation.isPending ? 'Calculating Smart Savings...' : 'Continue to Preview →'}
        </button>
      </div>
    )
  }

  // ============================================================
  // STEP 1: SCAN OR SELECT MERCHANT
  // ============================================================
  return (
    <div className="px-5 pt-2 pb-12 animate-fade-in">
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <div>
          <h1 className="text-2xl font-black text-slate-900 tracking-tight">LEVELLY Pay</h1>
          <p className="text-xs text-slate-500 font-medium">Direct Bank / UPI payments with Smart Save-at-Pay</p>
        </div>
        <div className="flex items-center gap-1.5 bg-emerald-50 border border-emerald-200/60 px-2.5 py-1 rounded-full">
          <Zap className="w-3.5 h-3.5 text-emerald-700" />
          <span className="text-[11px] font-bold text-emerald-800">Instant UPI</span>
        </div>
      </div>

      {/* Linked Source Banner */}
      <div className="bg-slate-900 text-white rounded-3xl p-4 shadow-md mb-5 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-xl bg-emerald-500/20 border border-emerald-500/30 flex items-center justify-center text-emerald-400">
            <CreditCard className="w-5 h-5" />
          </div>
          <div>
            <p className="text-[10px] text-slate-400 font-medium uppercase tracking-wider">Direct Payment Source</p>
            <p className="text-xs font-bold text-white">
              {linkedAccount?.bank_name || 'HDFC Bank'} ({linkedAccount?.account_mask || '****4821'})
            </p>
            <p className="text-[10px] text-emerald-400 font-mono">{linkedAccount?.upi_id || 'arjun@upi'}</p>
          </div>
        </div>
        <span className="text-[10px] font-bold bg-emerald-950 text-emerald-300 border border-emerald-800 px-2.5 py-1 rounded-full">
          Connected
        </span>
      </div>

      {/* Scan QR Hero Card */}
      <div
        onClick={() => setShowQRScannerModal(true)}
        className="cursor-pointer group relative overflow-hidden rounded-3xl bg-gradient-to-br from-emerald-800 to-teal-900 p-6 text-white shadow-xl shadow-emerald-900/20 border border-emerald-700/40 mb-5 transition hover:shadow-emerald-900/30 active:scale-[0.99]"
      >
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3.5">
            <div className="w-14 h-14 bg-white/10 rounded-2xl flex items-center justify-center backdrop-blur-md border border-white/20 group-hover:bg-white/20 transition">
              <QrCode className="w-8 h-8 text-emerald-300" />
            </div>
            <div>
              <p className="text-base font-extrabold text-white">Scan Any UPI QR Code</p>
              <p className="text-xs text-emerald-200/80 mt-0.5">Pay merchants & auto-save to Safety Wallet</p>
            </div>
          </div>
          <ChevronRight className="w-5 h-5 text-emerald-300 group-hover:translate-x-1 transition" />
        </div>
      </div>

      {/* Verified Merchants Quick Select */}
      <div className="mb-6">
        <div className="flex items-center justify-between mb-3">
          <h2 className="text-sm font-bold text-slate-800 uppercase tracking-wider">
            Verified Merchants (Demo)
          </h2>
          <span className="text-xs text-slate-400 font-medium">Tap to pay</span>
        </div>

        <div className="space-y-2.5">
          {merchants && merchants.length > 0 ? (
            merchants.map((m: any) => (
              <div
                key={m.id}
                onClick={() => handleSelectMerchant(m)}
                className="cursor-pointer bg-white hover:bg-slate-50 border border-slate-200/80 rounded-2xl p-3.5 shadow-sm transition flex items-center justify-between active:scale-[0.99]"
              >
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-xl bg-emerald-50 text-emerald-700 font-bold flex items-center justify-center text-sm">
                    {m.name.slice(0, 2).toUpperCase()}
                  </div>
                  <div>
                    <p className="text-xs font-bold text-slate-900">{m.name}</p>
                    <p className="text-[10px] text-slate-400">{m.category} • {m.upi_id}</p>
                  </div>
                </div>
                <div className="flex items-center gap-1.5 text-xs font-bold text-emerald-700">
                  <span>Pay</span>
                  <ChevronRight className="w-4 h-4 text-emerald-600" />
                </div>
              </div>
            ))
          ) : (
            <div className="p-4 bg-slate-50 rounded-2xl text-center text-xs text-slate-400">
              Loading verified merchants...
            </div>
          )}
        </div>
      </div>

      {/* QR Code Scanner Simulation Modal */}
      {showQRScannerModal && (
        <div className="fixed inset-0 bg-black/70 backdrop-blur-sm z-50 flex items-center justify-center p-5">
          <div className="bg-white w-full max-w-sm rounded-3xl p-6 shadow-2xl border border-slate-100 animate-scale-up">
            <h3 className="text-lg font-bold text-slate-900 mb-1">Scan or Enter UPI QR</h3>
            <p className="text-xs text-slate-500 mb-4">
              Enter any standard NPCI UPI intent string (upi://pay...) or merchant ID.
            </p>

            {/* Camera Viewfinder Mock */}
            <div className="relative w-full h-44 bg-slate-950 rounded-2xl flex flex-col items-center justify-center border-2 border-dashed border-emerald-500/40 mb-4 overflow-hidden">
              <div className="w-32 h-32 border-2 border-emerald-400 rounded-xl flex items-center justify-center relative">
                <div className="w-full h-0.5 bg-emerald-400 shadow-sm shadow-emerald-400 animate-pulse absolute" />
                <QrCode className="w-14 h-14 text-slate-700" />
              </div>
              <p className="text-[10px] text-emerald-300/80 mt-2">Aiming Camera at UPI QR</p>
            </div>

            <div className="mb-4">
              <label className="text-[11px] font-bold text-slate-600 mb-1 block">
                QR Payload / UPI ID
              </label>
              <input
                type="text"
                value={qrCodeInput}
                onChange={(e) => setQrCodeInput(e.target.value)}
                placeholder="upi://pay?pa=srikrishna@upi&pn=Sri%20Krishna"
                className="w-full px-3.5 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-xs font-mono text-slate-900 focus:outline-none focus:border-emerald-600 focus:bg-white"
              />
            </div>

            {/* Quick Demo QR Presets */}
            <div className="flex gap-1.5 mb-4">
              <button
                type="button"
                onClick={() => setQrCodeInput('upi://pay?pa=srikrishna@upi&pn=Sri%20Krishna%20Supermarket')}
                className="text-[10px] bg-slate-100 hover:bg-slate-200 px-2 py-1 rounded-lg text-slate-700 font-semibold"
              >
                Food QR
              </button>
              <button
                type="button"
                onClick={() => setQrCodeInput('upi://pay?pa=cityfuel@upi&pn=City%20Fuel%20Station')}
                className="text-[10px] bg-slate-100 hover:bg-slate-200 px-2 py-1 rounded-lg text-slate-700 font-semibold"
              >
                Fuel QR
              </button>
              <button
                type="button"
                onClick={() => setQrCodeInput('upi://pay?pa=bikecare@upi&pn=BikeCare%20Service')}
                className="text-[10px] bg-slate-100 hover:bg-slate-200 px-2 py-1 rounded-lg text-slate-700 font-semibold"
              >
                Repair QR
              </button>
            </div>

            <div className="flex gap-2">
              <button
                onClick={() => setShowQRScannerModal(false)}
                className="flex-1 py-3 bg-slate-100 hover:bg-slate-200 text-slate-700 font-bold rounded-xl text-xs transition"
              >
                Cancel
              </button>
              <button
                onClick={() => {
                  const payload = qrCodeInput || 'upi://pay?pa=srikrishna@upi&pn=Sri%20Krishna%20Supermarket'
                  scanMutation.mutate(payload)
                }}
                disabled={scanMutation.isPending}
                className="flex-1 py-3 bg-emerald-700 hover:bg-emerald-800 text-white font-bold rounded-xl text-xs transition disabled:opacity-50"
              >
                {scanMutation.isPending ? 'Validating...' : 'Scan & Pay'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
