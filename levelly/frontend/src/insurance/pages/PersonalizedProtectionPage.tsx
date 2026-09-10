import { useParams, useNavigate } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { ArrowLeft, ArrowRight, Sparkles, CloudRain, AlertCircle } from 'lucide-react'
import { insuranceApi } from '../api/insuranceApi'

const formatINR = (amt: number) =>
  new Intl.NumberFormat('en-IN', { style: 'currency', currency: 'INR', maximumFractionDigits: 0 }).format(amt)

export default function PersonalizedProtectionPage() {
  const { planId } = useParams()
  const navigate = useNavigate()

  const { data: personalizedData, isLoading } = useQuery({
    queryKey: ['insurance-personalized', planId],
    queryFn: () => insuranceApi.getPersonalized(Number(planId)).then((r) => r.data),
    enabled: Boolean(planId),
  })

  // Fallback / defaults based on existing income intelligence
  const expectedDaily = personalizedData?.expected_daily_income ?? 1050
  const typicalWeekly = personalizedData?.typical_weekly_income ?? 6800
  const estimatedDisrupted = personalizedData?.estimated_disrupted_income ?? 300
  const estimatedImpact = personalizedData?.estimated_income_impact ?? 750
  const planName = personalizedData?.plan_name ?? 'Standard IncomeShield'
  const exampleEvent = personalizedData?.example_event ?? {
    selected_plan: planName,
    event_type: 'Heavy rainfall',
    covered_area: 'Chennai work zone',
    typical_earnings: expectedDaily,
    estimated_income_impact: estimatedImpact,
    plan_trigger: 'Rainfall >= 45mm over 3 consecutive hours',
    explanation: 'Your selected plan determines the applicable trigger and payout rules.',
  }

  if (isLoading) {
    return (
      <div className="px-5 pt-8 animate-pulse space-y-4">
        <div className="h-6 bg-slate-200 rounded w-1/3" />
        <div className="h-32 bg-slate-200 rounded-2xl" />
        <div className="h-40 bg-slate-200 rounded-2xl" />
      </div>
    )
  }

  return (
    <div className="px-5 pb-8 animate-fade-in space-y-4 pt-2">
      {/* Back button */}
      <button
        onClick={() => navigate(`/incomeshield/plans/${planId}`)}
        className="flex items-center gap-2 text-xs font-semibold text-slate-500 hover:text-slate-800 transition py-1"
      >
        <ArrowLeft className="w-4 h-4" /> Back to Plan Details
      </button>

      {/* Header */}
      <div>
        <div className="flex items-center gap-1.5 text-xs font-bold text-emerald-700 uppercase tracking-wider mb-1">
          <Sparkles className="w-3.5 h-3.5" /> Income Intelligence
        </div>
        <h1 className="text-2xl font-black text-slate-900 tracking-tight">Personalized Protection</h1>
        <p className="text-xs text-slate-600 mt-1 leading-relaxed">
          How this plan relates to your income, based on your platform earning velocity.
        </p>
      </div>

      {/* Selected Plan Indicator Banner */}
      <div className="p-3 bg-emerald-50 rounded-2xl border border-emerald-200 flex items-center justify-between">
        <div>
          <span className="text-[10px] uppercase font-bold text-emerald-700 block">Selected Plan</span>
          <span className="text-sm font-black text-slate-900">{planName}</span>
        </div>
        <button
          onClick={() => navigate('/incomeshield/plans')}
          className="text-xs font-bold text-emerald-800 hover:underline"
        >
          Change Plan
        </button>
      </div>

      {/* Income Intelligence Baseline Metrics */}
      <div className="grid grid-cols-2 gap-3">
        <div className="card p-4 bg-white border border-slate-200/90 shadow-xs">
          <span className="text-[10px] uppercase font-bold text-slate-400 block mb-1">Average Daily Earnings</span>
          <span className="text-xl font-black text-slate-900">{formatINR(expectedDaily)}</span>
          <span className="text-[10px] text-slate-500 block mt-0.5">Based on active delivery shifts</span>
        </div>
        <div className="card p-4 bg-white border border-slate-200/90 shadow-xs">
          <span className="text-[10px] uppercase font-bold text-slate-400 block mb-1">Average Weekly Earnings</span>
          <span className="text-xl font-black text-slate-900">{formatINR(typicalWeekly)}</span>
          <span className="text-[10px] text-slate-500 block mt-0.5">Rolling earning baseline</span>
        </div>
      </div>

      {/* SECTION 6: HOW THIS PLAN RELATES TO YOUR INCOME */}
      <div className="card p-5 bg-white border border-slate-200 shadow-sm space-y-3">
        <div className="flex items-center justify-between pb-2 border-b border-slate-100">
          <h2 className="text-sm font-bold text-slate-900">How this plan relates to your income</h2>
          <span className="text-[10px] font-bold text-emerald-700 bg-emerald-100 px-2 py-0.5 rounded-full">
            Impact Analysis
          </span>
        </div>

        <div className="space-y-2.5 text-xs">
          <div className="flex justify-between items-center py-1">
            <span className="text-slate-600">Normal expected earnings:</span>
            <span className="font-bold text-slate-900 text-sm">{formatINR(expectedDaily)}</span>
          </div>
          <div className="flex justify-between items-center py-1">
            <span className="text-slate-600">Estimated disrupted earnings:</span>
            <span className="font-bold text-amber-700 text-sm">{formatINR(estimatedDisrupted)}</span>
          </div>
          <div className="flex justify-between items-center py-2 px-3 bg-rose-50 rounded-xl border border-rose-200">
            <span className="font-black text-rose-900 uppercase tracking-wider text-[11px]">
              ESTIMATED INCOME IMPACT
            </span>
            <span className="font-black text-rose-700 text-base">{formatINR(estimatedImpact)}</span>
          </div>
        </div>

        {/* Disclaimer (Section 6) */}
        <div className="p-3 bg-slate-50 rounded-xl border border-slate-200 flex items-start gap-2">
          <AlertCircle className="w-4 h-4 text-slate-500 flex-shrink-0 mt-0.5" />
          <p className="text-[11px] text-slate-600 leading-relaxed">
            <strong>Important:</strong> This estimate is based on your earnings history. It is not your guaranteed insurance payout. The actual insurance payout must come from the selected policy and insurance partner.
          </p>
        </div>
      </div>

      {/* SECTION 7: PLAN-SPECIFIC COVERAGE EXAMPLE */}
      <div className="card p-5 bg-gradient-to-b from-white to-slate-50 border border-slate-200 shadow-sm space-y-3">
        <div className="flex items-center justify-between pb-2 border-b border-slate-100">
          <div className="flex items-center gap-2">
            <CloudRain className="w-4 h-4 text-blue-600" />
            <h2 className="text-sm font-bold text-slate-900">Plan-Specific Coverage Example</h2>
          </div>
          <span className="text-[10px] font-mono font-bold bg-slate-100 text-slate-700 px-2 py-0.5 rounded">
            {exampleEvent.selected_plan}
          </span>
        </div>

        <div className="grid grid-cols-2 gap-2 text-xs">
          <div className="p-2.5 bg-white rounded-xl border border-slate-200">
            <span className="text-[10px] text-slate-400 block uppercase font-medium">Selected plan</span>
            <strong className="text-slate-900">{exampleEvent.selected_plan}</strong>
          </div>
          <div className="p-2.5 bg-white rounded-xl border border-slate-200">
            <span className="text-[10px] text-slate-400 block uppercase font-medium">Example covered event</span>
            <strong className="text-slate-900">{exampleEvent.event_type}</strong>
          </div>
          <div className="p-2.5 bg-white rounded-xl border border-slate-200">
            <span className="text-[10px] text-slate-400 block uppercase font-medium">Covered area</span>
            <strong className="text-slate-900">{exampleEvent.covered_area}</strong>
          </div>
          <div className="p-2.5 bg-white rounded-xl border border-slate-200">
            <span className="text-[10px] text-slate-400 block uppercase font-medium">Typical earnings</span>
            <strong className="text-slate-900">{formatINR(exampleEvent.typical_earnings)}</strong>
          </div>
        </div>

        <div className="p-3 bg-white rounded-xl border border-slate-200 space-y-1.5 text-xs">
          <div className="flex justify-between items-center">
            <span className="text-slate-500">Estimated income impact:</span>
            <strong className="text-rose-600 font-extrabold">{formatINR(exampleEvent.estimated_income_impact)}</strong>
          </div>
          <div className="flex justify-between items-center">
            <span className="text-slate-500">Plan trigger:</span>
            <strong className="text-slate-800 text-right">{exampleEvent.plan_trigger}</strong>
          </div>
        </div>

        <p className="text-[11px] text-slate-600 italic bg-blue-50/70 p-2.5 rounded-xl border border-blue-200">
          "{exampleEvent.explanation}"
        </p>
      </div>

      {/* ACTION BUTTONS */}
      <div className="space-y-2 pt-2">
        <button
          id="btn-continue-to-review"
          onClick={() => navigate(`/incomeshield/purchase-review/${planId}`)}
          className="btn-primary w-full py-3.5 flex items-center justify-center gap-2 text-sm font-bold shadow-md shadow-emerald-700/20"
        >
          Continue to Purchase Review <ArrowRight className="w-4 h-4" />
        </button>

        <button
          id="btn-change-plan"
          onClick={() => navigate('/incomeshield/plans')}
          className="w-full py-2.5 rounded-xl text-xs font-bold text-slate-600 hover:bg-slate-100 transition"
        >
          Change Plan
        </button>
      </div>
    </div>
  )
}
