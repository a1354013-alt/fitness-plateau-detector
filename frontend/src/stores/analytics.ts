import { ref, computed } from 'vue'
import { defineStore } from 'pinia'
import { analyticsApi, type SummaryData, type DashboardData, type TrendsData } from '@/services/api'
import { getApiErrorMessage } from '@/services/errors'

export const useAnalyticsStore = defineStore('analytics', () => {
  const summary = ref<SummaryData | null>(null)
  const dashboard = ref<DashboardData | null>(null)
  const trends = ref<TrendsData | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)
  const calorieTarget = ref(2000)

  async function fetchTrends(days: number = 30) {
    loading.value = true
    try {
      const res = await analyticsApi.trends(days)
      trends.value = res.data
    } catch (e: unknown) {
      error.value = getApiErrorMessage(e, 'Failed to fetch trends')
    } finally {
      loading.value = false
    }
  }

  async function fetchAll(days: number = 30, target: number = 2000) {
    loading.value = true
    error.value = null
    calorieTarget.value = target
    try {
      const [summaryRes, dashboardRes, trendsRes] = await Promise.all([
        analyticsApi.summary(target),
        analyticsApi.dashboard(),
        analyticsApi.trends(days),
      ])
      summary.value = summaryRes.data
      dashboard.value = dashboardRes.data
      trends.value = trendsRes.data
    } catch (e: unknown) {
      error.value = getApiErrorMessage(e, 'Failed to fetch analytics data')
    } finally {
      loading.value = false
    }
  }

  // Flattened Analysis Fields for simplified UI consumption
  const summaryText = computed(() => summary.value?.summary?.text || '')
  const summaryStatus = computed(() => summary.value?.summary?.status || 'insufficient_data')
  const summaryInsight = computed(() => summary.value?.summary?.insight || '')
  const topReasons = computed(() => summary.value?.summary?.top_reasons || [])
  const plateauStatus = computed(() => summary.value?.plateau?.status || 'insufficient_data')

  // Data Domains
  const plateauData = computed(() => summary.value?.plateau)
  const reasonsData = computed(() => summary.value?.reasons)
  const dashboardData = computed(() => dashboard.value)
  const trendsData = computed(() => trends.value)

  return {
    // UI State
    loading,
    error,
    calorieTarget,
    // Raw domains (for views that need full objects)
    summary,
    dashboard,
    trends,
    // Analysis Domain (Flattened)
    summaryText,
    summaryStatus,
    summaryInsight,
    topReasons,
    plateauStatus,
    // Data Domains
    plateauData,
    reasonsData,
    dashboardData,
    trendsData,
    // Actions
    fetchAll,
    fetchTrends,
  }
})
