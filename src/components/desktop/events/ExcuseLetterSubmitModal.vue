<template>
  <div v-if="modelValue" class="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm p-4">
    <div class="bg-white dark:bg-gray-800 rounded-xl shadow-xl w-full max-w-lg overflow-hidden flex flex-col max-h-[90vh]">
      <!-- Header -->
      <div class="px-6 py-4 border-b border-gray-100 dark:border-gray-700 flex justify-between items-center bg-gray-50 dark:bg-gray-800/50">
        <h3 class="text-lg font-bold text-gray-900 dark:text-white">Submit Excuse Letter</h3>
        <button @click="close" class="text-gray-400 hover:text-gray-600 dark:hover:text-gray-200 transition-colors">
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path></svg>
        </button>
      </div>

      <!-- Body -->
      <div class="p-6 overflow-y-auto flex-1 custom-scrollbar">
        <!-- Read Only Info -->
        <div class="bg-gray-50 dark:bg-gray-700/30 rounded-lg p-4 mb-6 space-y-3 border border-gray-100 dark:border-gray-700">
          <div class="grid grid-cols-2 gap-4 text-sm">
            <div>
              <span class="block text-gray-500 dark:text-gray-400 text-xs uppercase tracking-wider mb-1">Student Name</span>
              <span class="font-medium text-gray-900 dark:text-gray-100">{{ auth.user?.first_name }} {{ auth.user?.last_name }}</span>
            </div>
            <div>
              <span class="block text-gray-500 dark:text-gray-400 text-xs uppercase tracking-wider mb-1">Event</span>
              <span class="font-medium text-gray-900 dark:text-gray-100">{{ event?.name || 'Unknown Event' }}</span>
            </div>
            <div>
              <span class="block text-gray-500 dark:text-gray-400 text-xs uppercase tracking-wider mb-1">Date</span>
              <span class="font-medium text-gray-900 dark:text-gray-100">{{ formatDate(event?.date) }}</span>
            </div>
          </div>
        </div>

        <form @submit.prevent="handleSubmit" class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Reason for Absence <span class="text-red-500">*</span>
            </label>
            <textarea
              v-model="form.reason"
              required
              rows="4"
              class="w-full rounded-lg border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white shadow-sm focus:border-primary-500 focus:ring-primary-500 resize-none"
              placeholder="Please explain why you cannot attend this event..."
            ></textarea>
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Supporting Document (Optional)
            </label>
            <div class="mt-1 flex justify-center px-6 pt-5 pb-6 border-2 border-gray-300 dark:border-gray-600 border-dashed rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700/50 transition-colors cursor-pointer" @click="$refs.fileInput.click()">
              <div class="space-y-1 text-center">
                <svg class="mx-auto h-12 w-12 text-gray-400" stroke="currentColor" fill="none" viewBox="0 0 48 48" aria-hidden="true">
                  <path d="M28 8H12a4 4 0 00-4 4v20m32-12v8m0 0v8a4 4 0 01-4 4H12a4 4 0 01-4-4v-4m32-4l-3.172-3.172a4 4 0 00-5.656 0L28 28M8 32l9.172-9.172a4 4 0 015.656 0L28 28m0 0l4 4m4-24h8m-4-4v8m-12 4h.02" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" />
                </svg>
                <div class="flex text-sm text-gray-600 dark:text-gray-400 justify-center">
                  <span class="relative cursor-pointer rounded-md font-medium text-primary-600 hover:text-primary-500 focus-within:outline-none focus-within:ring-2 focus-within:ring-offset-2 focus-within:ring-primary-500">
                    <span>Upload a file</span>
                    <input ref="fileInput" id="file-upload" name="file-upload" type="file" class="sr-only" @change="handleFileChange">
                  </span>
                  <p class="pl-1">or drag and drop</p>
                </div>
                <p class="text-xs text-gray-500 dark:text-gray-400">
                  PNG, JPG, PDF up to 10MB
                </p>
                <p v-if="selectedFileName" class="text-sm font-medium text-primary-600 mt-2 truncate max-w-xs mx-auto">
                  Selected: {{ selectedFileName }}
                </p>
              </div>
            </div>
          </div>
        </form>
      </div>

      <!-- Footer -->
      <div class="px-6 py-4 border-t border-gray-100 dark:border-gray-700 flex justify-end gap-3 bg-gray-50 dark:bg-gray-800/50">
        <button
          type="button"
          @click="close"
          class="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 dark:bg-gray-800 dark:text-gray-300 dark:border-gray-600 dark:hover:bg-gray-700"
        >
          Cancel
        </button>
        <button
          @click="handleSubmit"
          :disabled="isSubmitting || !form.reason.trim()"
          class="px-4 py-2 text-sm font-medium text-white bg-primary-600 border border-transparent rounded-lg hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 disabled:opacity-50 disabled:cursor-not-allowed flex items-center shadow-sm"
        >
          <svg v-if="isSubmitting" class="animate-spin -ml-1 mr-2 h-4 w-4 text-white" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
          Submit Letter
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue';
import { useAuth } from '@/composables/useAuth';
import { useExcuseLetters } from '@/composables/useExcuseLetters';

const props = defineProps({
  modelValue: {
    type: Boolean,
    required: true
  },
  event: {
    type: Object,
    default: () => ({})
  }
});

const emit = defineEmits(['update:modelValue', 'submitted']);

const auth = useAuth();
const excuseLetters = useExcuseLetters();

const form = reactive({
  reason: ''
});

const selectedFile = ref(null);
const selectedFileName = ref('');
const fileInput = ref(null);
const isSubmitting = ref(false);

const close = () => {
  form.reason = '';
  selectedFile.value = null;
  selectedFileName.value = '';
  emit('update:modelValue', false);
};

const handleFileChange = (e) => {
  const file = e.target.files[0];
  if (file) {
    selectedFile.value = file;
    selectedFileName.value = file.name;
  }
};

const handleSubmit = async () => {
  if (!form.reason.trim()) return;
  
  isSubmitting.value = true;
  try {
    const payload = {
      reason: form.reason,
      attachmentUrl: selectedFile.value ? `mock-url-${selectedFileName.value}` : null
    };
    
    await excuseLetters.submitLetter(props.event.id, payload);
    emit('submitted', props.event.id);
    close();
  } catch (error) {
    console.error('Error submitting excuse letter:', error);
    alert('Failed to submit excuse letter. Please try again.');
  } finally {
    isSubmitting.value = false;
  }
};

const formatDate = (dateString) => {
  if (!dateString) return 'TBA';
  try {
    const options = { year: 'numeric', month: 'short', day: 'numeric' };
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
