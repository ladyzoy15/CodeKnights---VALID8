import { defineStore } from 'pinia'
import { ref } from 'vue'
import { useSessionStore } from '@/stores/session.js'
import * as api from '@/services/backendApi.js'

export const useExcuseLetterStore = defineStore('excuseLetter', () => {
  const sessionStore = useSessionStore()

  // State
  const myLetters = ref([])
  const currentEventStatus = ref(null) // for event-specific badge/details
  const submissions = ref([]) // officer submissions list
  const dashboardMetrics = ref({ total: 0, pending: 0, approved: 0, rejected: 0 })
  const loading = ref(false)
  const error = ref(null)

  // Actions
  async function fetchMyLetters() {
    loading.value = true
    error.value = null
    try {
      const res = await api.getMyExcuseLetters(sessionStore.apiBaseUrl, sessionStore.token)
      myLetters.value = res
      return res
    } catch (err) {
      error.value = err.message || 'Failed to fetch excuse letters.'
      throw err
    } finally {
      loading.value = false
    }
  }

  async function fetchStatusForEvent(eventId) {
    loading.value = true
    error.value = null
    try {
      const res = await api.getMyExcuseLetterStatusForEvent(sessionStore.apiBaseUrl, sessionStore.token, eventId)
      currentEventStatus.value = res
      return res
    } catch (err) {
      error.value = err.message || 'Failed to fetch status for event.'
      throw err
    } finally {
      loading.value = false
    }
  }

  async function submitLetter(eventId, reason, attachmentPath) {
    loading.value = true
    error.value = null
    try {
      const res = await api.submitExcuseLetter(sessionStore.apiBaseUrl, sessionStore.token, eventId, {
        reason,
        attachment_path: attachmentPath,
      })
      // Refresh my letters and status for this event
      await fetchMyLetters()
      await fetchStatusForEvent(eventId)
      return res
    } catch (err) {
      error.value = err.message || 'Failed to submit excuse letter.'
      throw err
    } finally {
      loading.value = false
    }
  }

  async function fetchSubmissionsForEvent(eventId, params = {}) {
    loading.value = true
    error.value = null
    try {
      const res = await api.listExcuseLettersForEvent(sessionStore.apiBaseUrl, sessionStore.token, eventId, params)
      submissions.value = res
      return res
    } catch (err) {
      error.value = err.message || 'Failed to fetch event submissions.'
      throw err
    } finally {
      loading.value = false
    }
  }

  async function fetchAllSubmissions(params = {}) {
    loading.value = true
    error.value = null
    try {
      const res = await api.listAllExcuseLetters(sessionStore.apiBaseUrl, sessionStore.token, params)
      submissions.value = res
      return res
    } catch (err) {
      error.value = err.message || 'Failed to fetch excuse letter submissions.'
      throw err
    } finally {
      loading.value = false
    }
  }

  async function approveLetter(letterId, remarks) {
    loading.value = true
    error.value = null
    try {
      const res = await api.approveExcuseLetter(sessionStore.apiBaseUrl, sessionStore.token, letterId, { remarks })
      // Update local item in list if exists
      const idx = submissions.value.findIndex(s => s.id === letterId)
      if (idx !== -1) {
        submissions.value[idx] = res
      }
      // Refresh metrics
      await fetchDashboardMetrics()
      return res
    } catch (err) {
      error.value = err.message || 'Failed to approve excuse letter.'
      throw err
    } finally {
      loading.value = false
    }
  }

  async function rejectLetter(letterId, remarks) {
    loading.value = true
    error.value = null
    try {
      const res = await api.rejectExcuseLetter(sessionStore.apiBaseUrl, sessionStore.token, letterId, { remarks })
      // Update local item in list if exists
      const idx = submissions.value.findIndex(s => s.id === letterId)
      if (idx !== -1) {
        submissions.value[idx] = res
      }
      // Refresh metrics
      await fetchDashboardMetrics()
      return res
    } catch (err) {
      error.value = err.message || 'Failed to reject excuse letter.'
      throw err
    } finally {
      loading.value = false
    }
  }

  async function fetchDashboardMetrics() {
    try {
      const res = await api.getExcuseLetterDashboard(sessionStore.apiBaseUrl, sessionStore.token)
      dashboardMetrics.value = res
      return res
    } catch (err) {
      console.error('Failed to load excuse letter dashboard metrics:', err)
    }
  }

  async function uploadAttachment(file) {
    loading.value = true
    error.value = null
    try {
      const res = await api.uploadExcuseLetterAttachment(sessionStore.apiBaseUrl, sessionStore.token, file)
      return res.attachment_path
    } catch (err) {
      error.value = err.message || 'Attachment upload failed.'
      throw err
    } finally {
      loading.value = false
    }
  }

  return {
    myLetters,
    currentEventStatus,
    submissions,
    dashboardMetrics,
    loading,
    error,
    fetchMyLetters,
    fetchStatusForEvent,
    submitLetter,
    fetchSubmissionsForEvent,
    fetchAllSubmissions,
    approveLetter,
    rejectLetter,
    fetchDashboardMetrics,
    uploadAttachment,
  }
})
