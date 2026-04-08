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
})
