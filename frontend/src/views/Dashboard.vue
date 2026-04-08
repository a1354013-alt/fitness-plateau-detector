<template>
  <div class="page-container">
    <div class="page-header">
      <h1 class="page-title">Dashboard</h1>
      <p class="page-subtitle">Your health overview and recent trends</p>
    </div>

    <StatePanel
      v-if="initialLoading"
      variant="loading"
      title="Loading dashboard..."
      message="Fetching your latest records and analytics."
    />

    <StatePanel
      v-else-if="pageError"
      variant="error"
      title="Couldn't load dashboard"
      :message="pageError"
    >
      <template #action>
        <Button label="Retry" icon="pi pi-refresh" severity="secondary" outlined @click="refreshAll" />
      </template>
    </StatePanel>

    <StatePanel
      v-else-if="isEmpty"
      variant="empty"
      title="No records yet"
      message="Add records to see KPIs and trends. Analysis unlocks after 5 recorded days within the last 7 days."
    >
      <template #action>
        <router-link to="/records">
          <Button label="Add Records" icon="pi pi-plus" />
        </router-link>
      </template>
    </StatePanel>

    <template v-else>
      <!-- KPI Cards -->
      <div class="grid-4" style="margin-bottom: 1.5rem;">
      <KpiCard
        label="Latest Weight"
        :value="dashboard?.current_weight"
        unit="kg"
        :decimals="1"
        icon="pi pi-user"
        icon-color="#6366f1"
        icon-bg="#eef2ff"
        :sub="weightChangeSub"
        :sub-class="weightChangeClass"
      />
      <KpiCard
        label="7-Day Avg Weight"
        :value="dashboard?.avg_weight_7d"
        unit="kg"
        :decimals="1"
        icon="pi pi-chart-line"
        icon-color="#8b5cf6"
        icon-bg="#f5f3ff"
      />
      <KpiCard
        label="7-Day Avg Sleep"
        :value="dashboard?.avg_sleep_7d"
        unit="h"
        :decimals="1"
        icon="pi pi-moon"
        icon-color="#0ea5e9"
        icon-bg="#e0f2fe"
        :sub="sleepSub"
        :sub-class="sleepSubClass"
      />
      <KpiCard
        label="7-Day Avg Calories"
        :value="dashboard?.avg_calories_7d"
        unit="kcal"
        :decimals="0"
        icon="pi pi-bolt"
        icon-color="#f59e0b"
        icon-bg="#fef3c7"
        :sub="caloriesSub"
        :sub-class="caloriesSubClass"
      />
      </div>

    <!-- Plateau Status Banner -->
    <div v-if="summary" class="plateau-banner" :class="`banner-${plateauStatus}`">
      <div class="banner-left">
        <span class="banner-status-icon">{{ statusIcon }}</span>
        <div>
          <div class="banner-title">{{ statusTitle }}</div>
          <div class="banner-desc">{{ summaryText }} <span class="text-muted">(based on last 7 calendar days, ending today)</span></div>
        </div>
      </div>
      <router-link to="/analysis" class="banner-cta">
        View Analysis <i class="pi pi-arrow-right" />
      </router-link>
    </div>

    <!-- Charts Row -->
    <div class="charts-grid">
      <!-- Weight Trend -->
      <div class="card chart-card">
        <div class="chart-header">
          <div>
            <div class="chart-title">Weight Trend</div>
            <div class="chart-sub text-muted text-sm">Charts: last {{ selectedDays }} days</div>
          </div>
          <div class="days-selector">
            <button
              v-for="d in [7, 14, 30]"
              :key="d"
              class="day-btn"
              :class="{ active: selectedDays === d }"
              @click="changeDays(d)"
            >{{ d }}d</button>
          </div>
        </div>
        <div class="chart-wrap">
          <Line v-if="weightChartData.labels.length" :data="weightChartData" :options="lineOptions" />
          <div v-else class="chart-empty">
            <span v-if="analyticsStore.trendsStatus.error">Failed to load charts.</span>
            <span v-else>No data available</span>
            <Button
              v-if="analyticsStore.trendsStatus.error"
              label="Retry"
              icon="pi pi-refresh"
              severity="secondary"
              text
              size="small"
              @click="analyticsStore.fetchTrendsOnly(selectedDays)"
              style="margin-left: 8px;"
            />
          </div>
        </div>
      </div>

      <!-- Sleep Trend -->
      <div class="card chart-card">
        <div class="chart-header">
          <div>
            <div class="chart-title">Sleep Hours</div>
            <div class="chart-sub text-muted text-sm">Charts: last {{ selectedDays }} days</div>
          </div>
        </div>
        <div class="chart-wrap">
          <Line v-if="sleepChartData.labels.length" :data="sleepChartData" :options="sleepOptions" />
          <div v-else class="chart-empty">
            <span v-if="analyticsStore.trendsStatus.error">Failed to load charts.</span>
            <span v-else>No data available</span>
          </div>
        </div>
      </div>

      <!-- Calories Trend -->
      <div class="card chart-card">
        <div class="chart-header">
          <div>
            <div class="chart-title">Calorie Intake</div>
            <div class="chart-sub text-muted text-sm">Charts: last {{ selectedDays }} days</div>
          </div>
        </div>
        <div class="chart-wrap">
          <Bar v-if="caloriesChartData.labels.length" :data="caloriesChartData" :options="barOptions" />
          <div v-else class="chart-empty">
            <span v-if="analyticsStore.trendsStatus.error">Failed to load charts.</span>
            <span v-else>No data available</span>
          </div>
        </div>
      </div>
    </div>

    <StatePanel
      v-if="dashboard?.total_records === 0"
      variant="empty"
      title="No data yet"
      message="Start by adding your first health record to see trends and insights."
    >
      <template #action>
        <router-link to="/records">
          <Button label="Add First Record" icon="pi pi-plus" />
        </router-link>
      </template>
    </StatePanel>
    </template>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { Line, Bar } from 'vue-chartjs'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
  Filler,
} from 'chart.js'

