<template>
  <div class="page-container">
    <div class="page-header-row">
      <div>
        <h1 class="page-title">Health Records</h1>
        <p class="page-subtitle">Log and manage your daily health data</p>
      </div>
      <Button
        label="Add Record"
        icon="pi pi-plus"
        @click="openForm(null)"
      />
    </div>

    <StatePanel
      v-if="store.error"
      variant="error"
      title="Couldn't load records"
      :message="store.error"
    >
      <template #action>
        <Button label="Retry" icon="pi pi-refresh" severity="secondary" outlined @click="loadRecords" />
      </template>
    </StatePanel>

    <StatePanel
      v-else-if="!store.loading && store.total === 0"
      variant="empty"
      title="No records yet"
      message="Add your first health record to start tracking trends and insights."
    >
      <template #action>
        <Button label="Add First Record" icon="pi pi-plus" @click="openForm(null)" />
      </template>
    </StatePanel>

    <!-- Record Form Dialog -->
    <Dialog
      v-model:visible="showForm"
      :header="editingRecord ? 'Edit Record' : 'Add Health Record'"
      :modal="true"
      :style="{ width: '520px', maxWidth: '95vw' }"
      :draggable="false"
    >
      <form @submit.prevent="submitForm" class="record-form">
        <div class="form-row">
          <div class="form-group">
            <label>Date *</label>
            <DatePicker v-model="form.record_date" dateFormat="yy-mm-dd" :maxDate="today" showIcon fluid />
          </div>
          <div class="form-group">
            <label>Weight (kg) *</label>
            <InputNumber v-model="form.weight" :min="20" :max="300" :minFractionDigits="1" :maxFractionDigits="1" fluid />
          </div>
        </div>

        <div class="form-row">
          <div class="form-group">
            <label>Sleep Hours *</label>
            <InputNumber v-model="form.sleep_hours" :min="0" :max="24" :minFractionDigits="1" :maxFractionDigits="1" fluid />
          </div>
          <div class="form-group">
            <label>Calories (kcal) *</label>
            <InputNumber v-model="form.calories" :min="0" :max="10000" fluid />
          </div>
        </div>

        <div class="form-row">
          <div class="form-group">
            <label>Protein (g)</label>
            <InputNumber v-model="form.protein" :min="0" :max="500" fluid placeholder="Optional" />
          </div>
          <div class="form-group">
            <label>Exercise (min)</label>
            <InputNumber v-model="form.exercise_minutes" :min="0" :max="600" fluid />
          </div>
        </div>

        <div class="form-row">
          <div class="form-group">
            <label>Exercise Type</label>
            <InputText v-model="form.exercise_type" placeholder="e.g. Running, Cycling" fluid />
          </div>
          <div class="form-group">
            <label>Steps</label>
            <InputNumber v-model="form.steps" :min="0" :max="100000" fluid placeholder="Optional" />
          </div>
        </div>

        <div class="form-group">
          <label>Note</label>
          <Textarea v-model="form.note" rows="2" placeholder="Any notes for today..." fluid />
        </div>

        <div v-if="formError" class="form-error">{{ formError }}</div>

        <div class="form-actions">
          <Button type="button" label="Cancel" severity="secondary" outlined @click="showForm = false" />
          <Button type="submit" :label="editingRecord ? 'Update' : 'Save Record'" :loading="store.loading" />
        </div>
      </form>
    </Dialog>

    <!-- Delete Confirm -->
    <ConfirmDialog />

    <!-- Records Table -->
    <div v-if="!(store.total === 0 && !store.loading && !store.error)" class="card table-card">
      <div class="table-toolbar">
        <span class="table-count">{{ pageRangeText }}</span>
        <div class="table-actions">
          <Button
            label="Refresh"
            icon="pi pi-refresh"
            severity="secondary"
            outlined
            size="small"
            @click="loadRecords"
            :loading="store.loading"
          />
        </div>
      </div>

      <DataTable
        :value="store.records"
        :loading="store.loading"
        stripedRows
        responsiveLayout="scroll"
        lazy
        :paginator="store.total > rows"
        :rows="rows"
        :first="first"
        :totalRecords="store.total"
        :rowsPerPageOptions="[20, 50, 100]"
        @page="onPage"
        class="records-table"
      >
        <template #empty>
          <div class="table-empty">
            <span>No records yet. Click "Add Record" to get started.</span>
          </div>
        </template>

        <Column field="record_date" header="Date" style="min-width: 110px">
          <template #body="{ data }">
            <span class="date-cell">{{ data.record_date }}</span>
          </template>
        </Column>

        <Column field="weight" header="Weight" style="min-width: 90px">
          <template #body="{ data }">
            <span class="weight-cell">{{ data.weight.toFixed(1) }} <small>kg</small></span>
          </template>
        </Column>

        <Column field="sleep_hours" header="Sleep" style="min-width: 80px">
          <template #body="{ data }">
            <span :class="data.sleep_hours < 6 ? 'val-warn' : 'val-ok'">
              {{ data.sleep_hours.toFixed(1) }}h
            </span>
          </template>
        </Column>

        <Column field="calories" header="Calories" style="min-width: 90px">
          <template #body="{ data }">
            <span :class="data.calories > analyticsStore.calorieTarget ? 'val-warn' : 'val-ok'">
              {{ data.calories.toLocaleString() }}
            </span>
          </template>
        </Column>

        <Column field="exercise_minutes" header="Exercise" style="min-width: 90px">
          <template #body="{ data }">
            {{ data.exercise_minutes }}min
            <small v-if="data.exercise_type" class="text-muted"> · {{ data.exercise_type }}</small>
          </template>
        </Column>

        <Column field="protein" header="Protein" style="min-width: 80px">
          <template #body="{ data }">
            <span v-if="data.protein">{{ data.protein }}g</span>
            <span v-else class="text-muted">—</span>
          </template>
        </Column>

        <Column field="note" header="Note" style="min-width: 120px">
          <template #body="{ data }">
            <span v-if="data.note" class="note-cell" :title="data.note">{{ data.note }}</span>
            <span v-else class="text-muted">—</span>
          </template>
        </Column>

        <Column header="Actions" style="min-width: 100px; text-align: right">
          <template #body="{ data }">
            <div class="row-actions">
              <Button
                icon="pi pi-pencil"
                severity="secondary"
                text
                rounded
                size="small"
                @click="openForm(data)"
                v-tooltip="'Edit'"
              />
              <Button
                icon="pi pi-trash"
                severity="danger"
                text
                rounded
                size="small"
                @click="confirmDelete(data)"
                v-tooltip="'Delete'"
              />
            </div>
          </template>
        </Column>
      </DataTable>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { useConfirm } from 'primevue/useconfirm'
