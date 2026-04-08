import { describe, expect, it, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { reactive } from 'vue'

import Analysis from '@/views/Analysis.vue'

function makeStore(overrides: Record<string, unknown> = {}) {
  return {
    calorieTarget: 2000,
    summary: null,

    summaryStatus: { loading: false, error: null },
    analysisPageError: null,

    summaryText: '',
    plateauStatus: 'insufficient_data',
    plateauData: null,
    reasonsData: null,
    summaryInsight: '',
    topReasons: [],

    fetchAnalysisBundle: vi.fn().mockResolvedValue(undefined),

    ...overrides,
  }
}

type StoreStub = ReturnType<typeof makeStore>
let store: StoreStub = makeStore()
vi.mock('@/stores/analytics', () => ({ useAnalyticsStore: () => store }))

describe('Analysis view states', () => {
  it('shows loading panel on initial analysis load', () => {
    store = makeStore({ summaryStatus: { loading: true, error: null } })

    const wrapper = mount(Analysis, {
      global: {
        stubs: {
          RouterLink: true,
          Button: true,
          InputNumber: true,
        },
      },
    })

    expect(wrapper.text()).toContain('Analyzing...')
  })

  it('shows error panel when analysis fails', () => {
    store = makeStore({ analysisPageError: 'Failed to fetch analysis summary' })

    const wrapper = mount(Analysis, {
      global: {
        stubs: {
          RouterLink: true,
          Button: true,
          InputNumber: true,
        },
      },
    })

    expect(wrapper.text()).toContain("Couldn't load analysis")
  })

  it('shows insufficient-data empty state', () => {
    store = makeStore({
      plateauStatus: 'insufficient_data',
      summaryStatus: { loading: false, error: null },
    })

    const wrapper = mount(Analysis, {
      global: {
        stubs: {
          RouterLink: true,
          Button: true,
          InputNumber: true,
        },
      },
    })

    expect(wrapper.text()).toContain('Not enough data for analysis')
  })

  it('renders plateau status and reasons when data is available', () => {
    store = makeStore({
      plateauStatus: 'plateau',
      summaryText: 'Plateau detected.',
      plateauData: {
        status: 'plateau',
        rule_a: true,
        rule_b: true,
        last7_avg: 75,
        prev7_avg: 75.1,
        avg_change: -0.1,
        last7_fluctuation: 0.6,
        last7_min: 74.7,
        last7_max: 75.3,
        data_completeness: 1,
        message: null,
      },
      reasonsData: {
        status: 'ok',
        message: null,
        reasons: [
          {
            code: 'HighCalories',
            label: 'Calorie Surplus',
            description: 'Average calories above target.',
            severity: 0.8,
            value: 2200,
            threshold: 2000,
          },
        ],
        all_reasons: [],
        data_points: 7,
        missing_days: 0,
      },
      summaryInsight: 'Do X.\nDo Y.',
    })

    const wrapper = mount(Analysis, {
      global: {
        stubs: {
          RouterLink: true,
          Button: true,
          InputNumber: true,
        },
      },
    })

    expect(wrapper.text()).toContain('PLATEAU')
    expect(wrapper.text()).toContain('Cause Analysis')
    expect(wrapper.text()).toContain('Calorie Surplus')
    expect(wrapper.text()).toContain('Actionable Insights')
  })

  it('refreshes analysis on calorie target blur', async () => {
    const fetchAnalysisBundle = vi.fn().mockResolvedValue(undefined)
    store = reactive(makeStore({ fetchAnalysisBundle })) as unknown as StoreStub

    const wrapper = mount(Analysis, {
      global: {
        stubs: {
          RouterLink: true,
          Button: {
            template: `<button @click="$emit('click')"><slot /></button>`,
          },
          InputNumber: {
            template: `<input :value="modelValue" @input="$emit('update:modelValue', Number($event.target.value))" @blur="$emit('blur')" />`,
            props: ['modelValue'],
          },
        },
      },
    })

    const input = wrapper.find('input')
    await input.setValue('2500')
    await input.trigger('blur')

    expect(fetchAnalysisBundle).toHaveBeenLastCalledWith(2500)
  })

  it('clicking refresh button calls fetchAnalysisBundle with current target', async () => {
    const fetchAnalysisBundle = vi.fn().mockResolvedValue(undefined)
    store = makeStore({ calorieTarget: 2200, fetchAnalysisBundle })

    const wrapper = mount(Analysis, {
      global: {
        stubs: {
          RouterLink: true,
          Button: {
            props: ['icon', 'loading', 'label'],
            template: `<button :data-icon="icon" @click="$emit('click')"><slot /></button>`,
          },
          InputNumber: true,
        },
      },
    })

    const refresh = wrapper.find('button[data-icon="pi pi-refresh"]')
    await refresh.trigger('click')

    expect(fetchAnalysisBundle).toHaveBeenCalledWith(2200)
  })
})
