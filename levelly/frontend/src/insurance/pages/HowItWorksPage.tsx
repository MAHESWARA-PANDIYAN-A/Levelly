import { useNavigate } from 'react-router-dom'
import {
  ArrowLeft,
  CloudRain,
  Sliders,
  CheckCircle2,
  Building2,
  Wallet,
  ArrowRight,
  Info,
  Shield,
} from 'lucide-react'

export default function HowItWorksPage() {
  const navigate = useNavigate()

  const workflowSteps = [
    {
      num: '01',
      title: 'EXTERNAL DISRUPTION',
      desc: 'Severe weather or civic disruption occurs in your registered delivery zone (e.g., heavy downpour >= 50mm over 3 hours).',
      icon: CloudRain,
      color: 'bg-blue-50 text-blue-600 border-blue-200',
    },
    {
      num: '02',
      title: 'COVERED TRIGGER',
      desc: 'IMD regional radars and verified civic telemetry sample conditions against your policy’s predefined parametric threshold.',
      icon: Sliders,
      color: 'bg-indigo-50 text-indigo-600 border-indigo-200',
    },
    {
      num: '03',
      title: 'TELEMETRY VERIFICATION',
      desc: 'Conditions are verified objectively. No claim forms, inspector appointments, or manual invoices required.',
      icon: CheckCircle2,
      color: 'bg-amber-50 text-amber-600 border-amber-200',
    },
    {
      num: '04',
      title: 'INSURANCE PARTNER DECISION',
      desc: 'The regulated insurance partner confirms policy compliance and authorizes settlement based on your plan coverage limit.',
      icon: Building2,
      color: 'bg-emerald-50 text-emerald-600 border-emerald-200',
    },
    {
      num: '05',
      title: 'CLAIM PAYOUT',
      desc: 'Settlement is transferred directly via instant UPI to your linked bank account, keeping your household liquidity intact.',
      icon: Wallet,
      color: 'bg-teal-50 text-teal-600 border-teal-200',
    },
  ]

  return (
    <div className="px-5 pb-8 animate-fade-in space-y-4 pt-2">
      <button
        onClick={() => navigate('/incomeshield')}
        className="flex items-center gap-2 text-xs font-semibold text-slate-500 hover:text-slate-800 transition py-1"
      >
        <ArrowLeft className="w-4 h-4" /> Back to IncomeShield
      </button>

      <div>
        <h1 className="text-xl font-bold text-slate-900">How IncomeShield Works</h1>
        <p className="text-xs text-slate-500 mt-0.5">
          Parametric income protection designed specifically for gig workers.
        </p>
      </div>

      {/* 5-Step Flowchart */}
      <div className="space-y-2.5">
        {workflowSteps.map((step) => {
          const Icon = step.icon
          return (
            <div
              key={step.num}
              className="card p-3.5 bg-white border border-slate-200/80 shadow-xs flex items-start gap-3 relative"
            >
              <div className={`p-2.5 rounded-xl border flex-shrink-0 ${step.color}`}>
                <Icon className="w-5 h-5" />
              </div>
              <div className="flex-1">
                <div className="flex items-center justify-between mb-0.5">
                  <h3 className="text-xs font-bold text-slate-900">{step.title}</h3>
                  <span className="text-[10px] font-black font-mono text-slate-400">{step.num}</span>
                </div>
                <p className="text-[11px] text-slate-600 leading-relaxed">{step.desc}</p>
              </div>
            </div>
          )
        })}
      </div>

      {/* Role Clarity Box */}
      <div className="card p-4 bg-slate-900 text-white border border-slate-800 space-y-3">
        <div className="flex items-center gap-2 text-emerald-400">
          <Shield className="w-4 h-4" />
          <h4 className="text-xs font-bold uppercase tracking-wider">Role of LEVELLY vs Insurance Partner</h4>
        </div>
        <p className="text-xs text-slate-300 leading-relaxed">
          <strong>LEVELLY</strong> uses your earning history and Income Intelligence to estimate how a disruption could affect your income and makes discovering policies seamless.
        </p>
        <p className="text-xs text-slate-300 leading-relaxed">
          <strong>The Insurance Partner</strong> acts as the regulated underwriter, determining actual policy terms, condition evaluations, and processing claim payouts.
        </p>
        <div className="p-2.5 rounded-xl bg-slate-800/80 border border-slate-700 flex items-start gap-2">
          <Info className="w-4 h-4 text-amber-400 flex-shrink-0 mt-0.5" />
          <p className="text-[11px] text-amber-200 leading-snug">
            <strong>Important distinction:</strong> Estimated income impact calculated by LEVELLY is an earning forecast and is not the same as your contractual insurance payout.
          </p>
        </div>
      </div>

      <button
        onClick={() => navigate('/incomeshield/plans')}
        className="btn-primary w-full py-3.5 flex items-center justify-center gap-2 text-sm font-bold shadow-md"
      >
        Explore Available Plans <ArrowRight className="w-4 h-4" />
      </button>
    </div>
  )
}
