<template>
  <Transition name="sheet">
    <div v-if="isOpen" class="sheet-backdrop" @click.self="$emit('close')">
      <div class="sheet-container">
        <div class="sheet-handle md:hidden"></div>
        
        <header class="sheet-header">
          <div class="sheet-title-area">
            <div class="sheet-icon-wrap md:flex hidden">
              <Megaphone :size="18" />
            </div>
            <h2 class="sheet-title">Announcements</h2>
          </div>
          <button class="sheet-close" @click="$emit('close')">
            <X :size="20" />
          </button>
        </header>

        <div class="sheet-content">
          <div v-if="announcements.length">
            <!-- List View -->
            <div v-if="!selectedAnnouncement || !isDesktop" class="ann-list">
              <article 
                v-for="ann in announcements" 
                :key="ann.id" 
                class="ann-item"
                :class="{ 'ann-item--clickable': isDesktop }"
                @click="handleSelect(ann)"
              >
                <div class="ann-indicator"></div>
                <div class="ann-info">
                  <h3 class="ann-item-title">{{ ann.title }}</h3>
                  <p v-if="!isDesktop" class="ann-item-body">{{ ann.body }}</p>
                  <div class="ann-item-footer">
                    <time class="ann-item-date">
                      <Calendar :size="12" class="inline-block mr-1" />
                      {{ formatDate(ann.created_at) }}
                    </time>
                    <span v-if="isDesktop" class="ann-item-more">Read More <ArrowRight :size="12" class="inline-block ml-1" /></span>
                    <span v-else class="ann-item-tag">Latest News</span>
                  </div>
                </div>
              </article>
            </div>

            <!-- Detail View (Desktop only) -->
            <div v-else class="ann-detail dashboard-enter">
              <button class="ann-detail-back" @click="selectedAnnouncement = null">
                <ArrowLeft :size="16" />
                <span>Back to list</span>
              </button>
              
              <div class="ann-detail-content">
                <h3 class="ann-detail-title">{{ selectedAnnouncement.title }}</h3>
                <div class="ann-detail-meta">
                  <Calendar :size="14" />
                  <span>{{ formatDate(selectedAnnouncement.created_at) }}</span>
                </div>
                <div class="ann-detail-divider"></div>
                <p class="ann-detail-body">{{ selectedAnnouncement.body }}</p>
              </div>
            </div>
          </div>

          <div v-else class="ann-empty">
            <Megaphone :size="48" class="mx-auto mb-4 opacity-20" />
            <p>No announcements at the moment.</p>
          </div>
        </div>
      </div>
    </div>
  </Transition>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch } from 'vue'
import { X, Megaphone, Calendar, ArrowLeft, ArrowRight } from 'lucide-vue-next'

const props = defineProps({
  isOpen: Boolean,
  announcements: {
    type: Array,
    default: () => [],
  },
})

defineEmits(['close'])

const selectedAnnouncement = ref(null)
const isDesktop = ref(false)

function checkIsDesktop() {
  isDesktop.value = window.innerWidth >= 768
}

onMounted(() => {
  checkIsDesktop()
  window.addEventListener('resize', checkIsDesktop)
})

onUnmounted(() => {
  window.removeEventListener('resize', checkIsDesktop)
})

watch(() => props.isOpen, (val) => {
  if (!val) {
    setTimeout(() => {
      selectedAnnouncement.value = null
    }, 300)
  }
})

function handleSelect(ann) {
  if (isDesktop.value) {
    selectedAnnouncement.value = ann
  }
}

function formatDate(date) {
  if (!date) return ''
  return new Date(date).toLocaleDateString('en-PH', {
    month: 'short',
    day: 'numeric',
    year: 'numeric'
  })
}
</script>

<style scoped>
.sheet-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.4);
  backdrop-filter: blur(4px);
  z-index: 1000;
  display: flex;
  align-items: flex-end;
  transition: all 0.3s ease;
}

.sheet-container {
  width: 100%;
  background: var(--color-surface);
  border-radius: 32px 32px 0 0;
  padding: 12px 20px 40px;
  max-height: 85vh;
  display: flex;
  flex-direction: column;
  box-shadow: 0 -10px 40px rgba(0, 0, 0, 0.2);
}

.sheet-handle {
  width: 40px;
  height: 4px;
  background: var(--color-surface-border);
  border-radius: 2px;
  margin: 0 auto 16px;
}

.sheet-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 20px;
}

.sheet-title-area {
  display: flex;
  align-items: center;
  gap: 12px;
}

.sheet-icon-wrap {
  width: 36px;
  height: 36px;
  border-radius: 12px;
  background: var(--color-primary-transparent, rgba(0, 87, 184, 0.1));
  color: var(--color-primary);
  align-items: center;
  justify-content: center;
}

.sheet-title {
  font-size: 20px;
  font-weight: 800;
  color: var(--color-text-primary);
}

.sheet-close {
  background: var(--color-surface-border);
  border: none;
  width: 32px;
  height: 32px;
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--color-text-primary);
  cursor: pointer;
  transition: all 0.2s ease;
}

