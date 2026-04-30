<template>
  <div v-if="modelValue" class="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm p-4">
    <div class="bg-white dark:bg-gray-800 rounded-xl shadow-xl w-full max-w-lg overflow-hidden flex flex-col max-h-[90vh]">
      <!-- Header -->
      <div class="px-6 py-4 border-b border-gray-100 dark:border-gray-700 flex justify-between items-center bg-gray-50 dark:bg-gray-800/50">
        <h3 class="text-lg font-bold text-gray-900 dark:text-white">Review Excuse Letter</h3>
        <button @click="close" class="text-gray-400 hover:text-gray-600 dark:hover:text-gray-200 transition-colors">
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path></svg>
        </button>
      </div>

      <!-- Body -->
      <div class="p-6 overflow-y-auto flex-1 custom-scrollbar space-y-6">
        
        <!-- Student Info -->
        <div class="flex items-start space-x-4">
          <div class="h-12 w-12 rounded-full bg-primary-100 dark:bg-primary-900/30 flex items-center justify-center text-primary-600 dark:text-primary-400 text-xl font-bold">
            {{ letter?.studentName?.charAt(0) || 'S' }}
          </div>
          <div>
            <h4 class="text-base font-semibold text-gray-900 dark:text-white">{{ letter?.studentName || 'Student Name' }}</h4>
            <p class="text-sm text-gray-500 dark:text-gray-400">{{ letter?.course || 'Course' }} • Year {{ letter?.yearLevel || 'Level' }}</p>
            <p class="text-xs text-gray-400 dark:text-gray-500 mt-1">Submitted: {{ formatDate(letter?.submittedAt) }}</p>
          </div>
        </div>

        <hr class="border-gray-100 dark:border-gray-700" />

        <!-- Event Info -->
        <div>
          <h5 class="text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Event details</h5>
          <p class="text-base text-gray-900 dark:text-gray-100">{{ letter?.eventName || 'Unknown Event' }}</p>
        </div>

        <!-- Reason -->
        <div>
          <h5 class="text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Reason for Absence</h5>
          <div class="bg-gray-50 dark:bg-gray-700/50 p-4 rounded-lg text-sm text-gray-800 dark:text-gray-200 border border-gray-100 dark:border-gray-600">
            {{ letter?.reason || 'No reason provided.' }}
          </div>
        </div>

        <!-- Attachment -->
        <div v-if="letter?.attachmentUrl">
          <h5 class="text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Attachment</h5>
          <a href="#" class="inline-flex items-center space-x-2 text-sm text-primary-600 hover:text-primary-700 dark:text-primary-400 dark:hover:text-primary-300 bg-primary-50 dark:bg-primary-900/20 px-3 py-2 rounded-lg border border-primary-100 dark:border-primary-800/50 transition-colors">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.172 7l-6.586 6.586a2 2 0 102.828 2.828l6.414-6.586a4 4 0 00-5.656-5.656l-6.415 6.585a6 6 0 108.486 8.486L20.5 13"></path></svg>
            <span>View Document</span>
          </a>
        </div>

        <hr class="border-gray-100 dark:border-gray-700" />

        <!-- Review Form -->
        <div v-if="letter?.status === 'Pending' && props.canReview" class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Remarks (Optional for Approve, Required for Reject)
            </label>
            <textarea
              v-model="remarks"
              rows="3"
              class="w-full rounded-lg border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white shadow-sm focus:border-primary-500 focus:ring-primary-500 resize-none"
              placeholder="Add notes about your decision..."
            ></textarea>
          </div>
        </div>
        
        <div v-else class="bg-gray-50 dark:bg-gray-700/30 p-4 rounded-lg border border-gray-100 dark:border-gray-600">
          <div class="flex items-center space-x-2 mb-2">
            <span class="text-sm font-medium text-gray-700 dark:text-gray-300">Status:</span>
            <span :class="{
              'px-2 py-0.5 rounded text-xs font-medium': true,
              'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400': letter?.status === 'Approved',
              'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-400': letter?.status === 'Rejected'
            }">{{ letter?.status }}</span>
          </div>
          <div v-if="letter?.reviewerRemarks">
            <span class="text-xs text-gray-500 dark:text-gray-400 block mb-1">Remarks:</span>
            <p class="text-sm text-gray-800 dark:text-gray-200">{{ letter?.reviewerRemarks }}</p>
          </div>
        </div>

      </div>

      <!-- Footer -->
      <div v-if="letter?.status === 'Pending' && props.canReview" class="px-6 py-4 border-t border-gray-100 dark:border-gray-700 flex justify-between items-center bg-gray-50 dark:bg-gray-800/50">
        <button
          type="button"
          @click="close"
          class="text-sm font-medium text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-300 transition-colors"
        >
          Cancel
        </button>
        <div class="flex space-x-3">
          <button
            @click="handleReview('Rejected')"
            :disabled="isSubmitting || !remarks.trim()"
            class="px-4 py-2 text-sm font-medium text-red-700 bg-red-50 border border-red-200 rounded-lg hover:bg-red-100 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500 disabled:opacity-50 disabled:cursor-not-allowed dark:bg-red-900/20 dark:text-red-400 dark:border-red-800/50 dark:hover:bg-red-900/40 transition-colors"
          >
            Reject
          </button>
          <button
            @click="handleReview('Approved')"
            :disabled="isSubmitting"
            class="px-4 py-2 text-sm font-medium text-white bg-green-600 border border-transparent rounded-lg hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500 disabled:opacity-50 disabled:cursor-not-allowed flex items-center shadow-sm transition-colors"
          >
            <svg v-if="isSubmitting" class="animate-spin -ml-1 mr-2 h-4 w-4 text-white" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            Approve
          </button>
        </div>
      </div>
      <div v-else-if="letter?.status === 'Pending' && !props.canReview" class="px-6 py-4 border-t border-gray-100 dark:border-gray-700 bg-yellow-50 dark:bg-yellow-900/10 p-4">
        <p class="text-xs text-yellow-700 dark:text-yellow-400 text-center font-medium">
          You do not have permission to review excuse letters.
        </p>
      </div>
      <div v-else class="px-6 py-4 border-t border-gray-100 dark:border-gray-700 flex justify-end bg-gray-50 dark:bg-gray-800/50">
        <button
          type="button"
          @click="close"
          class="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 dark:bg-gray-800 dark:text-gray-300 dark:border-gray-600 dark:hover:bg-gray-700"
        >
          Close
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useExcuseLetters } from '@/composables/useExcuseLetters';

