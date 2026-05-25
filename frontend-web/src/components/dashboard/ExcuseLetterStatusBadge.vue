<template>
  <div class="excuse-badge-wrap">
    <!-- Not a student or not upcoming: nothing -->
    <template v-if="showSendButton">
      <button
        class="excuse-btn"
        type="button"
        :disabled="loading"
        @click.stop="$emit('send')"
      >
        <MailIcon :size="13" />
        <span>Send Excuse Letter</span>
      </button>
    </template>

    <template v-else-if="status">
      <span class="excuse-status-badge" :class="`excuse-status-badge--${status}`">
        <component :is="statusIcon" :size="11" />
        {{ statusLabel }}
      </span>
    </template>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { Mail as MailIcon, Clock as ClockIcon, CheckCircle as CheckCircleIcon, XCircle as XCircleIcon } from 'lucide-vue-next'

const props = defineProps({
  /**
   * The event's lifecycle status: 'upcoming' | 'ongoing' | 'completed' | 'cancelled'
   */
  eventStatus: {
    type: String,
    default: 'upcoming',
  },
  /**
   * Whether the current user is a student
   */
  isStudent: {
    type: Boolean,
    default: false,
  },
  /**
   * The student's excuse letter status for this event: null | 'pending' | 'approved' | 'rejected'
   */
  status: {
    type: String,
    default: null,
  },
  loading: {
    type: Boolean,
    default: false,
  },
})

defineEmits(['send'])

const showSendButton = computed(() => (
  props.isStudent &&
  props.eventStatus === 'upcoming' &&
  !props.status
))

const statusIcon = computed(() => {
  if (props.status === 'pending') return ClockIcon
  if (props.status === 'approved') return CheckCircleIcon
  if (props.status === 'rejected') return XCircleIcon
  return ClockIcon
})

const statusLabel = computed(() => {
  if (props.status === 'pending') return 'Pending'
  if (props.status === 'approved') return 'Approved'
  if (props.status === 'rejected') return 'Rejected'
  return ''
})
</script>

<style scoped>
.excuse-badge-wrap {
  display: inline-flex;
  align-items: center;
}

.excuse-btn {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  padding: 5px 12px 5px 8px;
  border-radius: 999px;
  border: 1.5px solid color-mix(in srgb, var(--color-primary) 60%, transparent);
  background: color-mix(in srgb, var(--color-primary) 10%, transparent);
  color: var(--color-surface-text);
  font-size: 10px;
  font-weight: 700;
  cursor: pointer;
  transition: background 0.18s ease, transform 0.15s ease, opacity 0.15s ease;
  white-space: nowrap;
}

.excuse-btn:hover:not(:disabled) {
  background: color-mix(in srgb, var(--color-primary) 20%, transparent);
}

.excuse-btn:active:not(:disabled) {
  transform: scale(0.96);
}

.excuse-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.excuse-status-badge {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 4px 10px;
  border-radius: 999px;
  font-size: 10px;
  font-weight: 700;
  white-space: nowrap;
}

.excuse-status-badge--pending {
  background: rgba(245, 158, 11, 0.14);
  color: #d97706;
  border: 1px solid rgba(245, 158, 11, 0.25);
}

.excuse-status-badge--approved {
  background: rgba(34, 197, 94, 0.12);
  color: #16a34a;
  border: 1px solid rgba(34, 197, 94, 0.25);
}

.excuse-status-badge--rejected {
  background: rgba(239, 68, 68, 0.12);
  color: #dc2626;
  border: 1px solid rgba(239, 68, 68, 0.25);
}
</style>
