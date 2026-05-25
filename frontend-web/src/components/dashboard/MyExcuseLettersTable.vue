<template>
  <div class="my-letters">
    <div class="my-letters__header">
      <div>
        <p class="my-letters__eyebrow">Submitted Letters</p>
        <h2 class="my-letters__title">My Excuse Letters</h2>
      </div>
      <span v-if="letters.length" class="my-letters__count">{{ letters.length }}</span>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="my-letters__state">
      <Loader2Icon class="spin-icon" :size="20" />
      <p>Loading your excuse letters...</p>
    </div>

    <!-- Error -->
    <div v-else-if="error" class="my-letters__state my-letters__state--error">
      <AlertCircleIcon :size="18" />
      <p>{{ error }}</p>
    </div>

    <!-- Empty state -->
    <div v-else-if="!letters.length" class="my-letters__state my-letters__state--empty">
      <MailIcon :size="28" class="my-letters__empty-icon" />
      <p class="my-letters__empty-title">No excuse letters yet</p>
      <p class="my-letters__empty-sub">When you submit an excuse letter for an upcoming event, it will appear here.</p>
    </div>

    <!-- Table -->
    <div v-else class="my-letters__list">
      <div
        v-for="letter in letters"
        :key="letter.id"
        class="letter-card"
        :class="`letter-card--${letter.status}`"
      >
        <!-- Status indicator bar -->
        <div class="letter-card__bar"></div>

        <div class="letter-card__body">
          <div class="letter-card__top">
            <div class="letter-card__info">
              <p class="letter-card__event">{{ letter.event?.name || 'Unknown Event' }}</p>
              <p class="letter-card__date">Submitted {{ formatDate(letter.created_at) }}</p>
            </div>
            <span class="letter-badge" :class="`letter-badge--${letter.status}`">
              <component :is="statusIcon(letter.status)" :size="11" />
              {{ statusLabel(letter.status) }}
            </span>
          </div>

          <p class="letter-card__reason">{{ truncate(letter.reason, 120) }}</p>

          <!-- Decision details -->
          <div v-if="letter.status !== 'pending'" class="letter-card__decision">
            <div class="letter-card__decision-row">
              <UserCheckIcon v-if="letter.status === 'approved'" :size="13" />
              <UserXIcon v-else :size="13" />
              <span>
                {{ letter.status === 'approved' ? 'Approved' : 'Rejected' }} by
                {{ letter.reviewer?.full_name || 'Officer' }}
                {{ letter.reviewed_at ? '· ' + formatDate(letter.reviewed_at) : '' }}
              </span>
            </div>
            <p v-if="letter.reviewer_remarks" class="letter-card__remarks">
              "{{ letter.reviewer_remarks }}"
            </p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import {
  AlertCircle as AlertCircleIcon,
  Clock as ClockIcon,
  CheckCircle as CheckCircleIcon,
  XCircle as XCircleIcon,
  Loader2 as Loader2Icon,
  Mail as MailIcon,
  UserCheck as UserCheckIcon,
  UserX as UserXIcon,
} from 'lucide-vue-next'

defineProps({
  letters: {
    type: Array,
    default: () => [],
  },
  loading: {
    type: Boolean,
    default: false,
  },
  error: {
    type: String,
    default: null,
  },
})

function statusIcon(status) {
  if (status === 'approved') return CheckCircleIcon
  if (status === 'rejected') return XCircleIcon
  return ClockIcon
}

function statusLabel(status) {
  if (status === 'approved') return 'Approved'
  if (status === 'rejected') return 'Rejected'
  return 'Pending Review'
}

function truncate(text, max) {
  if (!text) return ''
  return text.length > max ? text.slice(0, max) + '…' : text
}

function formatDate(iso) {
  if (!iso) return ''
  return new Date(iso).toLocaleDateString('en-PH', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
  })
}
</script>

<style scoped>
.my-letters {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.my-letters__header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
}

