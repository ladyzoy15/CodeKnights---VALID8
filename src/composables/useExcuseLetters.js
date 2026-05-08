// Import Vue composition utilities and session composable
import { ref } from 'vue';
import { useDashboardSession } from '@/composables/useDashboardSession';
// Import API service functions for excuse letters
import { 
  getExcuseLetters, 
  submitExcuseLetter, 
  reviewExcuseLetter 
} from '@/services/backendApi';

// Composable function for managing excuse letter logic
export function useExcuseLetters() {
  // Get common session data
  const { apiBaseUrl, token, currentUser } = useDashboardSession();
  
  // Reactive state for loading, errors, and the list of letters
  const loading = ref(false);
  const error = ref(null);
  const letters = ref([]);

  // Function to submit a new excuse letter
  const submitLetter = async (eventId, payload) => {
    loading.value = true;
    error.value = null;
    try {
      const response = await submitExcuseLetter(apiBaseUrl.value, token.value, eventId, {
        student_id: currentUser.value?.id,
        ...payload
      });
      return response;
    } catch (err) {
      error.value = err.message || 'Failed to submit excuse letter';
      throw err;
    } finally {
      loading.value = false;
    }
  };

  // Function to fetch excuse letters for the current student
  const fetchStudentLetters = async () => {
    if (!currentUser.value?.id) return [];
    loading.value = true;
    error.value = null;
    try {
      const data = await getExcuseLetters(apiBaseUrl.value, token.value, { 
        scope: 'student',
        student_id: currentUser.value.id 
      });
      letters.value = Array.isArray(data) ? data : [];
      return data;
    } catch (err) {
      error.value = err.message || 'Failed to fetch student excuse letters';
      // Fallback to mock data if API fails in dev
      if (import.meta.env.DEV) {
        letters.value = [
          { id: 1, event_id: 101, eventName: 'General Assembly', status: 'Pending', submittedAt: new Date().toISOString(), reason: 'Medical emergency' },
          { id: 2, event_id: 102, eventName: 'Tech Workshop', status: 'Approved', submittedAt: new Date().toISOString(), reason: 'Family event', reviewerRemarks: 'Approved as requested' }
        ];
      }
      return [];
    } finally {
      loading.value = false;
    }
  };

  // Function to fetch excuse letters for governance/admin review
  const fetchGovernanceLetters = async (unitId) => {
    loading.value = true;
    error.value = null;
    try {
      const data = await getExcuseLetters(apiBaseUrl.value, token.value, { 
        scope: 'governance',
        unit_id: unitId 
      });
      letters.value = Array.isArray(data) ? data : [];
      return data;
    } catch (err) {
      error.value = err.message || 'Failed to fetch governance excuse letters';
      if (import.meta.env.DEV) {
        letters.value = [
          { id: 1, studentName: 'John Doe', eventName: 'General Assembly', status: 'Pending', submittedAt: new Date().toISOString(), reason: 'Medical emergency', course: 'BSIT', yearLevel: '3' },
          { id: 2, studentName: 'Jane Smith', eventName: 'Tech Workshop', status: 'Approved', submittedAt: new Date().toISOString(), reason: 'Family event', course: 'BSCS', yearLevel: '2', reviewerRemarks: 'Valid reason' }
        ];
      }
      return [];
    } finally {
      loading.value = false;
    }
  };

  // Function to approve or reject an excuse letter
  const reviewLetter = async (letterId, status, remarks) => {
    loading.value = true;
    error.value = null;
    try {
      const response = await reviewExcuseLetter(apiBaseUrl.value, token.value, letterId, {
        status,
        remarks,
        reviewer_id: currentUser.value?.id
      });
      
      // Update local state to reflect the review decision
      const index = letters.value.findIndex(l => String(l.id) === String(letterId));
      if (index !== -1) {
        letters.value[index] = { ...letters.value[index], status, reviewerRemarks: remarks };
      }
      
      return response;
    } catch (err) {
      error.value = err.message || 'Failed to review excuse letter';
      throw err;
    } finally {
      loading.value = false;
    }
  };

  // Helper to check if an excuse letter exists for a specific event
  const hasLetterForEvent = (eventId) => {
    return letters.value.find(l => String(l.eventId || l.event_id) === String(eventId));
  };

  // Return all states and methods
  return {
    loading,
    error,
    letters,
    submitLetter,
    fetchStudentLetters,
    fetchGovernanceLetters,
    reviewLetter,
    hasLetterForEvent
  };
}
