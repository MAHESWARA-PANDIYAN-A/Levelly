import { Outlet, NavLink, useNavigate } from 'react-router-dom'
import { Home, Wallet, TrendingUp, CreditCard, User, Bell, Shield } from 'lucide-react'
import { useQuery } from '@tanstack/react-query'
import { notificationAPI } from '../lib/api'
import { useAuthStore } from '../store/authStore'

const navItems = [
  { to: '/', icon: Home, label: 'Home', exact: true },
  { to: '/wallets', icon: Wallet, label: 'Wallets' },
  { to: '/grow', icon: TrendingUp, label: 'Grow' },
  { to: '/credit', icon: CreditCard, label: 'Credit' },
  { to: '/profile', icon: User, label: 'Profile' },
]

export default function Layout() {
  const navigate = useNavigate()
  const { user } = useAuthStore()
  const { data: unreadData } = useQuery({
    queryKey: ['unread-count'],
    queryFn: () => notificationAPI.unreadCount().then(r => r.data),
    refetchInterval: 30000,
  })

  const unreadCount = unreadData?.unread_count || 0

  return (
    <div className="flex flex-col min-h-dvh bg-levelly-bg max-w-md mx-auto relative">
      {/* Admin indicator banner if admin is viewing consumer app */}
      {user?.role === 'admin' && (
        <div className="bg-slate-900 text-white px-4 py-2 flex items-center justify-between text-xs sticky top-0 z-50 shadow">
          <div className="flex items-center gap-1.5">
            <Shield className="w-3.5 h-3.5 text-emerald-400" />
            <span className="font-semibold text-slate-200">Admin Mode Preview</span>
          </div>
          <button
            onClick={() => navigate('/admin')}
            className="bg-emerald-600 hover:bg-emerald-500 text-white px-2.5 py-1 rounded-lg text-[11px] font-bold transition shadow-sm"
          >
            Ops Portal →
          </button>
        </div>
      )}

      {/* Top bar */}
      <div className="flex items-center justify-between px-5 pt-8 pb-3 bg-levelly-bg sticky top-0 z-40">
        <div className="flex items-center gap-2">
          <div className="w-7 h-7 bg-emerald-700 rounded-lg flex items-center justify-center">
            <span className="text-white text-xs font-bold">L</span>
          </div>
          <span className="text-lg font-bold text-levelly-text">LEVELLY</span>
        </div>
        <div className="flex items-center gap-1">
          {user?.role === 'admin' && (
            <button
              onClick={() => navigate('/admin')}
              className="p-1.5 rounded-xl hover:bg-emerald-50 text-emerald-700 font-bold text-xs transition"
              title="Go to Admin Dashboard"
            >
              <Shield className="w-5 h-5 text-emerald-700" />
            </button>
          )}
          <button
            onClick={() => navigate('/notifications')}
            className="relative p-2 rounded-xl hover:bg-white transition-colors"
            aria-label="Notifications"
          >
            <Bell className="w-5 h-5 text-gray-600" />
            {unreadCount > 0 && (
              <span className="absolute top-1 right-1 w-4 h-4 bg-red-500 rounded-full text-white text-[10px] flex items-center justify-center font-bold">
                {unreadCount > 9 ? '9+' : unreadCount}
              </span>
            )}
          </button>
        </div>
      </div>

      {/* Main content */}
      <main className="flex-1 overflow-auto pb-safe">
        <Outlet />
      </main>

      {/* Bottom navigation */}
      <nav className="fixed bottom-0 left-0 right-0 bg-white/95 backdrop-blur-md border-t border-gray-200/70 z-50">
        <div className="max-w-md mx-auto flex items-center justify-around px-2 py-1 safe-bottom">
          {navItems.map(({ to, icon: Icon, label, exact }) => (
            <NavLink
              key={to}
              to={to}
              end={exact}
              className={({ isActive }) =>
                `flex flex-col items-center gap-0.5 py-1 px-3 rounded-xl transition-all ${
                  isActive
                    ? 'text-emerald-700 font-semibold'
                    : 'text-gray-400 hover:text-gray-600'
                }`
              }
            >
              {({ isActive }) => (
                <>
                  <div className={`p-1 rounded-xl transition-all ${isActive ? 'bg-emerald-50' : ''}`}>
                    <Icon className={`w-5 h-5 ${isActive ? 'text-emerald-700' : 'text-gray-400'}`} />
                  </div>
                  <span className="text-[10px]">
                    {label}
                  </span>
                </>
              )}
            </NavLink>
          ))}
        </div>
      </nav>
    </div>
  )
}
