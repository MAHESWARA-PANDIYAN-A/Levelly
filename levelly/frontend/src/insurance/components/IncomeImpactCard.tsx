import { TrendingDown, Info, ShieldAlert } from 'lucide-react'

interface IncomeImpactCardProps {
  expectedDaily: number
  disruptedDaily: number
  impactAmount: number
  eventTitle?: string
  disclaimer?: string
  className?: string
}

const formatINR = (amt: number) =>
  new Intl.NumberFormat('en-IN', { style: 'currency', currency: 'INR', maximumFractionDigits: 0 }).format(amt)

export default function IncomeImpactCard({
  expectedDaily,
  disruptedDaily,
  impactAmount,
  eventTitle = 'Heavy Rainfall Disruption',
  disclaimer = "This estimate is based on your earning history. Your actual insurance payout depends on your policy terms and the insurance partner's determination.",
  className = '',
}: IncomeImpactCardProps) {
  return (
    <div className={`card bg-gradient-to-b from-white to-slate-50 border border-slate-200/80 shadow-sm ${className}`}>
      <div className="flex items-center justify-between pb-3 border-b border-slate-100 mb-3">
        <div className="flex items-center gap-2">
          <div className="p-1.5 bg-amber-50 rounded-lg text-amber-700">
            <ShieldAlert className="w-4 h-4" />
          </div>
          <div>
            <h3 className="text-xs font-bold text-slate-800 uppercase tracking-wider">Estimated Income Impact</h3>
            <p className="text-[11px] text-slate-500">{eventTitle}</p>
          </div>
        </div>
        <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-slate-100 text-slate-600">
          Powered by Income Intelligence
        </span>
      </div>

      {/* 3-Way Metrics Comparison */}
      <div className="grid grid-cols-3 gap-2 text-center py-2 mb-3">
        <div className="p-2.5 rounded-xl bg-slate-100/70 border border-slate-200/50">
          <span className="text-[10px] uppercase font-bold text-slate-500 block mb-0.5">Normal Expected</span>
          <span className="text-base font-extrabold text-slate-800">{formatINR(expectedDaily)}</span>
          <span className="text-[9px] text-slate-400 block mt-0.5">daily baseline</span>
        </div>

        <div className="p-2.5 rounded-xl bg-amber-50/70 border border-amber-200/50">
          <span className="text-[10px] uppercase font-bold text-amber-700 block mb-0.5">Disrupted</span>
          <span className="text-base font-extrabold text-amber-900">{formatINR(disruptedDaily)}</span>
          <span className="text-[9px] text-amber-600 block mt-0.5">estimated pace</span>
        </div>

        <div className="p-2.5 rounded-xl bg-rose-50 border border-rose-200">
          <span className="text-[10px] uppercase font-bold text-rose-700 block mb-0.5">Income Gap</span>
          <span className="text-base font-extrabold text-rose-700 flex items-center justify-center gap-0.5">
            <TrendingDown className="w-3.5 h-3.5" />
            {formatINR(impactAmount)}
          </span>
          <span className="text-[9px] text-rose-600 font-medium block mt-0.5">daily impact</span>
        </div>
      </div>

      {/* Mandatory Disclaimer */}
      <div className="p-2.5 rounded-xl bg-slate-100/90 border border-slate-200 flex items-start gap-2">
        <Info className="w-3.5 h-3.5 text-slate-500 mt-0.5 flex-shrink-0" />
        <p className="text-[10px] text-slate-600 leading-relaxed font-normal">
          {disclaimer}
        </p>
      </div>
    </div>
  )
}
