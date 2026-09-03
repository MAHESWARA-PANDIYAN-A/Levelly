import { useQuery } from '@tanstack/react-query'
import { healthAPI, incomeAPI } from '../lib/api'
import { AreaChart, Area, XAxis, YAxis, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts'

const COLORS = ['#059669', '#d97706', '#6366f1', '#ef4444', '#0891b2', '#be185d', '#78716c']

export default function AnalyticsPage() {
  const { data: chartData, isLoading: chartLoading } = useQuery({
    queryKey: ['income-chart'],
    queryFn: () => incomeAPI.chart().then(r => r.data),
  })

  const { data: expenseData, isLoading: expenseLoading } = useQuery({
    queryKey: ['expense-analytics'],
    queryFn: () => healthAPI.expenseAnalytics().then(r => r.data),
  })

  const { data: history } = useQuery({
    queryKey: ['score-history'],
    queryFn: () => healthAPI.scoreHistory().then(r => r.data),
  })

  const weeklyData = chartData?.weekly_data?.map((w: any) => ({
    week: `W${w.week_offset || 0}`,
    amount: w.amount || w.total || 0,
  })) || []

  const categoryData = expenseData?.by_category
    ? Object.entries(expenseData.by_category).map(([name, value]) => ({ name, value: value as number }))
    : []

  const scoreHistory = (history || []).slice(0, 10).reverse().map((h: any, i: number) => ({
    period: `P${i + 1}`,
    score: h.resilience_score,
  }))

  return (
    <div className="px-5 pb-8 animate-fade-in">
      <h1 className="text-2xl font-bold text-levelly-text mb-5">Analytics</h1>

      {/* Income Chart */}
      <div className="card mb-4">
        <p className="text-sm font-semibold text-gray-600 mb-4">Weekly Income (last 8 weeks)</p>
        {chartLoading ? (
          <div className="skeleton h-40 rounded-xl" />
        ) : (
          <ResponsiveContainer width="100%" height={160}>
            <AreaChart data={weeklyData}>
              <defs>
                <linearGradient id="incomeGrad" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#059669" stopOpacity={0.3} />
                  <stop offset="95%" stopColor="#059669" stopOpacity={0} />
                </linearGradient>
              </defs>
              <XAxis dataKey="week" tick={{ fontSize: 11 }} />
              <YAxis tick={{ fontSize: 11 }} tickFormatter={(v) => `₹${v / 1000}k`} />
              <Tooltip formatter={(v: any) => [`₹${Number(v || 0).toLocaleString('en-IN')}`, 'Income']} />
              <Area type="monotone" dataKey="amount" stroke="#059669" strokeWidth={2} fill="url(#incomeGrad)" />
            </AreaChart>
          </ResponsiveContainer>
        )}
        {chartData && (
          <div className="flex justify-between mt-3 text-xs text-gray-500">
            <span>Weekly avg: ₹{((chartData.weekly_average || 0)).toLocaleString('en-IN', { maximumFractionDigits: 0 })}</span>
            <span className={`font-medium capitalize ${chartData.income_trend === 'declining' ? 'text-orange-500' : 'text-emerald-500'}`}>
              Trend: {chartData.income_trend}
            </span>
          </div>
        )}
      </div>

      {/* Expense Breakdown */}
      <div className="card mb-4">
        <p className="text-sm font-semibold text-gray-600 mb-4">Expense Breakdown</p>
        {expenseLoading ? (
          <div className="skeleton h-48 rounded-xl" />
        ) : categoryData.length > 0 ? (
          <div className="flex items-center gap-4">
            <ResponsiveContainer width="50%" height={160}>
              <PieChart>
                <Pie data={categoryData} cx="50%" cy="50%" innerRadius={40} outerRadius={70} dataKey="value">
                  {categoryData.map((_, i) => (
                    <Cell key={i} fill={COLORS[i % COLORS.length]} />
                  ))}
                </Pie>
              </PieChart>
            </ResponsiveContainer>
            <div className="flex-1 space-y-1.5">
              {categoryData.slice(0, 5).map(({ name, value }, i) => (
                <div key={name} className="flex items-center gap-2">
                  <div className="w-3 h-3 rounded-full" style={{ backgroundColor: COLORS[i % COLORS.length] }} />
                  <span className="text-xs text-gray-600 flex-1 capitalize">{name}</span>
                  <span className="text-xs font-semibold">₹{(value as number).toLocaleString('en-IN', { maximumFractionDigits: 0 })}</span>
                </div>
              ))}
            </div>
          </div>
        ) : (
          <p className="text-gray-400 text-sm text-center py-8">No expense data yet</p>
        )}
        {expenseData && (
          <div className="mt-3 pt-3 border-t flex justify-between text-sm">
            <span className="text-gray-500">Expense Ratio</span>
            <span className={`font-bold ${(expenseData.expense_ratio_pct || 0) > 85 ? 'text-orange-600' : 'text-emerald-600'}`}>
              {(expenseData.expense_ratio_pct || 0).toFixed(1)}%
            </span>
          </div>
        )}
      </div>

      {/* Resilience Score History */}
      {scoreHistory.length > 0 && (
        <div className="card mb-4">
          <p className="text-sm font-semibold text-gray-600 mb-4">Resilience Score Trend</p>
          <ResponsiveContainer width="100%" height={100}>
            <AreaChart data={scoreHistory}>
              <XAxis dataKey="period" tick={{ fontSize: 10 }} />
              <YAxis domain={[0, 100]} tick={{ fontSize: 10 }} />
              <Tooltip />
              <Area type="monotone" dataKey="score" stroke="#6366f1" strokeWidth={2} fill="#eef2ff" />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      )}
    </div>
  )
}
