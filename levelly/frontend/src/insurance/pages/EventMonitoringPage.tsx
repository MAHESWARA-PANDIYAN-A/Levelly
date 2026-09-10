import { useParams, useNavigate } from 'react-router-dom'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import {
  ArrowLeft,
  CloudRain,
  AlertTriangle,
  CheckCircle2,
  ArrowRight,
  Sparkles,
  RefreshCw,
} from 'lucide-react'
import toast from 'react-hot-toast'
import { insuranceApi } from '../api/insuranceApi'
import { MonitoringSkeleton } from '../components/InsuranceSkeletons'
import CoverageZoneMap from '../components/CoverageZoneMap'
import IncomeImpactCard from '../components/IncomeImpactCard'
import EventTimeline, { type TimelineStatus } from '../components/EventTimeline'

export default function EventMonitoringPage() {
  const { eventId } = useParams()
  const navigate = useNavigate()
  const queryClient = useQueryClient()

  const { data: event, isLoading: eventLoading } = useQuery({
    queryKey: ['insurance-event', eventId],
    queryFn: () => insuranceApi.getEventDetails(Number(eventId)).then((r) => r.data),
  })

  const { data: impact } = useQuery({
    queryKey: ['insurance-event-impact', eventId],
    queryFn: () => insuranceApi.getEventImpact(Number(eventId)).then((r) => r.data),
  })

  const { data: triggerEval } = useQuery({
    queryKey: ['insurance-event-trigger', eventId],
    queryFn: () => insuranceApi.getEventTrigger(Number(eventId)).then((r) => r.data),
    retry: false,
  })

  const { data: payouts } = useQuery({
    queryKey: ['insurance-payouts'],
    queryFn: () => insuranceApi.getPayouts().then((r) => r.data),
  })

  const evaluateMutation = useMutation({
    mutationFn: () => insuranceApi.evaluateTriggerDemo(Number(eventId)),
    onSuccess: (res) => {
      toast.success(res.data.message)
      queryClient.invalidateQueries({ queryKey: ['insurance-event-trigger', eventId] })
      queryClient.invalidateQueries({ queryKey: ['insurance-payouts'] })
      queryClient.invalidateQueries({ queryKey: ['insurance-status'] })
    },
    onError: (err: any) => {
      toast.error(err.response?.data?.detail || 'Evaluation error')
    },
  })

  const relatedPayout = payouts?.find((p) => p.event_id === Number(eventId))

  if (eventLoading || !event) {
    return (
      <div className="px-5 pt-8 animate-fade-in space-y-4">
        <MonitoringSkeleton />
      </div>
    )
  }

  // Derive Timeline Status
  let timelineStatus: TimelineStatus = 'MONITORING'
  if (triggerEval?.status === 'REACHED') {
    if (relatedPayout?.status === 'COMPLETED') {
      timelineStatus = 'PAYOUT_COMPLETED'
    } else {
      timelineStatus = 'PAYOUT_PROCESSING'
    }
  } else if (triggerEval?.status === 'NOT_REACHED') {
    timelineStatus = 'TRIGGER_NOT_REACHED'
  }

  return (
    <div className="px-5 pb-8 animate-fade-in space-y-4 pt-2">
      <button
        onClick={() => navigate('/incomeshield')}
        className="flex items-center gap-2 text-xs font-semibold text-slate-500 hover:text-slate-800 transition py-1"
      >
        <ArrowLeft className="w-4 h-4" /> Back to IncomeShield
      </button>

      {/* SCREEN 10: DISRUPTION DETECTED HEADER */}
      <div className="card p-5 bg-gradient-to-br from-amber-500/15 via-white to-slate-50 border-2 border-amber-300 rounded-3xl shadow-sm">
        <div className="flex items-center gap-2 mb-2">
          <div className="p-2 rounded-xl bg-amber-500 text-white shadow-xs">
            <CloudRain className="w-5 h-5 animate-bounce" />
          </div>
          <div>
            <span className="text-[10px] font-extrabold uppercase tracking-widest text-amber-700 block">
              Disruption Detected
            </span>
            <h1 className="text-base font-black text-slate-900 leading-tight">
              {event.event_type.replace('_', ' ').toUpperCase()} in your work area
            </h1>
          </div>
        </div>

        <p className="text-xs text-slate-600 mt-1 leading-relaxed">
          Heavy precipitation telemetry has been detected in your covered delivery zone. Your policy conditions are being monitored against active weather radar.
        </p>

        <div className="grid grid-cols-2 gap-2 mt-3 pt-3 border-t border-amber-200/60 text-xs">
          <div>
            <span className="text-[10px] text-slate-400 block font-medium">Zone</span>
            <strong className="text-slate-800">{event.zone}</strong>
          </div>
          <div>
            <span className="text-[10px] text-slate-400 block font-medium">Duration</span>
            <strong className="text-slate-800">{event.duration}</strong>
          </div>
          <div>
            <span className="text-[10px] text-slate-400 block font-medium">Telemetry Source</span>
            <strong className="text-slate-800">{event.source}</strong>
          </div>
          <div>
            <span className="text-[10px] text-slate-400 block font-medium">Policy Status</span>
            <span className="font-bold text-emerald-700 bg-emerald-100/70 px-2 py-0.5 rounded-full inline-block text-[10px]">
              ACTIVE
            </span>
          </div>
        </div>

        <p className="text-[10px] text-amber-900 bg-amber-100/80 p-2 rounded-xl border border-amber-200/80 mt-3 font-medium">
          Policy conditions are evaluated objectively. Payout is determined by the parametric trigger.
        </p>
      </div>

      {/* SCREEN 13: TRIGGER REACHED BANNER */}
      {triggerEval?.status === 'REACHED' && (
        <div className="card p-4 bg-emerald-50 border-2 border-emerald-300 rounded-2xl shadow-sm text-left animate-fade-in">
          <div className="flex items-center gap-2 mb-1 text-emerald-800 font-extrabold text-sm">
            <CheckCircle2 className="w-5 h-5 text-emerald-600 flex-shrink-0" />
            <span>Your covered trigger has been reached!</span>
          </div>
          <p className="text-xs text-emerald-700 leading-relaxed">
            {triggerEval.reason} Your insurance partner is processing the applicable claim settlement.
          </p>
          {relatedPayout ? (
            <button
              onClick={() => navigate(`/incomeshield/payouts/${relatedPayout.id}`)}
              className="mt-3 w-full py-2.5 px-3 bg-emerald-600 text-white rounded-xl text-xs font-bold shadow-xs hover:bg-emerald-700 transition flex items-center justify-center gap-1.5"
            >
              View Payout Status ({relatedPayout.status}) <ArrowRight className="w-3.5 h-3.5" />
            </button>
          ) : (
            <div className="mt-2 text-[11px] text-emerald-600 font-semibold">
              Payout initiation in progress with SafeWork Protection Partner...
            </div>
          )}
        </div>
      )}

      {/* SCREEN 14: TRIGGER NOT REACHED BANNER */}
      {triggerEval?.status === 'NOT_REACHED' && (
        <div className="card p-4 bg-slate-50 border-2 border-slate-200 rounded-2xl shadow-sm text-left animate-fade-in">
          <div className="flex items-center gap-2 mb-1 text-slate-800 font-bold text-sm">
            <AlertTriangle className="w-4 h-4 text-amber-600 flex-shrink-0" />
            <span>Coverage trigger not reached</span>
          </div>
          <p className="text-xs text-slate-600 leading-relaxed">
            {triggerEval.reason} The detected event does not currently satisfy the trigger conditions defined in your policy.
          </p>
          <p className="text-[11px] text-slate-500 mt-2">
            Your protection remains active for future eligible covered events during this weekly term.
          </p>
          <button
            onClick={() => navigate('/incomeshield/policy')}
            className="mt-3 py-2 px-3 bg-white border border-slate-200 rounded-xl text-xs font-bold text-slate-700 hover:bg-slate-100 transition"
          >
            View Coverage Details
          </button>
        </div>
      )}

      {/* SCREEN 11: EVENT MONITORING TIMELINE */}
      <EventTimeline
        status={timelineStatus}
        eventTime={`Started ${event.duration} ago (${event.source})`}
      />

      {/* SCREEN 12: ESTIMATED INCOME IMPACT CARD */}
      {impact && (
        <IncomeImpactCard
          expectedDaily={impact.expected_daily_income}
          disruptedDaily={impact.estimated_disrupted_income}
          impactAmount={impact.estimated_income_impact}
          eventTitle={`${event.event_type.replace('_', ' ')} (${event.zone})`}
          disclaimer={impact.disclaimer}
        />
      )}

      {/* Zone Map with Active Disruption Hotspot */}
      <CoverageZoneMap
        primaryZone={event.zone}
        affectedSubzones={event.telemetry_data?.affected_subzones || ['Chennai South', 'Velachery']}
        isDisruptionActive={true}
      />

      {/* Interactive Evaluation Trigger (for demonstration & testing) */}
      <div className="p-3 bg-slate-100 rounded-2xl border border-slate-200 text-center space-y-2">
        <span className="text-[10px] font-bold text-slate-500 uppercase tracking-wider block">
          Parametric Verification Engine
        </span>
        <button
          onClick={() => evaluateMutation.mutate()}
          disabled={evaluateMutation.isPending}
          className="w-full py-2.5 px-3 bg-slate-900 hover:bg-slate-800 text-white rounded-xl text-xs font-bold transition flex items-center justify-center gap-1.5 shadow-sm"
        >
          {evaluateMutation.isPending ? (
            <RefreshCw className="w-3.5 h-3.5 animate-spin" />
          ) : (
            <Sparkles className="w-3.5 h-3.5 text-emerald-400" />
          )}
          ⚡ Run Parametric Trigger Evaluation
        </button>
      </div>
    </div>
  )
}
