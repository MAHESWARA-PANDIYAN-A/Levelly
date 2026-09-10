import { MapPin, AlertCircle, CheckCircle2 } from 'lucide-react'

interface CoverageZoneMapProps {
  primaryZone?: string
  affectedSubzones?: string[]
  isDisruptionActive?: boolean
  className?: string
}

const subzones = [
  { id: 'north', name: 'Chennai North (Ennore/Madhavaram)', x: 140, y: 35, isPrimary: true },
  { id: 'central', name: 'Chennai Central (T.Nagar/Anna Nagar)', x: 150, y: 80, isPrimary: true },
  { id: 'south', name: 'Chennai South (Velachery/Guindy)', x: 140, y: 130, isPrimary: true },
  { id: 'omr', name: 'OMR - ECR Tech Corridor', x: 180, y: 175, isPrimary: true },
  { id: 'west', name: 'West Chennai (Porur/Tambaram)', x: 80, y: 125, isPrimary: true },
]

export default function CoverageZoneMap({
  primaryZone = 'Chennai Delivery Zone',
  affectedSubzones = ['Chennai South', 'OMR-ECR', 'Velachery'],
  isDisruptionActive = false,
  className = '',
}: CoverageZoneMapProps) {
  return (
    <div className={`p-4 bg-slate-900 text-white rounded-2xl shadow-inner overflow-hidden relative ${className}`}>
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2">
          <MapPin className="w-4 h-4 text-emerald-400" />
          <span className="text-xs font-bold text-slate-200 tracking-wide uppercase">{primaryZone}</span>
        </div>
        {isDisruptionActive ? (
          <span className="flex items-center gap-1 text-[11px] font-bold px-2 py-0.5 rounded-full bg-red-500/20 text-red-400 border border-red-500/30 animate-pulse">
            <AlertCircle className="w-3 h-3" /> Disruption Monitored
          </span>
        ) : (
          <span className="flex items-center gap-1 text-[11px] font-medium px-2 py-0.5 rounded-full bg-emerald-500/20 text-emerald-400 border border-emerald-500/30">
            <CheckCircle2 className="w-3 h-3" /> Zone Protected
          </span>
        )}
      </div>

      {/* Stylized Coastal Line & Zone Grid */}
      <div className="relative w-full h-44 bg-slate-950/70 rounded-xl border border-slate-800 flex items-center justify-center p-2">
        <svg viewBox="0 0 260 210" className="w-full h-full max-h-40">
          <defs>
            <linearGradient id="coastGrad" x1="0%" y1="0%" x2="100%" y2="0%">
              <stop offset="0%" stopColor="#0f172a" />
              <stop offset="85%" stopColor="#0284c7" stopOpacity="0.25" />
              <stop offset="100%" stopColor="#0284c7" stopOpacity="0.6" />
            </linearGradient>
            <radialGradient id="disruptPulse" cx="50%" cy="50%" r="50%">
              <stop offset="0%" stopColor="#ef4444" stopOpacity="0.7" />
              <stop offset="100%" stopColor="#ef4444" stopOpacity="0.0" />
            </radialGradient>
          </defs>

          {/* Bay of Bengal Coast Outline */}
          <path
            d="M 200,0 C 190,50 185,110 205,170 C 215,190 220,210 225,210 L 260,210 L 260,0 Z"
            fill="url(#coastGrad)"
          />

          {/* Zone Connection Mesh */}
          <line x1="140" y1="35" x2="150" y2="80" stroke="#334155" strokeWidth="1" strokeDasharray="3 3" />
          <line x1="150" y1="80" x2="140" y2="130" stroke="#334155" strokeWidth="1" strokeDasharray="3 3" />
          <line x1="140" y1="130" x2="180" y2="175" stroke="#334155" strokeWidth="1" strokeDasharray="3 3" />
          <line x1="140" y1="130" x2="80" y2="125" stroke="#334155" strokeWidth="1" strokeDasharray="3 3" />

          {/* Disruption Hotspot Glow if active */}
          {isDisruptionActive && (
            <circle cx="150" cy="145" r="45" fill="url(#disruptPulse)" className="animate-pulse" />
          )}

          {/* Subzone Nodes */}
          {subzones.map((sz) => {
            const isAffected =
              isDisruptionActive &&
              affectedSubzones.some((a) => sz.name.toLowerCase().includes(a.toLowerCase()))

            return (
              <g key={sz.id} className="transition-all cursor-pointer">
                {isAffected && (
                  <circle cx={sz.x} cy={sz.y} r="14" fill="#ef4444" fillOpacity="0.2" className="animate-ping" />
                )}
                <circle
                  cx={sz.x}
                  cy={sz.y}
                  r={isAffected ? '7' : '5'}
                  fill={isAffected ? '#ef4444' : '#10b981'}
                  stroke="#ffffff"
                  strokeWidth="1.5"
                />
                <text
                  x={sz.x + (sz.id === 'west' ? -8 : 9)}
                  y={sz.y + 3}
                  fontSize="8"
                  fontWeight="bold"
                  textAnchor={sz.id === 'west' ? 'end' : 'start'}
                  fill={isAffected ? '#fca5a5' : '#cbd5e1'}
                >
                  {sz.id.toUpperCase()}
                </text>
              </g>
            )
          })}
        </svg>

        {/* Legend */}
        <div className="absolute bottom-2 left-3 right-3 flex items-center justify-between text-[10px] text-slate-400 bg-slate-900/90 backdrop-blur px-2 py-1 rounded-lg border border-slate-800">
          <div className="flex items-center gap-1.5">
            <span className="w-2 h-2 rounded-full bg-emerald-500 inline-block" />
            <span>Active Coverage Zone</span>
          </div>
          {isDisruptionActive && (
            <div className="flex items-center gap-1.5">
              <span className="w-2 h-2 rounded-full bg-red-500 inline-block animate-pulse" />
              <span className="text-red-300 font-semibold">Affected Telemetry Area</span>
            </div>
          )}
        </div>
      </div>
      <p className="text-[10px] text-slate-400 mt-2 text-center">
        Zone-level coverage based on registered courier dispatch coordinates. Precise GPS is never exposed.
      </p>
    </div>
  )
}
