import { Routes, Route, Navigate } from 'react-router-dom'
import { useAuthStore } from './store/authStore'
import Layout from './components/Layout'
import LoginPage from './pages/LoginPage'
import RegisterPage from './pages/RegisterPage'
import HomePage from './pages/HomePage'
import WalletsPage from './pages/WalletsPage'
import GrowPage from './pages/GrowPage'
import CreditPage from './pages/CreditPage'
import ProfilePage from './pages/ProfilePage'
import PaymentPage from './pages/PaymentPage'
import LargeExpensePage from './pages/LargeExpensePage'
import CoachPage from './pages/CoachPage'
import NotificationsPage from './pages/NotificationsPage'
import TransactionsPage from './pages/TransactionsPage'
import AnalyticsPage from './pages/AnalyticsPage'
import IncomePage from './pages/IncomePage'
import InvestmentDetailPage from './pages/InvestmentDetailPage'
import AdminDashboardPage from './pages/AdminDashboardPage'

function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { isAuthenticated } = useAuthStore()
  if (!isAuthenticated) return <Navigate to="/login" replace />
  return <>{children}</>
}

function AdminRoute({ children }: { children: React.ReactNode }) {
  const { isAuthenticated, user } = useAuthStore()
  if (!isAuthenticated) return <Navigate to="/login" replace />
  if (user?.role !== 'admin') return <Navigate to="/" replace />
  return <>{children}</>
}

function PublicRoute({ children }: { children: React.ReactNode }) {
  const { isAuthenticated, user } = useAuthStore()
  if (isAuthenticated) {
    if (user?.role === 'admin') return <Navigate to="/admin" replace />
    return <Navigate to="/" replace />
  }
  return <>{children}</>
}

export default function App() {
  return (
    <Routes>
      {/* Public routes */}
      <Route path="/login" element={<PublicRoute><LoginPage /></PublicRoute>} />
      <Route path="/register" element={<PublicRoute><RegisterPage /></PublicRoute>} />

      {/* Admin Operations Portal */}
      <Route path="/admin" element={<AdminRoute><AdminDashboardPage /></AdminRoute>} />

      {/* Protected routes with bottom nav */}
      <Route path="/" element={<ProtectedRoute><Layout /></ProtectedRoute>}>
        <Route index element={<HomePage />} />
        <Route path="wallets" element={<WalletsPage />} />
        <Route path="grow" element={<GrowPage />} />
        <Route path="grow/invest/:productId" element={<InvestmentDetailPage />} />
        <Route path="credit" element={<CreditPage />} />
        <Route path="profile" element={<ProfilePage />} />
        <Route path="pay" element={<PaymentPage />} />
        <Route path="large-expense" element={<LargeExpensePage />} />
        <Route path="coach" element={<CoachPage />} />
        <Route path="notifications" element={<NotificationsPage />} />
        <Route path="transactions" element={<TransactionsPage />} />
        <Route path="analytics" element={<AnalyticsPage />} />
        <Route path="income" element={<IncomePage />} />
      </Route>

      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  )
}
