import { CheckCircle2, Clock, AlertTriangle, Circle } from 'lucide-react'

export type TimelineStatus =
  | 'MONITORING'
  | 'TRIGGER_NOT_REACHED'
  | 'TRIGGER_REACHED'
  | 'PAYOUT_PROCESSING'
  | 'PAYOUT_COMPLETED'

interface EventTimelineProps {
  status: TimelineStatus
  eventTime?: string
  className?: string
}

export default function EventTimeline({
  status = 'MONITORING',
  eventTime = 'Started 2h 45m ago',
  className = '',
}: EventTimelineProps) {
  const steps = [
    {
      id: 1,
      title: 'Event Detected',
      desc: 'IMD sensor radar telemetry confirmed',
      isDone: true,
    },
    {
      id: 2,
      title: 'Coverage Area Verified',
      desc: 'Chennai delivery zone validated',
      isDone: true,
    },
    {
      id: 3,
      title: 'Policy Active',
      desc: 'Weekly protection in effect',
      isDone: true,
    },
    {
      id: 4,
      title: 'Trigger Evaluation',
      desc:
        status === 'TRIGGER_NOT_REACHED'
          ? 'Threshold not met (coverage continues)'
          : status === 'MONITORING'
          ? 'Sampling 3-hour precipitation threshold...'
          : 'Parametric condition satisfied',
      isDone: status !== 'MONITORING',
      isActive: status === 'MONITORING',
      isFailed: status === 'TRIGGER_NOT_REACHED',
    },
    {
      id: 5,
      title: 'Payout Decision',
      desc:
        status === 'PAYOUT_COMPLETED'
          ? 'Settled by insurance partner'
          : status === 'PAYOUT_PROCESSING' || status === 'TRIGGER_REACHED'
          ? 'Insurer processing settlement'
          : status === 'TRIGGER_NOT_REACHED'
          ? 'No claim generated'
          : 'Awaiting trigger evaluation',
      isDone: status === 'PAYOUT_COMPLETED',
      isActive: status === 'PAYOUT_PROCESSING' || status === 'TRIGGER_REACHED',
      isIdle: status === 'MONITORING' || status === 'TRIGGER_NOT_REACHED',
    },
  ]

  return (
    <div className={`card p-4 border border-slate-200/90 shadow-sm ${className}`}>
      <div className="flex items-center justify-between pb-3 border-b border-slate-100 mb-4">
        <div>
          <h4 className="text-xs font-bold text-slate-800 uppercase tracking-wider">Event Verification Timeline</h4>
          <p className="text-[11px] text-slate-500">{eventTime}</p>
        </div>
        <span
          className={`text-[10px] font-bold px-2 py-0.5 rounded-full ${
            status === 'PAYOUT_COMPLETED'
              ? 'bg-emerald-100 text-emerald-800'
              : status === 'PAYOUT_PROCESSING' || status === 'TRIGGER_REACHED'
              ? 'bg-blue-100 text-blue-800'
              : status === 'TRIGGER_NOT_REACHED'
              ? 'bg-amber-100 text-amber-800'
              : 'bg-slate-100 text-slate-700'
          }`}
        >
          {status.replace(/_/g, ' ')}
        </span>
      </div>

      <div className="space-y-3 relative before:absolute before:left-3.5 before:top-2 before:bottom-2 before:w-0.5 before:bg-slate-200">
        {steps.map((s) => (
          <div key={s.id} className="flex items-start gap-3 relative z-10">
            {s.isDone ? (
              <div className="w-7 h-7 rounded-full bg-emerald-100 text-emerald-700 flex items-center justify-center flex-shrink-0 border-2 border-white shadow-xs">
                <CheckCircle2 className="w-4 h-4" />
              </div>
            ) : s.isActive ? (
              <div className="w-7 h-7 rounded-full bg-blue-600 text-white flex items-center justify-center flex-shrink-0 border-2 border-white shadow-xs animate-pulse">
                <Clock className="w-3.5 h-3.5" />
              </div>
            ) : s.isFailed ? (
              <div className="w-7 h-7 rounded-full bg-amber-100 text-amber-700 flex items-center justify-center flex-shrink-0 border-2 border-white shadow-xs">
                <AlertTriangle className="w-3.5 h-3.5" />
              </div>
            ) : (
              <div className="w-7 h-7 rounded-full bg-slate-100 text-slate-400 flex items-center justify-center flex-shrink-0 border-2 border-white shadow-xs">
                <Circle className="w-3 h-3" />
              </div>
            )}

            <div className="flex-1 pt-0.5">
              <p
                className={`text-xs font-bold leading-none ${
                  s.isDone
                    ? 'text-slate-900'
                    : s.isActive
                    ? 'text-blue-900'
                    : s.isFailed
                    ? 'text-amber-900'
                    : 'text-slate-400'
                }`}
              >
                {s.title}
              </p>
              <p className="text-[11px] text-slate-500 mt-0.5 leading-snug">{s.desc}</p>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
