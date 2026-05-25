<template>
  <div class="review-panel">
    <!-- Header with metrics -->
    <div class="review-panel__header">
      <div>
        <p class="review-panel__eyebrow">Governance</p>
        <h2 class="review-panel__title">Excuse Letters</h2>
      </div>

      <div class="metrics-row">
        <div class="metric metric--pending">
          <span class="metric__value">{{ metrics.pending }}</span>
          <span class="metric__label">Pending</span>
        </div>
        <div class="metric metric--approved">
          <span class="metric__value">{{ metrics.approved }}</span>
          <span class="metric__label">Approved</span>
        </div>
        <div class="metric metric--rejected">
          <span class="metric__value">{{ metrics.rejected }}</span>
          <span class="metric__label">Rejected</span>
        </div>
      </div>
    </div>

    <!-- Filter bar -->
    <div class="filter-bar">
      <button
        v-for="f in filters"
        :key="f.value"
        class="filter-btn"
        :class="{ 'filter-btn--active': activeFilter === f.value }"
        type="button"
        @click="activeFilter = f.value"
      >
        {{ f.label }}
        <span v-if="countForFilter(f.value)" class="filter-badge">{{ countForFilter(f.value) }}</span>
      </button>

      <div class="filter-spacer"></div>

      <input
        v-model="searchQuery"
        type="text"
        class="search-input"
        placeholder="Search student or event..."
      />
    </div>

    <!-- Loading -->
    <div v-if="loading" class="panel-state">
      <Loader2Icon :size="22" class="spin-icon" />
      <p>Loading submissions...</p>
    </div>

    <!-- Error -->
    <div v-else-if="error" class="panel-state panel-state--error">
      <AlertCircleIcon :size="18" />
      <p>{{ error }}</p>
    </div>

    <!-- Empty state -->
    <div v-else-if="!filteredLetters.length" class="panel-state">
      <InboxIcon :size="28" style="opacity: 0.4;" />
      <p>No excuse letters {{ activeFilter !== 'all' ? `with status "${activeFilter}"` : '' }}.</p>
    </div>

    <!-- Cards -->
    <div v-else class="submissions-list">
      <div
        v-for="letter in filteredLetters"
        :key="letter.id"
        class="submission-card"
        :class="`submission-card--${letter.status}`"
      >
        <div class="submission-card__bar"></div>

        <div class="submission-card__content">
          <!-- Top row: student + status -->
          <div class="submission-card__top">
            <div class="submission-student">
              <div class="student-avatar">
                {{ initials(letter.student?.full_name) }}
              </div>
              <div class="student-info">
                <p class="student-info__name">{{ letter.student?.full_name || 'Unknown Student' }}</p>
                <p class="student-info__meta">
                  {{ letter.student?.student_number }}
                  <template v-if="letter.student?.year_level"> · Year {{ letter.student.year_level }}</template>
                  <template v-if="letter.student?.course"> · {{ letter.student.course }}</template>
                </p>
              </div>
            </div>

            <div class="submission-card__right">
              <span class="submission-badge" :class="`submission-badge--${letter.status}`">
                <component :is="statusIcon(letter.status)" :size="11" />
                {{ statusLabel(letter.status) }}
              </span>
            </div>
          </div>

          <!-- Event info -->
          <div class="submission-event">
            <CalendarIcon :size="12" />
            <span>{{ letter.event?.name || 'Unknown Event' }}</span>
            <span v-if="letter.event?.start_at" class="submission-event__date">
              · {{ formatDate(letter.event.start_at) }}
            </span>
          </div>

          <!-- Reason -->
          <p class="submission-reason">{{ truncate(letter.reason, 180) }}</p>

          <!-- Attachment link -->
          <a
            v-if="letter.attachment_path"
            class="attachment-link"
            :href="resolveAttachmentUrl(letter.attachment_path)"
            target="_blank"
            rel="noopener noreferrer"
            @click.stop
          >
            <PaperclipIcon :size="12" />
            View attachment
          </a>

          <!-- Submitted date -->
          <p class="submission-date">Submitted {{ formatDate(letter.created_at) }}</p>

          <!-- Decision row (already decided) -->
          <div v-if="letter.status !== 'pending'" class="submission-decision">
            <span>Decision by {{ letter.reviewer?.full_name || 'Officer' }}</span>
            <span v-if="letter.reviewer_remarks" class="submission-decision__remarks">
              "{{ letter.reviewer_remarks }}"
            </span>
          </div>

          <!-- Action row (pending only) -->
          <div v-if="letter.status === 'pending'" class="submission-actions">
            <button
              class="action-btn action-btn--approve"
              type="button"
              :disabled="actionLoading === letter.id"
              @click="initiateReview(letter, 'approve')"
            >
              <CheckIcon :size="13" />
              Approve
            </button>
            <button
              class="action-btn action-btn--reject"
              type="button"
              :disabled="actionLoading === letter.id"
              @click="initiateReview(letter, 'reject')"
            >
              <XIcon :size="13" />
              Reject
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Review Confirm Dialog -->
    <Teleport to="body">
      <Transition name="dialog-fade">
        <div v-if="reviewDialog.open" class="dialog-overlay" @click.self="closeDialog">
          <div class="dialog-card">
            <h3 class="dialog-title">
              {{ reviewDialog.action === 'approve' ? 'Approve' : 'Reject' }} Excuse Letter?
            </h3>
            <p class="dialog-sub">
              Student: <strong>{{ reviewDialog.letter?.student?.full_name }}</strong><br/>
              Event: <strong>{{ reviewDialog.letter?.event?.name }}</strong>
            </p>

            <div class="dialog-field">
              <label class="dialog-label">
                Remarks <span class="dialog-label--optional">(optional)</span>
              </label>
              <textarea
                v-model="reviewDialog.remarks"
                rows="3"
                class="dialog-textarea"
                placeholder="Add a note to the student..."
              ></textarea>
            </div>

            <div v-if="actionError" class="dialog-error">
              <AlertCircleIcon :size="13" />
              {{ actionError }}
            </div>

            <div class="dialog-actions">
              <button class="dialog-btn dialog-btn--cancel" type="button" @click="closeDialog">
                Cancel
              </button>
              <button
                class="dialog-btn"
                :class="reviewDialog.action === 'approve' ? 'dialog-btn--approve' : 'dialog-btn--reject'"
                type="button"
                :disabled="confirming"
                @click="confirmReview"
              >
                <Loader2Icon v-if="confirming" :size="13" class="spin-icon" />
                {{ reviewDialog.action === 'approve' ? 'Confirm Approve' : 'Confirm Reject' }}
              </button>
            </div>
          </div>
        </div>
      </Transition>
    </Teleport>
  </div>
