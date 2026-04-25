<template>
  <Transition name="sheet-slide">
    <div v-if="isOpen" class="sheet-overlay" @click.self="$emit('close')">
      <div class="sheet-container">
        <div class="sheet-handle" @click="$emit('close')"></div>
        <div class="sheet-header">
          <h2 class="sheet-title">Announcements</h2>
          <button class="close-btn" @click="$emit('close')">
            <X :size="20" />
          </button>
        </div>
        
        <div class="sheet-body">
          <div v-if="isRefreshing" class="loading-state">
            <div class="spinner"></div>
            <p>Checking for updates...</p>
          </div>
          
          <div v-else-if="announcements.length === 0" class="empty-state">
            <BellOff :size="40" class="empty-icon" />
            <p>No announcements yet.</p>
          </div>
          
          <div v-else class="announcement-list">
            <div 
              v-for="ann in announcements" 
              :key="ann.id" 
              class="announcement-item"
            >
              <div class="announcement-meta">
                <span class="announcement-date">{{ formatDate(ann.created_at) }}</span>
              </div>
              <h3 class="announcement-item-title">{{ ann.title }}</h3>
              <p class="announcement-content">{{ ann.content }}</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </Transition>
</template>

<script setup>
import { X, BellOff } from 'lucide-vue-next'

const props = defineProps({
  isOpen: Boolean,
  announcements: {
    type: Array,
    default: () => []
  },
  isRefreshing: Boolean
})

defineEmits(['close'])

function formatDate(dateStr) {
  if (!dateStr) return ''
  return new Date(dateStr).toLocaleDateString('en-PH', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}
</script>

<style scoped>
.sheet-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.4);
  backdrop-filter: blur(2px);
  z-index: 2000;
  display: flex;
  flex-direction: column;
  justify-content: flex-end;
}

.sheet-container {
  background: var(--color-surface);
  border-radius: 28px 28px 0 0;
  width: 100%;
  max-height: 85vh;
  display: flex;
  flex-direction: column;
  padding-bottom: env(safe-area-inset-bottom, 20px);
  box-shadow: 0 -10px 25px rgba(0, 0, 0, 0.1);
}

.sheet-handle {
  width: 40px;
  height: 4px;
  background: rgba(0, 0, 0, 0.1);
  border-radius: 2px;
  margin: 12px auto 4px;
}

.sheet-header {
  padding: 16px 24px;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.sheet-title {
  font-size: 18px;
  font-weight: 800;
  color: var(--color-text-primary);
}

.close-btn {
  background: rgba(0, 0, 0, 0.05);
  border: none;
  color: var(--color-text-muted);
  width: 32px;
  height: 32px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.sheet-body {
  padding: 8px 24px 24px;
  overflow-y: auto;
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 0;
  color: var(--color-text-muted);
  text-align: center;
}

.empty-icon {
  margin-bottom: 12px;
  opacity: 0.4;
}

.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px 0;
  color: var(--color-text-muted);
}

.spinner {
  width: 32px;
  height: 32px;
  border: 3px solid rgba(0, 0, 0, 0.1);
  border-top-color: var(--color-primary);
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 12px;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.announcement-list {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.announcement-item {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.announcement-date {
  font-size: 10px;
  font-weight: 700;
  color: var(--color-text-muted);
  text-transform: uppercase;
  letter-spacing: 0.04em;
}

.announcement-item-title {
  font-size: 16px;
  font-weight: 800;
  color: var(--color-text-primary);
  line-height: 1.3;
}

.announcement-content {
  font-size: 13px;
  line-height: 1.6;
  color: var(--color-text-always-dark);
  opacity: 0.85;
}

/* Animations */
.sheet-slide-enter-active,
.sheet-slide-leave-active {
  transition: opacity 0.3s ease;
}

.sheet-slide-enter-active .sheet-container {
  transition: transform 0.4s cubic-bezier(0.22, 1, 0.36, 1);
}

.sheet-slide-leave-active .sheet-container {
  transition: transform 0.3s ease-in;
}

.sheet-slide-enter-from,
.sheet-slide-leave-to {
  opacity: 0;
}

.sheet-slide-enter-from .sheet-container {
  transform: translateY(100%);
}

.sheet-slide-leave-to .sheet-container {
  transform: translateY(100%);
}
</style>
