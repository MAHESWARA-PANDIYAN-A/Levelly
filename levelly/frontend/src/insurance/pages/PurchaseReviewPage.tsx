import { useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import {
  ArrowLeft,
  CheckCircle2,
  AlertTriangle,
  ShieldCheck,
  RefreshCw,
} from 'lucide-react'
import toast from 'react-hot-toast'
import { insuranceApi } from '../api/insuranceApi'
import type { InsurancePolicy } from '../types/insurance.types'

const formatINR = (amt: number) =>
  new Intl.NumberFormat('en-IN', { style: 'currency', currency: 'INR', maximumFractionDigits: 0 }).format(amt)

export default function PurchaseReviewPage() {
  const { planId } = useParams()
  const navigate = useNavigate()
  const queryClient = useQueryClient()

  const [termsAccepted, setTermsAccepted] = useState(false)
  const [confirmedPolicy, setConfirmedPolicy] = useState<InsurancePolicy | null>(null)

  const { data: plans, isLoading } = useQuery({
    queryKey: ['insurance-plans'],
    queryFn: () => insuranceApi.getPlans().then((r) => r.data),
  })

  const plan = plans?.find((p) => p.id === Number(planId))

  const purchaseMutation = useMutation({
    mutationFn: () =>
      insuranceApi.purchase({
        plan_id: Number(planId),
        terms_accepted: termsAccepted,
        terms_version: 'v1.0',
        work_zone: 'Chennai Delivery Zone',
      }),
    onSuccess: (res) => {
      setConfirmedPolicy(res.data.policy)
      queryClient.invalidateQueries({ queryKey: ['insurance-status'] })
      queryClient.invalidateQueries({ queryKey: ['insurance-policy'] })
      toast.success('Your protection is active.')
    },
    onError: (err: any) => {
      toast.error(err.response?.data?.detail || 'Failed to complete protection enrollment. Please try again.')
    },
  })

  // ============================================================
  // SECTION 10: POLICY CONFIRMATION
  // ============================================================
  if (confirmedPolicy) {
    return (
      <div className="px-5 pb-8 animate-fade-in space-y-4 pt-6 text-center">
        <div className="w-16 h-16 rounded-3xl bg-emerald-100 text-emerald-600 flex items-center justify-center mx-auto shadow-md shadow-emerald-500/20 animate-bounce">
          <CheckCircle2 className="w-9 h-9" />
        </div>

        <div>
          <h1 className="text-2xl font-black text-slate-900 tracking-tight">Your protection is active.</h1>
          <p className="text-xs text-slate-500 mt-1">
            Parametric coverage is now officially underwritten for your Chennai work zone.
          </p>
        </div>

        {/* Confirmation Details Card (Section 10) */}
        <div className="card p-5 bg-white border border-slate-200/90 shadow-sm text-left space-y-3 rounded-3xl">
          <div className="flex justify-between items-center pb-2.5 border-b border-slate-100">
            <span className="text-xs text-slate-500 font-medium">Product</span>
            <span className="text-xs font-bold text-slate-900">IncomeShield</span>
          </div>
          <div className="flex justify-between items-center pb-2.5 border-b border-slate-100">
            <span className="text-xs text-slate-500 font-medium">Status</span>
            <span className="text-xs font-black text-emerald-800 bg-emerald-100 px-2.5 py-0.5 rounded-full border border-emerald-300">
              ACTIVE
            </span>
          </div>
          <div className="flex justify-between items-center pb-2.5 border-b border-slate-100">
            <span className="text-xs text-slate-500 font-medium">Policy Number</span>
            <span className="text-xs font-mono font-bold text-slate-900">{confirmedPolicy.policy_number}</span>
          </div>
          <div className="flex justify-between items-center pb-2.5 border-b border-slate-100">
            <span className="text-xs text-slate-500 font-medium">Plan</span>
            <span className="text-xs font-bold text-slate-900">{confirmedPolicy.plan_name}</span>
          </div>
          <div className="flex justify-between items-center pb-2.5 border-b border-slate-100">
            <span className="text-xs text-slate-500 font-medium">Coverage</span>
            <span className="text-sm font-black text-emerald-700">{formatINR(confirmedPolicy.coverage_limit)}</span>
          </div>
          <div className="flex justify-between items-center pb-2.5 border-b border-slate-100">
            <span className="text-xs text-slate-500 font-medium">Premium</span>
            <span className="text-xs font-bold text-slate-800">{formatINR(confirmedPolicy.premium)}/week</span>
          </div>
          <div className="flex justify-between items-center pb-2.5 border-b border-slate-100">
            <span className="text-xs text-slate-500 font-medium">Valid until</span>
            <span className="text-xs font-bold text-slate-900">
              {new Date(confirmedPolicy.end_date).toLocaleDateString('en-IN', {
                day: '2-digit',
                month: '2-digit',
                year: 'numeric',
              })}
            </span>
          </div>
          <div className="flex justify-between items-center">
            <span className="text-xs text-slate-500 font-medium">Covered work zone</span>
            <span className="text-xs font-bold text-slate-900">Chennai</span>
          </div>
        </div>

        {/* CTA: View My Policy (Section 10) */}
        <button
          id="btn-view-my-policy"
          onClick={() => navigate('/incomeshield/policy')}
          className="btn-primary w-full py-3.5 text-sm font-bold shadow-md shadow-emerald-700/20"
        >
          View My Policy
        </button>
      </div>
    )
  }

  if (isLoading || !plan) {
    return (
      <div className="px-5 pt-8 animate-pulse space-y-4">
        <div className="h-6 bg-slate-200 rounded w-1/3" />
        <div className="h-40 bg-slate-200 rounded-2xl" />
      </div>
    )
  }

  // ============================================================
  // SECTION 8 & 9: PURCHASE REVIEW
  // ============================================================
  return (
    <div className="px-5 pb-8 animate-fade-in space-y-4 pt-2">
      {/* Back button */}
      <button
        onClick={() => navigate(`/incomeshield/personalized/${planId}`)}
        className="flex items-center gap-2 text-xs font-semibold text-slate-500 hover:text-slate-800 transition py-1"
      >
        <ArrowLeft className="w-4 h-4" /> Back to Personalized Protection
      </button>

      <div>
        <div className="flex items-center gap-1.5 text-xs font-bold text-emerald-700 uppercase tracking-wider mb-1">
          <ShieldCheck className="w-3.5 h-3.5" /> Purchase Review
        </div>
        <h1 className="text-2xl font-black text-slate-900 tracking-tight">Review Your Protection</h1>
        <p className="text-xs text-slate-600 mt-1 leading-relaxed">
          Please confirm your plan selection, coverage limits, and policy terms before enrollment.
        </p>
      </div>

      {/* ACTUAL SELECTED PLAN DETAILS (Section 8) */}
      <div className="card p-5 bg-white border border-slate-200 shadow-sm space-y-3.5 rounded-3xl">
        <div className="flex justify-between items-start pb-3 border-b border-slate-100">
          <div>
            <span className="text-[10px] uppercase font-bold text-emerald-700 block">IncomeShield</span>
            <h2 className="text-lg font-black text-slate-900 uppercase tracking-wide">{plan.name}</h2>
            <p className="text-xs text-slate-500">{plan.description}</p>
          </div>
          <div className="text-right">
            <span className="text-xl font-black text-slate-900">{formatINR(plan.premium)}</span>
            <span className="text-[10px] text-slate-500 block font-medium">/{plan.premium_frequency}</span>
          </div>
        </div>

        <div className="space-y-2 text-xs">
          <div className="flex justify-between items-center py-1">
            <span className="text-slate-500">Coverage:</span>
            <span className="font-black text-emerald-700 text-sm">Up to {formatINR(plan.coverage_limit)}</span>
          </div>
          <div className="flex justify-between items-center py-1">
            <span className="text-slate-500">Policy duration:</span>
            <span className="font-semibold text-slate-800">{plan.policy_duration}</span>
          </div>
          <div className="flex justify-between items-center py-1">
            <span className="text-slate-500">Waiting period:</span>
            <span className="font-semibold text-slate-800">{plan.waiting_period}</span>
          </div>
          <div className="flex justify-between items-center py-1">
            <span className="text-slate-500">Insurance partner:</span>
            <span className="font-bold text-slate-900">{plan.partner_name || 'SafeWork Protection Partner'}</span>
          </div>
        </div>

        {/* Covered Events */}
        <div className="pt-2 border-t border-slate-100">
          <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider block mb-1.5">
            Covered events:
          </span>
          <div className="flex flex-wrap gap-1.5">
            {plan.covered_events.map((evt) => (
              <span
                key={evt}
                className="text-[10px] font-semibold px-2.5 py-0.5 rounded-md bg-emerald-50 text-emerald-800 border border-emerald-200"
              >
                {evt.replace(/_/g, ' ')}
              </span>
            ))}
          </div>
        </div>

        {/* Important Exclusions */}
        <div className="p-3 bg-amber-50/70 rounded-xl border border-amber-200/80 space-y-1 text-xs">
          <div className="flex items-center gap-1.5 text-amber-900 font-bold text-xs">
            <AlertTriangle className="w-3.5 h-3.5 text-amber-700" />
            <span>Important exclusions:</span>
          </div>
          <ul className="text-[11px] text-amber-800 space-y-0.5 list-disc list-inside">
            {plan.exclusions?.slice(0, 3).map((exc, i) => (
              <li key={i}>{exc}</li>
            ))}
          </ul>
        </div>
      </div>

      {/* Checkbox: User Consent (Section 8) */}
      <div className="card p-4 bg-slate-50 border border-slate-200 rounded-2xl shadow-xs">
        <label className="flex items-start gap-3 cursor-pointer select-none">
          <input
            id="checkbox-policy-terms"
            type="checkbox"
            checked={termsAccepted}
            onChange={(e) => setTermsAccepted(e.target.checked)}
            className="w-4 h-4 rounded mt-0.5 accent-emerald-600 cursor-pointer flex-shrink-0"
          />
          <span className="text-xs text-slate-700 leading-snug font-medium">
            I have reviewed the coverage, exclusions and policy terms.
          </span>
        </label>
      </div>

      {/* Actions (Section 8 & 9) */}
      <div className="space-y-2 pt-1">
        {/* Primary CTA: "Confirm Protection" */}
        <button
          id="btn-confirm-protection"
          onClick={() => purchaseMutation.mutate()}
          disabled={!termsAccepted || purchaseMutation.isPending}
          className={`btn-primary w-full py-3.5 text-sm font-bold shadow-md shadow-emerald-700/20 transition ${
            !termsAccepted ? 'opacity-50 cursor-not-allowed' : ''
          }`}
        >
          {purchaseMutation.isPending ? 'Activating Policy...' : 'Confirm Protection'}
        </button>

        {/* Secondary CTA: "Change Plan" (Section 8 & 9) */}
        <button
          id="btn-change-plan-review"
          onClick={() => navigate('/incomeshield/plans')}
          className="w-full py-2.5 rounded-xl text-xs font-bold text-slate-600 hover:bg-slate-100 transition flex items-center justify-center gap-1.5"
        >
          <RefreshCw className="w-3.5 h-3.5" /> Change Plan
        </button>
      </div>
    </div>
  )
}