import { useToast } from 'primevue/usetoast'

import Button from 'primevue/button'
import Dialog from 'primevue/dialog'
import DataTable from 'primevue/datatable'
import type { DataTablePageEvent } from 'primevue/datatable'
import Column from 'primevue/column'
import InputNumber from 'primevue/inputnumber'
import InputText from 'primevue/inputtext'
import Textarea from 'primevue/textarea'
import DatePicker from 'primevue/datepicker'
import ConfirmDialog from 'primevue/confirmdialog'

import StatePanel from '@/components/StatePanel.vue'
import { useHealthRecordsStore } from '@/stores/healthRecords'
import { useAnalyticsStore } from '@/stores/analytics'
import type { HealthRecord } from '@/services/api'

const store = useHealthRecordsStore()
const analyticsStore = useAnalyticsStore()
const confirm = useConfirm()
const toast = useToast()

const today = new Date()
const first = computed(() => store.query.skip)
const rows = computed(() => store.query.limit)

const pageRangeText = computed(() => {
  if (store.total === 0) return 'No records'
  const start = Math.min(store.query.skip + 1, store.total)
  const end = Math.min(store.query.skip + store.records.length, store.total)
  return `Showing ${start}–${end} of ${store.total}`
})

const showForm = ref(false)
const editingRecord = ref<HealthRecord | null>(null)
const formError = ref('')

const defaultForm = () => ({
  record_date: new Date(),
  weight: null as number | null,
  sleep_hours: null as number | null,
  calories: null as number | null,
  protein: null as number | null,
  exercise_minutes: 0,
  exercise_type: '',
  steps: null as number | null,
  note: '',
})

const form = reactive(defaultForm())

