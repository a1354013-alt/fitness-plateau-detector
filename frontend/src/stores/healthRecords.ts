import { defineStore } from 'pinia'
import { ref } from 'vue'

import {
  healthRecordsApi,
  type HealthRecord,
  type HealthRecordCreate,
  type HealthRecordUpdate,
} from '@/services/api'
import { getApiErrorMessage } from '@/services/errors'

export type HealthRecordsQuery = {
  skip: number
  limit: number
  start_date?: string
  end_date?: string
}

function normalizeQuery(query: HealthRecordsQuery): HealthRecordsQuery {
  const limit = Math.min(Math.max(query.limit, 1), 500)
  const skip = Math.max(query.skip, 0)
  const out: HealthRecordsQuery = { skip, limit }
  if (query.start_date) out.start_date = query.start_date
  if (query.end_date) out.end_date = query.end_date
  return out
}

export const useHealthRecordsStore = defineStore('healthRecords', () => {
  const records = ref<HealthRecord[]>([])
  const total = ref(0)
  const loading = ref(false)
  const error = ref<string | null>(null)

  const query = ref<HealthRecordsQuery>({ skip: 0, limit: 20 })

  function setQuery(next: HealthRecordsQuery) {
    query.value = normalizeQuery(next)
  }

  async function fetchRecords(next?: HealthRecordsQuery) {
    loading.value = true
    error.value = null

    if (next) {
      setQuery(next)
    }

    try {
      const res = await healthRecordsApi.list(query.value)
      records.value = res.data.records
      total.value = res.data.total
    } catch (e: unknown) {
      error.value = getApiErrorMessage(e, 'Failed to fetch records')
    } finally {
      loading.value = false
    }
  }

  async function refetchWithEmptyPageFix() {
    await fetchRecords(query.value)

    // If we deleted the last row on a non-first page, automatically step back.
    if (records.value.length === 0 && total.value > 0 && query.value.skip > 0) {
      const newSkip = Math.max(0, query.value.skip - query.value.limit)
      if (newSkip !== query.value.skip) {
        await fetchRecords({ ...query.value, skip: newSkip })
      }
    }
  }

  async function createRecord(data: HealthRecordCreate): Promise<HealthRecord | null> {
    error.value = null
    try {
      const res = await healthRecordsApi.create(data)
      await refetchWithEmptyPageFix()
      return res.data
    } catch (e: unknown) {
      error.value = getApiErrorMessage(e, 'Failed to create record')
      return null
    }
  }

  async function updateRecord(id: number, data: HealthRecordUpdate): Promise<HealthRecord | null> {
    error.value = null
    try {
      const res = await healthRecordsApi.update(id, data)
      await refetchWithEmptyPageFix()
      return res.data
    } catch (e: unknown) {
      error.value = getApiErrorMessage(e, 'Failed to update record')
      return null
    }
  }

  async function deleteRecord(id: number): Promise<boolean> {
    error.value = null
    try {
      await healthRecordsApi.delete(id)
      await refetchWithEmptyPageFix()
      return true
    } catch (e: unknown) {
      error.value = getApiErrorMessage(e, 'Failed to delete record')
      return false
    }
  }

  return {
    records,
    total,
    loading,
    error,
    query,
    setQuery,
    fetchRecords,
    createRecord,
    updateRecord,
    deleteRecord,
  }
})
