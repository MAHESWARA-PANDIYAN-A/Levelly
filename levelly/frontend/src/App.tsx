import { Routes, Route, Navigate } from 'react-router-dom'
import { useAuthStore } from './store/authStore'
import Layout from './components/Layout'
import LoginPage from './pages/LoginPage'
import RegisterPage from './pages/RegisterPage'
import HomePage from './pages/HomePage'
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

import SafetyWalletPage from './pages/SafetyWalletPage'

// IncomeShield Insurance Module
import IncomeShieldHomePage from './insurance/pages/IncomeShieldHomePage'
import HowItWorksPage from './insurance/pages/HowItWorksPage'
import PersonalizedProtectionPage from './insurance/pages/PersonalizedProtectionPage'
import PlansPage from './insurance/pages/PlansPage'
import PlanDetailPage from './insurance/pages/PlanDetailPage'
import PurchaseReviewPage from './insurance/pages/PurchaseReviewPage'
import ActivePolicyPage from './insurance/pages/ActivePolicyPage'
import EventMonitoringPage from './insurance/pages/EventMonitoringPage'
import PayoutStatusPage from './insurance/pages/PayoutStatusPage'

function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { isAuthenticated, user } = useAuthStore()
  if (!isAuthenticated) return <Navigate to="/login" replace />
  // If admin lands directly on consumer home, redirect them to admin operations portal
  if (user?.role === 'admin' && window.location.pathname === '/') {
    return <Navigate to="/admin" replace />
  }
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
        <Route path="safety" element={<SafetyWalletPage />} />
        <Route path="wallets" element={<SafetyWalletPage />} />
        <Route path="pay" element={<PaymentPage />} />
        <Route path="grow" element={<GrowPage />} />
        <Route path="grow/invest/:productId" element={<InvestmentDetailPage />} />
        <Route path="credit" element={<CreditPage />} />
        <Route path="profile" element={<ProfilePage />} />
        <Route path="large-expense" element={<LargeExpensePage />} />
        <Route path="coach" element={<CoachPage />} />
        <Route path="notifications" element={<NotificationsPage />} />
        <Route path="transactions" element={<TransactionsPage />} />
        <Route path="analytics" element={<AnalyticsPage />} />
        <Route path="income" element={<IncomePage />} />

        {/* LEVELLY IncomeShield Native Module */}
        <Route path="incomeshield" element={<IncomeShieldHomePage />} />
        <Route path="incomeshield/how-it-works" element={<HowItWorksPage />} />
        <Route path="incomeshield/personalized" element={<PersonalizedProtectionPage />} />
        <Route path="incomeshield/personalized/:planId" element={<PersonalizedProtectionPage />} />
        <Route path="incomeshield/plans" element={<PlansPage />} />
        <Route path="incomeshield/plans/:planId" element={<PlanDetailPage />} />
        <Route path="incomeshield/review/:planId" element={<PurchaseReviewPage />} />
        <Route path="incomeshield/purchase-review/:planId" element={<PurchaseReviewPage />} />
        <Route path="incomeshield/policy" element={<ActivePolicyPage />} />
        <Route path="incomeshield/events/:eventId" element={<EventMonitoringPage />} />
        <Route path="incomeshield/payouts/:payoutId" element={<PayoutStatusPage />} />
        <Route path="insurance" element={<Navigate to="/incomeshield" replace />} />
      </Route>

      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  )
}