function openForm(record: HealthRecord | null) {
  formError.value = ''
  if (record) {
    editingRecord.value = record
    const d = new Date(record.record_date + 'T00:00:00')
    Object.assign(form, {
      record_date: d,
      weight: record.weight,
      sleep_hours: record.sleep_hours,
      calories: record.calories,
      protein: record.protein ?? null,
      exercise_minutes: record.exercise_minutes,
      exercise_type: record.exercise_type ?? '',
      steps: record.steps ?? null,
      note: record.note ?? '',
    })
  } else {
    editingRecord.value = null
    Object.assign(form, defaultForm())
  }
  showForm.value = true
}

async function submitForm() {
  formError.value = ''
  if (!form.record_date || form.weight === null || form.sleep_hours === null || form.calories === null) {
    formError.value = 'Please fill in all required fields (Date, Weight, Sleep, Calories).'
    return
  }

  const dateStr = form.record_date instanceof Date
    ? `${form.record_date.getFullYear()}-${String(form.record_date.getMonth() + 1).padStart(2, "0")}-${String(form.record_date.getDate()).padStart(2, "0")}`
    : String(form.record_date)

  const payload = {
    record_date: dateStr,
    weight: form.weight!,
    sleep_hours: form.sleep_hours!,
    calories: form.calories!,
    protein: form.protein ?? undefined,
    exercise_minutes: form.exercise_minutes ?? 0,
    exercise_type: form.exercise_type || undefined,
    steps: form.steps ?? undefined,
    note: form.note || undefined,
  }

  let result
  if (editingRecord.value) {
    result = await store.updateRecord(editingRecord.value.id, payload)
    if (result) {
      toast.add({ severity: 'success', summary: 'Updated', detail: 'Record updated successfully.', life: 3000 })
      showForm.value = false
    } else {
      formError.value = store.error || 'Failed to update record.'
    }
  } else {
    result = await store.createRecord(payload)
    if (result) {
      toast.add({ severity: 'success', summary: 'Saved', detail: 'Record saved successfully.', life: 3000 })
      showForm.value = false
    } else {
      formError.value = store.error || 'Failed to save record.'
    }
  }
}

function confirmDelete(record: HealthRecord) {
  confirm.require({
    message: `Delete record for ${record.record_date}?`,
    header: 'Confirm Delete',
    icon: 'pi pi-exclamation-triangle',
    rejectLabel: 'Cancel',
    acceptLabel: 'Delete',
    acceptClass: 'p-button-danger',
    accept: async () => {
      const ok = await store.deleteRecord(record.id)
      if (ok) {
        toast.add({ severity: 'info', summary: 'Deleted', detail: 'Record deleted.', life: 3000 })
      }
    },
  })
}

async function loadRecords() {
  await store.fetchRecords({ skip: store.query.skip, limit: store.query.limit })
}

async function onPage(event: DataTablePageEvent) {
  await store.fetchRecords({ skip: event.first, limit: event.rows })
}

onMounted(loadRecords)
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

.record-form { display: flex; flex-direction: column; gap: 0.75rem; }
.form-row { display: grid; grid-template-columns: 1fr 1fr; gap: 0.75rem; }
.form-group { display: flex; flex-direction: column; gap: 6px; }
.form-group label { font-size: 0.82rem; font-weight: 600; color: var(--color-text-secondary); }
.form-error { color: var(--color-danger); font-size: 0.85rem; padding: 8px 12px; background: #fee2e2; border-radius: 6px; }
.form-actions { display: flex; justify-content: flex-end; gap: 0.5rem; margin-top: 0.5rem; }

.table-card { padding: 0; overflow: hidden; }
.table-toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1rem 1.25rem;
  border-bottom: 1px solid var(--color-border);
}
.table-count { font-size: 0.85rem; color: var(--color-text-secondary); font-weight: 500; }
.table-empty { padding: 2rem; text-align: center; color: var(--color-text-secondary); }

.date-cell { font-weight: 600; font-size: 0.875rem; }
.weight-cell { font-weight: 700; font-size: 1rem; }
.weight-cell small { font-weight: 400; font-size: 0.75rem; color: var(--color-text-secondary); }
.val-warn { color: #dc2626; font-weight: 600; }
.val-ok   { color: #16a34a; font-weight: 500; }
.note-cell {
  display: block;
  max-width: 150px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  font-size: 0.8rem;
  color: var(--color-text-secondary);
}
.row-actions { display: flex; gap: 2px; justify-content: flex-end; }

@media (max-width: 480px) {
  .form-row { grid-template-columns: 1fr; }
}
</style>
