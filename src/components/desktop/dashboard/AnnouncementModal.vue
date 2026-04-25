<template>
  <Transition name="modal-fade">
    <div v-if="isOpen" class="modal-overlay" @click.self="$emit('close')">
      <div class="modal-container">
        <div class="modal-header">
          <h2 class="modal-title">Latest Announcements</h2>
          <button class="close-btn" @click="$emit('close')">
            <X :size="20" />
          </button>
        </div>
        
        <div class="modal-body">
          <div v-if="isRefreshing" class="loading-state">
            <div class="spinner"></div>
            <p>Checking for updates...</p>
          </div>
          
          <div v-else-if="announcements.length === 0" class="empty-state">
            <BellOff :size="48" class="empty-icon" />
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
    month: 'long',
    day: 'numeric',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 20px;
}

.modal-container {
  background: var(--color-surface);
  width: 100%;
  max-width: 600px;
  border-radius: 24px;
  overflow: hidden;
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
  display: flex;
  flex-direction: column;
  max-height: 80vh;
}

.modal-header {
  padding: 20px 24px;
  border-bottom: 1px solid var(--color-border);
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.modal-title {
  font-size: 18px;
  font-weight: 800;
  color: var(--color-text-primary);
}

.close-btn {
  background: transparent;
  border: none;
  color: var(--color-text-muted);
  cursor: pointer;
  padding: 4px;
  border-radius: 50%;
  transition: background 0.2s;
}

.close-btn:hover {
  background: var(--color-bg-hover);
}

.modal-body {
  padding: 24px;
  overflow-y: auto;
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px 0;
  color: var(--color-text-muted);
}

.empty-icon {
  margin-bottom: 16px;
  opacity: 0.5;
}

.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 0;
  color: var(--color-text-muted);
}

.spinner {
  width: 40px;
  height: 40px;
  border: 4px solid rgba(0, 0, 0, 0.1);
  border-top-color: var(--color-primary);
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 16px;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.announcement-list {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.announcement-item {
  padding-bottom: 20px;
  border-bottom: 1px solid var(--color-border);
}

.announcement-item:last-child {
  border-bottom: none;
}

.announcement-meta {
  margin-bottom: 4px;
}

.announcement-date {
  font-size: 11px;
  font-weight: 600;
  color: var(--color-text-muted);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.announcement-item-title {
  font-size: 16px;
  font-weight: 700;
  color: var(--color-text-primary);
  margin-bottom: 8px;
}

.announcement-content {
  font-size: 14px;
  line-height: 1.6;
  color: var(--color-text-always-dark);
}

/* Animations */
.modal-fade-enter-active,
.modal-fade-leave-active {
  transition: opacity 0.3s ease;
}

.modal-fade-enter-from,
.modal-fade-leave-to {
  opacity: 0;
}

.modal-fade-enter-active .modal-container {
  animation: modal-pop 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
}

@keyframes modal-pop {
  0% { transform: scale(0.9); opacity: 0; }
  100% { transform: scale(1); opacity: 1; }
}
</style>
