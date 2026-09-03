import { useQuery } from '@tanstack/react-query'

import { transactionAPI } from '../lib/api'

const categoryEmoji: Record<string, string> = {
  food: '🍛', fuel: '⛽', education: '📚', entertainment: '🎬',
  shopping: '🛒', family: '👨‍👩‍👧', healthcare: '🏥', rent: '🏠',
  bills: '📄', income: '💰', savings: '🛡️', other: '💳',
}

export default function TransactionsPage() {
  const { data, isLoading } = useQuery({
    queryKey: ['transactions'],
    queryFn: () => transactionAPI.getAll(50).then(r => r.data),
  })

  const transactions = data?.transactions || []

  return (
    <div className="px-5 pb-8 animate-fade-in">
      <h1 className="text-2xl font-bold text-levelly-text mb-5">Transactions</h1>

      {isLoading ? (
        <div className="space-y-3">
          {[1, 2, 3, 4, 5].map(i => <div key={i} className="skeleton h-16 rounded-2xl" />)}
        </div>
      ) : transactions.length === 0 ? (
        <div className="text-center py-12 text-gray-400">
          <p>No transactions yet</p>
        </div>
      ) : (
        <div className="space-y-2">
          {transactions.map((t: any) => (
            <div key={t.id} className="card flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-gray-50 flex items-center justify-center text-lg flex-shrink-0">
                {t.type === 'savings' ? '🛡️' : (categoryEmoji[t.category] || '💳')}
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-sm font-semibold text-gray-800 truncate">{t.description}</p>
                <p className="text-xs text-gray-400 capitalize">
                  {t.category}
                  {t.save_at_pay && <span className="ml-1.5 text-emerald-500">• Save-at-Pay ✓</span>}
                </p>
              </div>
              <div className="text-right flex-shrink-0">
                <p className={`text-sm font-bold ${
                  t.direction === 'credit' ? 'text-emerald-600' : 'text-gray-800'
                }`}>
                  {t.direction === 'credit' ? '+' : '-'}₹{t.amount?.toLocaleString('en-IN')}
                </p>
                <p className="text-[10px] text-gray-400">
                  {new Date(t.date).toLocaleDateString('en-IN', { day: 'numeric', month: 'short' })}
                </p>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
