import { Outlet, NavLink, useNavigate } from 'react-router-dom'
import {
  Home,
  QrCode,
  ShieldCheck,
  TrendingUp,
  User,
  Bell,
  Shield,
} from 'lucide-react'
import { useQuery } from '@tanstack/react-query'
import { notificationAPI } from '../lib/api'
import { useAuthStore } from '../store/authStore'

const navItems = [
  { to: '/', icon: Home, label: 'HOME', exact: true },
  { to: '/safety', icon: ShieldCheck, label: 'SAFETY' },
  { to: '/pay', icon: QrCode, label: 'PAY', isCenter: true },
  { to: '/grow', icon: TrendingUp, label: 'GROW' },
  { to: '/profile', icon: User, label: 'PROFILE' },
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
    <div className="flex flex-col min-h-screen bg-[#F8FAFC] max-w-md mx-auto relative shadow-2xl overflow-x-hidden">
      {/* Admin indicator banner if admin is previewing consumer app */}
      {user?.role === 'admin' && (
        <div className="bg-slate-900 text-white px-4 py-2 flex items-center justify-between text-xs sticky top-0 z-50 border-b border-slate-800">
          <div className="flex items-center gap-1.5">
            <Shield className="w-3.5 h-3.5 text-emerald-400" />
            <span className="font-semibold text-slate-200">Admin Mode</span>
          </div>
          <button
            onClick={() => navigate('/admin')}
            className="bg-emerald-600 hover:bg-emerald-500 text-white px-2.5 py-1 rounded-lg text-[11px] font-bold transition shadow-sm"
          >
            Ops Portal →
          </button>
        </div>
      )}

      {/* Top Header */}
      <header className="flex items-center justify-between px-5 pt-5 pb-3 bg-[#F8FAFC]/90 backdrop-blur-md sticky top-0 z-40 border-b border-slate-100">
        <div className="flex items-center gap-2.5">
          <div className="w-8 h-8 bg-gradient-to-br from-emerald-600 to-teal-800 rounded-xl flex items-center justify-center shadow-sm shadow-emerald-700/30">
            <span className="text-white text-sm font-black tracking-wider">L</span>
          </div>
          <div>
            <span className="text-base font-black tracking-tight text-slate-900">LEVELLY</span>
            <span className="text-[9px] block text-emerald-700 font-bold uppercase tracking-widest -mt-0.5">
              Pay & Resilience
            </span>
          </div>
        </div>

        <div className="flex items-center gap-1.5">
          {user?.role === 'admin' && (
            <button
              onClick={() => navigate('/admin')}
              className="p-2 rounded-xl bg-slate-100 hover:bg-emerald-50 text-emerald-800 font-bold text-xs transition"
              title="Admin Portal"
            >
              <Shield className="w-4 h-4 text-emerald-700" />
            </button>
          )}

          <button
            onClick={() => navigate('/notifications')}
            className="relative p-2 rounded-xl bg-white border border-slate-200/80 text-slate-700 hover:bg-slate-50 transition shadow-sm"
            aria-label="Notifications"
          >
            <Bell className="w-4 h-4 text-slate-700" />
            {unreadCount > 0 && (
              <span className="absolute -top-1 -right-1 w-4 h-4 bg-red-500 rounded-full text-white text-[9px] flex items-center justify-center font-bold shadow-sm">
                {unreadCount > 9 ? '9+' : unreadCount}
              </span>
            )}
          </button>
        </div>
      </header>

      {/* Main Screen Content */}
      <main className="flex-1 pb-24 pt-2">
        <Outlet />
      </main>

      {/* Fixed Bottom Navigation Dock (flush with bottom) */}
      <nav className="fixed bottom-0 left-0 right-0 z-50 pointer-events-none">
        <div className="max-w-md mx-auto pointer-events-auto bg-white/95 backdrop-blur-xl border-t border-slate-200/90 shadow-[0_-4px_20px_rgba(0,0,0,0.06)] px-3 py-1.5 flex items-center justify-between">
          {navItems.map((item) => {
            const Icon = item.icon
            const isPayCenter = item.isCenter

            if (isPayCenter) {
              return (
                <NavLink
                  key={item.to}
                  to={item.to}
                  className="flex flex-col items-center -mt-5 transition transform active:scale-95 group"
                >
                  {({ isActive }) => (
                    <div className="flex flex-col items-center">
                      <div
                        className={`w-12 h-12 rounded-2xl flex items-center justify-center shadow-lg transition-all ${
                          isActive
                            ? 'bg-gradient-to-tr from-emerald-600 to-teal-500 text-white shadow-emerald-600/40 ring-4 ring-emerald-50'
                            : 'bg-gradient-to-tr from-slate-900 to-slate-800 text-emerald-400 shadow-slate-900/30 group-hover:scale-105'
                        }`}
                      >
                        <Icon className="w-6 h-6" />
                      </div>
                      <span
                        className={`text-[9px] font-black uppercase tracking-wider mt-1 transition ${
                          isActive ? 'text-emerald-700' : 'text-slate-600'
                        }`}
                      >
                        {item.label}
                      </span>
                    </div>
                  )}
                </NavLink>
              )
            }

            return (
              <NavLink
                key={item.to}
                to={item.to}
                end={item.exact}
                className={({ isActive }) =>
                  `flex flex-col items-center gap-1 py-1 px-3 rounded-xl transition ${
                    isActive
                      ? 'text-emerald-700 font-bold'
                      : 'text-slate-400 hover:text-slate-600'
                  }`
                }
              >
                {({ isActive }) => (
                  <>
                    <div
                      className={`p-1 rounded-lg transition ${
                        isActive ? 'bg-emerald-50 text-emerald-700' : 'text-slate-400'
                      }`}
                    >
                      <Icon className="w-5 h-5" />
                    </div>
                    <span className="text-[10px] font-bold tracking-tight">
                      {item.label}
                    </span>
                  </>
                )}
              </NavLink>
            )
          })}
        </div>
      </nav>
    </div>
  )
}
