import { useQuery } from '@tanstack/react-query'
import { useNavigate } from 'react-router-dom'
import {
  Umbrella,
  ShieldCheck,
  TrendingUp,
  ArrowRight,
  ChevronRight,
  CloudRain,
  FileText,
  HelpCircle,
  Clock,
  MapPin,
} from 'lucide-react'
import { insuranceApi } from '../api/insuranceApi'
import { PolicyHeaderSkeleton } from '../components/InsuranceSkeletons'

const formatINR = (amt: number) =>
  new Intl.NumberFormat('en-IN', { style: 'currency', currency: 'INR', maximumFractionDigits: 0 }).format(amt)

export default function IncomeShieldHomePage() {
  const navigate = useNavigate()

  const { data: status, isLoading } = useQuery({
    queryKey: ['insurance-status'],
    queryFn: () => insuranceApi.getStatus().then((r) => r.data),
  })

  const hasPolicy = Boolean(status?.has_active_policy && status?.policy)
  const policy = status?.policy
  const activeEvents = status?.active_events || []
  const hasDisruption = activeEvents.length > 0

  if (isLoading) {
    return (
      <div className="px-5 pb-8 animate-fade-in space-y-4 pt-2">
        <PolicyHeaderSkeleton />
      </div>
    )
  }

  // ============================================================
  // STATE 1: ACTIVE POLICY HOME (Section 11 & 12)
  // After purchase, reopening IncomeShield displays Active Policy Home directly.
  // ============================================================
  if (hasPolicy && policy) {
    return (
      <div className="px-5 pb-8 animate-fade-in space-y-4 pt-2">
        {/* Active Policy Header */}
        <div className="flex items-center justify-between pt-1">
          <div className="flex items-center gap-2">
            <div className="p-2 bg-emerald-100 text-emerald-800 rounded-xl shadow-xs">
              <Umbrella className="w-5 h-5 text-emerald-700" />
            </div>
            <div>
              <h1 className="text-xl font-black text-slate-900 tracking-tight">IncomeShield</h1>
              <p className="text-[11px] text-slate-500 font-medium">Your parametric income protection is active</p>
            </div>
          </div>
          <span className="px-3 py-1 text-xs font-black rounded-full bg-emerald-100 text-emerald-800 border border-emerald-300 tracking-wider flex items-center gap-1 shadow-xs">
            <span className="w-2 h-2 rounded-full bg-emerald-600 animate-pulse" /> ACTIVE
          </span>
        </div>

        {/* Disruption Alert Banner if active */}
        {hasDisruption && (
          <div
            onClick={() => navigate(`/incomeshield/events/${activeEvents[0].id}`)}
            className="p-3.5 bg-amber-500/10 border border-amber-300 rounded-2xl cursor-pointer hover:bg-amber-500/15 transition flex items-center justify-between shadow-xs"
          >
            <div className="flex items-center gap-2.5">
              <div className="p-2 bg-amber-500 text-white rounded-xl">
                <CloudRain className="w-4 h-4 animate-bounce" />
              </div>
              <div>
                <div className="flex items-center gap-1.5">
                  <span className="text-xs font-bold text-amber-900">Disruption Detected in Work Zone</span>
                  <span className="w-2 h-2 rounded-full bg-amber-500 animate-ping" />
                </div>
                <p className="text-[11px] text-amber-800 font-medium">
                  {activeEvents[0].event_type.replace(/_/g, ' ')} • {activeEvents[0].zone}
                </p>
              </div>
            </div>
            <ChevronRight className="w-5 h-5 text-amber-700 flex-shrink-0" />
          </div>
        )}

        {/* Active Policy Card */}
        <div className="card bg-gradient-to-br from-slate-900 via-slate-850 to-emerald-950 text-white p-5 shadow-xl border border-slate-800">
          <div className="flex items-center justify-between mb-3">
            <div className="flex items-center gap-1.5">
              <ShieldCheck className="w-5 h-5 text-emerald-400" />
              <span className="text-sm font-bold text-slate-200">Selected Plan: {policy.plan_name}</span>
            </div>
            <span className="font-mono text-xs text-slate-400">{policy.policy_number}</span>
          </div>

          <div className="grid grid-cols-2 gap-4 py-3 border-y border-slate-800/80 my-2">
            <div>
              <span className="text-[10px] text-slate-400 block font-medium uppercase">Coverage</span>
              <span className="text-2xl font-black text-emerald-300">{formatINR(policy.coverage_limit)}</span>
            </div>
            <div>
              <span className="text-[10px] text-slate-400 block font-medium uppercase">Premium</span>
              <span className="text-lg font-bold text-slate-100">{formatINR(policy.premium)}/week</span>
            </div>
          </div>

          <div className="space-y-1.5 pt-2 text-xs text-slate-300">
            <div className="flex items-center justify-between">
              <span className="flex items-center gap-1 text-slate-400">
                <Clock className="w-3.5 h-3.5" /> Valid until:
              </span>
              <strong className="text-slate-100">
                {new Date(policy.end_date).toLocaleDateString('en-IN', {
                  day: 'numeric',
                  month: 'short',
                  year: 'numeric',
                })}
              </strong>
            </div>
            <div className="flex items-center justify-between">
              <span className="flex items-center gap-1 text-slate-400">
                <MapPin className="w-3.5 h-3.5" /> Covered work zone:
              </span>
              <strong className="text-slate-100">{policy.covered_work_zone}</strong>
            </div>
          </div>
        </div>

        {/* Active Policy Action Grid (Section 11) */}
        <div>
          <h2 className="text-xs font-bold uppercase tracking-wider text-slate-500 mb-2.5">Policy Actions</h2>
          <div className="grid grid-cols-2 gap-2.5">
            <button
              onClick={() => navigate('/incomeshield/policy')}
              className="p-3.5 bg-white rounded-2xl border border-slate-200 hover:border-emerald-300 transition text-left flex items-start justify-between shadow-xs group"
            >
              <div>
                <ShieldCheck className="w-5 h-5 text-emerald-600 mb-1.5" />
                <span className="text-xs font-bold text-slate-800 block">Coverage Details</span>
                <span className="text-[10px] text-slate-500">Limits & triggers</span>
              </div>
              <ChevronRight className="w-4 h-4 text-slate-400 group-hover:text-emerald-600 transition" />
            </button>

            <button
              onClick={() => {
                if (hasDisruption && activeEvents[0]) {
                  navigate(`/incomeshield/events/${activeEvents[0].id}`)
                } else {
                  navigate('/incomeshield/policy')
                }
              }}
              className="p-3.5 bg-white rounded-2xl border border-slate-200 hover:border-amber-300 transition text-left flex items-start justify-between shadow-xs group"
            >
              <div>
                <CloudRain className="w-5 h-5 text-amber-600 mb-1.5" />
                <span className="text-xs font-bold text-slate-800 block">Event History</span>
                <span className="text-[10px] text-slate-500">Telemetry & triggers</span>
              </div>
              <ChevronRight className="w-4 h-4 text-slate-400 group-hover:text-amber-600 transition" />
            </button>

            <button
              onClick={() => navigate('/incomeshield/policy')}
              className="p-3.5 bg-white rounded-2xl border border-slate-200 hover:border-blue-300 transition text-left flex items-start justify-between shadow-xs group"
            >
              <div>
                <FileText className="w-5 h-5 text-blue-600 mb-1.5" />
                <span className="text-xs font-bold text-slate-800 block">Policy Documents</span>
                <span className="text-[10px] text-slate-500">Schedules & terms</span>
              </div>
              <ChevronRight className="w-4 h-4 text-slate-400 group-hover:text-blue-600 transition" />
            </button>

            <button
              onClick={() => navigate('/incomeshield/policy')}
              className="p-3.5 bg-white rounded-2xl border border-slate-200 hover:border-purple-300 transition text-left flex items-start justify-between shadow-xs group"
            >
              <div>
                <HelpCircle className="w-5 h-5 text-purple-600 mb-1.5" />
                <span className="text-xs font-bold text-slate-800 block">Support</span>
                <span className="text-[10px] text-slate-500">Helpline & claims desk</span>
              </div>
              <ChevronRight className="w-4 h-4 text-slate-400 group-hover:text-purple-600 transition" />
            </button>
          </div>
        </div>

        {/* Regulatory footer */}
        <div className="p-3.5 bg-slate-100 rounded-2xl border border-slate-200/70">
          <p className="text-[10px] text-slate-500 leading-relaxed text-center">
            Underwritten by <strong>{policy.partner_name || 'SafeWork Protection Partner'}</strong>. Parametric claim settlements are automated upon sensor threshold verification.
          </p>
        </div>
      </div>
    )
  }

  // ============================================================
  // STATE 2: NO ACTIVE POLICY — CLEAN INTRODUCTION (Section 1 & 12)
  // Clean discovery entry screen. NO preselected plans, NO income baseline yet.
  // ============================================================
  return (
    <div className="px-5 pb-8 animate-fade-in space-y-4 pt-2">
      {/* Header & Tagline */}
      <div className="pt-2">
        <div className="flex items-center gap-2 mb-2">
          <div className="p-2 bg-emerald-100 text-emerald-800 rounded-xl shadow-xs">
            <Umbrella className="w-5 h-5 text-emerald-700" />
          </div>
          <div>
            <span className="text-xs font-bold text-emerald-700 uppercase tracking-wider">LEVELLY IncomeShield</span>
            <p className="text-[11px] text-slate-500 font-medium">Parametric Income Protection</p>
          </div>
        </div>
        <h1 className="text-2xl font-black text-slate-900 tracking-tight leading-tight mt-2">
          Protect your income when disruption stops your work.
        </h1>
        <p className="text-xs text-slate-600 mt-2 leading-relaxed font-normal">
          Choose an income-protection plan designed for eligible disruptions that can affect your ability to earn.
        </p>
      </div>

      {/* Disruption Alert Banner if active */}
      {hasDisruption && (
        <div
          onClick={() => navigate('/incomeshield/plans')}
          className="p-3.5 bg-amber-500/10 border border-amber-300 rounded-2xl cursor-pointer hover:bg-amber-500/15 transition flex items-center justify-between shadow-xs"
        >
          <div className="flex items-center gap-2.5">
            <div className="p-2 bg-amber-500 text-white rounded-xl">
              <CloudRain className="w-4 h-4 animate-bounce" />
            </div>
            <div>
              <div className="flex items-center gap-1.5">
                <span className="text-xs font-bold text-amber-900">Active Weather Telemetry in Chennai</span>
                <span className="w-2 h-2 rounded-full bg-amber-500 animate-ping" />
              </div>
              <p className="text-[11px] text-amber-800 font-medium">
                Heavy rain conditions monitored across OMR-ECR and Velachery
              </p>
            </div>
          </div>
          <ChevronRight className="w-5 h-5 text-amber-700 flex-shrink-0" />
        </div>
      )}

      {/* Primary & Secondary Call to Actions (Section 1) */}
      <div className="card p-5 bg-gradient-to-b from-white to-emerald-50/40 border border-emerald-200 shadow-sm space-y-3.5">
        <div>
          <h2 className="text-base font-bold text-slate-900 mb-1">
            Parametric coverage made for gig delivery workers.
          </h2>
          <p className="text-xs text-slate-600 leading-relaxed">
            When severe rain, flooding, or extreme heat disrupts road delivery, IncomeShield automatically evaluates conditions and provides financial protection without manual claim forms.
          </p>
        </div>

        <div className="flex flex-col gap-2.5 pt-1">
          <button
            id="btn-explore-plans"
            onClick={() => navigate('/incomeshield/plans')}
            className="btn-primary w-full py-3.5 flex items-center justify-center gap-2 text-sm font-bold shadow-md shadow-emerald-700/20"
          >
            Explore Plans <ArrowRight className="w-4 h-4" />
          </button>
          <button
            id="btn-how-it-works"
            onClick={() => navigate('/incomeshield/how-it-works')}
            className="w-full py-3 rounded-xl border border-slate-200 bg-white hover:bg-slate-50 text-xs font-bold text-slate-700 text-center transition shadow-xs"
          >
            How It Works
          </button>
        </div>
      </div>

      {/* Feature Pillars */}
      <div className="grid grid-cols-3 gap-2 text-center">
        <div className="p-3 bg-white rounded-2xl border border-slate-200/80 shadow-xs">
          <CloudRain className="w-5 h-5 text-blue-600 mx-auto mb-1.5" />
          <span className="text-[11px] font-bold text-slate-800 block">Parametric Trigger</span>
          <span className="text-[9px] text-slate-500">Auto-sensor verified</span>
        </div>
        <div className="p-3 bg-white rounded-2xl border border-slate-200/80 shadow-xs">
          <ShieldCheck className="w-5 h-5 text-emerald-600 mx-auto mb-1.5" />
          <span className="text-[11px] font-bold text-slate-800 block">Weekly Shield</span>
          <span className="text-[9px] text-slate-500">Flexible micro-plans</span>
        </div>
        <div className="p-3 bg-white rounded-2xl border border-slate-200/80 shadow-xs">
          <TrendingUp className="w-5 h-5 text-amber-600 mx-auto mb-1.5" />
          <span className="text-[11px] font-bold text-slate-800 block">Direct Settlement</span>
          <span className="text-[9px] text-slate-500">Bank / UPI payout</span>
        </div>
      </div>

      {/* Regulatory Notice */}
      <div className="p-3.5 bg-slate-100/90 rounded-2xl border border-slate-200/70">
        <p className="text-[10px] text-slate-500 leading-relaxed text-center">
          <strong>Important:</strong> Parametric insurance is underwritten by licensed insurance partners. LEVELLY acts as a technology and resilience intelligence platform. Payout triggers depend on verified sensor metrics in registered zones.
        </p>
      </div>
    </div>
  )
}
