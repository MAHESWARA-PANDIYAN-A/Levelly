import { useState } from 'react'
import { useMutation, useQuery } from '@tanstack/react-query'
import { useNavigate } from 'react-router-dom'
import { ArrowLeft, Shield, AlertTriangle, Info } from 'lucide-react'
import { creditAPI, healthAPI } from '../lib/api'
import toast from 'react-hot-toast'

const formatINR = (amount: number) =>
  new Intl.NumberFormat('en-IN', { style: 'currency', currency: 'INR', maximumFractionDigits: 0 }).format(amount)

type CreditStep = 'input' | 'recommendation' | 'offer' | 'apply' | 'success'

export default function CreditPage() {
  const navigate = useNavigate()

  const [step, setStep] = useState<CreditStep>('input')
  const [requestedAmount, setRequestedAmount] = useState('')
  const [purpose, setPurpose] = useState('')
  const [recommendation, setRecommendation] = useState<any>(null)
  const [offer, setOffer] = useState<any>(null)
  const [appResult, setAppResult] = useState<any>(null)

  const { data: dashboard } = useQuery({
    queryKey: ['dashboard'],
    queryFn: () => healthAPI.dashboard().then(r => r.data),
  })

  const recommendMutation = useMutation({
    mutationFn: () => creditAPI.recommend(parseFloat(requestedAmount), purpose),
    onSuccess: (res) => {
      setRecommendation(res.data)
      setStep('recommendation')
    },
    onError: () => toast.error('Could not load credit recommendation'),
  })

  const offerMutation = useMutation({
    mutationFn: () => creditAPI.partnerOffer(parseFloat(requestedAmount), purpose),
    onSuccess: (res) => {
      setOffer(res.data)
      setStep('offer')
    },
    onError: () => toast.error('Could not load partner offer'),
  })

  const applyMutation = useMutation({
    mutationFn: () => creditAPI.applyOffer(offer.offer_id),
    onSuccess: (res) => {
      setAppResult(res.data)
      setStep('success')
    },
    onError: () => toast.error('Application submission failed'),
  })

  if (step === 'success') {
    return (
      <div className="px-5 pt-12 pb-8 text-center animate-fade-in">
        <div className="w-20 h-20 bg-emerald-100 rounded-full flex items-center justify-center mx-auto mb-5">
          <span className="text-4xl">✅</span>
        </div>
        <h2 className="text-2xl font-bold mb-2">Application Submitted</h2>
        <p className="text-gray-500 mb-6">{appResult?.message}</p>

        <div className="card text-left mb-4">
          <div className="space-y-2 text-sm">
            <div className="flex justify-between">
              <span className="text-gray-500">Application ID</span>
              <span className="font-mono font-medium">{appResult?.application_id}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-500">Partner</span>
              <span>{appResult?.partner}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-500">Est. Decision</span>
              <span>{appResult?.estimated_decision_time}</span>
            </div>
          </div>
        </div>

        <button onClick={() => navigate('/')} className="btn-primary">Back to Home</button>
      </div>
    )
  }

  if (step === 'offer' && offer) {
    return (
      <div className="px-5 pt-12 pb-8 animate-fade-in">
        <button onClick={() => setStep('recommendation')} className="flex items-center gap-2 text-gray-600 mb-5">
          <ArrowLeft className="w-4 h-4" /> Back
        </button>
        <h2 className="text-xl font-bold mb-5">Partner Credit Offer</h2>

        <div className="card-premium mb-4">
          <p className="text-emerald-200 text-sm mb-1">{offer.partner}</p>
          <p className="text-4xl font-bold text-white mb-1">{formatINR(offer.offered_amount)}</p>
          <p className="text-emerald-200 text-sm">Offered amount</p>
        </div>

        <div className="card mb-4">
          <div className="space-y-3 text-sm">
            {[
              { label: 'Annual Interest Rate', value: `${offer.annual_interest_rate}% p.a.` },
              { label: 'Tenure', value: `${offer.tenure_months} months` },
              { label: 'EMI Amount', value: formatINR(offer.emi_amount) },
              { label: 'Processing Fee', value: formatINR(offer.processing_fee) },
              { label: 'Total Repayment', value: formatINR(offer.total_repayment), bold: true },
            ].map(({ label, value, bold }) => (
              <div key={label} className="flex justify-between">
                <span className="text-gray-500">{label}</span>
                <span className={`${bold ? 'font-bold text-gray-900' : 'font-medium text-gray-700'}`}>{value}</span>
              </div>
            ))}
          </div>
        </div>

        <div className="p-3 bg-blue-50 rounded-xl border border-blue-100 mb-5 flex items-start gap-2">
          <Info className="w-4 h-4 text-blue-500 mt-0.5 flex-shrink-0" />
          <p className="text-xs text-blue-700">{offer.disclaimer}</p>
        </div>

        <button
          id="btn-apply-credit"
          onClick={() => applyMutation.mutate()}
          disabled={applyMutation.isPending}
          className="btn-primary mb-2"
        >
          {applyMutation.isPending ? 'Submitting...' : 'Apply with Partner'}
        </button>
        <button onClick={() => navigate('/')} className="btn-ghost">Not Now</button>
      </div>
    )
  }

  if (step === 'recommendation' && recommendation) {
    const guardrail = recommendation.guardrail
    const isHeld = guardrail.status === 'held'
    const isReduced = guardrail.status === 'reduced'

    return (
      <div className="px-5 pt-12 pb-8 animate-fade-in">
        <button onClick={() => setStep('input')} className="flex items-center gap-2 text-gray-600 mb-5">
          <ArrowLeft className="w-4 h-4" /> Back
        </button>

        <h2 className="text-xl font-bold mb-5">Credit Assessment</h2>

        {/* LEVELLY Recommendation */}
        <div className="card mb-4">
          <p className="text-sm text-gray-500 mb-3">LEVELLY Assessment</p>
          <div className="flex items-center justify-between mb-3">
            <div>
              <p className="text-xs text-gray-400">Requested</p>
              <p className="text-lg font-bold">{formatINR(recommendation.requested_amount)}</p>
            </div>
            <div className="text-right">
              <p className="text-xs text-gray-400">LEVELLY Recommends</p>
              <p className="text-xl font-bold text-emerald-600">
                {formatINR(recommendation.levelly_recommendation.recommended_amount)}
              </p>
            </div>
          </div>
          <div className="flex gap-2 text-xs text-gray-500">
            <span>Resilience: {recommendation.resilience_score}/100</span>
            <span>•</span>
            <span>Distress: {recommendation.distress_level}</span>
          </div>
        </div>

        {/* Guardrail */}
        <div className={`card mb-4 border-2 ${
          isHeld ? 'border-orange-200 bg-orange-50' :
          isReduced ? 'border-amber-200 bg-amber-50' :
          'border-emerald-200 bg-emerald-50'
        }`}>
          <div className="flex items-start gap-3">
            {isHeld && <AlertTriangle className="w-5 h-5 text-orange-600 mt-0.5 flex-shrink-0" />}
            {isReduced && <Shield className="w-5 h-5 text-amber-600 mt-0.5 flex-shrink-0" />}
            {!isHeld && !isReduced && <Shield className="w-5 h-5 text-emerald-600 mt-0.5 flex-shrink-0" />}
            <div>
              <p className={`font-semibold text-sm ${isHeld ? 'text-orange-800' : isReduced ? 'text-amber-800' : 'text-emerald-800'}`}>
                {guardrail.ui_message}
              </p>
              {guardrail.guidance && (
                <p className="text-xs mt-1 text-gray-600">{guardrail.guidance}</p>
              )}
            </div>
          </div>
        </div>

        {/* Reasons */}
        {recommendation.levelly_recommendation.reasons?.length > 0 && (
          <div className="card mb-4">
            <p className="text-sm font-medium text-gray-600 mb-2">Factors considered</p>
            <ul className="space-y-1.5">
              {recommendation.levelly_recommendation.reasons.map((r: string, i: number) => (
                <li key={i} className="text-xs text-gray-500 flex items-center gap-2">
                  <span className="w-1.5 h-1.5 bg-gray-300 rounded-full flex-shrink-0" />
                  {r}
                </li>
              ))}
            </ul>
          </div>
        )}

        {!isHeld && recommendation.can_proceed_to_partner ? (
          <button
            id="btn-get-partner-offer"
            onClick={() => offerMutation.mutate()}
            disabled={offerMutation.isPending}
            className="btn-primary"
          >
            {offerMutation.isPending ? 'Getting Offer...' : 'Get Partner Offer →'}
          </button>
        ) : (
          <div className="space-y-2">
            <button onClick={() => navigate('/coach')} className="btn-primary">
              Talk to Levelly Coach
            </button>
            <button onClick={() => navigate('/')} className="btn-ghost">Back to Home</button>
          </div>
        )}
      </div>
    )
  }

  return (
    <div className="px-5 pb-8 animate-fade-in">
      <h1 className="text-2xl font-bold text-levelly-text mb-1">Borrow Responsibly</h1>
      <p className="text-sm text-gray-500 mb-5">LEVELLY only recommends credit when it's safe to do so.</p>

      {/* Distress status */}
      {dashboard?.distress?.level && dashboard.distress.level !== 'LOW' && (
        <div className="card border-2 border-orange-200 bg-orange-50 mb-4">
          <div className="flex items-center gap-2">
            <AlertTriangle className="w-4 h-4 text-orange-600" />
            <p className="text-sm font-semibold text-orange-800">
              Credit guardrail active — {dashboard.distress.level.toLowerCase()} financial pressure
            </p>
          </div>
          <p className="text-xs text-orange-700 mt-1">
            LEVELLY may limit credit recommendations to protect your financial stability.
          </p>
        </div>
      )}

      <div className="card mb-4">
        <label className="text-sm font-medium text-gray-600 block mb-2">Amount needed (₹)</label>
        <div className="flex items-center gap-2 mb-3">
          <span className="text-3xl font-bold text-gray-400">₹</span>
          <input
            id="credit-amount"
            type="number"
            value={requestedAmount}
            onChange={(e) => setRequestedAmount(e.target.value)}
            placeholder="0"
            className="flex-1 text-4xl font-bold text-gray-900 focus:outline-none bg-transparent"
          />
        </div>
        <div className="flex gap-2">
          {[5000, 10000, 15000, 20000].map((v) => (
            <button
              key={v}
              onClick={() => setRequestedAmount(String(v))}
              className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-all
                ${requestedAmount === String(v) ? 'bg-emerald-600 text-white' : 'bg-gray-100 text-gray-600'}
              `}
            >
              ₹{(v / 1000).toFixed(0)}k
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
          placeholder="e.g., Vehicle repair, Medical expense"
          className="input-field"
        />
      </div>

      <button
        id="btn-check-credit"
        onClick={() => {
          if (!requestedAmount || parseFloat(requestedAmount) <= 0) {
            toast.error('Enter a valid amount')
            return
          }
          recommendMutation.mutate()
        }}
        disabled={recommendMutation.isPending}
        className="btn-primary"
      >
        {recommendMutation.isPending ? 'Checking...' : 'Check Credit Eligibility →'}
      </button>

      <div className="mt-5 p-4 bg-gray-100 rounded-2xl">
        <p className="text-xs text-gray-500">
          LEVELLY is not the lender. Credit is provided by our partner NBFC. 
          LEVELLY's recommendation does not guarantee partner approval. 
          Final credit decision belongs to the regulated partner.
        </p>
      </div>
    </div>
  )
}
