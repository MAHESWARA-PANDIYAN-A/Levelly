export interface InsurancePlan {
  id: number
  name: string
  code: string
  description: string
  premium: number
  premium_frequency: string
  coverage_limit: number
  policy_duration: string
  covered_events: string[]
  trigger_conditions: Record<string, string>
  waiting_period: string
  exclusions: string[]
  coverage_area_rules: Record<string, any>
  active: boolean
  partner_name?: string
}

export interface InsuranceDocument {
  id: number
  title: string
  document_type: string
  file_url: string
  created_at: string
}

export interface InsurancePolicy {
  id: number
  user_id: number
  plan_id: number
  plan_name: string
  partner_name?: string
  policy_number: string
  status: 'ACTIVE' | 'EXPIRED' | 'CANCELLED' | 'PENDING'
  start_date: string
  end_date: string
  premium: number
  coverage_limit: number
  covered_work_zone: string
  created_at: string
  documents: InsuranceDocument[]
}

export interface InsuranceEvent {
  id: number
  event_type: 'HEAVY_RAIN' | 'FLOOD' | 'EXTREME_HEAT' | 'WORK_DISRUPTION' | string
  zone: string
  start_time: string
  end_time?: string
  duration: string
  source: string
  source_reference?: string
  verification_status: 'VERIFIED' | 'MONITORING' | 'UNVERIFIED' | string
  severity: 'LOW' | 'MODERATE' | 'SEVERE' | string
  telemetry_data?: Record<string, any>
  created_at: string
}

export interface InsuranceIncomeImpact {
  user_id: number
  event_id?: number
  event_type: string
  zone: string
  expected_daily_income: number
  typical_weekly_income: number
  estimated_disrupted_income: number
  estimated_income_impact: number
  volatility_level: string
  trend: string
  disclaimer: string
}

export interface InsuranceTriggerEvaluation {
  id: number
  policy_id: number
  event_id: number
  trigger_type: string
  threshold: string
  observed_value: string
  required_value: string
  status: 'NOT_REACHED' | 'REACHED' | 'INVALID' | 'PENDING'
  evaluated_at: string
  reason: string
}

export interface InsurancePayout {
  id: number
  policy_id: number
  event_id?: number
  payout_id_from_partner?: string
  amount?: number
  currency: string
  status: 'PENDING' | 'PROCESSING' | 'COMPLETED' | 'FAILED' | 'REJECTED'
  reason: string
  processed_at?: string
  destination_reference?: string
  destination_type: string
  created_at: string
  amount_display: string
}

export interface InsuranceStatus {
  has_active_policy: boolean
  insurance_state?: 'NO_POLICY' | 'PLAN_SELECTED' | 'PURCHASE_REVIEW' | 'PURCHASE_PENDING' | 'ACTIVE' | 'EXPIRED' | string
  selected_plan_id?: number | null
  policy?: InsurancePolicy | null
  active_events: InsuranceEvent[]
  latest_payout?: InsurancePayout | null
  safety_wallet_balance: number
  safety_wallet_target: number
  safety_wallet_shortfall: number
  resilience_score: number
  average_daily_income: number
  average_weekly_income: number
}

export interface InsurancePersonalizedImpact {
  user_id: number
  plan_id: number
  plan_name: string
  plan_code: string
  premium: number
  premium_frequency: string
  coverage_limit: number
  expected_daily_income: number
  typical_weekly_income: number
  estimated_disrupted_income: number
  estimated_income_impact: number
  volatility_level: string
  trend: string
  work_zone: string
  example_event: {
    selected_plan: string
    event_type: string
    covered_area: string
    typical_earnings: number
    estimated_income_impact: number
    plan_trigger: string
    explanation: string
  }
  disclaimer: string
  impact_label: string
}
