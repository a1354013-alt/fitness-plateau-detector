<template>
  <div class="page-container">
    <div class="page-header-row">
      <div class="page-header">
        <h1 class="page-title">Analysis</h1>
        <p class="page-subtitle">Deep dive into your weight plateau causes</p>
      </div>
      <div class="header-controls">
        <span class="target-label">Calorie Target:</span>
        <InputNumber
          v-model="calorieTarget"
          suffix=" kcal"
          :min="1000"
          :max="5000"
          :useGrouping="false"
          :inputStyle="{ width: '100px', textAlign: 'center' }"
          @blur="refresh"
        />
        <Button
          icon="pi pi-refresh"
          @click="refresh"
          :loading="analyticsStore.summaryStatus.loading"
          severity="secondary"
          text
          rounded
        />
      </div>
    </div>

    <Message
      v-if="analyticsStore.staleDataWarning"
      severity="warn"
      :closable="true"
      @close="analyticsStore.dismissStaleDataWarning()"
      style="margin-bottom: 1rem;"
    >
      {{ analyticsStore.staleDataWarning }}
    </Message>

    <StatePanel
      v-if="analyticsStore.summaryStatus.loading && analyticsStore.summary == null"
      variant="loading"
      title="Analyzing..."
      message="Running plateau detection and reason analysis (last 7 calendar days, ending today)."
    />

    <StatePanel
      v-else-if="pageError"
      variant="error"
      title="Couldn't load analysis"
      :message="pageError"
    >
      <template #action>
        <Button label="Retry" icon="pi pi-refresh" severity="secondary" outlined @click="refresh" />
      </template>
    </StatePanel>

    <template v-else-if="plateauStatus !== 'insufficient_data'">
      <!-- Plateau Status Card -->
      <div class="status-section">
        <div class="status-card" :class="`status-${plateauStatus}`">
          <div class="status-main">
            <div class="status-emoji">{{ statusEmoji }}</div>
            <div class="status-info">
              <div class="status-title">{{ statusTitle }}</div>
              <div class="status-summary">{{ analyticsStore.summaryText || '—' }}</div>
            </div>
          </div>
          <div class="status-badges">
            <span class="badge" :class="`badge-${plateauStatus}`">{{ plateauStatus.toUpperCase() }}</span>
          </div>
        </div>
      </div>

      <!-- Metrics Grid -->
      <div class="grid-3" style="margin-bottom: 1.5rem;">
        <div class="card metric-card">
          <div class="metric-label">Last 7-Day Avg</div>
          <div class="metric-value">
            {{ analyticsStore.plateauData?.last7_avg != null ? analyticsStore.plateauData.last7_avg.toFixed(1) + ' kg' : '—' }}
          </div>
          <div class="metric-sub">
            Range: {{ analyticsStore.plateauData?.last7_min?.toFixed(1) ?? '—' }} – {{ analyticsStore.plateauData?.last7_max?.toFixed(1) ?? '—' }} kg
          </div>
        </div>
        <div class="card metric-card">
          <div class="metric-label">Prev 7-Day Avg</div>
          <div class="metric-value">
            {{ analyticsStore.plateauData?.prev7_avg != null ? analyticsStore.plateauData.prev7_avg.toFixed(1) + ' kg' : '—' }}
          </div>
          <div class="metric-sub" v-if="analyticsStore.plateauData?.avg_change != null">
            Change:
            <span
              :class="analyticsStore.plateauData.avg_change < 0 ? 'text-success' : analyticsStore.plateauData.avg_change > 0 ? 'text-danger' : ''"
            >
              {{ analyticsStore.plateauData.avg_change > 0 ? '+' : '' }}{{ analyticsStore.plateauData.avg_change.toFixed(2) }} kg
            </span>
          </div>
          <div class="metric-sub" v-else>Not enough data</div>
        </div>
        <div class="card metric-card">
          <div class="metric-label">7-Day Fluctuation</div>
          <div class="metric-value">
            {{ analyticsStore.plateauData?.last7_fluctuation != null ? '±' + (analyticsStore.plateauData.last7_fluctuation / 2).toFixed(2) + ' kg' : '—' }}
          </div>
          <div class="metric-sub">
            <span :class="(analyticsStore.plateauData?.last7_fluctuation ?? 1) <= 0.6 ? 'text-warning' : 'text-success'">
              {{ (analyticsStore.plateauData?.last7_fluctuation ?? 1) <= 0.6 ? 'Plateau range (±0.3 kg)' : 'Active fluctuation' }}
            </span>
          </div>
        </div>
      </div>

      <!-- Detection Rules -->
      <div class="card rules-card" style="margin-bottom: 1.5rem;">
        <h3 class="section-title">Detection Rules</h3>
        <div class="rules-grid">
          <div
            class="rule-item"
            :class="analyticsStore.plateauData?.rule_a === true ? 'rule-triggered' : analyticsStore.plateauData?.rule_a === false ? 'rule-clear' : 'rule-na'"
          >
            <div class="rule-icon">
              <i
                :class="analyticsStore.plateauData?.rule_a === true ? 'pi pi-exclamation-circle' : analyticsStore.plateauData?.rule_a === false ? 'pi pi-check-circle' : 'pi pi-minus-circle'"
              />
            </div>
            <div class="rule-content">
              <div class="rule-name">Rule A — Average Weight Change</div>
              <div class="rule-desc">Last 7-day avg vs previous 7-day avg change &lt; 0.2 kg</div>
              <div class="rule-result">
                <span v-if="analyticsStore.plateauData?.rule_a === true" class="result-plateau">Plateau Detected</span>
                <span v-else-if="analyticsStore.plateauData?.rule_a === false" class="result-clear">No Plateau</span>
                <span v-else class="result-na">Insufficient data (need 5+ days in the previous window)</span>
              </div>
            </div>
          </div>

          <div
            class="rule-item"
            :class="analyticsStore.plateauData?.rule_b === true ? 'rule-triggered' : analyticsStore.plateauData?.rule_b === false ? 'rule-clear' : 'rule-na'"
          >
            <div class="rule-icon">
              <i
                :class="analyticsStore.plateauData?.rule_b === true ? 'pi pi-exclamation-circle' : analyticsStore.plateauData?.rule_b === false ? 'pi pi-check-circle' : 'pi pi-minus-circle'"
              />
            </div>
            <div class="rule-content">
              <div class="rule-name">Rule B — Weight Fluctuation</div>
              <div class="rule-desc">7-day weight fluctuation within ±0.3 kg range</div>
              <div class="rule-result">
                <span v-if="analyticsStore.plateauData?.rule_b === true" class="result-plateau">Plateau Detected</span>
                <span v-else-if="analyticsStore.plateauData?.rule_b === false" class="result-clear">No Plateau</span>
                <span v-else class="result-na">Insufficient data (need 5+ recent days)</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Reasons Analysis -->
      <div class="card reasons-card" style="margin-bottom: 1.5rem;">
        <h3 class="section-title">Cause Analysis</h3>
        <p class="section-sub">Top factors contributing to your current weight trend (last 7 days)</p>

        <div v-if="analyticsStore.reasonsData && analyticsStore.reasonsData.reasons.length > 0" class="reasons-list">
          <div
            v-for="(reason, idx) in analyticsStore.reasonsData.reasons"
            :key="reason.code"
            class="reason-item"
          >
            <div class="reason-rank">
              <span class="rank-badge" :class="idx === 0 ? 'rank-1' : 'rank-2'">
                {{ idx === 0 ? '1st' : '2nd' }}
              </span>
            </div>
            <div class="reason-body">
              <div class="reason-header-row">
                <span class="reason-label">{{ reason.label }}</span>
                <span class="reason-code badge badge-gray">{{ reason.code }}</span>
              </div>
              <div class="reason-desc">{{ reason.description }}</div>
              <div class="reason-bar-wrap">
                <div class="reason-bar" :style="{ width: Math.min(reason.severity * 100, 100) + '%' }" />
              </div>
            </div>
          </div>
        </div>

        <div v-else class="no-reasons">
          <i class="pi pi-check-circle" style="font-size: 2rem; color: #22c55e;" />
          <p>No significant issues detected in the last 7 days.</p>
        </div>

        <div v-if="analyticsStore.reasonsData && analyticsStore.reasonsData.missing_days > 0" class="missing-warn">
          <i class="pi pi-info-circle" />
          {{ analyticsStore.reasonsData.missing_days }} day(s) of data missing in the last 7 days — analysis may be incomplete.
        </div>
      </div>

      <!-- Insight Summary -->
      <div class="card insight-card">
        <h3 class="section-title">Actionable Insights</h3>
        <div class="insight-summary">{{ analyticsStore.summaryText || '—' }}</div>
        <div class="insight-detail" v-if="analyticsStore.summaryInsight">
          <pre class="insight-pre">{{ analyticsStore.summaryInsight }}</pre>
        </div>
      </div>
    </template>

    <!-- Insufficient data state -->
    <StatePanel
      v-else
      variant="empty"
      title="Not enough data for analysis"
      message="Log at least 5 recent days of health records to unlock analysis."
    >
      <template #action>
        <router-link to="/records">
          <Button label="Add Records" icon="pi pi-plus" />
        </router-link>
      </template>
    </StatePanel>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted } from 'vue'

