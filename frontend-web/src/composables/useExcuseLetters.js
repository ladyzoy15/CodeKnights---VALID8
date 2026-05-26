import { ref } from 'vue';
import { useDashboardSession } from '@/composables/useDashboardSession';
import { 
  getExcuseLetters, 
  submitExcuseLetter, 
  reviewExcuseLetter 
} from '@/services/backendApi';

export function useExcuseLetters() {
  const { apiBaseUrl, token, currentUser } = useDashboardSession();
  
  const loading = ref(false);
  const error = ref(null);
  const letters = ref([]);

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
      return [];
    } finally {
      loading.value = false;
    }
  };

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
      return [];
    } finally {
      loading.value = false;
    }
  };

  const reviewLetter = async (letterId, status, remarks) => {
    loading.value = true;
    error.value = null;
    try {
      const response = await reviewExcuseLetter(apiBaseUrl.value, token.value, letterId, {
        status,
        remarks,
        reviewer_id: currentUser.value?.id
      });
      
      // Update local state
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

  const hasLetterForEvent = (eventId) => {
    return letters.value.find(l => String(l.eventId || l.event_id) === String(eventId));
  };

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