.my-letters__eyebrow {
  margin: 0 0 3px;
  font-size: 10px;
  font-weight: 800;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: var(--color-surface-text-muted);
}

.my-letters__title {
  margin: 0;
  font-size: 16px;
  font-weight: 800;
  color: var(--color-surface-text);
}

.my-letters__count {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 24px;
  height: 24px;
  padding: 0 7px;
  border-radius: 999px;
  background: color-mix(in srgb, var(--color-primary) 18%, transparent);
  color: var(--color-surface-text);
  font-size: 11px;
  font-weight: 800;
}

.my-letters__state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 32px 16px;
  text-align: center;
  color: var(--color-surface-text-muted);
  font-size: 13px;
  font-weight: 600;
  border-radius: 12px;
  border: 1px dashed color-mix(in srgb, var(--color-surface-border) 70%, transparent);
}

.my-letters__state--error {
  color: #ef4444;
  border-color: rgba(239, 68, 68, 0.2);
  background: rgba(239, 68, 68, 0.04);
}

.my-letters__empty-icon {
  color: var(--color-primary);
  opacity: 0.6;
}

.my-letters__empty-title {
  margin: 0;
  font-size: 14px;
  font-weight: 700;
  color: var(--color-surface-text);
}

.my-letters__empty-sub {
  margin: 0;
  font-size: 12px;
  max-width: 280px;
  line-height: 1.5;
}

.spin-icon {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.my-letters__list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.letter-card {
  display: flex;
  border-radius: 14px;
  background: var(--color-surface);
  border: 1px solid color-mix(in srgb, var(--color-surface-border) 80%, transparent);
  overflow: hidden;
  transition: box-shadow 0.18s ease;
}

.letter-card:hover {
  box-shadow: 0 6px 20px color-mix(in srgb, var(--color-nav) 8%, transparent);
}

.letter-card__bar {
  width: 4px;
  flex-shrink: 0;
  border-radius: 4px 0 0 4px;
}

.letter-card--pending .letter-card__bar { background: #f59e0b; }
.letter-card--approved .letter-card__bar { background: #22c55e; }
.letter-card--rejected .letter-card__bar { background: #ef4444; }

.letter-card__body {
  flex: 1;
  padding: 12px 14px;
  display: flex;
  flex-direction: column;
  gap: 8px;
  min-width: 0;
}

.letter-card__top {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 8px;
}

.letter-card__info {
  min-width: 0;
}

.letter-card__event {
  margin: 0;
  font-size: 13px;
  font-weight: 700;
  color: var(--color-surface-text);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.letter-card__date {
  margin: 2px 0 0;
  font-size: 11px;
  color: var(--color-surface-text-muted);
  font-weight: 500;
}

.letter-badge {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 3px 9px;
  border-radius: 999px;
  font-size: 10px;
  font-weight: 700;
  white-space: nowrap;
  flex-shrink: 0;
}

.letter-badge--pending  { background: rgba(245,158,11,0.14); color: #d97706; }
.letter-badge--approved { background: rgba(34,197,94,0.12);  color: #16a34a; }
.letter-badge--rejected { background: rgba(239,68,68,0.12);  color: #dc2626; }

.letter-card__reason {
  margin: 0;
  font-size: 12px;
  line-height: 1.5;
  color: var(--color-surface-text-secondary);
  font-style: italic;
}

.letter-card__decision {
  display: flex;
  flex-direction: column;
  gap: 4px;
  padding-top: 8px;
  border-top: 1px solid color-mix(in srgb, var(--color-surface-border) 60%, transparent);
}

.letter-card__decision-row {
  display: flex;
  align-items: center;
  gap: 5px;
  font-size: 11px;
  font-weight: 600;
  color: var(--color-surface-text-muted);
}

.letter-card__remarks {
  margin: 0;
  font-size: 11px;
  line-height: 1.4;
  color: var(--color-surface-text-secondary);
  font-style: italic;
  padding-left: 4px;
  border-left: 2px solid color-mix(in srgb, var(--color-surface-border) 80%, transparent);
}
</style>