import Button from 'primevue/button'

import KpiCard from '@/components/KpiCard.vue'
import StatePanel from '@/components/StatePanel.vue'
import { useAnalyticsStore } from '@/stores/analytics'

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
  Filler,
)

const analyticsStore = useAnalyticsStore()
const selectedDays = ref(7)
const calorieTarget = computed(() => analyticsStore.calorieTarget)

const dashboard = computed(() => analyticsStore.dashboard)
const trendsData = computed(() => analyticsStore.trends?.trends || [])
const summary = computed(() => analyticsStore.summary)
const summaryText = computed(() => analyticsStore.summaryText)
const plateauStatus = computed(() => analyticsStore.plateauStatus)
const initialLoading = computed(() => {
  const needsData = analyticsStore.dashboard == null || analyticsStore.summary == null
  const loading = analyticsStore.dashboardStatus.loading || analyticsStore.summaryStatus.loading
  return needsData && loading
})
const pageError = computed(() => analyticsStore.dashboardPageError)
const isEmpty = computed(() => dashboard.value != null && dashboard.value.total_records === 0)

const statusIcon = computed(() => {
  const map: Record<string, string> = {
    plateau: '⏸️',
    losing: '📉',
    gaining: '📈',
    insufficient_data: '📊',
  }
  return map[plateauStatus.value] || '📊'
})

const statusTitle = computed(() => {
  const map: Record<string, string> = {
    plateau: 'Weight Plateau Detected',
    losing: 'Active Weight Loss',
    gaining: 'Weight Gaining Trend',
    insufficient_data: 'Collecting Data...',
  }
  return map[plateauStatus.value] || 'Status Unknown'
})

const weightChangeSub = computed(() => {
  const asOf = dashboard.value?.last_record_date ? `As of ${dashboard.value.last_record_date}` : undefined
  const c = dashboard.value?.weight_change_7d
  if (c === null || c === undefined) {
    const hint = '7-day change unavailable (needs records for today and exactly 7 days ago)'
    return asOf ? `${asOf} · ${hint}` : hint
  }
  const sign = c > 0 ? '+' : ''
  return asOf ? `${asOf} · ${sign}${c.toFixed(1)} kg vs 7 days ago` : `${sign}${c.toFixed(1)} kg vs 7 days ago`
})

const weightChangeClass = computed(() => {
  const c = dashboard.value?.weight_change_7d
  if (c === null || c === undefined) return 'neutral'
  return c < 0 ? 'positive' : c > 0 ? 'negative' : 'neutral'
})

const sleepSub = computed(() => {
  const s = dashboard.value?.avg_sleep_7d
  if (s === null || s === undefined) return undefined
  return s < 6 ? 'Below recommended 6h' : 'Good sleep quality'
})
const sleepSubClass = computed(() => {
  const s = dashboard.value?.avg_sleep_7d
  if (!s) return 'neutral'
  return s < 6 ? 'negative' : 'positive'
})

const caloriesSub = computed(() => {
  const c = dashboard.value?.avg_calories_7d
  if (c === null || c === undefined) return undefined
  return c > analyticsStore.calorieTarget
    ? `Above ${analyticsStore.calorieTarget} kcal target`
    : 'Within target range'
})
const caloriesSubClass = computed(() => {
  const c = dashboard.value?.avg_calories_7d
  if (!c) return 'neutral'
  return c > analyticsStore.calorieTarget ? 'negative' : 'positive'
})