const props = defineProps({
  modelValue: {
    type: Boolean,
    required: true
  },
  letter: {
    type: Object,
    default: null
  },
  canReview: {
    type: Boolean,
    default: false
  }
});

const emit = defineEmits(['update:modelValue', 'reviewed']);

const excuseLetters = useExcuseLetters();
const remarks = ref('');
const isSubmitting = ref(false);

const close = () => {
  remarks.value = '';
  emit('update:modelValue', false);
};

const handleReview = async (status) => {
  if (status === 'Rejected' && !remarks.value.trim()) return;
  
  isSubmitting.value = true;
  try {
    await excuseLetters.reviewLetter(props.letter.id, status, remarks.value);
    emit('reviewed');
    close();
  } catch (error) {
    console.error(`Error ${status.toLowerCase()} excuse letter:`, error);
    alert(`Failed to ${status.toLowerCase()} letter. Please try again.`);
  } finally {
    isSubmitting.value = false;
  }
};

const formatDate = (dateString) => {
  if (!dateString) return '';
  try {
    const options = { year: 'numeric', month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' };
    return new Date(dateString).toLocaleDateString(undefined, options);
  } catch (e) {
    return dateString;
  }
};
</script>

<style scoped>
.custom-scrollbar::-webkit-scrollbar {
  width: 6px;
}
.custom-scrollbar::-webkit-scrollbar-track {
  background: transparent;
}
.custom-scrollbar::-webkit-scrollbar-thumb {
  background-color: rgba(156, 163, 175, 0.5);
  border-radius: 20px;
}
</style>
