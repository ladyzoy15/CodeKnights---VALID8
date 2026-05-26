<template>
  <div class="sg-page">
    <StandardHeader
      :avatar-url="currentUser?.avatar_url || currentUser?.student_profile?.photo_url"
      :school-name="currentUser?.school_name || 'University Name'"
      :display-name="(currentUser?.first_name || '') + ' ' + (currentUser?.last_name || '')"
      :initials="(currentUser?.first_name?.[0] || '') + (currentUser?.last_name?.[0] || '')"
    />

    <div class="dashboard-enter dashboard-enter--1">
      <h1 class="sg-page-title">Home</h1>
    </div>

    <div class="search-area dashboard-enter dashboard-enter--1">
      <div class="search-shell">
        <input v-model="searchQuery" type="text" placeholder="Search Cards Here..." class="search-input" />
        <Search :size="14" />
      </div>
    </div>

    <div v-if="isLoading" class="sg-loading-state">
      <p>Loading dashboard...</p>
    </div>

    <div v-else-if="error" class="sg-error-state">
      <p>{{ error }}</p>
      <button class="sg-retry-btn" type="button" @click="reloadDashboard">Retry</button>
    </div>

    <template v-else>
      <div class="sg-hero dashboard-enter dashboard-enter--2">
        <p class="sg-hero-subtitle">Welcome to</p>
        <h2 class="sg-hero-title">{{ acronym }} Dashboard</h2>
        <p class="sg-hero-officer">{{ officerPosition }} {{ officerName }}</p>
      </div>

      <div v-for="section in filteredSections" :key="section.id" class="sg-section dashboard-enter dashboard-enter--3">
        <h2 class="sg-section-title">{{ section.title }}</h2>
        <div class="sg-cards-grid">
          <button v-for="mod in section.modules" :key="mod.id" class="sg-card" @click="handleModuleClick(mod)">
            <div class="sg-card-content">
              <p class="sg-card-label">{{ mod.label }}</p>
            </div>
            <ArrowRight :size="18" class="sg-card-arrow" />
          </button>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { Search, ArrowRight } from 'lucide-vue-next'
import StandardHeader from '@/components/desktop/dashboard/StandardHeader.vue'
import { useSgDashboard } from '@/composables/useSgDashboard.js'
import { getVisibleSections, filterSectionsBySearch } from '@/data/sgModules.js'

const router = useRouter()
const searchQuery = ref('')
const {
  isLoading,
  error,
  reload,
  permissionCodes,
  officerPosition,
  officerName,
  acronym,
  currentUser,
} = useSgDashboard()

const visibleSections = computed(() => getVisibleSections(permissionCodes.value))
const filteredSections = computed(() => filterSectionsBySearch(visibleSections.value, searchQuery.value))

function handleModuleClick(mod) {
  if (mod.route) router.push(mod.route)
}

async function reloadDashboard() {
  if (typeof reload === 'function') {
    await reload()
  }
}
</script>

<style scoped>
.sg-page { 
  display: flex; 
  flex-direction: column; 
  gap: 24px; 
  padding: 24px; 
  max-width: 1120px; 
  margin: 0 auto; 
  width: 100%;
}

.sg-page-title { 
  font-size: 24px; 
  font-weight: 800; 
  color: var(--color-text-primary);
  margin-left: 4px;
}

.search-shell { 
  background: var(--color-surface); 
  border-radius: 16px; 
  padding: 12px 18px; 
  display: flex;
  align-items: center;
  gap: 12px;
  border: 1px solid var(--color-surface-border);
  box-shadow: var(--aura-shadow-soft);
}

.search-input { 
  border: none; 
  outline: none; 
  width: 100%; 
  background: transparent;
  color: var(--color-text-primary);
  font-size: 14px;
}

.sg-loading-state, .sg-error-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 80px 20px;
  text-align: center;
  color: var(--color-text-muted);
}

.sg-retry-btn {
  margin-top: 16px;
  padding: 8px 20px;
  border-radius: 12px;
  border: none;
  background: var(--color-primary);
  color: var(--color-primary-text);
  font-weight: 700;
  cursor: pointer;
}

.sg-hero { 
  background: var(--color-primary); 
  border-radius: 32px; 
  padding: 48px 36px; 
  color: var(--color-primary-text);
  box-shadow: var(--aura-shadow-soft);
  min-height: 260px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  position: relative;
  overflow: hidden;
}

.sg-hero-subtitle { font-size: 16px; font-weight: 600; opacity: 0.85; margin-bottom: 8px; }
.sg-hero-title { font-size: 42px; font-weight: 800; line-height: 1; letter-spacing: -0.04em; margin: 0 0 16px; }
.sg-hero-officer { font-size: 15px; font-weight: 700; opacity: 0.9; }

.sg-section { display: flex; flex-direction: column; gap: 14px; margin-top: 10px; }
.sg-section-title { 
  font-size: 15px; 
  font-weight: 800; 
  color: var(--color-text-primary);
  margin-left: 4px;
}

.sg-cards-grid { 
  display: grid; 
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); 
  gap: 14px; 
}

.sg-card { 
  background: var(--color-surface); 
  border-radius: 18px; 
  padding: 24px; 
  border: 1px solid var(--color-surface-border); 
  text-align: left; 
  display: flex; 
  align-items: center;
  justify-content: space-between;
  cursor: pointer;
  transition: all 0.2s ease;
  box-shadow: var(--aura-shadow-soft);
}

.sg-card:hover {
  border-color: var(--color-primary);
  transform: translateY(-2px);
}

.sg-card-label { font-weight: 700; font-size: 15px; color: var(--color-text-primary); }

.sg-card-arrow {
  color: var(--color-text-muted);
  opacity: 0.4;
  transition: transform 0.2s;
}
.sg-card:hover .sg-card-arrow {
  opacity: 1;
  color: var(--color-primary);
  transform: translateX(4px);
}
</style>
