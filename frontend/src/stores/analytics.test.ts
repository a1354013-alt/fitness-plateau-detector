import { beforeEach, describe, expect, it, vi } from 'vitest'
import { createPinia, setActivePinia } from 'pinia'

import { useAnalyticsStore } from '@/stores/analytics'
import { analyticsApi, type DashboardData, type SummaryData, type TrendsData } from '@/services/api'

vi.mock('@/services/api', async (importOriginal) => {
  const actual = await importOriginal<typeof import('@/services/api')>()
  return {
    ...actual,
    analyticsApi: {
      ...actual.analyticsApi,
      dashboard: vi.fn(),
      trends: vi.fn(),
      summary: vi.fn(),
    },
  }
})

function wrap<T>(data: T) {
  return { data } as unknown as { data: T }
}

describe('analytics store', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
  })

  it('fetchAll populates domains and clears error', async () => {
    const store = useAnalyticsStore()

    const dashboardMock = vi.mocked(analyticsApi.dashboard)
    const trendsMock = vi.mocked(analyticsApi.trends)
    const summaryMock = vi.mocked(analyticsApi.summary)

    const dashboard: DashboardData = {
      current_weight: 75,
      avg_weight_7d: 74.5,
      avg_sleep_7d: 7,
      avg_calories_7d: 2000,
      weight_change_7d: null,
      total_records: 10,
      last_record_date: '2026-04-01',
    }

    const trends: TrendsData = { days: 30, data_points: 0, trends: [] }

    const summary: SummaryData = {
      plateau: {
        status: 'insufficient_data',
        rule_a: null,
        rule_b: null,
        last7_avg: null,
        prev7_avg: null,
        last7_fluctuation: null,
        last7_min: null,
        last7_max: null,
        message: 'Need data',
      },
      reasons: {
        status: 'insufficient_data',
        reasons: [],
        all_reasons: [],
        data_points: 0,
        missing_days: 7,
      },
      summary: {
        text: 'Need data',
        insight: 'Recommended actions:\n- Log more',
        status: 'insufficient_data',
        top_reasons: [],
      },
    }

    dashboardMock.mockResolvedValueOnce(wrap(dashboard))
    trendsMock.mockResolvedValueOnce(wrap(trends))
    summaryMock.mockResolvedValueOnce(wrap(summary))

    await store.fetchAll(30, 2000)

    expect(store.error).toBe(null)
    expect(store.dashboard?.total_records).toBe(10)
    expect(store.summaryText).toContain('Need data')
    expect(store.trends?.days).toBe(30)
  })
})