</template>

<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import {
  AlertCircle as AlertCircleIcon,
  Calendar as CalendarIcon,
  Check as CheckIcon,
  CheckCircle as CheckCircleIcon,
  Clock as ClockIcon,
  Inbox as InboxIcon,
  Loader2 as Loader2Icon,
  Paperclip as PaperclipIcon,
  X as XIcon,
  XCircle as XCircleIcon,
} from 'lucide-vue-next'
import { useExcuseLetterStore } from '@/stores/excuseLetterStore.js'
import { resolveApiBaseUrl } from '@/services/backendApi.js'

const store = useExcuseLetterStore()

const activeFilter = ref('all')
const searchQuery = ref('')
const actionLoading = ref(null)
const actionError = ref(null)
const confirming = ref(false)

const reviewDialog = ref({
  open: false,
  letter: null,
  action: null, // 'approve' | 'reject'
  remarks: '',
})

const filters = [
  { value: 'all', label: 'All' },
  { value: 'pending', label: 'Pending' },
  { value: 'approved', label: 'Approved' },
  { value: 'rejected', label: 'Rejected' },
]

const letters = computed(() => store.submissions)
const metrics = computed(() => store.dashboardMetrics)
const loading = computed(() => store.loading)
const error = computed(() => store.error)

const filteredLetters = computed(() => {
  let result = letters.value
  if (activeFilter.value !== 'all') {
    result = result.filter(l => l.status === activeFilter.value)
  }
  if (searchQuery.value.trim()) {
    const q = searchQuery.value.trim().toLowerCase()
    result = result.filter(l =>
      l.student?.full_name?.toLowerCase().includes(q) ||
      l.student?.student_number?.toLowerCase().includes(q) ||
      l.event?.name?.toLowerCase().includes(q)
    )
  }
  return result
})