.sheet-close:hover {
  background: var(--color-primary);
  color: white;
  transform: rotate(90deg);
}

.sheet-content {
  overflow-y: auto;
  flex: 1;
  scrollbar-width: none;
}

.sheet-content::-webkit-scrollbar {
  display: none;
}

.ann-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.ann-item {
  display: flex;
  gap: 16px;
  padding: 18px;
  background: var(--color-surface-border);
  border-radius: 24px;
  position: relative;
  transition: all 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);
  border: 1px solid transparent;
}

.ann-indicator {
  width: 4px;
  height: 32px;
  background: var(--color-primary);
  border-radius: 2px;
  flex-shrink: 0;
  margin-top: 2px;
}

.ann-info {
  flex: 1;
}

.ann-item-title {
  font-size: 16px;
  font-weight: 700;
  color: var(--color-text-primary);
  margin-bottom: 6px;
}

.ann-item-body {
  font-size: 13.5px;
  color: var(--color-text-muted);
  line-height: 1.6;
  margin-bottom: 12px;
  overflow-wrap: break-word;
  word-break: break-word;
}

.ann-item-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.ann-item-date {
  font-size: 11px;
  font-weight: 700;
  color: var(--color-text-muted);
  opacity: 0.8;
  display: flex;
  align-items: center;
}

.ann-item-tag {
  font-size: 10px;
  font-weight: 800;
  padding: 4px 10px;
  border-radius: 8px;
  background: white;
  color: var(--color-primary);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  box-shadow: 0 2px 8px rgba(0,0,0,0.05);
}

.ann-empty {
  text-align: center;
  padding: 60px 20px;
  color: var(--color-text-muted);
}

/* Desktop Overrides */
@media (min-width: 768px) {
  .sheet-backdrop {
    align-items: center;
    justify-content: center;
    background: rgba(0, 0, 0, 0.6);
  }

  .sheet-container {
    width: 100%;
    max-width: 580px;
    border-radius: 32px;
    padding: 32px;
    max-height: 70vh;
    animation: modal-pop 0.4s cubic-bezier(0.34, 1.56, 0.64, 1);
  }

  .ann-item {
    background: white;
    box-shadow: 0 4px 12px rgba(0,0,0,0.03);
  }

  .ann-item:hover {
    transform: scale(1.02) translateY(-2px);
    box-shadow: 0 12px 24px rgba(0,0,0,0.08);
    border-color: var(--color-primary-transparent, rgba(0, 87, 184, 0.2));
  }

  .ann-item-title {
    font-size: 18px;
  }

  .ann-item--clickable {
    cursor: pointer;
  }

  .ann-item-more {
    font-size: 11px;
    font-weight: 700;
    color: var(--color-primary);
    opacity: 0;
    transform: translateX(-10px);
    transition: all 0.3s ease;
  }

  .ann-item:hover .ann-item-more {
    opacity: 1;
    transform: translateX(0);
  }

  /* Detail View Styles */
  .ann-detail-back {
    display: flex;
    align-items: center;
    gap: 8px;
    background: none;
    border: none;
    color: var(--color-text-muted);
    font-size: 13px;
    font-weight: 700;
    padding: 8px 12px;
    margin-bottom: 24px;
    border-radius: 10px;
    cursor: pointer;
    transition: all 0.2s ease;
  }

  .ann-detail-back:hover {
    background: var(--color-surface-border);
    color: var(--color-primary);
  }

  .ann-detail-content {
    padding: 0 12px;
  }

  .ann-detail-title {
    font-size: 24px;
    font-weight: 800;
    color: var(--color-text-primary);
    line-height: 1.2;
    margin-bottom: 12px;
  }

  .ann-detail-meta {
    display: flex;
    align-items: center;
    gap: 8px;
    color: var(--color-text-muted);
    font-size: 13px;
    font-weight: 600;
    opacity: 0.8;
  }

  .ann-detail-divider {
    height: 1px;
    background: var(--color-surface-border);
    margin: 24px 0;
  }

  .ann-detail-body {
    font-size: 15px;
    color: var(--color-text-primary);
    line-height: 1.8;
    white-space: pre-wrap;
    overflow-wrap: break-word;
    word-break: break-word;
  }
}

@keyframes modal-pop {
  0% { transform: scale(0.9) translateY(20px); opacity: 0; }
  100% { transform: scale(1) translateY(0); opacity: 1; }
}

/* Transitions */
.sheet-enter-active, .sheet-leave-active {
  transition: opacity 0.3s ease;
}

.sheet-enter-active .sheet-container, .sheet-leave-active .sheet-container {
  transition: transform 0.4s cubic-bezier(0.22, 1, 0.36, 1);
}

.sheet-enter-from, .sheet-leave-to {
  opacity: 0;
}

.sheet-enter-from .sheet-container {
  transform: translateY(100%);
}

.sheet-leave-to .sheet-container {
  transform: translateY(100%);
}

@media (min-width: 768px) {
  .sheet-enter-from .sheet-container, .sheet-leave-to .sheet-container {
    transform: scale(0.95);
  }
}
</style>
