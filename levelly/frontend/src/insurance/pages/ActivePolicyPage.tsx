import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { useNavigate } from 'react-router-dom'
import {
  ArrowLeft,
  ShieldCheck,
  FileText,
  Clock,
  ChevronRight,
  ExternalLink,
  MapPin,
  Sparkles,
  PhoneCall,
  Mail,
  CloudRain,
} from 'lucide-react'
import { insuranceApi } from '../api/insuranceApi'
import { PolicyHeaderSkeleton } from '../components/InsuranceSkeletons'
import CoverageZoneMap from '../components/CoverageZoneMap'

const formatINR = (amt: number) =>
  new Intl.NumberFormat('en-IN', { style: 'currency', currency: 'INR', maximumFractionDigits: 0 }).format(amt)

export default function ActivePolicyPage() {
  const navigate = useNavigate()
  const [activeTab, setActiveTab] = useState<'details' | 'history' | 'documents' | 'support'>('details')

  const { data: policyData, isLoading: policyLoading } = useQuery({
    queryKey: ['insurance-policy'],
    queryFn: () => insuranceApi.getPolicy().then((r) => r.data),
  })

  const { data: payouts } = useQuery({
    queryKey: ['insurance-payouts'],
    queryFn: () => insuranceApi.getPayouts().then((r) => r.data),
  })

  const { data: events } = useQuery({
    queryKey: ['insurance-events'],
    queryFn: () => insuranceApi.getEvents().then((r) => r.data),
  })

  const { data: documents } = useQuery({
    queryKey: ['insurance-documents'],
    queryFn: () => insuranceApi.getDocuments().then((r) => r.data),
  })

  const { data: supportInfo } = useQuery({
    queryKey: ['insurance-support'],
    queryFn: () => insuranceApi.getSupport().then((r) => r.data),
  })

  const policy = policyData?.policy

  if (policyLoading) {
    return (
      <div className="px-5 pb-8 animate-fade-in pt-4">
        <PolicyHeaderSkeleton />
      </div>
    )
  }

  if (!policy) {
    return (
      <div className="px-5 pb-8 animate-fade-in text-center pt-8 space-y-4">
        <ShieldCheck className="w-12 h-12 mx-auto text-slate-300" />
        <h2 className="text-lg font-bold text-slate-800">No Active Policy Found</h2>
        <p className="text-xs text-slate-500 max-w-xs mx-auto">
          You are not currently enrolled in IncomeShield. Browse our weekly plans to protect against disruption.
        </p>
        <button
          onClick={() => navigate('/incomeshield/plans')}
          className="btn-primary py-3 px-6 text-xs font-bold"
        >
          Explore Protection Plans
        </button>
      </div>
    )
  }

  return (
    <div className="px-5 pb-8 animate-fade-in space-y-4 pt-2">
      <button
        onClick={() => navigate('/incomeshield')}
        className="flex items-center gap-2 text-xs font-semibold text-slate-500 hover:text-slate-800 transition py-1"
      >
        <ArrowLeft className="w-4 h-4" /> Back to IncomeShield
      </button>

      {/* Policy Card Header */}
      <div className="card bg-gradient-to-br from-slate-900 via-slate-850 to-emerald-950 text-white p-5 rounded-3xl shadow-xl border border-slate-800">
        <div className="flex items-center justify-between mb-2">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-xl bg-emerald-500/20 text-emerald-400 flex items-center justify-center border border-emerald-500/30">
              <ShieldCheck className="w-5 h-5" />
            </div>
            <div>
              <h1 className="text-base font-black text-white">{policy.plan_name}</h1>
              <p className="text-[10px] text-slate-400 font-mono">No. {policy.policy_number}</p>
            </div>
          </div>
          <span className="px-2.5 py-0.5 text-[10px] font-black rounded-full bg-emerald-500/20 text-emerald-300 border border-emerald-500/40">
            {policy.status}
          </span>
        </div>

        <div className="grid grid-cols-2 gap-3 py-3 border-y border-slate-800/80 my-2">
          <div>
            <span className="text-[10px] text-slate-400 block uppercase font-medium">Coverage Limit</span>
            <span className="text-xl font-black text-emerald-300">{formatINR(policy.coverage_limit)}</span>
          </div>
          <div>
            <span className="text-[10px] text-slate-400 block uppercase font-medium">Valid Until</span>
            <span className="text-sm font-bold text-slate-200 mt-1 block">
              {new Date(policy.end_date).toLocaleDateString('en-IN', {
                day: 'numeric',
                month: 'short',
                year: 'numeric',
              })}
            </span>
          </div>
        </div>

        <div className="flex items-center justify-between text-xs text-slate-300 pt-1">
          <span>Premium: <strong>{formatINR(policy.premium)}/wk</strong></span>
          <span className="flex items-center gap-1">
            <MapPin className="w-3.5 h-3.5 text-emerald-400" />
            <strong>{policy.covered_work_zone}</strong>
          </span>
        </div>
      </div>

      {/* Navigation Tabs */}
      <div className="flex items-center justify-between border-b border-slate-200 text-xs font-bold text-slate-500">
        <button
          onClick={() => setActiveTab('details')}
          className={`pb-2.5 px-2 border-b-2 transition ${
            activeTab === 'details' ? 'border-emerald-600 text-emerald-700 font-black' : 'border-transparent'
          }`}
        >
          Coverage Details
        </button>
        <button
          onClick={() => setActiveTab('history')}
          className={`pb-2.5 px-2 border-b-2 transition ${
            activeTab === 'history' ? 'border-emerald-600 text-emerald-700 font-black' : 'border-transparent'
          }`}
        >
          Event History
        </button>
        <button
          onClick={() => setActiveTab('documents')}
          className={`pb-2.5 px-2 border-b-2 transition ${
            activeTab === 'documents' ? 'border-emerald-600 text-emerald-700 font-black' : 'border-transparent'
          }`}
        >
          Documents
        </button>
        <button
          onClick={() => setActiveTab('support')}
          className={`pb-2.5 px-2 border-b-2 transition ${
            activeTab === 'support' ? 'border-emerald-600 text-emerald-700 font-black' : 'border-transparent'
          }`}
        >
          Support
        </button>
      </div>

      {/* TAB 1: COVERAGE DETAILS */}
      {activeTab === 'details' && (
        <div className="space-y-4 animate-fade-in">
          <CoverageZoneMap
            primaryZone={policy.covered_work_zone}
            affectedSubzones={['Chennai South', 'Velachery', 'OMR-ECR']}
          />

          <div className="card p-4 bg-white border border-slate-200/80 shadow-xs space-y-2 text-xs">
            <h4 className="font-bold text-slate-900 mb-1">Underwriting Scope & Terms</h4>
            <div className="flex justify-between py-1.5 border-b border-slate-100">
              <span className="text-slate-500">Underwriting Partner</span>
              <span className="font-bold text-slate-800">{policy.partner_name}</span>
            </div>
            <div className="flex justify-between py-1.5 border-b border-slate-100">
              <span className="text-slate-500">Waiting Period</span>
              <span className="font-bold text-slate-800">24 hours from inception</span>
            </div>
            <div className="flex justify-between py-1.5 border-b border-slate-100">
              <span className="text-slate-500">Claim Settlement</span>
              <span className="font-bold text-emerald-700">Parametric Automatic Settlement</span>
            </div>
            <div className="flex justify-between py-1.5">
              <span className="text-slate-500">Renewal Cycle</span>
              <span className="font-bold text-slate-800">Weekly On-Demand</span>
            </div>
          </div>

          {/* Quick link to Disruption Monitor if active */}
          {events && events.length > 0 && (
            <div
              onClick={() => navigate(`/incomeshield/events/${events[0].id}`)}
              className="p-3 bg-amber-500/10 border border-amber-300 rounded-2xl cursor-pointer hover:bg-amber-500/15 transition flex items-center justify-between"
            >
              <div className="flex items-center gap-2 text-xs text-amber-900">
                <CloudRain className="w-4 h-4 text-amber-700" />
                <span>Active disruption detected: <strong>{events[0].event_type.replace('_', ' ')}</strong></span>
              </div>
              <ChevronRight className="w-4 h-4 text-amber-700" />
            </div>
          )}
        </div>
      )}

      {/* TAB 2: SCREEN 18 — POLICY HISTORY */}
      {activeTab === 'history' && (
        <div className="space-y-3 animate-fade-in">
          <div className="flex justify-between items-center text-xs text-slate-500 px-1">
            <span>Historical Disruption Events & Payouts</span>
            <span>{payouts?.length || 0} Records</span>
          </div>

          {(!payouts || payouts.length === 0) && (!events || events.length === 0) ? (
            <div className="card p-6 text-center text-slate-400">
              <Clock className="w-8 h-8 mx-auto mb-2 text-slate-300" />
              <p className="text-xs font-semibold">No disruption events recorded during this term</p>
            </div>
          ) : (
            <div className="space-y-2.5">
              {payouts?.map((p) => (
                <div
                  key={p.id}
                  onClick={() => navigate(`/incomeshield/payouts/${p.id}`)}
                  className="card p-3.5 bg-white border border-slate-200/80 shadow-xs cursor-pointer hover:shadow-sm transition"
                >
                  <div className="flex justify-between items-start mb-1">
                    <div>
                      <h4 className="text-xs font-bold text-slate-900">{p.reason}</h4>
                      <p className="text-[10px] text-slate-500">
                        {new Date(p.created_at).toLocaleDateString('en-IN', {
                          day: 'numeric',
                          month: 'short',
                          year: 'numeric',
                        })}
                      </p>
                    </div>
                    <span
                      className={`text-[10px] font-bold px-2 py-0.5 rounded-full ${
                        p.status === 'COMPLETED'
                          ? 'bg-emerald-100 text-emerald-800'
                          : 'bg-blue-100 text-blue-800'
                      }`}
                    >
                      {p.status}
                    </span>
                  </div>

                  <div className="flex justify-between items-center text-xs mt-2 pt-2 border-t border-slate-100">
                    <span className="text-slate-500 text-[11px]">Settlement Amount</span>
                    <span className="font-extrabold text-emerald-700">
                      {p.amount ? formatINR(p.amount) : 'Pending partner'}
                    </span>
                  </div>
                </div>
              ))}

              {events?.map((e) => (
                <div
                  key={`event-${e.id}`}
                  onClick={() => navigate(`/incomeshield/events/${e.id}`)}
                  className="card p-3.5 bg-slate-50 border border-slate-200 shadow-xs cursor-pointer hover:bg-slate-100 transition"
                >
                  <div className="flex justify-between items-start">
                    <div>
                      <h4 className="text-xs font-bold text-slate-800">{e.event_type.replace('_', ' ')}</h4>
                      <p className="text-[10px] text-slate-500">{e.zone} • {e.duration}</p>
                    </div>
                    <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-slate-200 text-slate-700">
                      {e.verification_status}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* TAB 3: SCREEN 19 — POLICY DOCUMENTS */}
      {activeTab === 'documents' && (
        <div className="space-y-3 animate-fade-in">
          <p className="text-xs text-slate-500 px-1">
            Access official legal schedules and terms underwritten by SafeWork Protection Partner.
          </p>

          <div className="space-y-2.5">
            {documents?.map((doc, idx) => (
              <div
                key={idx}
                className="card p-3.5 bg-white border border-slate-200/80 shadow-xs flex items-center justify-between"
              >
                <div className="flex items-center gap-2.5">
                  <div className="p-2 rounded-xl bg-slate-100 text-slate-600">
                    <FileText className="w-4 h-4" />
                  </div>
                  <div>
                    <h4 className="text-xs font-bold text-slate-900">{doc.title}</h4>
                    <span className="text-[10px] text-slate-400 uppercase font-semibold">
                      {doc.document_type.replace(/_/g, ' ')}
                    </span>
                  </div>
                </div>
                <a
                  href={doc.file_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="p-1.5 rounded-lg text-slate-400 hover:text-emerald-700 hover:bg-emerald-50 transition"
                  title="Open Document"
                >
                  <ExternalLink className="w-4 h-4" />
                </a>
              </div>
            ))}
          </div>

          <div className="p-3 bg-slate-100 rounded-2xl text-[10px] text-slate-500 leading-relaxed">
            All schedules are cryptographically verified by the insurer. Downloadable PDF receipts are sent to your registered email.
          </div>
        </div>
      )}

      {/* TAB 4: SCREEN 20 — SUPPORT */}
      {activeTab === 'support' && (
        <div className="space-y-3 animate-fade-in">
          <div className="card p-4 bg-white border border-slate-200/80 shadow-xs space-y-3">
            <h4 className="text-xs font-bold text-slate-900 uppercase tracking-wider">Frequently Asked Questions</h4>
            <div className="space-y-2.5">
              {supportInfo?.faqs?.map((f: any, i: number) => (
                <div key={i} className="p-2.5 bg-slate-50 rounded-xl border border-slate-100 text-xs">
                  <span className="text-[10px] font-bold text-emerald-700 uppercase tracking-wider block mb-0.5">
                    {f.topic}
                  </span>
                  <p className="font-bold text-slate-900 mb-1">{f.question}</p>
                  <p className="text-slate-600 leading-relaxed text-[11px]">{f.answer}</p>
                </div>
              ))}
            </div>
          </div>

          <div className="card p-4 bg-slate-900 text-white border border-slate-800 space-y-2.5 text-xs">
            <h4 className="font-bold uppercase tracking-wider text-emerald-400 text-xs">Official Helplines</h4>
            <div className="flex items-center gap-2">
              <PhoneCall className="w-4 h-4 text-slate-400" />
              <span>Toll-Free Helpline: <strong>{supportInfo?.helpline || '1800-419-7443'}</strong></span>
            </div>
            <div className="flex items-center gap-2">
              <Mail className="w-4 h-4 text-slate-400" />
              <span>Claims Desk: <strong>{supportInfo?.email || 'incomeshield-support@levelly.in'}</strong></span>
            </div>
            <div className="pt-2 border-t border-slate-800">
              <button
                onClick={() => navigate('/coach')}
                className="w-full py-2 px-3 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white font-bold text-xs text-center transition flex items-center justify-center gap-1.5"
              >
                <Sparkles className="w-3.5 h-3.5" /> Ask Levelly Coach About IncomeShield
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