function countForFilter(filterValue) {
  if (filterValue === 'all') return letters.value.length || null
  return letters.value.filter(l => l.status === filterValue).length || null
}

function statusIcon(status) {
  if (status === 'approved') return CheckCircleIcon
  if (status === 'rejected') return XCircleIcon
  return ClockIcon
}

function statusLabel(status) {
  if (status === 'approved') return 'Approved'
  if (status === 'rejected') return 'Rejected'
  return 'Pending'
}

function initials(name) {
  if (!name) return '?'
  return name.split(' ').slice(0, 2).map(w => w[0]).join('').toUpperCase()
}

function truncate(text, max) {
  if (!text) return ''
  return text.length > max ? text.slice(0, max) + '…' : text
}

function formatDate(iso) {
  if (!iso) return ''
  return new Date(iso).toLocaleDateString('en-PH', { month: 'short', day: 'numeric', year: 'numeric' })
}

function resolveAttachmentUrl(path) {
  const base = resolveApiBaseUrl()
  return `${base}/api/media/${path}`
}

function initiateReview(letter, action) {
  reviewDialog.value = { open: true, letter, action, remarks: '' }
  actionError.value = null
}

function closeDialog() {
  reviewDialog.value = { open: false, letter: null, action: null, remarks: '' }
  actionError.value = null
}

async function confirmReview() {
  const { letter, action, remarks } = reviewDialog.value
  if (!letter) return

  confirming.value = true
  actionError.value = null
  actionLoading.value = letter.id

  try {
    if (action === 'approve') {
      await store.approveLetter(letter.id, remarks)
    } else {
      await store.rejectLetter(letter.id, remarks)
    }
    closeDialog()
  } catch (err) {
    actionError.value = err.message || 'Action failed. Please try again.'
  } finally {
    confirming.value = false
    actionLoading.value = null
  }
}

onMounted(async () => {
  await Promise.allSettled([
    store.fetchAllSubmissions(),
    store.fetchDashboardMetrics(),
  ])
})
</script>

<style scoped>
.review-panel {
  display: flex;
  flex-direction: column;
  gap: 18px;
}

.review-panel__header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 12px;
}

.review-panel__eyebrow {
  margin: 0 0 3px;
  font-size: 10px;
  font-weight: 800;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: var(--color-surface-text-muted);
}

.review-panel__title {
  margin: 0;
  font-size: 18px;
  font-weight: 800;
  color: var(--color-surface-text);
}

.metrics-row {
  display: flex;
  gap: 8px;
}

.metric {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 8px 14px;
  border-radius: 12px;
  background: var(--color-surface);
  border: 1px solid color-mix(in srgb, var(--color-surface-border) 70%, transparent);
  min-width: 56px;
}

.metric__value {
  font-size: 18px;
  font-weight: 800;
  line-height: 1;
}

.metric__label {
  font-size: 9px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  margin-top: 3px;
  color: var(--color-surface-text-muted);
}

