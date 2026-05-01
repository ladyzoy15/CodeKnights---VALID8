<template>
  <div v-if="modelValue" class="fixed inset-0 z-50 flex items-center justify-center bg-black/40 backdrop-blur-sm p-4 transition-opacity">
    <div class="rounded-2xl shadow-xl w-full max-w-xl overflow-hidden flex flex-col max-h-[90vh] transition-transform scale-100" style="background-color: var(--color-surface); border: 1px solid var(--color-surface-border);">
      <!-- Header -->
      <div class="px-6 py-5 flex justify-between items-center" style="border-bottom: 1px solid var(--color-surface-border); background-color: color-mix(in srgb, var(--color-surface) 90%, transparent);">
        <h3 class="text-xl font-bold tracking-tight" style="color: var(--color-primary);">Submit Excuse</h3>
        <button @click="close" class="p-2 rounded-lg transition-colors hover:opacity-70" style="color: var(--color-surface-text); background-color: transparent;">
          <svg class="w-5 h-5" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12"></path></svg>
        </button>
      </div>

      <!-- Body -->
      <div class="p-6 overflow-y-auto flex-1 custom-scrollbar">
        <!-- Read Only Info -->
        <div class="rounded-xl p-5 mb-6 shadow-sm flex flex-col sm:flex-row sm:justify-between sm:items-center gap-4" style="background-color: color-mix(in srgb, var(--color-bg) 50%, transparent); border: 1px solid var(--color-surface-border);">
          <div>
            <span class="block text-[11px] font-bold uppercase tracking-wider opacity-60 mb-0.5" style="color: var(--color-surface-text);">Student</span>
            <span class="font-bold text-sm" style="color: var(--color-surface-text);">{{ auth.user?.first_name }} {{ auth.user?.last_name }}</span>
          </div>
          <div class="hidden sm:block w-px h-8" style="background-color: var(--color-surface-border);"></div>
          <div>
            <span class="block text-[11px] font-bold uppercase tracking-wider opacity-60 mb-0.5" style="color: var(--color-surface-text);">Event</span>
            <span class="font-bold text-sm" style="color: var(--color-primary);">{{ event?.name || 'Unknown Event' }}</span>
          </div>
          <div class="hidden sm:block w-px h-8" style="background-color: var(--color-surface-border);"></div>
          <div>
            <span class="block text-[11px] font-bold uppercase tracking-wider opacity-60 mb-0.5" style="color: var(--color-surface-text);">Date</span>
            <span class="font-bold text-sm" style="color: var(--color-surface-text);">{{ formatDate(event?.date) }}</span>
          </div>
        </div>

        <form @submit.prevent="handleSubmit" class="space-y-6">
          <div>
            <label class="block text-xs font-bold uppercase tracking-wider opacity-70 mb-2" style="color: var(--color-surface-text);">
              Reason for Absence <span class="text-red-500">*</span>
            </label>
            <textarea
              v-model="form.reason"
              required
              rows="4"
              class="w-full rounded-xl p-3 text-sm shadow-sm focus:outline-none focus:ring-2 focus:border-transparent transition-all resize-none"
              style="background-color: var(--color-bg); border: 1px solid var(--color-surface-border); color: var(--color-surface-text); outline-color: var(--color-primary);"
              placeholder="Please explain why you cannot attend this event..."
            ></textarea>
          </div>

          <div>
            <label class="block text-xs font-bold uppercase tracking-wider opacity-70 mb-2" style="color: var(--color-surface-text);">
              Supporting Document (Optional)
            </label>
            <div class="mt-2 flex justify-center px-6 pt-5 pb-6 border-2 border-dashed rounded-xl transition-colors cursor-pointer hover:bg-opacity-50" 
                 style="border-color: color-mix(in srgb, var(--color-surface-border) 80%, var(--color-primary)); background-color: var(--color-bg);"
                 @click="$refs.fileInput.click()">
              <div class="space-y-1 text-center">
                <div class="mx-auto w-12 h-12 rounded-full flex items-center justify-center mb-2 shadow-sm" style="background-color: color-mix(in srgb, var(--color-primary) 10%, transparent); color: var(--color-primary);">
                  <svg class="h-6 w-6" stroke="currentColor" fill="none" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12"></path>
                  </svg>
                </div>
                <div class="flex text-sm justify-center">
                  <span class="relative font-bold hover:underline transition-all cursor-pointer" style="color: var(--color-primary);">
                    <span>Upload a file</span>
                    <input ref="fileInput" id="file-upload" name="file-upload" type="file" class="sr-only" @change="handleFileChange">
                  </span>
                  <p class="pl-1 font-medium opacity-70" style="color: var(--color-surface-text);">or drag and drop</p>
                </div>
                <p class="text-xs opacity-50" style="color: var(--color-surface-text);">
                  PNG, JPG, PDF up to 10MB
                </p>
                <div v-if="selectedFileName" class="mt-3 inline-flex items-center px-3 py-1 rounded-md text-xs font-bold truncate max-w-[200px]" style="background-color: color-mix(in srgb, var(--color-primary) 10%, transparent); color: var(--color-primary);">
                  <svg class="w-3.5 h-3.5 mr-1.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.172 7l-6.586 6.586a2 2 0 102.828 2.828l6.414-6.586a4 4 0 00-5.656-5.656l-6.415 6.585a6 6 0 108.486 8.486L20.5 13"></path></svg>
                  <span class="truncate">{{ selectedFileName }}</span>
                </div>
              </div>
            </div>
          </div>
        </form>
      </div>

      <!-- Footer -->
      <div class="px-6 py-4 flex justify-end gap-3" style="border-top: 1px solid var(--color-surface-border); background-color: color-mix(in srgb, var(--color-surface) 90%, transparent);">
        <button
          type="button"
          @click="close"
          class="px-5 py-2 text-sm font-semibold rounded-lg transition-colors hover:bg-gray-100 dark:hover:bg-gray-800"
          style="color: var(--color-surface-text); background-color: transparent; border: 1px solid var(--color-surface-border);"
        >
          Cancel
        </button>
        <button
          @click="handleSubmit"
          :disabled="isSubmitting || !form.reason.trim()"
          class="px-5 py-2 text-sm font-semibold rounded-lg transition-colors disabled:opacity-50 flex items-center shadow-sm hover:opacity-90"
          style="background-color: var(--color-primary); color: #ffffff;"
        >
          <svg v-if="isSubmitting" class="animate-spin -ml-1 mr-2 h-4 w-4 text-white" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
          {{ isSubmitting ? 'Submitting...' : 'Submit Letter' }}
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
