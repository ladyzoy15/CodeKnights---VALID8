<template>
  <Transition name="onboarding-fade">
    <div v-if="show" class="onboarding-overlay" @click.self="handleCancel">
      <div class="onboarding-modal">
        <header class="onboarding-header">
          <div class="onboarding-icon">
            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 10v6M2 10l10-5 10 5-10 5z"/><path d="M6 12v5c3 3 9 3 12 0v-5"/></svg>
          </div>
          <h2 class="onboarding-title">Almost there!</h2>
          <p class="onboarding-subtitle">Please select your school to finish setting up your account.</p>
        </header>

        <div class="onboarding-body">
          <div v-if="isLoadingSchools" class="onboarding-loading">
            <div class="spinner"></div>
            <span>Loading schools...</span>
          </div>

          <div v-else-if="schools.length === 0" class="onboarding-empty">
            <p>No active schools found. Please contact your administrator.</p>
          </div>

          <div v-else class="onboarding-grid">
            <button 
              v-for="school in schools" 
              :key="school.school_id"
              class="school-card"
              :class="{ 'school-card--selected': selectedSchoolId === school.school_id }"
              @click="selectedSchoolId = school.school_id"
            >
              <div class="school-card__logo">
                <img v-if="school.logo_url" :src="school.logo_url" :alt="school.school_name">
                <div v-else class="school-card__initials">{{ school.school_name.charAt(0) }}</div>
              </div>
              <div class="school-card__info">
                <span class="school-card__name">{{ school.school_name }}</span>
                <span v-if="school.school_code" class="school-card__code">{{ school.school_code }}</span>
              </div>
              <div class="school-card__check">
                <svg v-if="selectedSchoolId === school.school_id" xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"/></svg>
              </div>
            </button>
          </div>
        </div>

        <footer class="onboarding-footer">
          <BaseButton 
            variant="secondary" 
            size="md" 
            :disabled="isSubmitting"
            @click="handleCancel"
          >
            Cancel
          </BaseButton>
          <BaseButton 
            variant="primary" 
            size="md" 
            :loading="isSubmitting"
            :disabled="!selectedSchoolId || isSubmitting"
            @click="handleSubmit"
          >
            Finish Registration
          </BaseButton>
        </footer>
      </div>
    </div>
  </Transition>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getPublicSchools, resolveApiBaseUrl } from '@/services/backendApi.js'
import BaseButton from '@/components/desktop/ui/BaseButton.vue'

const props = defineProps({
  show: Boolean,
  email: String,
  firstName: String,
  lastName: String
})

const emit = defineEmits(['close', 'submit'])

const schools = ref([])
const isLoadingSchools = ref(false)
const isSubmitting = ref(false)
const selectedSchoolId = ref(null)

async function fetchSchools() {
  isLoadingSchools.value = true
  try {
    const apiBaseUrl = resolveApiBaseUrl()
    schools.ref = await getPublicSchools(apiBaseUrl)
    // Actually fixing a typo in my thought: schools.ref -> schools.value
    schools.value = await getPublicSchools(apiBaseUrl)
  } catch (err) {
    console.error('Failed to load schools:', err)
  } finally {
    isLoadingSchools.value = false
  }
}

function handleCancel() {
  if (isSubmitting.value) return
  emit('close')
}

function handleSubmit() {
  if (!selectedSchoolId.value) return
  isSubmitting.value = true
  emit('submit', selectedSchoolId.value)
}

onMounted(() => {
  fetchSchools()
})
</script>

<style scoped>
.onboarding-overlay {
  position: fixed;
  inset: 0;
  z-index: 1000;
  background: rgba(17, 26, 18, 0.4);
  backdrop-filter: blur(8px);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 24px;
}

.onboarding-modal {
  width: 100%;
  max-width: 520px;
  background: white;
  border-radius: 24px;
  box-shadow: 0 40px 80px rgba(0, 0, 0, 0.15);
  overflow: hidden;
  display: flex;
  flex-direction: column;
  border: 1px solid rgba(17, 26, 18, 0.1);
}

.onboarding-header {
  padding: 32px 32px 20px;
  text-align: center;
}

.onboarding-icon {
  width: 56px;
  height: 56px;
  background: #f0f4f0;
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 16px;
  color: #425740;
}

.onboarding-title {
  margin: 0;
  font-size: 24px;
  font-weight: 800;
  color: #111a12;
  letter-spacing: -0.02em;
}

.onboarding-subtitle {
  margin: 8px 0 0;
  font-size: 14px;
  color: #536355;
  line-height: 1.5;
}

.onboarding-body {
  padding: 0 32px;
  max-height: 400px;
  overflow-y: auto;
}

.onboarding-loading, .onboarding-empty {
  padding: 40px 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  color: #536355;
  font-size: 14px;
}

.spinner {
  width: 24px;
  height: 24px;
  border: 3px solid rgba(66, 87, 64, 0.1);
  border-top-color: #425740;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.onboarding-grid {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.school-card {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 12px 16px;
  background: #f9fbf9;
  border: 2px solid transparent;
  border-radius: 16px;
  cursor: pointer;
  transition: all 0.2s ease;
  text-align: left;
  width: 100%;
}

.school-card:hover {
  background: #f1f5f1;
}

.school-card--selected {
  background: #ffffff;
  border-color: #425740;
  box-shadow: 0 4px 12px rgba(66, 87, 64, 0.08);
}

.school-card__logo {
  width: 44px;
  height: 44px;
  background: white;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
  border: 1px solid rgba(17, 26, 18, 0.05);
  flex-shrink: 0;
}

.school-card__logo img {
  width: 100%;
  height: 100%;
  object-fit: contain;
}

.school-card__initials {
  font-size: 18px;
  font-weight: 700;
  color: #425740;
}

.school-card__info {
  flex-grow: 1;
  display: flex;
  flex-direction: column;
}

.school-card__name {
  font-size: 15px;
  font-weight: 700;
  color: #111a12;
}

.school-card__code {
  font-size: 12px;
  color: #536355;
}

.school-card__check {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  background: transparent;
  color: #425740;
  display: flex;
  align-items: center;
  justify-content: center;
}

.onboarding-footer {
  padding: 24px 32px 32px;
  display: grid;
  grid-template-columns: 1fr 1.5fr;
  gap: 12px;
}

/* Transitions */
.onboarding-fade-enter-active,
.onboarding-fade-leave-active {
  transition: opacity 0.3s ease;
}

.onboarding-fade-enter-from,
.onboarding-fade-leave-to {
  opacity: 0;
}

.onboarding-fade-enter-active .onboarding-modal {
  animation: modal-in 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
}

@keyframes modal-in {
  from { transform: scale(0.9) translateY(20px); opacity: 0; }
  to { transform: scale(1) translateY(0); opacity: 1; }
}
</style>
