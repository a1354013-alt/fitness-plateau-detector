<template>
  <div class="state-panel" :class="`state-${variant}`">
    <div class="state-icon">
      <ProgressSpinner v-if="variant === 'loading'" style="width:48px;height:48px" />
      <i v-else :class="iconClass" />
    </div>
    <div class="state-body">
      <div class="state-title">{{ title }}</div>
      <div v-if="message" class="state-message">{{ message }}</div>
      <div class="state-action">
        <slot name="action" />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import ProgressSpinner from 'primevue/progressspinner'

const props = defineProps<{
  variant: 'loading' | 'error' | 'empty'
  title: string
  message?: string
}>()

const iconClass = computed(() => {
  if (props.variant === 'error') return 'pi pi-exclamation-triangle'
  return 'pi pi-inbox'
})
</script>

<style scoped>
.state-panel {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1.25rem 1.5rem;
  border-radius: var(--radius-lg);
  border: 1px solid var(--color-border);
  background: white;
  margin-bottom: 1.5rem;
}
.state-icon {
  width: 52px;
  height: 52px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}
.state-icon i {
  font-size: 1.6rem;
}
.state-body { flex: 1; min-width: 0; }
.state-title { font-weight: 700; font-size: 1rem; margin-bottom: 2px; }
.state-message { color: var(--color-text-secondary); font-size: 0.9rem; line-height: 1.5; }
.state-action { margin-top: 0.75rem; }

.state-loading { background: #f8fafc; }
.state-empty { background: #f8fafc; }
.state-error { background: #fff7ed; border-color: #fed7aa; }
.state-error .state-icon i { color: #c2410c; }
</style>
