// JSDOM doesn't implement canvas; Chart.js may touch it during module init.
// We stub it globally so view tests don't emit noisy "Not implemented" warnings.
Object.defineProperty(HTMLCanvasElement.prototype, 'getContext', {
  value: () => null,
})

// Prevent Chart.js from trying to create real charts in unit tests.
// Tests should verify state/UI logic, not Chart.js rendering internals.
import { vi } from 'vitest'
import { defineComponent, h } from 'vue'

vi.mock('vue-chartjs', () => ({
  Line: defineComponent({ name: 'Line', render: () => h('div', { 'data-test': 'chart-line' }) }),
  Bar: defineComponent({ name: 'Bar', render: () => h('div', { 'data-test': 'chart-bar' }) }),
}))

vi.mock('chart.js', () => ({
  Chart: { register: () => undefined },
  CategoryScale: {},
  LinearScale: {},
  PointElement: {},
  LineElement: {},
  BarElement: {},
  Title: {},
  Tooltip: {},
  Legend: {},
  Filler: {},
}))