.metric--pending .metric__value  { color: #d97706; }
.metric--approved .metric__value { color: #16a34a; }
.metric--rejected .metric__value { color: #dc2626; }

/* Filter bar */
.filter-bar {
  display: flex;
  align-items: center;
  gap: 6px;
  flex-wrap: wrap;
}

.filter-btn {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  padding: 6px 14px;
  border-radius: 999px;
  border: 1px solid color-mix(in srgb, var(--color-surface-border) 80%, transparent);
  background: var(--color-surface);
  color: var(--color-surface-text-muted);
  font-size: 12px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.15s ease;
}

.filter-btn:hover { color: var(--color-surface-text); }

.filter-btn--active {
  background: var(--color-primary);
  border-color: var(--color-primary);
  color: var(--color-banner-text);
}

.filter-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 16px;
  height: 16px;
  border-radius: 999px;
  background: rgba(0,0,0,0.12);
  font-size: 9px;
  font-weight: 800;
  padding: 0 4px;
}

.filter-spacer { flex: 1; }

.search-input {
  padding: 7px 14px;
  border-radius: 999px;
  border: 1px solid color-mix(in srgb, var(--color-surface-border) 80%, transparent);
  background: var(--color-surface);
  color: var(--color-surface-text);
  font-size: 12px;
  font-weight: 500;
  outline: none;
  transition: border-color 0.18s ease;
  min-width: 180px;
}

.search-input:focus {
  border-color: var(--color-primary);
}

/* Panel states */
.panel-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 40px 16px;
  text-align: center;
  color: var(--color-surface-text-muted);
  font-size: 13px;
  font-weight: 600;
  border-radius: 14px;
  border: 1px dashed color-mix(in srgb, var(--color-surface-border) 70%, transparent);
}

.panel-state--error {
  color: #ef4444;
  border-color: rgba(239,68,68,0.2);
  background: rgba(239,68,68,0.04);
}

.spin-icon { animation: spin 1s linear infinite; }
@keyframes spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }

/* Submission cards */
.submissions-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.submission-card {
  display: flex;
  border-radius: 14px;
  background: var(--color-surface);
  border: 1px solid color-mix(in srgb, var(--color-surface-border) 80%, transparent);
  overflow: hidden;
  transition: box-shadow 0.18s ease;
}

.submission-card:hover {
  box-shadow: 0 6px 20px color-mix(in srgb, var(--color-nav) 8%, transparent);
}

.submission-card__bar {
  width: 4px;
  flex-shrink: 0;
}

