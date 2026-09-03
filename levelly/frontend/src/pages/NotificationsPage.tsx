import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Bell, CheckCheck } from 'lucide-react'
import { notificationAPI } from '../lib/api'

const notifColors: Record<string, string> = {
  payout_received: 'bg-green-100 text-green-700',
  payment_completed: 'bg-gray-100 text-gray-600',
  save_at_pay_accepted: 'bg-emerald-100 text-emerald-700',
  safety_wallet_updated: 'bg-emerald-100 text-emerald-700',
  income_trend_changed: 'bg-orange-100 text-orange-700',
  financial_pressure_detected: 'bg-red-100 text-red-700',
  credit_recommendation_changed: 'bg-amber-100 text-amber-700',
  investment_suggestion_available: 'bg-purple-100 text-purple-700',
}

export default function NotificationsPage() {
  const queryClient = useQueryClient()

  const { data: notifications, isLoading } = useQuery({
    queryKey: ['notifications'],
    queryFn: () => notificationAPI.getAll().then(r => r.data),
  })

  const readAllMutation = useMutation({
    mutationFn: () => notificationAPI.markAllRead(),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['notifications'] })
      queryClient.invalidateQueries({ queryKey: ['unread-count'] })
    },
  })

  const readMutation = useMutation({
    mutationFn: (id: number) => notificationAPI.markRead(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['notifications'] })
      queryClient.invalidateQueries({ queryKey: ['unread-count'] })
    },
  })

  const unread = notifications?.filter((n: any) => !n.is_read).length || 0

  return (
    <div className="px-5 pb-8 animate-fade-in">
      <div className="flex items-center justify-between mb-5">
        <h1 className="text-2xl font-bold text-levelly-text">Notifications</h1>
        {unread > 0 && (
          <button
            onClick={() => readAllMutation.mutate()}
            className="flex items-center gap-1 text-sm text-emerald-600 font-medium"
          >
            <CheckCheck className="w-4 h-4" /> Mark all read
          </button>
        )}
      </div>

      {isLoading ? (
        <div className="space-y-3">
          {[1, 2, 3].map(i => <div key={i} className="skeleton h-16 rounded-2xl" />)}
        </div>
      ) : !notifications?.length ? (
        <div className="text-center py-12 text-gray-400">
          <Bell className="w-12 h-12 mx-auto mb-3 text-gray-200" />
          <p>No notifications yet</p>
        </div>
      ) : (
        <div className="space-y-2">
          {notifications.map((n: any) => (
            <div
              key={n.id}
              onClick={() => !n.is_read && readMutation.mutate(n.id)}
              className={`p-4 rounded-2xl border transition-all cursor-pointer
                ${!n.is_read ? 'bg-white border-gray-200 shadow-card' : 'bg-gray-50 border-gray-100'}
              `}
            >
              <div className="flex items-start gap-3">
                <div className={`w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 text-xs font-bold
                  ${notifColors[n.type] || 'bg-gray-100 text-gray-500'}
                `}>
                  {!n.is_read && <div className="w-2 h-2 bg-current rounded-full" />}
                  {n.is_read && '✓'}
                </div>
                <div className="flex-1 min-w-0">
                  <p className={`text-sm font-semibold ${!n.is_read ? 'text-gray-900' : 'text-gray-500'}`}>
                    {n.title}
                  </p>
                  <p className={`text-xs mt-0.5 leading-relaxed ${!n.is_read ? 'text-gray-600' : 'text-gray-400'}`}>
                    {n.message}
                  </p>
                  <p className="text-[10px] text-gray-400 mt-1">
                    {new Date(n.created_at).toLocaleDateString('en-IN', {
                      day: 'numeric', month: 'short', hour: '2-digit', minute: '2-digit'
                    })}
                  </p>
                </div>
                {!n.is_read && (
                  <div className="w-2 h-2 bg-emerald-500 rounded-full mt-1.5 flex-shrink-0" />
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
