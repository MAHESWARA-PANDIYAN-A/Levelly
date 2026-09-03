import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useNavigate } from 'react-router-dom'
import { 
  Users, 
  Sliders, 
  TrendingUp, 
  FileText, 
  ShieldAlert, 
  ArrowRight, 
  LogOut, 
  RefreshCw, 
  Search, 
  Check, 
  ShieldCheck 
} from 'lucide-react'
import { adminAPI } from '../lib/api'
import { useAuthStore } from '../store/authStore'
import toast from 'react-hot-toast'

export default function AdminDashboardPage() {
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const { user, clearAuth } = useAuthStore()

  const [activeTab, setActiveTab] = useState<'overview' | 'users' | 'policies' | 'investments' | 'audit'>('overview')
  const [searchTerm, setSearchTerm] = useState('')
  const [distressFilter, setDistressFilter] = useState<string>('ALL')
  const [editingCategory, setEditingCategory] = useState<string | null>(null)
  const [newPercentage, setNewPercentage] = useState<number>(0)

  // 1. Distress Overview
  const { data: overview, isLoading: loadingOverview, refetch: refetchOverview } = useQuery({
    queryKey: ['admin-distress-overview'],
    queryFn: () => adminAPI.getDistressOverview().then(r => r.data),
  })

  // 2. Users Roster
  const { data: users, isLoading: loadingUsers } = useQuery({
    queryKey: ['admin-users'],
    queryFn: () => adminAPI.getUsers(100).then(r => r.data),
  })

  // 3. Category Policies
  const { data: policies, isLoading: loadingPolicies } = useQuery({
    queryKey: ['admin-policies'],
    queryFn: () => adminAPI.getCategoryPolicies().then(r => r.data),
  })

  // 4. Investment Products
  const { data: products, isLoading: loadingProducts } = useQuery({
    queryKey: ['admin-products'],
    queryFn: () => adminAPI.getInvestmentProducts().then(r => r.data),
  })

  // 5. Audit Logs
  const { data: auditLogs, isLoading: loadingAudit } = useQuery({
    queryKey: ['admin-audit-logs'],
    queryFn: () => adminAPI.getAuditLogs(50).then(r => r.data),
  })

  // Mutation for updating category policy
  const updatePolicyMutation = useMutation({
    mutationFn: ({ category, pct }: { category: string; pct: number }) =>
      adminAPI.updateCategoryPolicy(category, { base_percentage: pct }),
    onSuccess: (_, vars) => {
      queryClient.invalidateQueries({ queryKey: ['admin-policies'] })
      toast.success(`Updated ${vars.category} baseline to ${(vars.pct * 100).toFixed(1)}%`)
      setEditingCategory(null)
    },
    onError: (err: any) => {
      toast.error(err?.response?.data?.detail || 'Failed to update policy')
    },
  })

  const handleLogout = () => {
    clearAuth()
    navigate('/login')
  }

  // Filter users
  const filteredUsers = (users || []).filter((u: any) => {
    const matchesSearch = 
      u.full_name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      u.email?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      u.occupation?.toLowerCase().includes(searchTerm.toLowerCase())
    const matchesDistress = distressFilter === 'ALL' || u.distress_level === distressFilter
    return matchesSearch && matchesDistress
  })

  return (
    <div className="min-h-dvh bg-gray-50 text-gray-900 pb-16">
      {/* Top Admin Header */}
      <header className="bg-slate-900 text-white border-b border-slate-800 sticky top-0 z-30 shadow-md">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 py-4 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 bg-emerald-600 rounded-xl flex items-center justify-center font-black text-white text-lg shadow-sm">
              L
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h1 className="text-xl font-bold tracking-tight">LEVELLY Ops Portal</h1>
                <span className="bg-emerald-500/20 text-emerald-300 text-xs font-semibold px-2 py-0.5 rounded-full border border-emerald-500/30">
                  Admin
                </span>
              </div>
              <p className="text-xs text-slate-400">
                Financial Intelligence & Platform Governance • <span className="text-emerald-400 font-mono">{user?.email || 'admin@levelly.app'}</span>
              </p>
            </div>
          </div>

          <div className="flex items-center gap-2 sm:gap-3">
            <button
              onClick={() => navigate('/')}
              className="flex items-center gap-1.5 px-3 py-1.5 bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-medium rounded-xl border border-slate-700 transition"
              title="View consumer app as a user"
            >
              Consumer App View <ArrowRight className="w-3.5 h-3.5" />
            </button>
            <button
              onClick={handleLogout}
              className="flex items-center gap-1.5 px-3 py-1.5 bg-red-950/40 hover:bg-red-900/60 text-red-300 text-xs font-medium rounded-xl border border-red-800/40 transition"
            >
              <LogOut className="w-3.5 h-3.5" /> Logout
            </button>
          </div>
        </div>

        {/* Navigation Tabs */}
        <div className="max-w-7xl mx-auto px-4 sm:px-6 flex gap-2 overflow-x-auto border-t border-slate-800/80 pt-2 pb-1 scrollbar-none text-xs font-medium">
          {[
            { id: 'overview', label: 'Platform Pulse', icon: ShieldAlert },
            { id: 'users', label: 'User Risk Profiles', icon: Users },
            { id: 'policies', label: 'Save-at-Pay Policies', icon: Sliders },
            { id: 'investments', label: 'Investment Products', icon: TrendingUp },
            { id: 'audit', label: 'Compliance Audit Trail', icon: FileText },
          ].map(tab => {
            const Icon = tab.icon
            const active = activeTab === tab.id
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id as any)}
                className={`flex items-center gap-2 px-3 py-2 rounded-lg transition-all whitespace-nowrap ${
                  active 
                    ? 'bg-emerald-600 text-white font-semibold shadow-sm' 
                    : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800'
                }`}
              >
                <Icon className="w-4 h-4" />
                {tab.label}
              </button>
            )
          })}
        </div>
      </header>

      {/* Main Content Area */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 py-6 space-y-6">

        {/* KPI Strip */}
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
          <div className="bg-white p-4 rounded-2xl border border-gray-200 shadow-sm">
            <p className="text-xs font-semibold text-gray-500 uppercase tracking-wider">Total Registered</p>
            <p className="text-3xl font-extrabold text-gray-900 mt-1">
              {loadingOverview ? '...' : overview?.total_users ?? 0}
            </p>
            <p className="text-xs text-gray-400 mt-1">Gig workers & informal earners</p>
          </div>

          <div className="bg-emerald-50 p-4 rounded-2xl border border-emerald-200 shadow-sm">
            <p className="text-xs font-semibold text-emerald-800 uppercase tracking-wider">Healthy Stability</p>
            <div className="flex items-baseline gap-2 mt-1">
              <span className="text-3xl font-extrabold text-emerald-700">
                {loadingOverview ? '...' : overview?.by_level?.LOW ?? 0}
              </span>
              <span className="text-xs text-emerald-600 font-medium">LOW Distress</span>
            </div>
            <p className="text-xs text-emerald-600 mt-1">Normal savings recommendations active</p>
          </div>

          <div className="bg-orange-50 p-4 rounded-2xl border border-orange-200 shadow-sm">
            <p className="text-xs font-semibold text-orange-800 uppercase tracking-wider">Under Financial Stress</p>
            <div className="flex items-baseline gap-2 mt-1">
              <span className="text-3xl font-extrabold text-orange-600">
                {loadingOverview ? '...' : (overview?.by_level?.HIGH ?? 0) + (overview?.by_level?.SEVERE ?? 0)}
              </span>
              <span className="text-xs text-orange-600 font-medium">HIGH / SEVERE</span>
            </div>
            <p className="text-xs text-orange-600 mt-1">Dampened Save-at-Pay & credit guardrails on</p>
          </div>

          <div className="bg-purple-50 p-4 rounded-2xl border border-purple-200 shadow-sm">
            <p className="text-xs font-semibold text-purple-800 uppercase tracking-wider">Active Policies</p>
            <p className="text-3xl font-extrabold text-purple-700 mt-1">
              {loadingPolicies ? '...' : policies?.length ?? 0}
            </p>
            <p className="text-xs text-purple-600 mt-1">Category micro-saving rules configured</p>
          </div>
        </div>

        {/* TAB 1: PLATFORM PULSE / OVERVIEW */}
        {activeTab === 'overview' && (
          <div className="space-y-6">
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              {/* Distress Distribution Breakdown */}
              <div className="lg:col-span-2 bg-white p-6 rounded-2xl border border-gray-200 shadow-sm">
                <div className="flex items-center justify-between mb-4">
                  <div>
                    <h2 className="text-lg font-bold text-gray-900">Distress Level Distribution</h2>
                    <p className="text-xs text-gray-500">Live classification from the Income & Volatility Engine</p>
                  </div>
                  <button 
                    onClick={() => refetchOverview()}
                    className="p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-lg transition"
                    title="Refresh overview"
                  >
                    <RefreshCw className="w-4 h-4" />
                  </button>
                </div>

                <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
                  {[
                    { level: 'LOW', label: 'Low Distress', count: overview?.by_level?.LOW || 0, color: 'emerald', desc: 'Full micro-saving active' },
                    { level: 'MODERATE', label: 'Moderate', count: overview?.by_level?.MODERATE || 0, color: 'amber', desc: '50% Save-at-Pay dampening' },
                    { level: 'HIGH', label: 'High Pressure', count: overview?.by_level?.HIGH || 0, color: 'orange', desc: '75% dampening + loan hold' },
                    { level: 'SEVERE', label: 'Severe Strain', count: overview?.by_level?.SEVERE || 0, color: 'red', desc: 'Zero saving + emergency aid' },
                  ].map(item => (
                    <div key={item.level} className={`p-4 rounded-xl border border-${item.color}-200 bg-${item.color}-50/60`}>
                      <span className={`text-xs font-bold text-${item.color}-700`}>{item.label}</span>
                      <p className={`text-2xl font-black text-${item.color}-900 my-1`}>{item.count}</p>
                      <p className={`text-[11px] text-${item.color}-700/80 leading-tight`}>{item.desc}</p>
                    </div>
                  ))}
                </div>

                <div className="mt-6 p-4 bg-slate-50 rounded-xl border border-slate-200 flex items-start gap-3">
                  <ShieldCheck className="w-5 h-5 text-emerald-600 flex-shrink-0 mt-0.5" />
                  <div className="text-xs text-slate-600 leading-relaxed">
                    <strong className="text-slate-800">Responsible Lending System Status: Active.</strong> When users like Arjun Kumar enter HIGH or SEVERE distress, loan offers are automatically intercepted and held with dignity-preserving guidance instead of rejection notices.
                  </div>
                </div>
              </div>

              {/* Quick Admin Actions */}
              <div className="bg-white p-6 rounded-2xl border border-gray-200 shadow-sm space-y-4">
                <h2 className="text-lg font-bold text-gray-900">Governance Quick Links</h2>
                <div className="space-y-2">
                  <button
                    onClick={() => setActiveTab('policies')}
                    className="w-full text-left p-3 rounded-xl border border-gray-200 hover:border-emerald-500 hover:bg-emerald-50/50 transition group flex items-center justify-between"
                  >
                    <div>
                      <p className="text-sm font-semibold text-gray-800 group-hover:text-emerald-700">Tune Save-at-Pay Rules</p>
                      <p className="text-xs text-gray-500">Adjust category baseline percentages</p>
                    </div>
                    <ArrowRight className="w-4 h-4 text-gray-400 group-hover:text-emerald-600" />
                  </button>

                  <button
                    onClick={() => setActiveTab('users')}
                    className="w-full text-left p-3 rounded-xl border border-gray-200 hover:border-emerald-500 hover:bg-emerald-50/50 transition group flex items-center justify-between"
                  >
                    <div>
                      <p className="text-sm font-semibold text-gray-800 group-hover:text-emerald-700">Inspect User Roster</p>
                      <p className="text-xs text-gray-500">View individual resilience scores</p>
                    </div>
                    <ArrowRight className="w-4 h-4 text-gray-400 group-hover:text-emerald-600" />
                  </button>

                  <button
                    onClick={() => setActiveTab('audit')}
                    className="w-full text-left p-3 rounded-xl border border-gray-200 hover:border-emerald-500 hover:bg-emerald-50/50 transition group flex items-center justify-between"
                  >
                    <div>
                      <p className="text-sm font-semibold text-gray-800 group-hover:text-emerald-700">Compliance & Audit Trail</p>
                      <p className="text-xs text-gray-500">Immutable statutory consent logs</p>
                    </div>
                    <ArrowRight className="w-4 h-4 text-gray-400 group-hover:text-emerald-600" />
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* TAB 2: USER RISK PROFILES */}
        {activeTab === 'users' && (
          <div className="bg-white rounded-2xl border border-gray-200 shadow-sm overflow-hidden">
            <div className="p-5 border-b border-gray-100 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
              <div>
                <h2 className="text-lg font-bold text-gray-900">User Financial Telemetry</h2>
                <p className="text-xs text-gray-500">Real-time health profiles and score tracking</p>
              </div>

              <div className="flex items-center gap-2">
                <div className="relative">
                  <Search className="w-4 h-4 text-gray-400 absolute left-3 top-2.5" />
                  <input
                    type="text"
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    placeholder="Search user, email, occupation..."
                    className="pl-9 pr-3 py-1.5 text-xs rounded-xl border border-gray-200 focus:outline-none focus:border-emerald-500 w-52"
                  />
                </div>

                <select
                  value={distressFilter}
                  onChange={(e) => setDistressFilter(e.target.value)}
                  className="text-xs py-1.5 px-3 rounded-xl border border-gray-200 bg-white focus:outline-none focus:border-emerald-500 font-medium"
                >
                  <option value="ALL">All Levels</option>
                  <option value="LOW">LOW</option>
                  <option value="MODERATE">MODERATE</option>
                  <option value="HIGH">HIGH</option>
                  <option value="SEVERE">SEVERE</option>
                </select>
              </div>
            </div>

            <div className="overflow-x-auto">
              <table className="w-full text-left border-collapse">
                <thead>
                  <tr className="bg-gray-50 text-[11px] font-semibold text-gray-500 uppercase tracking-wider border-b border-gray-200">
                    <th className="py-3 px-5">User</th>
                    <th className="py-3 px-5">Role & Occupation</th>
                    <th className="py-3 px-5">Distress Status</th>
                    <th className="py-3 px-5">Resilience Score</th>
                    <th className="py-3 px-5">Account Status</th>
                    <th className="py-3 px-5">Registered</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-100 text-xs">
                  {loadingUsers ? (
                    <tr>
                      <td colSpan={6} className="py-8 text-center text-gray-400">Loading user profiles...</td>
                    </tr>
                  ) : filteredUsers.length === 0 ? (
                    <tr>
                      <td colSpan={6} className="py-8 text-center text-gray-400">No users match the search filter.</td>
                    </tr>
                  ) : (
                    filteredUsers.map((u: any) => {
                      const badgeColor = {
                        LOW: 'bg-emerald-50 text-emerald-700 border-emerald-200',
                        MODERATE: 'bg-amber-50 text-amber-700 border-amber-200',
                        HIGH: 'bg-orange-50 text-orange-700 border-orange-200',
                        SEVERE: 'bg-red-50 text-red-700 border-red-200',
                      }[u.distress_level as string] || 'bg-gray-50 text-gray-600 border-gray-200'

                      return (
                        <tr key={u.id} className="hover:bg-gray-50/80 transition">
                          <td className="py-3.5 px-5">
                            <p className="font-bold text-gray-900">{u.full_name}</p>
                            <p className="text-[11px] text-gray-500">{u.email}</p>
                          </td>
                          <td className="py-3.5 px-5">
                            <span className="capitalize font-medium text-gray-700">{u.occupation || 'Freelancer'}</span>
                            <span className="text-[10px] text-gray-400 block uppercase font-mono">{u.role}</span>
                          </td>
                          <td className="py-3.5 px-5">
                            <span className={`inline-block px-2.5 py-1 rounded-full text-[11px] font-bold border ${badgeColor}`}>
                              {u.distress_level}
                            </span>
                          </td>
                          <td className="py-3.5 px-5">
                            <div className="flex items-center gap-2">
                              <div className="w-16 bg-gray-100 rounded-full h-2 overflow-hidden">
                                <div 
                                  className="bg-emerald-600 h-full rounded-full" 
                                  style={{ width: `${Math.min(100, Math.max(0, u.resilience_score))}%` }} 
                                />
                              </div>
                              <span className="font-bold text-gray-800">{u.resilience_score}</span>
                            </div>
                          </td>
                          <td className="py-3.5 px-5">
                            <span className={`px-2 py-0.5 rounded text-[10px] font-semibold ${
                              u.is_active ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-600'
                            }`}>
                              {u.is_active ? 'ACTIVE' : 'INACTIVE'}
                            </span>
                          </td>
                          <td className="py-3.5 px-5 text-gray-500 text-[11px]">
                            {new Date(u.created_at).toLocaleDateString()}
                          </td>
                        </tr>
                      )
                    })
                  )}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* TAB 3: SAVE-AT-PAY POLICIES */}
        {activeTab === 'policies' && (
          <div className="bg-white rounded-2xl border border-gray-200 shadow-sm p-6 space-y-6">
            <div>
              <h2 className="text-lg font-bold text-gray-900">Save-at-Pay Category Policies</h2>
              <p className="text-xs text-gray-500 mt-0.5">
                Govern baseline micro-saving rates attached to checkout payments. When a user experiences distress, the engine dynamically scales down these baseline values.
              </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {loadingPolicies ? (
                <p className="text-gray-400 text-sm">Loading policies...</p>
              ) : (
                policies?.map((policy: any) => {
                  const isEditing = editingCategory === policy.category
                  return (
                    <div key={policy.id} className="p-4 rounded-xl border border-gray-200 bg-gray-50/50 flex flex-col justify-between">
                      <div className="flex items-center justify-between mb-2">
                        <div className="flex items-center gap-2">
                          <span className="text-base font-bold text-gray-900 capitalize">{policy.category}</span>
                          <span className="text-[10px] px-2 py-0.5 rounded bg-emerald-100 text-emerald-800 font-semibold">
                            ACTIVE
                          </span>
                        </div>
                        <span className="text-xs font-mono text-gray-400">ID: {policy.id}</span>
                      </div>

                      <p className="text-xs text-gray-600 mb-4">{policy.description || 'Standard micro-saving rate for this category.'}</p>

                      <div className="pt-3 border-t border-gray-200/80 flex items-center justify-between">
                        <div>
                          <p className="text-[10px] text-gray-400 uppercase font-semibold">Baseline Saving</p>
                          {isEditing ? (
                            <div className="flex items-center gap-1.5 mt-1">
                              <input
                                type="number"
                                step="0.5"
                                min="0"
                                max="30"
                                value={newPercentage}
                                onChange={(e) => setNewPercentage(parseFloat(e.target.value) || 0)}
                                className="w-16 px-2 py-1 text-xs border border-emerald-500 rounded font-bold"
                              />
                              <span className="text-xs text-gray-600">%</span>
                              <button
                                onClick={() => updatePolicyMutation.mutate({ category: policy.category, pct: newPercentage / 100 })}
                                className="p-1 bg-emerald-600 text-white rounded hover:bg-emerald-700 transition"
                                title="Confirm update"
                              >
                                <Check className="w-3.5 h-3.5" />
                              </button>
                            </div>
                          ) : (
                            <p className="text-lg font-black text-emerald-700">
                              {(policy.base_percentage * 100).toFixed(1)}%
                            </p>
                          )}
                        </div>

                        {!isEditing && (
                          <button
                            onClick={() => {
                              setEditingCategory(policy.category)
                              setNewPercentage(policy.base_percentage * 100)
                            }}
                            className="px-3 py-1 bg-white border border-gray-300 hover:border-emerald-500 text-gray-700 hover:text-emerald-700 text-xs font-semibold rounded-lg shadow-sm transition"
                          >
                            Edit Rate
                          </button>
                        )}
                      </div>
                    </div>
                  )
                })
              )}
            </div>
          </div>
        )}

        {/* TAB 4: INVESTMENT PRODUCTS */}
        {activeTab === 'investments' && (
          <div className="bg-white rounded-2xl border border-gray-200 shadow-sm p-6 space-y-6">
            <div>
              <h2 className="text-lg font-bold text-gray-900">Safety-Gated Investment Products</h2>
              <p className="text-xs text-gray-500 mt-0.5">
                Financial products available to users who have completed 100% of their Safety Wallet buffer.
              </p>
            </div>

            <div className="space-y-3">
              {loadingProducts ? (
                <p className="text-gray-400 text-sm">Loading products...</p>
              ) : (
                products?.map((p: any) => (
                  <div key={p.id} className="p-4 rounded-xl border border-gray-200 flex items-center justify-between hover:bg-gray-50 transition">
                    <div>
                      <div className="flex items-center gap-2">
                        <p className="font-bold text-gray-900 text-sm">{p.name}</p>
                        <span className="text-[10px] px-2 py-0.5 rounded font-bold uppercase bg-purple-100 text-purple-700">
                          {p.type}
                        </span>
                      </div>
                      <p className="text-xs text-gray-500 mt-0.5">
                        Issuer: <span className="font-medium text-gray-700">{p.issuer}</span> • Risk: <span className="font-medium text-gray-700 capitalize">{p.risk_level}</span>
                      </p>
                    </div>

                    <div className="text-right">
                      <p className="text-xs font-semibold text-gray-500">Min Investment</p>
                      <p className="text-base font-extrabold text-gray-900">₹{p.min_investment?.toLocaleString('en-IN')}</p>
                      <span className={`inline-block text-[10px] font-bold mt-0.5 ${p.active ? 'text-emerald-600' : 'text-gray-400'}`}>
                        {p.active ? '● AVAILABLE' : '○ INACTIVE'}
                      </span>
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>
        )}

        {/* TAB 5: COMPLIANCE AUDIT TRAIL */}
        {activeTab === 'audit' && (
          <div className="bg-white rounded-2xl border border-gray-200 shadow-sm overflow-hidden">
            <div className="p-5 border-b border-gray-100">
              <h2 className="text-lg font-bold text-gray-900">Statutory Compliance & Audit Trail</h2>
              <p className="text-xs text-gray-500">
                Immutable ledger of policy updates, credit decisions, and statutory user consent records.
              </p>
            </div>

            <div className="overflow-x-auto">
              <table className="w-full text-left border-collapse">
                <thead>
                  <tr className="bg-gray-50 text-[11px] font-semibold text-gray-500 uppercase tracking-wider border-b border-gray-200">
                    <th className="py-3 px-5">Timestamp</th>
                    <th className="py-3 px-5">Event Type</th>
                    <th className="py-3 px-5">Action</th>
                    <th className="py-3 px-5">Entity</th>
                    <th className="py-3 px-5">Actor / User ID</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-100 text-xs font-mono">
                  {loadingAudit ? (
                    <tr>
                      <td colSpan={5} className="py-8 text-center text-gray-400 font-sans">Loading audit records...</td>
                    </tr>
                  ) : (auditLogs || []).length === 0 ? (
                    <tr>
                      <td colSpan={5} className="py-8 text-center text-gray-400 font-sans">No audit events recorded yet.</td>
                    </tr>
                  ) : (
                    auditLogs.map((log: any) => (
                      <tr key={log.id} className="hover:bg-gray-50/80 transition">
                        <td className="py-3 px-5 text-gray-500 text-[11px]">
                          {log.created_at ? new Date(log.created_at).toLocaleString() : 'N/A'}
                        </td>
                        <td className="py-3 px-5 font-bold text-emerald-800">
                          {log.event_type}
                        </td>
                        <td className="py-3 px-5 text-gray-700">
                          {log.action}
                        </td>
                        <td className="py-3 px-5 text-gray-500">
                          {log.entity_type || 'system'}
                        </td>
                        <td className="py-3 px-5 text-gray-600">
                          User #{log.user_id || log.actor_id}
                        </td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>
          </div>
        )}

      </main>
    </div>
  )
}
