import { ref, computed, reactive } from 'vue'
import { defineStore } from 'pinia'
import { analyticsApi, type SummaryData, type DashboardData, type TrendsData } from '@/services/api'
import { getApiErrorMessage } from '@/services/errors'

type DomainStatus = {
  loading: boolean
  error: string | null
}

export const useAnalyticsStore = defineStore('analytics', () => {
  const summary = ref<SummaryData | null>(null)
  const dashboard = ref<DashboardData | null>(null)
  const trends = ref<TrendsData | null>(null)

  const calorieTarget = ref(2000)

  const dashboardStatus = reactive<DomainStatus>({ loading: false, error: null })
  const summaryStatus = reactive<DomainStatus>({ loading: false, error: null })
  const trendsStatus = reactive<DomainStatus>({ loading: false, error: null })

  const dashboardPageError = computed(() => {
    if (!dashboard.value && dashboardStatus.error) return dashboardStatus.error
    if (!summary.value && summaryStatus.error) return summaryStatus.error
    return null
  })

  const analysisPageError = computed(() => {
    if (!summary.value && summaryStatus.error) return summaryStatus.error
    return null
  })

  async function fetchDashboard() {
    dashboardStatus.loading = true
    dashboardStatus.error = null
    try {
      const res = await analyticsApi.dashboard()
      dashboard.value = res.data
    } catch (e: unknown) {
      dashboardStatus.error = getApiErrorMessage(e, 'Failed to fetch dashboard')
    } finally {
      dashboardStatus.loading = false
    }
  }

  async function fetchTrends(days: number = 30) {
    trendsStatus.loading = true
    trendsStatus.error = null
    try {
      const res = await analyticsApi.trends(days)
      trends.value = res.data
    } catch (e: unknown) {
      trendsStatus.error = getApiErrorMessage(e, 'Failed to fetch trends')
    } finally {
      trendsStatus.loading = false
    }
  }

  // Explicit domain-boundary aliases (preferred API)
  async function fetchTrendsOnly(days: number = 30) {
    await fetchTrends(days)
  }

  async function fetchDashboardBundle(days: number = 30, target: number = 2000) {
    calorieTarget.value = target

    dashboardStatus.loading = true
    summaryStatus.loading = true
    trendsStatus.loading = true

    dashboardStatus.error = null
    summaryStatus.error = null
    trendsStatus.error = null

    const [summaryRes, dashboardRes, trendsRes] = await Promise.allSettled([
      analyticsApi.summary(target),
      analyticsApi.dashboard(),
      analyticsApi.trends(days),
    ])

    if (summaryRes.status === 'fulfilled') {
      summary.value = summaryRes.value.data
    } else {
      summaryStatus.error = getApiErrorMessage(summaryRes.reason, 'Failed to fetch analysis summary')
    }

    if (dashboardRes.status === 'fulfilled') {
      dashboard.value = dashboardRes.value.data
    } else {
      dashboardStatus.error = getApiErrorMessage(dashboardRes.reason, 'Failed to fetch dashboard')
    }

    if (trendsRes.status === 'fulfilled') {
      trends.value = trendsRes.value.data
    } else {
      trendsStatus.error = getApiErrorMessage(trendsRes.reason, 'Failed to fetch trends')
    }

    dashboardStatus.loading = false
    summaryStatus.loading = false
    trendsStatus.loading = false
  }

  async function fetchAnalysisBundle(target: number = 2000) {
    // Analysis bundle = summary endpoint (includes plateau + reasons + summary payload).
    summaryStatus.loading = true
    summaryStatus.error = null
    calorieTarget.value = target
    try {
      const res = await analyticsApi.summary(target)
      summary.value = res.data
    } catch (e: unknown) {
      summaryStatus.error = getApiErrorMessage(e, 'Failed to fetch analysis summary')
    } finally {
      summaryStatus.loading = false
    }
  }

  const summaryText = computed(() => summary.value?.summary?.text || '')
  const analysisResultStatus = computed(() => summary.value?.summary?.status || 'insufficient_data')
  const summaryInsight = computed(() => summary.value?.summary?.insight || '')
  const topReasons = computed(() => summary.value?.summary?.top_reasons || [])
  const plateauStatus = computed(() => summary.value?.plateau?.status || 'insufficient_data')

  const plateauData = computed(() => summary.value?.plateau)
  const reasonsData = computed(() => summary.value?.reasons)
  const dashboardData = computed(() => dashboard.value)
  const trendsData = computed(() => trends.value)

  return {
    calorieTarget,
    summary,
    dashboard,
    trends,

    dashboardStatus,
    summaryStatus,
    trendsStatus,
    dashboardPageError,
    analysisPageError,

    summaryText,
    analysisResultStatus,
    summaryInsight,
    topReasons,
    plateauStatus,

    plateauData,
    reasonsData,
    dashboardData,
    trendsData,

    fetchDashboard,
    fetchTrendsOnly,
    fetchDashboardBundle,
    fetchAnalysisBundle,

    fetchAll: fetchDashboardBundle,
  }
})
