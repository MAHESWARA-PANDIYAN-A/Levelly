
export function PlanCardSkeleton() {
  return (
    <div className="card p-5 space-y-4 animate-pulse">
      <div className="flex justify-between items-start">
        <div className="space-y-2 flex-1">
          <div className="h-5 bg-slate-200 rounded-md w-1/3" />
          <div className="h-3 bg-slate-100 rounded-md w-2/3" />
        </div>
        <div className="h-7 bg-slate-200 rounded-md w-16" />
      </div>
      <div className="h-10 bg-slate-100 rounded-xl" />
      <div className="h-10 bg-slate-200 rounded-xl" />
    </div>
  )
}

export function PolicyHeaderSkeleton() {
  return (
    <div className="card p-5 space-y-4 animate-pulse bg-slate-900">
      <div className="h-4 bg-slate-800 rounded w-1/4" />
      <div className="h-7 bg-slate-700 rounded w-1/2" />
      <div className="grid grid-cols-2 gap-3 pt-2">
        <div className="h-12 bg-slate-800 rounded-xl" />
        <div className="h-12 bg-slate-800 rounded-xl" />
      </div>
    </div>
  )
}

export function MonitoringSkeleton() {
  return (
    <div className="space-y-4 animate-pulse">
      <div className="h-32 bg-slate-200 rounded-2xl" />
      <div className="h-44 bg-slate-200 rounded-2xl" />
      <div className="h-36 bg-slate-200 rounded-2xl" />
    </div>
  )
}