import Button from 'primevue/button'
import InputNumber from 'primevue/inputnumber'
import Message from 'primevue/message'
import StatePanel from '@/components/StatePanel.vue'

import { useAnalyticsStore } from '@/stores/analytics'

const analyticsStore = useAnalyticsStore()

const calorieTarget = computed<number | null>({
  get: () => analyticsStore.calorieTarget,
  set: (val) => {
    analyticsStore.calorieTarget = val ?? 2000
  },
})

const plateauStatus = computed(() => analyticsStore.plateauStatus)
const pageError = computed(() => analyticsStore.analysisPageError)

const statusEmoji = computed(() => {
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
    losing: 'You Are Losing Weight!',
    gaining: 'Weight is Increasing',
    insufficient_data: 'Insufficient Data',
  }
  return map[plateauStatus.value] || 'Unknown Status'
})

async function refresh() {
  await analyticsStore.fetchAnalysisBundle(calorieTarget.value ?? 2000)
}

onMounted(async () => {
  await refresh()
})
</script>

<style scoped>
.page-header-row {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 1rem;
  margin-bottom: 1.5rem;
  flex-wrap: wrap;
}
.header-controls {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  flex-wrap: wrap;
}
.target-label { font-size: 0.85rem; font-weight: 600; color: var(--color-text-secondary); white-space: nowrap; }

