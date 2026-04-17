import { beforeEach, describe, expect, it, vi } from 'vitest'
import { createPinia, setActivePinia } from 'pinia'

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

function mockListResponse(payload: HealthRecordListResponse) {
  return { data: payload } as unknown as { data: HealthRecordListResponse }
}

describe('healthRecords store', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
  })

  it('fetchRecords applies query and stores results', async () => {
    const store = useHealthRecordsStore()
    const listMock = vi.mocked(healthRecordsApi.list)

    listMock.mockResolvedValueOnce(
      mockListResponse({
        total: 1,
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

    await store.fetchRecords({ skip: 0, limit: 20 })

    expect(store.query.skip).toBe(0)
    expect(store.query.limit).toBe(20)
    expect(store.total).toBe(1)
    expect(store.records).toHaveLength(1)
  })

  it('fetchRecords normalizes query bounds and surfaces errors', async () => {
    const store = useHealthRecordsStore()
    const listMock = vi.mocked(healthRecordsApi.list)

    listMock.mockRejectedValueOnce(new Error('boom'))
    await store.fetchRecords({ skip: -10, limit: 9999 })

    expect(store.query.skip).toBe(0)
    expect(store.query.limit).toBe(500)
    expect(store.loading).toBe(false)
    expect(store.error).toContain('boom')
  })

  it('createRecord calls API and refetches; returns null on error', async () => {
    const store = useHealthRecordsStore()
    const createMock = vi.mocked(healthRecordsApi.create)
    const listMock = vi.mocked(healthRecordsApi.list)

    createMock.mockResolvedValueOnce({
      data: {
        id: 1,
        record_date: '2026-04-01',
        weight: 75,
        sleep_hours: 7,
        calories: 2000,
        exercise_minutes: 0,
        created_at: '2026-04-01T00:00:00Z',
        updated_at: '2026-04-01T00:00:00Z',
      },
    } as unknown as never)
    listMock.mockResolvedValueOnce(mockListResponse({ total: 1, records: [] }))

    const ok = await store.createRecord({
      record_date: '2026-04-01',
      weight: 75,
      sleep_hours: 7,
      calories: 2000,
      exercise_minutes: 0,
    })
    expect(ok?.id).toBe(1)
    expect(createMock).toHaveBeenCalledTimes(1)
    expect(listMock).toHaveBeenCalledTimes(1)

    createMock.mockRejectedValueOnce(new Error('nope'))
    const bad = await store.createRecord({
      record_date: '2026-04-02',
      weight: 75,
      sleep_hours: 7,
      calories: 2000,
      exercise_minutes: 0,
    })
    expect(bad).toBe(null)
    expect(store.error).toContain('nope')
  })

  it('updateRecord returns null and sets error on failure', async () => {
    const store = useHealthRecordsStore()
    const updateMock = vi.mocked(healthRecordsApi.update)

    updateMock.mockRejectedValueOnce(new Error('boom'))
    const res = await store.updateRecord(1, { weight: 76 })
    expect(res).toBe(null)
    expect(store.error).toContain('boom')
  })

  it('deleteRecord steps back when current page becomes empty', async () => {
    const store = useHealthRecordsStore()

    const deleteMock = vi.mocked(healthRecordsApi.delete)
    const listMock = vi.mocked(healthRecordsApi.list)

    // Start on page 2 (skip=20, limit=20)
    listMock.mockResolvedValueOnce(mockListResponse({ total: 1, records: [] }))
    await store.fetchRecords({ skip: 20, limit: 20 })
    listMock.mockClear()

    deleteMock.mockResolvedValueOnce({} as unknown as never)

    listMock
      .mockResolvedValueOnce(mockListResponse({ total: 1, records: [] }))
      .mockResolvedValueOnce(
        mockListResponse({
          total: 1,
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

    const ok = await store.deleteRecord(123)
    expect(ok).toBe(true)

    expect(listMock).toHaveBeenCalledTimes(2)
    expect(listMock.mock.calls[0]?.[0]).toEqual({ skip: 20, limit: 20 })
    expect(listMock.mock.calls[1]?.[0]).toEqual({ skip: 0, limit: 20 })
  })

  it('deleteRecord returns false and sets error on failure', async () => {
    const store = useHealthRecordsStore()
    const deleteMock = vi.mocked(healthRecordsApi.delete)

    deleteMock.mockRejectedValueOnce(new Error('boom'))
    const ok = await store.deleteRecord(1)
    expect(ok).toBe(false)
    expect(store.error).toContain('boom')
  })
})
