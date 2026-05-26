<template>
  <div v-if="modelValue" class="fixed inset-0 z-50 flex items-center justify-center bg-black/40 backdrop-blur-md p-4 transition-opacity">
    <div class="rounded-[2rem] shadow-2xl w-full max-w-lg overflow-hidden flex flex-col max-h-[90vh] transition-transform scale-100" style="background-color: var(--color-surface); border: 1px solid var(--color-surface-border);">
      <!-- Header -->
      <div class="px-8 py-6 flex justify-between items-center" style="border-bottom: 1px solid var(--color-surface-border); background-color: color-mix(in srgb, var(--color-surface) 90%, transparent);">
        <h3 class="text-2xl font-black tracking-tight" style="color: var(--color-primary);">Review Letter</h3>
        <button @click="close" class="p-2.5 rounded-full transition-transform active:scale-90 hover:opacity-70" style="color: var(--color-surface-text); background-color: transparent;">
          <svg class="w-5 h-5" fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12"></path></svg>
        </button>
      </div>

      <!-- Body -->
      <div class="p-8 overflow-y-auto flex-1 custom-scrollbar space-y-8">
        
        <!-- Student Info -->
        <div class="flex items-center space-x-5">
          <div class="h-16 w-16 rounded-[1.5rem] flex items-center justify-center text-2xl font-black flex-shrink-0 shadow-sm" style="color: var(--color-primary); background-color: color-mix(in srgb, var(--color-primary) 15%, transparent);">
            {{ letter?.studentName?.charAt(0) || 'S' }}
          </div>
          <div>
            <h4 class="text-lg font-bold leading-tight mb-1" style="color: var(--color-surface-text);">{{ letter?.studentName || 'Student Name' }}</h4>
            <p class="text-xs font-bold opacity-60 uppercase tracking-wider mb-1" style="color: var(--color-surface-text);">{{ letter?.course || 'Course' }} ΓÇó Year {{ letter?.yearLevel || 'Level' }}</p>
            <p class="text-[10px] font-black uppercase tracking-widest opacity-40" style="color: var(--color-surface-text);">Submitted: {{ formatDate(letter?.submittedAt) }}</p>
          </div>
        </div>

        <div style="border-top: 1px dashed var(--color-surface-border);"></div>

        <!-- Event Info -->
        <div>
          <h5 class="text-xs font-black uppercase tracking-widest opacity-50 mb-2" style="color: var(--color-surface-text);">Event details</h5>
          <p class="text-lg font-bold leading-tight" style="color: var(--color-primary);">{{ letter?.eventName || 'Unknown Event' }}</p>
        </div>

        <!-- Reason -->
        <div>
          <h5 class="text-xs font-black uppercase tracking-widest opacity-50 mb-2" style="color: var(--color-surface-text);">Reason for Absence</h5>
          <div class="p-5 rounded-2xl text-sm font-medium leading-relaxed italic" style="color: var(--color-surface-text); background-color: color-mix(in srgb, var(--color-bg) 50%, transparent); border: 1px solid var(--color-surface-border);">
            "{{ letter?.reason || 'No reason provided.' }}"
          </div>
        </div>

        <!-- Attachment -->
        <div v-if="letter?.attachmentUrl">
          <h5 class="text-xs font-black uppercase tracking-widest opacity-50 mb-2" style="color: var(--color-surface-text);">Attachment</h5>
          <a :href="letter?.attachmentUrl" target="_blank" rel="noopener noreferrer" class="inline-flex items-center space-x-2 text-xs font-black uppercase tracking-wider px-4 py-2.5 rounded-xl transition-all active:scale-95 shadow-sm" style="color: var(--color-primary); background-color: color-mix(in srgb, var(--color-primary) 15%, transparent); border: 1px solid color-mix(in srgb, var(--color-primary) 30%, transparent);">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M15.172 7l-6.586 6.586a2 2 0 102.828 2.828l6.414-6.586a4 4 0 00-5.656-5.656l-6.415 6.585a6 6 0 108.486 8.486L20.5 13"></path></svg>
            <span>View Document</span>
          </a>
        </div>

        <div style="border-top: 1px dashed var(--color-surface-border);"></div>

        <!-- Review Form -->
        <div v-if="letter?.status === 'Pending' && props.canReview" class="space-y-4">
          <div>
            <label class="block text-xs font-black uppercase tracking-widest opacity-70 mb-2" style="color: var(--color-surface-text);">
              Remarks (Optional for Approve, Required for Reject)
            </label>
            <textarea
              v-model="remarks"
              rows="3"
              class="w-full rounded-2xl p-4 text-sm font-medium shadow-sm focus:outline-none focus:ring-2 focus:border-transparent transition-all resize-none"
              style="background-color: var(--color-bg); border: 1px solid var(--color-surface-border); color: var(--color-surface-text); outline-color: var(--color-primary);"
              placeholder="Add notes about your decision..."
            ></textarea>
          </div>
        </div>
        
        <div v-else class="p-5 rounded-2xl shadow-inner space-y-4" style="background-color: color-mix(in srgb, var(--color-bg) 50%, transparent); border: 1px solid var(--color-surface-border);">
          <div class="flex items-center space-x-3">
            <span class="text-xs font-black uppercase tracking-widest opacity-60" style="color: var(--color-surface-text);">Status:</span>
            <span class="px-3 py-1.5 rounded-xl text-[10px] font-black uppercase tracking-widest shadow-sm inline-block"
                  :style="{
                    backgroundColor: letter?.status === 'Approved' ? 'color-mix(in srgb, #10B981 15%, transparent)' : (letter?.status === 'Rejected' ? 'color-mix(in srgb, #EF4444 15%, transparent)' : 'color-mix(in srgb, #F59E0B 15%, transparent)'),
                    color: letter?.status === 'Approved' ? '#059669' : (letter?.status === 'Rejected' ? '#DC2626' : '#D97706')
                  }">
              {{ letter?.status }}
            </span>
          </div>
          <div v-if="letter?.reviewerRemarks">
            <span class="block text-xs font-black uppercase tracking-widest opacity-60 mb-2" style="color: var(--color-surface-text);">Remarks:</span>
            <p class="text-sm font-medium leading-relaxed p-3 rounded-xl" style="background-color: var(--color-surface); color: var(--color-surface-text); border: 1px solid var(--color-surface-border);">
              {{ letter?.reviewerRemarks }}
            </p>
          </div>
        </div>

      </div>

      <!-- Footer -->
      <div v-if="letter?.status === 'Pending' && props.canReview" class="px-8 py-5 flex justify-between items-center" style="border-top: 1px solid var(--color-surface-border); background-color: color-mix(in srgb, var(--color-surface) 90%, transparent);">
        <button
          type="button"
          @click="close"
          class="px-5 py-2.5 text-xs font-black uppercase tracking-wider rounded-xl transition-all hover:bg-gray-100 dark:hover:bg-gray-800"
          style="color: var(--color-surface-text); background-color: transparent; border: 1px solid var(--color-surface-border);"
        >
          Cancel
        </button>
        <div class="flex space-x-3">
          <button
            @click="handleReview('Rejected')"
            :disabled="isSubmitting || !remarks.trim()"
            class="px-5 py-2.5 text-xs font-black uppercase tracking-wider rounded-xl transition-all active:scale-95 disabled:opacity-50 disabled:active:scale-100 flex items-center shadow-sm"
            style="color: #DC2626; background-color: color-mix(in srgb, #EF4444 15%, transparent); border: 1px solid color-mix(in srgb, #EF4444 30%, transparent);"
          >
            Reject
          </button>
          <button
            @click="handleReview('Approved')"
            :disabled="isSubmitting"
            class="px-6 py-2.5 text-xs font-black uppercase tracking-wider rounded-xl transition-all active:scale-95 disabled:opacity-50 disabled:active:scale-100 flex items-center shadow-md"
            style="background-color: #10B981; color: #ffffff;"
          >
            <svg v-if="isSubmitting" class="animate-spin -ml-1 mr-2.5 h-4 w-4 text-white" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            Approve
          </button>
        </div>
      </div>
      <div v-else-if="letter?.status === 'Pending' && !props.canReview" class="px-8 py-5 text-center" style="border-top: 1px solid var(--color-surface-border); background-color: color-mix(in srgb, #F59E0B 10%, transparent);">
        <p class="text-xs font-black uppercase tracking-widest" style="color: #D97706;">
          You do not have permission to review excuse letters.
        </p>
      </div>
      <div v-else class="px-8 py-5 flex justify-end" style="border-top: 1px solid var(--color-surface-border); background-color: color-mix(in srgb, var(--color-surface) 90%, transparent);">
        <button
          type="button"
          @click="close"
          class="px-6 py-2.5 text-sm font-black uppercase tracking-wider rounded-xl transition-all active:scale-95 shadow-sm hover:bg-gray-100 dark:hover:bg-gray-800"
          style="color: var(--color-surface-text); background-color: transparent; border: 1px solid var(--color-surface-border);"
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
