import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useNavigate, useParams } from 'react-router-dom'
import { ArrowLeft, AlertTriangle, TrendingUp, Shield, Info } from 'lucide-react'
import { investmentAPI } from '../lib/api'
import toast from 'react-hot-toast'

const formatINR = (amount: number) =>
  new Intl.NumberFormat('en-IN', { style: 'currency', currency: 'INR', maximumFractionDigits: 0 }).format(amount)

type ConsentStep = 'detail' | 'amount' | 'terms' | 'confirm' | 'success'

export default function InvestmentDetailPage() {
  const navigate = useNavigate()
  const { productId } = useParams()
  const queryClient = useQueryClient()

  const [step, setStep] = useState<ConsentStep>('detail')
  const [investAmount, setInvestAmount] = useState('')
  const [termsAccepted, setTermsAccepted] = useState(false)
  const [consentId, setConsentId] = useState<number | null>(null)
  const [orderResult, setOrderResult] = useState<any>(null)

  const { data: product, isLoading } = useQuery({
    queryKey: ['product', productId],
    queryFn: () => investmentAPI.productDetails(Number(productId)).then(r => r.data),
  })

  const { data: status } = useQuery({
    queryKey: ['invest-status'],
    queryFn: () => investmentAPI.status().then(r => r.data),
  })

  const consentMutation = useMutation({
    mutationFn: () => investmentAPI.createConsent({
      product_id: Number(productId),
      amount: parseFloat(investAmount),
      terms_accepted: true,
    }),
    onSuccess: (res) => {
      setConsentId(res.data.consent_id)
      setStep('confirm')
    },
    onError: (err: any) => toast.error(err.response?.data?.detail?.message || 'Error creating consent'),
  })

  const confirmMutation = useMutation({
    mutationFn: () => investmentAPI.confirmInvestment(consentId!),
    onSuccess: (res) => {
      setOrderResult(res.data)
      setStep('success')
      queryClient.invalidateQueries({ queryKey: ['invest-status'] })
    },
    onError: (err: any) => toast.error(err.response?.data?.detail?.message || 'Error confirming investment'),
  })

  if (status?.is_paused) {
    return (
      <div className="px-5 pt-12 pb-8 animate-fade-in">
        <button onClick={() => navigate(-1)} className="flex items-center gap-2 text-gray-600 mb-5">
          <ArrowLeft className="w-4 h-4" /> Back
        </button>
        <div className="card border-2 border-orange-200 bg-orange-50">
          <div className="flex items-center gap-2 mb-2">
            <Shield className="w-5 h-5 text-orange-600" />
            <p className="font-semibold text-orange-800">Investment Suggestions Paused</p>
          </div>
          <p className="text-orange-700 text-sm">{status.pause_reason}</p>
        </div>
      </div>
    )
  }

  if (step === 'success' && orderResult) {
    return (
      <div className="px-5 pt-12 pb-8 text-center animate-fade-in">
        <div className="w-20 h-20 bg-emerald-100 rounded-full flex items-center justify-center mx-auto mb-5">
          <TrendingUp className="w-10 h-10 text-emerald-600" />
        </div>
        <h2 className="text-2xl font-bold mb-2">Investment Submitted</h2>
        <p className="text-gray-500 mb-6">{orderResult.message}</p>

        <div className="card mb-4 text-left">
          <div className="space-y-2 text-sm">
            <div className="flex justify-between">
              <span className="text-gray-500">Product</span>
              <span className="font-medium">{orderResult.product_name}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-500">Amount</span>
              <span className="font-bold">{formatINR(orderResult.amount)}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-500">Status</span>
              <span className="text-emerald-600 font-medium capitalize">{orderResult.status}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-500">Partner Ref</span>
              <span className="font-mono text-xs">{orderResult.partner_order_id}</span>
            </div>
          </div>
        </div>

        <div className="card bg-gray-50 text-left mb-4">
          <div className="flex items-start gap-2">
            <Info className="w-4 h-4 text-gray-400 mt-0.5 flex-shrink-0" />
            <p className="text-xs text-gray-500">{orderResult.disclaimer}</p>
          </div>
        </div>

        <button onClick={() => navigate('/grow')} className="btn-primary">Back to Grow</button>
      </div>
    )
  }

  if (step === 'confirm') {
    return (
      <div className="px-5 pt-12 pb-8 animate-fade-in">
        <button onClick={() => setStep('terms')} className="flex items-center gap-2 text-gray-600 mb-5">
          <ArrowLeft className="w-4 h-4" /> Back
        </button>
        <h2 className="text-xl font-bold mb-2">Final Confirmation</h2>
        <p className="text-gray-500 text-sm mb-5">Please review before proceeding.</p>

        <div className="card mb-4">
          <div className="space-y-3 text-sm">
            <div className="flex justify-between">
              <span className="text-gray-500">Product</span>
              <span className="font-medium">{product?.name}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-500">Amount</span>
              <span className="font-bold text-lg">{formatINR(parseFloat(investAmount))}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-500">Risk Level</span>
              <span className={`font-medium ${product?.risk_level === 'LOW' ? 'text-green-600' : 'text-amber-600'}`}>
                {product?.risk_level}
              </span>
            </div>
          </div>
        </div>

        <div className="p-4 bg-amber-50 border border-amber-200 rounded-2xl mb-5 flex items-start gap-3">
          <AlertTriangle className="w-5 h-5 text-amber-600 flex-shrink-0 mt-0.5" />
          <div>
            <p className="font-semibold text-amber-800 text-sm">Investments involve risk</p>
            <p className="text-amber-700 text-xs mt-0.5">
              Past performance does not indicate future results. Please review product terms carefully.
            </p>
          </div>
        </div>

        <button
          id="btn-confirm-investment"
          onClick={() => confirmMutation.mutate()}
          disabled={confirmMutation.isPending}
          className="btn-primary mb-2"
        >
          {confirmMutation.isPending ? 'Submitting...' : 'Confirm Investment'}
        </button>
        <button onClick={() => navigate('/grow')} className="btn-ghost">Cancel</button>
      </div>
    )
  }

  if (step === 'amount') {
    return (
      <div className="px-5 pt-12 pb-8 animate-fade-in">
        <button onClick={() => setStep('detail')} className="flex items-center gap-2 text-gray-600 mb-5">
          <ArrowLeft className="w-4 h-4" /> Back
        </button>
        <h2 className="text-xl font-bold mb-5">Investment Amount</h2>
        <div className="card mb-4">
          <label className="text-sm text-gray-500 block mb-2">Amount (₹)</label>
          <div className="flex items-center gap-2">
            <span className="text-3xl text-gray-400 font-bold">₹</span>
            <input
              type="number"
              value={investAmount}
              onChange={(e) => setInvestAmount(e.target.value)}
              placeholder="0"
              className="flex-1 text-4xl font-bold text-gray-900 focus:outline-none bg-transparent"
              min={product?.min_investment || 500}
            />
          </div>
          <p className="text-xs text-gray-400 mt-2">
            Minimum: {formatINR(product?.min_investment || 500)}
          </p>
          {status?.available_for_investment > 0 && (
            <p className="text-xs text-emerald-600 mt-1">
              Available surplus: {formatINR(status.available_for_investment)}
            </p>
          )}
        </div>
        <button
          onClick={() => {
            if (!investAmount || parseFloat(investAmount) < (product?.min_investment || 500)) {
              toast.error(`Minimum investment is ${formatINR(product?.min_investment || 500)}`)
              return
            }
            setStep('terms')
          }}
          className="btn-primary"
        >
          Continue →
        </button>
      </div>
    )
  }

  if (step === 'terms') {
    return (
      <div className="px-5 pt-12 pb-8 animate-fade-in">
        <button onClick={() => setStep('amount')} className="flex items-center gap-2 text-gray-600 mb-5">
          <ArrowLeft className="w-4 h-4" /> Back
        </button>
        <h2 className="text-xl font-bold mb-2">Terms & Risks</h2>
        <p className="text-gray-500 text-sm mb-5">Please read before proceeding.</p>
        <div className="card mb-4 space-y-3 text-sm text-gray-600">
          <p>{product?.terms}</p>
          <p>{product?.tax_notes}</p>
          <p><span className="font-medium text-gray-700">Fees:</span> {product?.fees}</p>
          <div className="border-t pt-3">
            <p className="text-xs text-gray-500">
              LEVELLY facilitates the connection to the investment partner. 
              LEVELLY is not the investment manager and does not guarantee returns.
            </p>
          </div>
        </div>
        <label className="flex items-start gap-3 mb-5 cursor-pointer">
          <input
            type="checkbox"
            checked={termsAccepted}
            onChange={(e) => setTermsAccepted(e.target.checked)}
            className="mt-1 w-4 h-4 accent-emerald-600"
          />
          <span className="text-sm text-gray-700">
            I have read and understood the terms, risks, and fees. I consent to this investment.
          </span>
        </label>
        <button
          onClick={() => {
            if (!termsAccepted) { toast.error('Please accept the terms'); return }
            consentMutation.mutate()
          }}
          disabled={!termsAccepted || consentMutation.isPending}
          className="btn-primary"
        >
          {consentMutation.isPending ? 'Processing...' : 'I Agree & Continue →'}
        </button>
      </div>
    )
  }

  // Product detail step
  if (isLoading) {
    return <div className="px-5 pt-12"><div className="skeleton h-48 rounded-2xl" /></div>
  }

  return (
    <div className="px-5 pt-12 pb-8 animate-fade-in">
      <button onClick={() => navigate('/grow')} className="flex items-center gap-2 text-gray-600 mb-5">
        <ArrowLeft className="w-4 h-4" /> Back
      </button>

      <div className="card mb-4 bg-emerald-900 text-white">
        <p className="text-emerald-300 text-sm mb-1">{product?.type?.replace('_', ' ')}</p>
        <h2 className="text-2xl font-bold mb-1">{product?.name}</h2>
        <p className="text-emerald-200 text-sm">{product?.issuer}</p>
        <div className="flex gap-2 mt-3">
          <span className={`px-2 py-0.5 rounded-full text-xs font-semibold
            ${product?.risk_level === 'LOW' ? 'bg-green-100 text-green-800' : 'bg-amber-100 text-amber-800'}
          `}>{product?.risk_level} Risk</span>
          <span className="px-2 py-0.5 rounded-full text-xs font-semibold bg-blue-100 text-blue-800">
            {product?.liquidity}
          </span>
        </div>
      </div>

      <div className="card mb-4">
        <p className="text-sm text-gray-700 leading-relaxed">{product?.description}</p>
      </div>

      <div className="card mb-4">
        <div className="space-y-3 text-sm">
          {[
            { label: 'Indicative Return', value: product?.interest_or_coupon, color: 'text-emerald-600' },
            { label: 'Holding Period', value: product?.holding_period },
            { label: 'Liquidity', value: product?.liquidity },
            { label: 'Min. Investment', value: formatINR(product?.min_investment) },
            { label: 'Fees', value: product?.fees },
          ].map(({ label, value, color }) => (
            <div key={label} className="flex justify-between">
              <span className="text-gray-500">{label}</span>
              <span className={`font-medium text-right max-w-[60%] ${color || 'text-gray-800'}`}>{value}</span>
            </div>
          ))}
        </div>
      </div>

      <div className="p-3 bg-blue-50 rounded-xl border border-blue-100 mb-5">
        <p className="text-xs text-blue-700">
          <strong>Suitable for:</strong> {product?.suitable_for}
        </p>
      </div>

      <button
        id="btn-invest-now"
        onClick={() => setStep('amount')}
        className="btn-primary"
      >
        Invest in This Product →
      </button>
    </div>
  )
}