// Chart data
const weightChartData = computed(() => ({
  labels: trendsData.value.map((d) => d.date.slice(5)),
  datasets: [
    {
      label: 'Weight (kg)',
      data: trendsData.value.map((d) => d.weight),
      borderColor: '#6366f1',
      backgroundColor: 'rgba(99,102,241,0.08)',
      fill: true,
      tension: 0.4,
      pointRadius: 4,
      pointHoverRadius: 6,
    },
  ],
}))

const sleepChartData = computed(() => ({
  labels: trendsData.value.map((d) => d.date.slice(5)),
  datasets: [
    {
      label: 'Sleep (h)',
      data: trendsData.value.map((d) => d.sleep_hours),
      borderColor: '#0ea5e9',
      backgroundColor: 'rgba(14,165,233,0.08)',
      fill: true,
      tension: 0.4,
      pointRadius: 4,
      pointHoverRadius: 6,
    },
  ],
}))

const caloriesChartData = computed(() => ({
  labels: trendsData.value.map((d) => d.date.slice(5)),
  datasets: [
    {
      label: 'Calories (kcal)',
      data: trendsData.value.map((d) => d.calories),
      backgroundColor: trendsData.value.map((d) =>
        d.calories > analyticsStore.calorieTarget
          ? 'rgba(239,68,68,0.7)'
          : 'rgba(34,197,94,0.7)',
      ),
      borderRadius: 4,
    },
  ],
}))

const baseOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: { display: false },
    tooltip: { mode: 'index' as const, intersect: false },
  },
  scales: {
    x: { grid: { display: false }, ticks: { maxRotation: 0, font: { size: 11 } } },
    y: { grid: { color: '#f1f5f9' }, ticks: { font: { size: 11 } } },
  },
}

const lineOptions = { ...baseOptions }
const sleepOptions = {
  ...baseOptions,
  scales: {
    ...baseOptions.scales,
    y: { ...baseOptions.scales.y, min: 0, max: 12 },
  },
}
const barOptions = { ...baseOptions }

async function changeDays(days: number) {
  selectedDays.value = days
  await analyticsStore.fetchTrendsOnly(days)
}

async function refreshAll() {
  await analyticsStore.fetchDashboardBundle(selectedDays.value, calorieTarget.value)
}

onMounted(async () => {
  await refreshAll()
})
</script>

<style scoped>
.page-header { margin-bottom: 1.5rem; }

.plateau-banner {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  padding: 1rem 1.5rem;
  border-radius: var(--radius-lg);
  margin-bottom: 1.5rem;
  border: 1px solid transparent;
  flex-wrap: wrap;
}
.banner-plateau { background: #fef3c7; border-color: #fde68a; }
.banner-losing  { background: #dcfce7; border-color: #bbf7d0; }
.banner-gaining { background: #fee2e2; border-color: #fecaca; }
.banner-insufficient_data { background: #f1f5f9; border-color: #e2e8f0; }

.banner-left {
  display: flex;
  align-items: flex-start;
  gap: 12px;
}
.banner-status-icon { font-size: 1.5rem; line-height: 1; margin-top: 2px; }
.banner-title { font-weight: 700; font-size: 1rem; margin-bottom: 2px; }
.banner-desc { font-size: 0.85rem; color: var(--color-text-secondary); }

.banner-cta {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 0.85rem;
  font-weight: 600;
  color: var(--color-accent);
  text-decoration: none;
  white-space: nowrap;
  padding: 6px 14px;
  border-radius: var(--radius-md);
  background: white;
  border: 1px solid #c7d2fe;
  transition: all 0.15s;
}
.banner-cta:hover { background: #eef2ff; }

.charts-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
}
.charts-grid .chart-card:first-child {
  grid-column: 1 / -1;
}

.chart-card { padding: 1.25rem; }
.chart-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  margin-bottom: 1rem;
}
.chart-title { font-weight: 600; font-size: 0.95rem; }
.chart-sub { margin-top: 2px; }
.chart-wrap { height: 200px; position: relative; }
.chart-empty {
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--color-text-secondary);
  font-size: 0.875rem;
}

.days-selector { display: flex; gap: 4px; }
.day-btn {
  padding: 4px 10px;
  border: 1px solid var(--color-border);
  border-radius: 6px;
  background: white;
  font-size: 0.8rem;
  font-weight: 500;
  cursor: pointer;
  color: var(--color-text-secondary);
  transition: all 0.15s;
}
.day-btn:hover { border-color: var(--color-accent); color: var(--color-accent); }
.day-btn.active { background: var(--color-accent); color: white; border-color: var(--color-accent); }

@media (max-width: 768px) {
  .charts-grid { grid-template-columns: 1fr; }
  .charts-grid .chart-card:first-child { grid-column: auto; }
}
</style>
