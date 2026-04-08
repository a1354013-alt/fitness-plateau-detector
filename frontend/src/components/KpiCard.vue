<template>
  <div class="kpi-card">
    <div class="kpi-header">
      <span class="kpi-icon" :style="{ background: iconBg }">
        <i :class="icon" :style="{ color: iconColor }" />
      </span>
      <span class="kpi-label">{{ label }}</span>
    </div>
    <div class="kpi-value">
      <span v-if="value !== null && value !== undefined">{{ formattedValue }}</span>
      <span v-else class="kpi-empty">—</span>
    </div>
    <div v-if="sub" class="kpi-sub" :class="subClass">{{ sub }}</div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{
  label: string
  value: number | string | null | undefined
  unit?: string
  icon?: string
  iconColor?: string
  iconBg?: string
  decimals?: number
  sub?: string
  subClass?: string
}>()

const formattedValue = computed(() => {
  if (props.value === null || props.value === undefined) return '—'
  if (typeof props.value === 'string') return props.value
  const dec = props.decimals ?? 1
  return `${props.value.toFixed(dec)}${props.unit ? ' ' + props.unit : ''}`
})
</script>

<style scoped>
.kpi-card {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  padding: 1.25rem 1.5rem;
  box-shadow: var(--shadow-sm);
  transition: box-shadow 0.2s;
}
.kpi-card:hover { box-shadow: var(--shadow-md); }
.kpi-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 0.75rem;
}
.kpi-icon {
  width: 36px;
  height: 36px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}
.kpi-icon i { font-size: 1rem; }
.kpi-label {
  font-size: 0.8rem;
  font-weight: 600;
  color: var(--color-text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}
.kpi-value {
  font-size: 1.9rem;
  font-weight: 700;
  color: var(--color-text-primary);
  line-height: 1.1;
  margin-bottom: 0.3rem;
}
.kpi-empty { color: #cbd5e1; }
.kpi-sub {
  font-size: 0.8rem;
  color: var(--color-text-secondary);
}
.kpi-sub.positive { color: #16a34a; }
.kpi-sub.negative { color: #dc2626; }
.kpi-sub.neutral  { color: var(--color-text-secondary); }
</style>
