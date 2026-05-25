<template>
  <div class="excuse-dashboard dashboard-enter">
    <TopBar
      class="dashboard-enter dashboard-enter--1"
      :user="currentUser"
      :unread-count="0"
    />

    <div class="excuse-content dashboard-enter dashboard-enter--2">
      <!-- Back button if navigated from somewhere else, or just raw title -->
      <header class="excuse-header">
        <button
          type="button"
          class="back-btn"
          @click="goBack"
        >
          <ArrowLeft :size="20" :stroke-width="2.3" />
        </button>
        <h1 class="page-title">Excuse Letters Management</h1>
      </header>

      <section class="excuse-panel-wrapper dashboard-enter dashboard-enter--3">
        <ExcuseLetterReviewPanel />
      </section>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { ArrowLeft } from 'lucide-vue-next'
import TopBar from '@/components/dashboard/TopBar.vue'
import ExcuseLetterReviewPanel from '@/components/dashboard/ExcuseLetterReviewPanel.vue'
import { useDashboardSession } from '@/composables/useDashboardSession.js'

const router = useRouter()
const { currentUser } = useDashboardSession()

function goBack() {
  router.back()
}
</script>

<style scoped>
.excuse-dashboard {
  min-height: 100vh;
  padding: 28px 22px 100px;
  background: var(--color-bg);
}

.excuse-content {
  display: flex;
  flex-direction: column;
  width: 100%;
  max-width: 1080px;
  margin: 0 auto;
}

.excuse-header {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 24px;
}

.back-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  border-radius: 50%;
  border: none;
  background: transparent;
  color: var(--color-text-always-dark);
  cursor: pointer;
  transition: background 0.15s ease;
}

.back-btn:hover {
  background: rgba(0, 0, 0, 0.05);
}

.page-title {
  margin: 0;
  font-size: 24px;
  font-weight: 800;
  color: var(--color-text-always-dark);
  letter-spacing: -0.5px;
}

.excuse-panel-wrapper {
  background: var(--color-surface);
  border-radius: 20px;
  padding: 24px;
  box-shadow: 0 14px 40px color-mix(in srgb, var(--color-nav) 6%, transparent);
  border: 1px solid color-mix(in srgb, var(--color-surface-border) 60%, transparent);
}

@media (min-width: 768px) {
  .excuse-dashboard {
    padding: 36px 36px 40px;
  }
}
</style>