/* Status Card */
.status-card {
  padding: 1.5rem;
  border-radius: var(--radius-lg);
  border: 1px solid transparent;
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 1rem;
  margin-bottom: 1.5rem;
  flex-wrap: wrap;
}
.status-plateau { background: #fef3c7; border-color: #fde68a; }
.status-losing  { background: #dcfce7; border-color: #bbf7d0; }
.status-gaining { background: #fee2e2; border-color: #fecaca; }
.status-insufficient_data { background: #f1f5f9; border-color: #e2e8f0; }

.status-main { display: flex; align-items: flex-start; gap: 1rem; }
.status-emoji { font-size: 2.5rem; line-height: 1; }
.status-title { font-size: 1.2rem; font-weight: 700; margin-bottom: 6px; }
.status-summary { font-size: 0.9rem; color: var(--color-text-secondary); max-width: 600px; }

/* Metric Cards */
.metric-card { text-align: center; }
.metric-label { font-size: 0.78rem; font-weight: 600; color: var(--color-text-secondary); text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 0.5rem; }
.metric-value { font-size: 1.6rem; font-weight: 700; color: var(--color-text-primary); margin-bottom: 4px; }
.metric-sub { font-size: 0.8rem; color: var(--color-text-secondary); }
.text-success { color: #16a34a; font-weight: 600; }
.text-danger  { color: #dc2626; font-weight: 600; }
.text-warning { color: #d97706; font-weight: 600; }

/* Rules */
.section-title { font-size: 1rem; font-weight: 700; margin-bottom: 0.5rem; }
.section-sub { font-size: 0.85rem; color: var(--color-text-secondary); margin-bottom: 1rem; }

.rules-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; }
.rule-item {
  display: flex;
  gap: 12px;
  padding: 1rem;
  border-radius: var(--radius-md);
  border: 1px solid var(--color-border);
}
.rule-triggered { background: #fef3c7; border-color: #fde68a; }
.rule-clear     { background: #f0fdf4; border-color: #bbf7d0; }
.rule-na        { background: #f8fafc; }

.rule-icon { font-size: 1.25rem; flex-shrink: 0; margin-top: 2px; }
.rule-triggered .rule-icon { color: #d97706; }
.rule-clear .rule-icon     { color: #16a34a; }
.rule-na .rule-icon        { color: #94a3b8; }

.rule-name { font-weight: 600; font-size: 0.9rem; margin-bottom: 4px; }
.rule-desc { font-size: 0.8rem; color: var(--color-text-secondary); margin-bottom: 6px; }
.rule-result { font-size: 0.8rem; font-weight: 600; }
.result-plateau { color: #d97706; }
.result-clear   { color: #16a34a; }
.result-na      { color: #94a3b8; }

/* Reasons */
.reasons-list { display: flex; flex-direction: column; gap: 1rem; }
.reason-item {
  display: flex;
  gap: 1rem;
  padding: 1rem;
  background: #f8fafc;
  border-radius: var(--radius-md);
  border: 1px solid var(--color-border);
}
.rank-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  border-radius: 50%;
  font-size: 0.75rem;
  font-weight: 700;
  flex-shrink: 0;
}
.rank-1 { background: #fef3c7; color: #92400e; }
.rank-2 { background: #e0e7ff; color: #3730a3; }

.reason-body { flex: 1; }
.reason-header-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 4px;
  gap: 8px;
  flex-wrap: wrap;
}
.reason-label { font-weight: 600; font-size: 0.9rem; }
.reason-desc { font-size: 0.82rem; color: var(--color-text-secondary); margin-bottom: 8px; }
.reason-bar-wrap {
  height: 6px;
  background: #e2e8f0;
  border-radius: 3px;
  overflow: hidden;
}
.reason-bar {
  height: 100%;
  background: linear-gradient(90deg, #f59e0b, #ef4444);
  border-radius: 3px;
  transition: width 0.5s ease;
}

.no-reasons {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.75rem;
  padding: 2rem;
  color: var(--color-text-secondary);
}

.missing-warn {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 1rem;
  padding: 10px 14px;
  background: #fef3c7;
  border-radius: var(--radius-sm);
  font-size: 0.82rem;
  color: #92400e;
}

/* Insight */
.insight-summary {
  font-size: 1rem;
  font-weight: 600;
  color: var(--color-text-primary);
  margin-bottom: 1rem;
  padding: 1rem;
  background: #f8fafc;
  border-radius: var(--radius-md);
  border-left: 4px solid var(--color-accent);
}
.insight-detail { margin-top: 0.75rem; }
.insight-pre {
  font-family: inherit;
  font-size: 0.875rem;
  color: var(--color-text-secondary);
  white-space: pre-wrap;
  line-height: 1.7;
}

@media (max-width: 768px) {
  .rules-grid { grid-template-columns: 1fr; }
}
</style>
