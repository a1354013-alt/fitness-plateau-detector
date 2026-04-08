import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// ----------------------------------------------------------------------------
// Types (API contracts)
// ----------------------------------------------------------------------------

export interface HealthRecord {
  id: number
  record_date: string
  weight: number
  sleep_hours: number
  calories: number
  protein?: number
  exercise_minutes: number
  exercise_type?: string
  steps?: number
  note?: string
  created_at: string
  updated_at: string
}

export interface HealthRecordCreate {
  record_date: string
  weight: number
  sleep_hours: number
  calories: number
  protein?: number
  exercise_minutes?: number
  exercise_type?: string
  steps?: number
  note?: string
}

export interface HealthRecordUpdate extends Partial<HealthRecordCreate> {}

export interface HealthRecordListResponse {
  total: number
  records: HealthRecord[]
}

export interface DashboardData {
  current_weight: number | null
  avg_weight_7d: number | null
  avg_sleep_7d: number | null
  avg_calories_7d: number | null
  weight_change_7d: number | null
  total_records: number
  last_record_date: string | null
}

export interface TrendPoint {
  date: string
  weight: number
  sleep_hours: number
  calories: number
  exercise_minutes: number
  steps?: number
}

export interface TrendsData {
  days: number
  data_points: number
  trends: TrendPoint[]
}

export interface PlateauData {
  status: 'losing' | 'plateau' | 'gaining' | 'insufficient_data'
  rule_a: boolean | null
  rule_b: boolean | null
  last7_avg: number | null
  prev7_avg: number | null
  avg_change?: number | null
  last7_fluctuation: number | null
  last7_min: number | null
  last7_max: number | null
  data_completeness?: number
  message?: string
}

export interface ReasonItem {
  code: string
  label: string
  description: string
  severity: number
  value: number
  threshold: number
  details?: Record<string, unknown>
}

export interface ReasonsData {
  status: 'ok' | 'insufficient_data'
  message?: string
  reasons: ReasonItem[]
  all_reasons: ReasonItem[]
  data_points: number
  missing_days: number
}

export interface SummaryData {
  plateau: PlateauData
  reasons: ReasonsData
  summary: {
    text: string
    insight: string
    status: PlateauData['status']
    top_reasons: string[]
  }
}

// ----------------------------------------------------------------------------
// Health Records API
// ----------------------------------------------------------------------------

export const healthRecordsApi = {
  list(params?: { skip?: number; limit?: number; start_date?: string; end_date?: string }) {
    return api.get<HealthRecordListResponse>('/health-records', { params })
  },

  get(id: number) {
    return api.get<HealthRecord>(`/health-records/${id}`)
  },

  create(data: HealthRecordCreate) {
    return api.post<HealthRecord>('/health-records', data)
  },

  update(id: number, data: HealthRecordUpdate) {
    return api.put<HealthRecord>(`/health-records/${id}`, data)
  },

  delete(id: number) {
    return api.delete(`/health-records/${id}`)
  },
}

// ----------------------------------------------------------------------------
// Analytics API
// ----------------------------------------------------------------------------

export const analyticsApi = {
  dashboard() {
    return api.get<DashboardData>('/analytics/dashboard')
  },

  trends(days: number = 30) {
    return api.get<TrendsData>('/analytics/trends', { params: { days } })
  },

  plateau() {
    return api.get<PlateauData>('/analytics/plateau')
  },

  reasons(calorieTarget: number) {
    return api.get<ReasonsData>('/analytics/reasons', {
      params: { calorie_target: calorieTarget },
    })
  },

  summary(calorieTarget: number) {
    return api.get<SummaryData>('/analytics/summary', {
      params: { calorie_target: calorieTarget },
    })
  },
}

export default api
