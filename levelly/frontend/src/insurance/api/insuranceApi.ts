import api from '../../lib/api'
import type {
  InsurancePlan,
  InsurancePolicy,
  InsuranceEvent,
  InsuranceIncomeImpact,
  InsuranceTriggerEvaluation,
  InsurancePayout,
  InsuranceDocument,
  InsuranceStatus,
} from '../types/insurance.types'

export const insuranceApi = {
  // Status summary
  getStatus: () => api.get<InsuranceStatus>('/insurance/status'),

  // Plans
  getPlans: () => api.get<InsurancePlan[]>('/insurance/plans'),
  getPlan: (id: number) => api.get<InsurancePlan>(`/insurance/plans/${id}`),
  selectPlan: (planId: number) =>
    api.post<{ success: boolean; message: string; plan_id: number; plan_name: string; state: string }>(
      '/insurance/select-plan',
      { plan_id: planId }
    ),

  // Personalized Intelligence for Chosen Plan
  getPersonalized: (planId: number) =>
    api.get<any>(`/insurance/personalized/${planId}`),

  // Policy
  getPolicy: () => api.get<{ has_policy: boolean; policy: InsurancePolicy | null }>('/insurance/policy'),
  purchase: (data: {
    plan_id: number
    terms_accepted: boolean
    terms_version?: string
    work_zone?: string
  }) => api.post<{ success: boolean; message: string; policy: InsurancePolicy }>('/insurance/purchase', data),

  // Events & Telemetry
  getEvents: (zone?: string) =>
    api.get<InsuranceEvent[]>(`/insurance/events${zone ? `?zone=${encodeURIComponent(zone)}` : ''}`),
  getEventDetails: (id: number) => api.get<InsuranceEvent>(`/insurance/events/${id}`),
  getEventImpact: (id: number) => api.get<InsuranceIncomeImpact>(`/insurance/events/${id}/impact`),
  getEventTrigger: (id: number) => api.get<InsuranceTriggerEvaluation>(`/insurance/events/${id}/trigger`),

  // Payouts
  getPayouts: () => api.get<InsurancePayout[]>('/insurance/payouts'),
  getPayoutDetails: (id: number) => api.get<InsurancePayout>(`/insurance/payouts/${id}`),
  moveToSafetyWallet: (payoutId: number, amount: number) =>
    api.post(`/insurance/payouts/${payoutId}/move-to-safety`, { amount }),

  // Documents & Support
  getDocuments: () => api.get<InsuranceDocument[]>('/insurance/documents'),
  getSupport: () => api.get<any>('/insurance/support'),

  // Demo helpers for testing
  simulateDisruption: (data?: any) => api.post('/insurance/demo/simulate-disruption', data || {}),
  evaluateTriggerDemo: (eventId: number) => api.post(`/insurance/demo/evaluate-trigger?event_id=${eventId}`),
  completePayoutDemo: (payoutId: number) => api.post(`/insurance/demo/complete-payout/${payoutId}`),
}
