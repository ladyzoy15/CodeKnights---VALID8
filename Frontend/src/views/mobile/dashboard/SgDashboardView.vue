<template>
  <div class="sg-page">
    <TopBar :user="currentUser" />

    <div class="mt-1 px-1">
      <h1 class="sg-page-title">Home</h1>
    </div>

    <div class="search-area">
      <div class="search-row">
        <div class="search-wrap">
          <div class="search-shell">
            <div class="search-input-row">
              <input v-model="searchQuery" type="text" placeholder="Search Cards Here..." class="search-input" />
              <Search :size="14" />
            </div>
          </div>
        </div>
      </div>
    </div>

    <template v-if="!isLoading">
      <div class="sg-hero">
        <div class="sg-hero-content">
          <p class="sg-hero-subtitle">Welcome to</p>
          <h2 class="sg-hero-title">{{ acronym }} Dashboard</h2>
          <p class="sg-hero-officer">{{ officerPosition }} {{ officerName }}</p>
        </div>
      </div>

      <div v-for="section in filteredSections" :key="section.id" class="sg-section">
        <h2 class="sg-section-title">{{ section.title }}</h2>
        <div class="sg-cards-grid">
          <button v-for="mod in section.modules" :key="mod.id" class="sg-card" @click="handleModuleClick(mod)">
            <div class="sg-card-content">
              <p class="sg-card-label">{{ mod.label }}</p>
            </div>
            <ArrowRight :size="18" />
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
import TopBar from '@/components/mobile/dashboard/TopBar.vue'
import { useSgDashboard } from '@/composables/useSgDashboard.js'
import { getVisibleSections, filterSectionsBySearch } from '@/data/sgModules.js'

const router = useRouter()
const searchQuery = ref('')
const {
  isLoading,
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
</script>

<style scoped>
.sg-page { display: flex; flex-direction: column; gap: 20px; padding: 20px; }
.sg-page-title { font-size: 24px; font-weight: 800; }
.search-shell { background: white; border-radius: 20px; padding: 10px 15px; box-shadow: 0 4px 12px rgba(0,0,0,0.05); }
.search-input { border: none; outline: none; width: 100%; }
.sg-hero { background: var(--color-primary, #a3e635); border-radius: 20px; padding: 24px; color: black; }
.sg-hero-title { font-size: 28px; font-weight: 800; }
.sg-section-title { font-size: 16px; font-weight: 800; margin-top: 10px; }
.sg-cards-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(140px, 1fr)); gap: 12px; }
.sg-card { background: white; border-radius: 18px; padding: 20px; border: none; text-align: left; display: flex; flex-direction: column; justify-content: space-between; min-height: 120px; box-shadow: 0 4px 10px rgba(0,0,0,0.04); }
.sg-card-label { font-weight: 700; font-size: 14px; }
</style>
