import { beforeEach, describe, expect, it, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import { defineComponent, h, nextTick } from 'vue'

import Records from '@/views/Records.vue'
import { useHealthRecordsStore } from '@/stores/healthRecords'
import { healthRecordsApi, type HealthRecordListResponse } from '@/services/api'

vi.mock('@/services/api', async (importOriginal) => {
  const actual = await importOriginal<typeof import('@/services/api')>()
  return {
    ...actual,
    healthRecordsApi: {
      ...actual.healthRecordsApi,
      list: vi.fn(),
      create: vi.fn(),
      update: vi.fn(),
      delete: vi.fn(),
    },
  }
})

vi.mock('@/stores/analytics', () => ({
  useAnalyticsStore: () => ({ calorieTarget: 2000 }),
}))

const confirmRequire = vi.fn()
vi.mock('primevue/useconfirm', () => ({
  useConfirm: () => ({ require: confirmRequire }),
}))

vi.mock('primevue/usetoast', () => ({
  useToast: () => ({ add: vi.fn() }),
}))

function wrapList(payload: HealthRecordListResponse) {
  return { data: payload } as unknown as { data: HealthRecordListResponse }
}

async function flushUi() {
  // flush pending promises + Vue re-render
  await Promise.resolve()
  await nextTick()
  await Promise.resolve()
  await nextTick()
}

const ButtonStub = defineComponent({
  name: 'ButtonStub',
  props: {
    label: { type: String, default: '' },
    icon: { type: String, default: '' },
    loading: { type: Boolean, default: false },
  },
  emits: ['click'],
  setup(props, { emit, slots }) {
    return () =>
      h(
        'button',
        {
          'data-label': props.label,
          'data-icon': props.icon,
          disabled: props.loading,
          onClick: () => emit('click'),
        },
        slots.default ? slots.default() : props.label,
      )
  },
})

const DataTableStub = defineComponent({
  name: 'DataTableStub',
  props: {
    value: { type: Array, default: () => [] },
    paginator: { type: Boolean, default: false },
  },
  setup(props, { slots }) {
    // Provide the rows to Column stubs so they can render body templates.
    return () =>
      h(
        'div',
        { 'data-test': 'datatable', 'data-paginator': String(props.paginator) },
        [
          ...(slots.default ? slots.default() : []),
          (props.value as unknown[]).length === 0 && slots.empty ? slots.empty() : null,
        ],
      )
  },
})

const ColumnStub = defineComponent({
  name: 'ColumnStub',
  setup(_, { slots }) {
    // PrimeVue DataTable normally provides `data` in the body slot; in unit tests we render it ourselves.
    const store = useHealthRecordsStore()
    return () =>
      h(
        'div',
        { 'data-test': 'column' },
        store.records.map((row) => (slots.body ? slots.body({ data: row }) : null)),
      )
  },
})

const DialogStub = defineComponent({
  name: 'DialogStub',
  props: { visible: { type: Boolean, default: false } },
  setup(props, { slots }) {
    return () => (props.visible ? h('div', { 'data-test': 'dialog' }, slots.default?.()) : null)
  },
})

describe('Records view', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
  })

  it('renders empty state when total=0 and not loading', async () => {
    const listMock = vi.mocked(healthRecordsApi.list)
    listMock.mockResolvedValueOnce(wrapList({ total: 0, records: [] }))

    const wrapper = mount(Records, {
      global: {
        directives: {
          tooltip: () => undefined,
        },
        stubs: {
          Button: ButtonStub,
          Dialog: DialogStub,
          ConfirmDialog: true,
          DatePicker: true,
          InputNumber: true,
          InputText: true,
          Textarea: true,
          DataTable: DataTableStub,
          Column: ColumnStub,
        },
      },
    })

    await flushUi()
    expect(wrapper.text()).toContain('No records yet')
  })

  it('renders error state when store has an error', async () => {
    const listMock = vi.mocked(healthRecordsApi.list)
    listMock.mockRejectedValueOnce(new Error('boom'))

    const wrapper = mount(Records, {
      global: {
        directives: {
          tooltip: () => undefined,
        },
        stubs: {
          Button: ButtonStub,
          Dialog: DialogStub,
          ConfirmDialog: true,
          DatePicker: true,
          InputNumber: true,
          InputText: true,
          Textarea: true,
          DataTable: DataTableStub,
          Column: ColumnStub,
        },
      },
    })

    await flushUi()
    expect(wrapper.text()).toContain("Couldn't load records")
  })

  it('renders paginator when total > rows', async () => {
    const listMock = vi.mocked(healthRecordsApi.list)
    listMock.mockResolvedValueOnce(
      wrapList({
        total: 50,
        records: [
          {
            id: 1,
            record_date: '2026-04-01',
            weight: 75,
            sleep_hours: 7,
            calories: 2000,
            exercise_minutes: 0,
            created_at: '2026-04-01T00:00:00Z',
            updated_at: '2026-04-01T00:00:00Z',
          },
        ],
      }),
    )

    const wrapper = mount(Records, {
      global: {
        directives: {
          tooltip: () => undefined,
        },
        stubs: {
          Button: ButtonStub,
          Dialog: DialogStub,
          ConfirmDialog: true,
          DatePicker: true,
          InputNumber: true,
          InputText: true,
          Textarea: true,
          DataTable: DataTableStub,
          Column: ColumnStub,
        },
      },
    })

    await flushUi()
    const table = wrapper.get('[data-test="datatable"]')
    expect(table.attributes('data-paginator')).toBe('true')
    expect(wrapper.text()).toContain('Showing')
  })

  it('delete triggers confirm, and store performs empty-page fallback (refetch twice)', async () => {
    const store = useHealthRecordsStore()
    store.setQuery({ skip: 20, limit: 20 })

    const listMock = vi.mocked(healthRecordsApi.list)
    const deleteMock = vi.mocked(healthRecordsApi.delete)

    // Initial page load (skip=20) returns 1 record (e.g. last page).
    listMock.mockResolvedValueOnce(
      wrapList({
        total: 21,
        records: [
          {
            id: 21,
            record_date: '2026-04-21',
            weight: 75,
            sleep_hours: 7,
            calories: 2000,
            exercise_minutes: 0,
            created_at: '2026-04-21T00:00:00Z',
            updated_at: '2026-04-21T00:00:00Z',
          },
        ],
      }),
    )

    deleteMock.mockResolvedValueOnce({} as unknown as never)

    // After delete: current page becomes empty.
    listMock
      .mockResolvedValueOnce(wrapList({ total: 21, records: [] }))
      // Fallback to previous page (skip=0)
      .mockResolvedValueOnce(
        wrapList({
          total: 21,
          records: [
            {
              id: 1,
              record_date: '2026-04-01',
              weight: 75,
              sleep_hours: 7,
              calories: 2000,
              exercise_minutes: 0,
              created_at: '2026-04-01T00:00:00Z',
              updated_at: '2026-04-01T00:00:00Z',
            },
          ],
        }),
      )

    confirmRequire.mockImplementationOnce((opts: { accept: () => Promise<void> }) => {
      // Auto-accept deletes in the test.
      void opts.accept()
    })

    const wrapper = mount(Records, {
      global: {
        directives: {
          tooltip: () => undefined,
        },
        stubs: {
          Button: ButtonStub,
          Dialog: DialogStub,
          ConfirmDialog: true,
          DatePicker: true,
          InputNumber: true,
          InputText: true,
          Textarea: true,
          DataTable: DataTableStub,
          Column: ColumnStub,
        },
      },
    })

    await flushUi()

    // Find the delete icon button (trash).
    const deleteBtn = wrapper.findAll('button').find((b) => b.attributes('data-icon') === 'pi pi-trash')
    expect(deleteBtn).toBeTruthy()

    await deleteBtn!.trigger('click')
    await flushUi()

    // store.deleteRecord triggers refetch (current page) then fallback (previous page)
    expect(listMock).toHaveBeenCalledWith({ skip: 20, limit: 20 })
    expect(listMock).toHaveBeenCalledWith({ skip: 0, limit: 20 })
  })
})
