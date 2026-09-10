import { useQuery } from '@tanstack/react-query'
import { useNavigate } from 'react-router-dom'
import { ArrowLeft, ChevronRight, AlertCircle, Shield } from 'lucide-react'
import { insuranceApi } from '../api/insuranceApi'
import { PlanCardSkeleton } from '../components/InsuranceSkeletons'

const formatINR = (amt: number) =>
  new Intl.NumberFormat('en-IN', { style: 'currency', currency: 'INR', maximumFractionDigits: 0 }).format(amt)

export default function PlansPage() {
  const navigate = useNavigate()

  const { data: plans, isLoading } = useQuery({
    queryKey: ['insurance-plans'],
    queryFn: () => insuranceApi.getPlans().then((r) => r.data),
  })

  return (
    <div className="px-5 pb-8 animate-fade-in space-y-4 pt-2">
      {/* Back button */}
      <button
        onClick={() => navigate('/incomeshield')}
        className="flex items-center gap-2 text-xs font-semibold text-slate-500 hover:text-slate-800 transition py-1"
      >
        <ArrowLeft className="w-4 h-4" /> Back to IncomeShield
      </button>

      {/* Page Heading */}
      <div>
        <div className="flex items-center gap-1.5 text-xs font-bold text-emerald-700 uppercase tracking-wider mb-1">
          <Shield className="w-3.5 h-3.5" /> Plan Selection
        </div>
        <h1 className="text-2xl font-black text-slate-900 tracking-tight">Available Protection Plans</h1>
        <p className="text-xs text-slate-600 mt-1 leading-relaxed">
          Choose an income-protection plan designed for eligible disruptions that can affect your ability to earn.
        </p>
      </div>

      {isLoading ? (
        <div className="space-y-3">
          <PlanCardSkeleton />
          <PlanCardSkeleton />
          <PlanCardSkeleton />
        </div>
      ) : plans?.length === 0 ? (
        <div className="card p-8 text-center text-slate-500">
          <AlertCircle className="w-8 h-8 mx-auto mb-2 text-slate-400" />
          <p className="font-semibold text-sm">No plans available currently</p>
          <p className="text-xs text-slate-400 mt-1">Check back soon for partner offerings.</p>
        </div>
      ) : (
        <div className="space-y-3.5">
          {plans?.map((plan) => (
            <div
              key={plan.id}
              className="card p-4 transition-all border border-slate-200 bg-white hover:border-emerald-300 hover:shadow-md rounded-2xl"
            >
              {/* Header: Name and Premium */}
              <div className="flex items-start justify-between mb-2">
                <div>
                  <h2 className="text-base font-black text-slate-900 uppercase tracking-wide">{plan.name}</h2>
                  <p className="text-xs text-slate-500 mt-0.5 line-clamp-1">{plan.description}</p>
                </div>
                <div className="text-right flex-shrink-0">
                  <span className="text-xl font-black text-slate-900">{formatINR(plan.premium)}</span>
                  <span className="text-[10px] text-slate-500 block font-medium">/ {plan.premium_frequency}</span>
                </div>
              </div>

              {/* Coverage & Duration Grid */}
              <div className="grid grid-cols-2 gap-2 my-3 p-2.5 bg-slate-50 rounded-xl border border-slate-100 text-xs">
                <div>
                  <span className="text-[10px] text-slate-400 block font-medium uppercase">Coverage</span>
                  <span className="font-extrabold text-emerald-700">Up to {formatINR(plan.coverage_limit)}</span>
                </div>
                <div className="text-right">
                  <span className="text-[10px] text-slate-400 block font-medium uppercase">Duration</span>
                  <span className="font-semibold text-slate-800">{plan.policy_duration}</span>
                </div>
              </div>

              {/* Major Covered Event Categories */}
              <div className="space-y-1.5 pt-1">
                <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider block">
                  Covered events:
                </span>
                <div className="flex flex-wrap gap-1.5">
                  {plan.covered_events.map((evt) => (
                    <span
                      key={evt}
                      className="text-[10px] font-semibold px-2.5 py-0.5 rounded-md bg-slate-100 text-slate-700 border border-slate-200"
                    >
                      {evt.replace(/_/g, ' ').toLowerCase().replace(/\b\w/g, (c) => c.toUpperCase())}
                    </span>
                  ))}
                </div>
              </div>

              {/* CTA (Section 3: Clean "View Plan", no urgency language) */}
              <div className="pt-3.5 mt-3 border-t border-slate-100 flex items-center justify-between">
                <span className="text-[10px] text-slate-400 font-medium">Underwritten by {plan.partner_name || 'Insurance Partner'}</span>
                <button
                  id={`btn-view-plan-${plan.id}`}
                  onClick={() => navigate(`/incomeshield/plans/${plan.id}`)}
                  className="px-4 py-2 bg-emerald-600 hover:bg-emerald-700 active:scale-98 text-white text-xs font-bold rounded-xl transition flex items-center gap-1 shadow-sm"
                >
                  View Plan <ChevronRight className="w-3.5 h-3.5" />
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Regulatory Footer */}
      <div className="p-3 bg-slate-100 rounded-xl text-[10px] text-slate-500 leading-relaxed text-center">
        Underwritten by SafeWork Protection Partner. Coverage limits and trigger criteria are governed by the policy schedule.
      </div>
    </div>
  )
}