.submission-card--pending .submission-card__bar  { background: #f59e0b; }
.submission-card--approved .submission-card__bar { background: #22c55e; }
.submission-card--rejected .submission-card__bar { background: #ef4444; }

.submission-card__content {
  flex: 1;
  padding: 14px 16px;
  display: flex;
  flex-direction: column;
  gap: 8px;
  min-width: 0;
}

.submission-card__top {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 10px;
}

.submission-student {
  display: flex;
  align-items: center;
  gap: 10px;
  min-width: 0;
}

.student-avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: color-mix(in srgb, var(--color-primary) 20%, transparent);
  color: var(--color-surface-text);
  font-size: 12px;
  font-weight: 800;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.student-info__name {
  margin: 0;
  font-size: 13px;
  font-weight: 700;
  color: var(--color-surface-text);
}

.student-info__meta {
  margin: 2px 0 0;
  font-size: 11px;
  color: var(--color-surface-text-muted);
  font-weight: 500;
}

.submission-card__right {
  flex-shrink: 0;
}

.submission-badge {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 3px 9px;
  border-radius: 999px;
  font-size: 10px;
  font-weight: 700;
  white-space: nowrap;
}

.submission-badge--pending  { background: rgba(245,158,11,0.14); color: #d97706; }
.submission-badge--approved { background: rgba(34,197,94,0.12);  color: #16a34a; }
.submission-badge--rejected { background: rgba(239,68,68,0.12);  color: #dc2626; }

.submission-event {
  display: flex;
  align-items: center;
  gap: 5px;
  font-size: 11px;
  font-weight: 600;
  color: var(--color-primary);
}

.submission-event__date {
  color: var(--color-surface-text-muted);
  font-weight: 500;
}

.submission-reason {
  margin: 0;
  font-size: 12px;
  line-height: 1.5;
  color: var(--color-surface-text-secondary);
  font-style: italic;
}

.attachment-link {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  font-size: 11px;
  font-weight: 600;
  color: var(--color-primary);
  text-decoration: none;
  transition: opacity 0.15s ease;
}

.attachment-link:hover { opacity: 0.75; }

.submission-date {
  margin: 0;
  font-size: 11px;
  color: var(--color-surface-text-muted);
  font-weight: 500;
}

.submission-decision {
  padding-top: 8px;
  border-top: 1px solid color-mix(in srgb, var(--color-surface-border) 60%, transparent);
  font-size: 11px;
  color: var(--color-surface-text-muted);
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.submission-decision__remarks {
  font-style: italic;
  padding-left: 4px;
  border-left: 2px solid color-mix(in srgb, var(--color-surface-border) 80%, transparent);
}

.submission-actions {
  display: flex;
  gap: 8px;
  padding-top: 8px;
  border-top: 1px solid color-mix(in srgb, var(--color-surface-border) 60%, transparent);
}

.action-btn {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  padding: 6px 14px;
  border-radius: 8px;
  border: none;
  font-size: 12px;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.15s ease;
}

.action-btn:disabled { opacity: 0.55; cursor: not-allowed; }

.action-btn--approve {
  background: rgba(34,197,94,0.14);
  color: #16a34a;
}

.action-btn--approve:hover:not(:disabled) {
  background: rgba(34,197,94,0.24);
}

.action-btn--reject {
  background: rgba(239,68,68,0.12);
  color: #dc2626;
}

.action-btn--reject:hover:not(:disabled) {
  background: rgba(239,68,68,0.22);
}

/* Dialog */
.dialog-overlay {
  position: fixed;
  inset: 0;
  z-index: 60;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 16px;
  background: rgba(0,0,0,0.5);
  backdrop-filter: blur(8px);
}

.dialog-card {
  background: var(--color-surface);
  border: 1px solid color-mix(in srgb, var(--color-surface-border) 80%, transparent);
  border-radius: 20px;
  padding: 24px;
  width: 100%;
  max-width: 420px;
  box-shadow: 0 24px 60px rgba(0,0,0,0.18);
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.dialog-title {
  margin: 0;
  font-size: 17px;
  font-weight: 800;
  color: var(--color-surface-text);
}

.dialog-sub {
  margin: 0;
  font-size: 13px;
  line-height: 1.55;
  color: var(--color-surface-text-secondary);
}

.dialog-field {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.dialog-label {
  font-size: 11px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  color: var(--color-surface-text-muted);
}

.dialog-label--optional {
  font-weight: 500;
  text-transform: none;
  letter-spacing: 0;
}

.dialog-textarea {
  border-radius: 10px;
  border: 1px solid color-mix(in srgb, var(--color-surface-border) 80%, transparent);
  background: color-mix(in srgb, var(--color-bg) 50%, var(--color-surface));
  color: var(--color-surface-text);
  font-size: 13px;
  padding: 10px 12px;
  resize: none;
  outline: none;
  transition: border-color 0.18s ease;
}

.dialog-textarea:focus {
  border-color: var(--color-primary);
}

.dialog-error {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 10px 12px;
  border-radius: 10px;
  background: rgba(239,68,68,0.08);
  color: #dc2626;
  font-size: 12px;
  font-weight: 600;
  border: 1px solid rgba(239,68,68,0.2);
}

.dialog-actions {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
}

.dialog-btn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 8px 18px;
  border-radius: 10px;
  border: none;
  font-size: 13px;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.15s ease;
}

.dialog-btn:disabled { opacity: 0.6; cursor: not-allowed; }

.dialog-btn--cancel {
  background: color-mix(in srgb, var(--color-surface-border) 50%, transparent);
  color: var(--color-surface-text-muted);
}

.dialog-btn--approve {
  background: #16a34a;
  color: #fff;
}

.dialog-btn--reject {
  background: #dc2626;
  color: #fff;
}

.dialog-fade-enter-active,
.dialog-fade-leave-active {
  transition: all 0.3s cubic-bezier(0.22, 1, 0.36, 1);
}

.dialog-fade-enter-from,
.dialog-fade-leave-to {
  opacity: 0;
  transform: scale(0.95) translateY(10px);
}
</style>
