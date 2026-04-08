import { describe, expect, it, vi } from 'vitest'
import { mount } from '@vue/test-utils'

import Dashboard from '@/views/Dashboard.vue'

function makeStore(overrides: Record<string, unknown> = {}) {
  return {
    calorieTarget: 2000,
    summary: null,
    dashboard: null,
    trends: null,

    dashboardStatus: { loading: false, error: null },
    summaryStatus: { loading: false, error: null },
    trendsStatus: { loading: false, error: null },

    dashboardPageError: null,

    summaryText: '',
    plateauStatus: 'insufficient_data',

    fetchTrendsOnly: vi.fn().mockResolvedValue(undefined),
    fetchDashboardBundle: vi.fn().mockResolvedValue(undefined),

    ...overrides,
  }
}

type StoreStub = ReturnType<typeof makeStore>
let store: StoreStub = makeStore()
vi.mock('@/stores/analytics', () => ({ useAnalyticsStore: () => store }))

describe('Dashboard view states', () => {
  it('shows loading state on initial load', () => {
    store = makeStore({
      summaryStatus: { loading: true, error: null },
      dashboardStatus: { loading: true, error: null },
    })

    const wrapper = mount(Dashboard, {
      global: {
        stubs: {
          Line: true,
          Bar: true,
          RouterLink: true,
          Button: true,
        },
      },
    })

    expect(wrapper.text()).toContain('Loading dashboard...')
  })

  it('shows page error when required domains are missing', () => {
    store = makeStore({
      dashboardPageError: 'Failed to fetch dashboard',
    })

    const wrapper = mount(Dashboard, {
      global: {
        stubs: {
          Line: true,
          Bar: true,
          RouterLink: true,
          Button: true,
        },
      },
    })

    expect(wrapper.text()).toContain("Couldn't load dashboard")
  })

  it('shows empty state when total_records is 0', () => {
    store = makeStore({
      dashboard: {
        current_weight: null,
        avg_weight_7d: null,
        avg_sleep_7d: null,
        avg_calories_7d: null,
        weight_change_7d: null,
        total_records: 0,
        last_record_date: null,
      },
    })

    const wrapper = mount(Dashboard, {
      global: {
        stubs: {
          Line: true,
          Bar: true,
          RouterLink: true,
          Button: true,
        },
      },
    })

    expect(wrapper.text()).toContain('No records yet')
  })

  it('switching day range only refreshes trends', async () => {
    const fetchDashboardBundle = vi.fn().mockResolvedValue(undefined)
    const fetchTrendsOnly = vi.fn().mockResolvedValue(undefined)

    store = makeStore({
      dashboard: {
        current_weight: 75,
        avg_weight_7d: 74.5,
        avg_sleep_7d: 7,
        avg_calories_7d: 2000,
        weight_change_7d: null,
        total_records: 10,
        last_record_date: '2026-04-01',
      },
      summary: {
        plateau: {
          status: 'plateau',
          rule_a: true,
          rule_b: true,
          last7_avg: 75,
          prev7_avg: 75,
          avg_change: 0,
          last7_fluctuation: 0.6,
          last7_min: 74.7,
          last7_max: 75.3,
          data_completeness: 1,
          message: null,
        },
        reasons: { status: 'ok', message: null, reasons: [], all_reasons: [], data_points: 7, missing_days: 0 },
        summary: { text: 'ok', insight: '', status: 'plateau', top_reasons: [] },
      },
      summaryText: 'ok',
      plateauStatus: 'plateau',
      trends: { days: 7, data_points: 1, trends: [{ date: '2026-04-01', weight: 75, sleep_hours: 7, calories: 2000, exercise_minutes: 0 }] },
      fetchDashboardBundle,
      fetchTrendsOnly,
    })

    const wrapper = mount(Dashboard, {
      global: {
        stubs: {
          Line: true,
          Bar: true,
          RouterLink: true,
          Button: true,
        },
      },
    })

    // onMounted triggers initial bundle fetch once
    await Promise.resolve()
    expect(fetchDashboardBundle).toHaveBeenCalledTimes(1)

    const btn = wrapper.findAll('button').find((b) => b.text() === '14d')
    expect(btn).toBeTruthy()
    await btn!.trigger('click')

    expect(fetchTrendsOnly).toHaveBeenCalledWith(14)
    expect(fetchDashboardBundle).toHaveBeenCalledTimes(1)
  })

  it('does not show page error when only trends fails', () => {
    store = makeStore({
      dashboard: {
        current_weight: 75,
        avg_weight_7d: 74.5,
        avg_sleep_7d: 7,
        avg_calories_7d: 2000,
        weight_change_7d: null,
        total_records: 10,
        last_record_date: '2026-04-01',
      },
      summary: {
        plateau: {
          status: 'plateau',
          rule_a: true,
          rule_b: true,
          last7_avg: 75,
          prev7_avg: 75,
          avg_change: 0,
          last7_fluctuation: 0.6,
          last7_min: 74.7,
          last7_max: 75.3,
          data_completeness: 1,
          message: null,
        },
        reasons: { status: 'ok', message: null, reasons: [], all_reasons: [], data_points: 7, missing_days: 0 },
        summary: { text: 'ok', insight: '', status: 'plateau', top_reasons: [] },
      },
      summaryText: 'ok',
      plateauStatus: 'plateau',
      trendsStatus: { loading: false, error: 'trends down' },
      dashboardPageError: null,
      trends: { days: 7, data_points: 0, trends: [] },
    })

    const wrapper = mount(Dashboard, {
      global: {
        stubs: {
          Line: true,
          Bar: true,
          RouterLink: true,
          Button: true,
        },
      },
    })

    expect(wrapper.text()).not.toContain("Couldn't load dashboard")
    expect(wrapper.text()).toContain('Failed to load charts.')
  })
})
