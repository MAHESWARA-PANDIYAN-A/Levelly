import { useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { useQuery, useMutation } from '@tanstack/react-query'
import {
  ArrowLeft,
  ArrowRight,
  ChevronDown,
  ChevronUp,
  ShieldCheck,
  Building2,
  Clock,
  CheckCircle2,
  AlertTriangle,
  FileText,
  MapPin,
} from 'lucide-react'
import { insuranceApi } from '../api/insuranceApi'
import CoverageZoneMap from '../components/CoverageZoneMap'
import toast from 'react-hot-toast'

const formatINR = (amt: number) =>
  new Intl.NumberFormat('en-IN', { style: 'currency', currency: 'INR', maximumFractionDigits: 0 }).format(amt)

export default function PlanDetailPage() {
  const { planId } = useParams()
  const navigate = useNavigate()

  const { data: plans, isLoading } = useQuery({
    queryKey: ['insurance-plans'],
    queryFn: () => insuranceApi.getPlans().then((r) => r.data),
  })

  const plan = plans?.find((p) => p.id === Number(planId))

  // Expandable sections state (Section 4)
  const [openSections, setOpenSections] = useState<Record<string, boolean>>({
    covered: true,
    triggers: false,
    area: false,
    payout: false,
    waiting: false,
    exclusions: false,
    terms: false,
    partner: false,
  })

  const toggle = (sec: string) => {
    setOpenSections((prev) => ({ ...prev, [sec]: !prev[sec] }))
  }

  // Plan selection mutation (Section 5)
  const selectPlanMutation = useMutation({
    mutationFn: () => insuranceApi.selectPlan(Number(planId)),
    onSuccess: () => {
      navigate(`/incomeshield/personalized/${planId}`)
    },
    onError: (err: any) => {
      toast.error(err.response?.data?.detail || 'Failed to select plan. Proceeding with details...')
      navigate(`/incomeshield/personalized/${planId}`)
    },
  })

  if (isLoading || !plan) {
    return (
      <div className="px-5 pt-8 animate-pulse space-y-4">
        <div className="h-6 bg-slate-200 rounded w-1/3" />
        <div className="h-40 bg-slate-200 rounded-2xl" />
      </div>
    )
  }

  return (
    <div className="px-5 pb-8 animate-fade-in space-y-4 pt-2">
      {/* Back button */}
      <button
        onClick={() => navigate('/incomeshield/plans')}
        className="flex items-center gap-2 text-xs font-semibold text-slate-500 hover:text-slate-800 transition py-1"
      >
        <ArrowLeft className="w-4 h-4" /> Back to Plans
      </button>

      {/* PLAN DETAILS HEADER CARD */}
      <div className="card bg-slate-900 text-white p-5 rounded-3xl shadow-xl border border-slate-800">
        <span className="text-[10px] font-bold uppercase tracking-widest text-emerald-400 block mb-1">
          PLAN DETAILS
        </span>
        <h1 className="text-xl font-black text-white tracking-tight">{plan.name}</h1>
        <p className="text-xs text-slate-400 mt-1 leading-relaxed">{plan.description}</p>

        <div className="grid grid-cols-2 gap-3 pt-4 mt-3 border-t border-slate-800">
          <div>
            <span className="text-[10px] text-slate-400 block uppercase font-medium">Premium</span>
            <div className="flex items-baseline gap-1 mt-0.5">
              <span className="text-2xl font-black text-white">{formatINR(plan.premium)}</span>
              <span className="text-xs text-slate-400 font-medium">/{plan.premium_frequency}</span>
            </div>
          </div>
          <div>
            <span className="text-[10px] text-slate-400 block uppercase font-medium">Coverage Limit</span>
            <span className="text-2xl font-black text-emerald-300 block mt-0.5">
              {formatINR(plan.coverage_limit)}
            </span>
          </div>
        </div>

        <div className="flex items-center gap-4 text-xs text-slate-400 pt-3 mt-3 border-t border-slate-800">
          <span className="flex items-center gap-1">
            <Clock className="w-3.5 h-3.5 text-slate-400" /> Duration: <strong className="text-slate-200">{plan.policy_duration}</strong>
          </span>
          <span className="flex items-center gap-1">
            <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" /> Waiting Period: <strong className="text-slate-200">{plan.waiting_period}</strong>
          </span>
        </div>
      </div>

      {/* EXPANDABLE SECTIONS (Section 4) */}

      {/* 1. What is covered? */}
      <div className="card p-4 space-y-2 border border-slate-200 bg-white">
        <button
          onClick={() => toggle('covered')}
          className="w-full flex items-center justify-between font-bold text-xs text-slate-900"
        >
          <span className="flex items-center gap-2">
            <CheckCircle2 className="w-4 h-4 text-emerald-600" /> What is covered?
          </span>
          {openSections.covered ? <ChevronUp className="w-4 h-4 text-slate-500" /> : <ChevronDown className="w-4 h-4 text-slate-500" />}
        </button>
        {openSections.covered && (
          <div className="pt-2 space-y-2 text-xs text-slate-600 animate-fade-in border-t border-slate-100 mt-2">
            <p className="leading-relaxed">
              This plan protects against lost earning hours during extreme environmental and civic disruption events:
            </p>
            <div className="flex flex-wrap gap-1.5 pt-1">
              {plan.covered_events.map((evt) => (
                <span
                  key={evt}
                  className="text-[10px] font-semibold px-2.5 py-1 rounded-md bg-emerald-50 text-emerald-800 border border-emerald-200"
                >
                  ✓ {evt.replace(/_/g, ' ')}
                </span>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* 2. Trigger conditions */}
      <div className="card p-4 space-y-2 border border-slate-200 bg-white">
        <button
          onClick={() => toggle('triggers')}
          className="w-full flex items-center justify-between font-bold text-xs text-slate-900"
        >
          <span className="flex items-center gap-2">
            <Clock className="w-4 h-4 text-blue-600" /> Trigger conditions
          </span>
          {openSections.triggers ? <ChevronUp className="w-4 h-4 text-slate-500" /> : <ChevronDown className="w-4 h-4 text-slate-500" />}
        </button>
        {openSections.triggers && (
          <div className="pt-2 space-y-2 text-xs text-slate-600 animate-fade-in border-t border-slate-100 mt-2">
            {Object.entries(plan.trigger_conditions || {}).map(([evt, cond]) => (
              <div key={evt} className="p-2.5 bg-slate-50 rounded-xl border border-slate-100">
                <span className="text-[11px] font-bold text-slate-800 block mb-0.5">{evt.replace(/_/g, ' ')}</span>
                <span className="text-[11px] text-slate-600">{cond}</span>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* 3. Covered area */}
      <div className="card p-4 space-y-2 border border-slate-200 bg-white">
        <button
          onClick={() => toggle('area')}
          className="w-full flex items-center justify-between font-bold text-xs text-slate-900"
        >
          <span className="flex items-center gap-2">
            <MapPin className="w-4 h-4 text-amber-600" /> Covered area
          </span>
          {openSections.area ? <ChevronUp className="w-4 h-4 text-slate-500" /> : <ChevronDown className="w-4 h-4 text-slate-500" />}
        </button>
        {openSections.area && (
          <div className="pt-2 space-y-2.5 text-xs text-slate-600 animate-fade-in border-t border-slate-100 mt-2">
            <p className="leading-relaxed">
              Disruptions must occur within your registered metropolitan delivery work zone:
            </p>
            <div className="p-2.5 bg-slate-50 rounded-xl border border-slate-100 font-medium text-slate-800">
              📍 Primary Zone: Chennai Delivery Zone (OMR-ECR, Velachery, Guindy, Chennai Central)
            </div>
            <CoverageZoneMap
              primaryZone="Chennai Delivery Zone"
              affectedSubzones={['Chennai South', 'Velachery', 'OMR-ECR']}
            />
          </div>
        )}
      </div>

      {/* 4. Payout structure */}
      <div className="card p-4 space-y-2 border border-slate-200 bg-white">
        <button
          onClick={() => toggle('payout')}
          className="w-full flex items-center justify-between font-bold text-xs text-slate-900"
        >
          <span className="flex items-center gap-2">
            <Building2 className="w-4 h-4 text-emerald-600" /> Payout structure
          </span>
          {openSections.payout ? <ChevronUp className="w-4 h-4 text-slate-500" /> : <ChevronDown className="w-4 h-4 text-slate-500" />}
        </button>
        {openSections.payout && (
          <div className="pt-2 space-y-2 text-xs text-slate-600 animate-fade-in border-t border-slate-100 mt-2">
            <p className="leading-relaxed">
              Parametric payouts are pre-fixed by the insurance partner up to <strong>{formatINR(plan.coverage_limit)}</strong>. Once official radar telemetry verifies that a trigger threshold is reached, claim settlement begins automatically.
            </p>
            <p className="text-[11px] text-slate-500">
              Payouts are transferred directly to your linked UPI / Bank account or can optionally be moved into your Safety Wallet.
            </p>
          </div>
        )}
      </div>

      {/* 5. Waiting period */}
      <div className="card p-4 space-y-2 border border-slate-200 bg-white">
        <button
          onClick={() => toggle('waiting')}
          className="w-full flex items-center justify-between font-bold text-xs text-slate-900"
        >
          <span className="flex items-center gap-2">
            <Clock className="w-4 h-4 text-slate-600" /> Waiting period
          </span>
          {openSections.waiting ? <ChevronUp className="w-4 h-4 text-slate-500" /> : <ChevronDown className="w-4 h-4 text-slate-500" />}
        </button>
        {openSections.waiting && (
          <div className="pt-2 text-xs text-slate-600 animate-fade-in border-t border-slate-100 mt-2 leading-relaxed">
            Standard waiting period: <strong>{plan.waiting_period}</strong> from enrollment confirmation before weather telemetry events are eligible for trigger evaluation.
          </div>
        )}
      </div>

      {/* 6. Exclusions */}
      <div className="card p-4 space-y-2 border border-slate-200 bg-white">
        <button
          onClick={() => toggle('exclusions')}
          className="w-full flex items-center justify-between font-bold text-xs text-slate-900"
        >
          <span className="flex items-center gap-2">
            <AlertTriangle className="w-4 h-4 text-rose-600" /> Exclusions
          </span>
          {openSections.exclusions ? <ChevronUp className="w-4 h-4 text-slate-500" /> : <ChevronDown className="w-4 h-4 text-slate-500" />}
        </button>
        {openSections.exclusions && (
          <div className="pt-2 space-y-1.5 text-xs text-slate-600 animate-fade-in border-t border-slate-100 mt-2">
            {plan.exclusions.map((exc, i) => (
              <div key={i} className="flex items-start gap-2 text-[11px]">
                <span className="text-rose-500 font-bold">•</span>
                <span>{exc}</span>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* 7. Important terms */}
      <div className="card p-4 space-y-2 border border-slate-200 bg-white">
        <button
          onClick={() => toggle('terms')}
          className="w-full flex items-center justify-between font-bold text-xs text-slate-900"
        >
          <span className="flex items-center gap-2">
            <FileText className="w-4 h-4 text-slate-600" /> Important terms
          </span>
          {openSections.terms ? <ChevronUp className="w-4 h-4 text-slate-500" /> : <ChevronDown className="w-4 h-4 text-slate-500" />}
        </button>
        {openSections.terms && (
          <div className="pt-2 text-xs text-slate-600 animate-fade-in border-t border-slate-100 mt-2 space-y-1.5 leading-relaxed">
            <p>• Weekly renewals are non-compulsory and can be paused before the renewal cycle.</p>
            <p>• Telemetry values are captured via Indian Meteorological Department (IMD) radar feeds.</p>
            <p>• Coverage applies exclusively to delivery partner gig operations during scheduled shifts.</p>
          </div>
        )}
      </div>

      {/* 8. Insurance partner */}
      <div className="card p-4 space-y-2 border border-slate-200 bg-white">
        <button
          onClick={() => toggle('partner')}
          className="w-full flex items-center justify-between font-bold text-xs text-slate-900"
        >
          <span className="flex items-center gap-2">
            <Building2 className="w-4 h-4 text-purple-600" /> Insurance partner
          </span>
          {openSections.partner ? <ChevronUp className="w-4 h-4 text-slate-500" /> : <ChevronDown className="w-4 h-4 text-slate-500" />}
        </button>
        {openSections.partner && (
          <div className="pt-2 text-xs text-slate-600 animate-fade-in border-t border-slate-100 mt-2 space-y-1 leading-relaxed">
            <p>Underwritten by <strong>{plan.partner_name || 'SafeWork Protection Partner'}</strong>.</p>
            <p className="text-[11px] text-slate-500">Regulated parametric insurance underwriting partner for informal economy resilience.</p>
          </div>
        )}
      </div>

      {/* PRIMARY CTA: "Choose This Plan" (Section 4) */}
      <div className="pt-3">
        <button
          id="btn-choose-this-plan"
          onClick={() => selectPlanMutation.mutate()}
          disabled={selectPlanMutation.isPending}
          className="btn-primary w-full py-3.5 flex items-center justify-center gap-2 text-sm font-bold shadow-md shadow-emerald-700/20"
        >
          {selectPlanMutation.isPending ? 'Selecting Plan...' : 'Choose This Plan'} <ArrowRight className="w-4 h-4" />
        </button>
      </div>
    </div>
  )
}
