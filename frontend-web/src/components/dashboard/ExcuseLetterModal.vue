<template>
  <Teleport to="body">
    <Transition name="modal-fade">
      <div 
        v-if="isOpen" 
        class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-md"
        @click.self="close"
      >
        <div 
          class="w-full max-w-lg max-h-[85vh] flex flex-col rounded-[32px] shadow-2xl overflow-hidden border border-white/10 glass-card"
        >
          <!-- Header -->
          <div class="p-6 border-b border-white/5 flex justify-between items-center shrink-0">
            <div>
              <h2 class="text-xl font-bold text-white">
                Submit Excuse Letter
              </h2>
              <p class="text-[12px] text-white/50 mt-0.5">
                {{ event?.name }}
              </p>
            </div>
            <button 
              @click="close"
              class="p-2 rounded-full hover:bg-white/10 transition-colors text-white/50 hover:text-white"
            >
              <XIcon class="w-5 h-5" />
            </button>
          </div>

          <!-- Body -->
          <div class="p-6 overflow-y-auto flex-1 font-[Manrope] text-[14px] leading-relaxed space-y-5 text-white/80 custom-scrollbar">
            <!-- Alert Banner -->
            <div v-if="localError" class="p-3.5 rounded-2xl bg-red-500/15 border border-red-500/30 text-red-400 text-xs flex items-start gap-2.5">
              <AlertCircleIcon class="w-4 h-4 shrink-0 mt-0.5" />
              <span>{{ localError }}</span>
            </div>

            <!-- Reason Area -->
            <div class="space-y-2">
              <label class="block text-xs font-bold uppercase tracking-wider text-white/60">
                Reason for Absence
              </label>
              <textarea
                v-model="reason"
                rows="4"
                placeholder="Explain in detail why you cannot attend this event..."
                class="w-full rounded-2xl bg-white/[0.03] border border-white/10 focus:border-primary focus:ring-1 focus:ring-primary p-4 text-white placeholder-white/30 text-sm outline-none transition-all resize-none"
                :disabled="submitting || uploading"
              ></textarea>
            </div>

            <!-- File Upload -->
            <div class="space-y-2">
              <label class="block text-xs font-bold uppercase tracking-wider text-white/60">
                Supporting Document (Optional)
              </label>
              
              <div 
                class="upload-zone"
                :class="{ 
                  'upload-zone--active': isDragging, 
                  'upload-zone--has-file': attachmentPath || selectedFile 
                }"
                @dragenter.prevent="isDragging = true"
                @dragleave.prevent="isDragging = false"
                @dragover.prevent
                @drop.prevent="handleDrop"
                @click="triggerFileInput"
              >
                <input 
                  ref="fileInput"
                  type="file"
                  accept="image/*,application/pdf"
                  class="hidden"
                  @change="handleFileSelect"
                />

                <div class="flex flex-col items-center justify-center p-6 text-center space-y-2.5">
                  <div class="p-3 rounded-full bg-white/[0.03] text-white/60 group-hover:text-white transition-colors">
                    <UploadCloudIcon v-if="!selectedFile && !attachmentPath" class="w-6 h-6 text-white/40" />
                    <FileTextIcon v-else class="w-6 h-6 text-primary" />
                  </div>
                  
                  <div class="space-y-1">
                    <p class="text-sm font-semibold text-white/80">
                      {{ (selectedFile || attachmentPath) ? (selectedFile?.name || 'Document Attached') : 'Click or drag supporting document here' }}
                    </p>
                    <p class="text-xs text-white/40">
                      {{ selectedFile ? `${(selectedFile.size / 1024 / 1024).toFixed(2)} MB` : 'Supports PDF, JPG, PNG (Max 5MB)' }}
                    </p>
                  </div>

                  <!-- Upload status indicator -->
                  <div v-if="uploading" class="text-xs text-primary font-semibold flex items-center gap-1.5 mt-1">
                    <Loader2Icon class="w-3.5 h-3.5 animate-spin" />
                    <span>Uploading attachment...</span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Footer -->
          <div class="p-6 border-t border-white/5 shrink-0 flex justify-end gap-3 bg-white/[0.02]">
            <BaseButton
              variant="ghost"
              size="md"
              :disabled="submitting || uploading"
              @click="close"
            >
              Cancel
            </BaseButton>
            <BaseButton
              variant="primary"
              size="md"
              class="premium-submit-btn"
              :disabled="!reason.trim() || submitting || uploading"
              @click="handleSubmit"
            >
              <Loader2Icon v-if="submitting" class="w-4 h-4 animate-spin mr-1.5" />
              Submit Letter
            </BaseButton>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
import { ref, watch } from 'vue'
import { X as XIcon, UploadCloud as UploadCloudIcon, FileText as FileTextIcon, AlertCircle as AlertCircleIcon, Loader2 as Loader2Icon } from 'lucide-vue-next'
import BaseButton from '@/components/ui/BaseButton.vue'
import { useExcuseLetterStore } from '@/stores/excuseLetterStore.js'

const props = defineProps({
  isOpen: {
    type: Boolean,
    required: true,
  },
  event: {
    type: Object,
    required: true,
  },
})

const emit = defineEmits(['close', 'submitted'])
const store = useExcuseLetterStore()

const reason = ref('')
const selectedFile = ref(null)
const attachmentPath = ref(null)
const isDragging = ref(false)
const uploading = ref(false)
const submitting = ref(false)
const localError = ref(null)
const fileInput = ref(null)

// Reset state on open/close
watch(() => props.isOpen, (isOpen) => {
  if (isOpen) {
    reason.value = ''
    selectedFile.value = null
    attachmentPath.value = null
    localError.value = null
    uploading.value = false
    submitting.value = false
  }
})

function close() {
  emit('close')
}

function triggerFileInput() {
  if (submitting.value || uploading.value) return
  fileInput.value?.click()
}

async function validateAndUploadFile(file) {
  if (!file) return
  
  // 5MB limit
  const maxBytes = 5 * 1024 * 1024
  if (file.size > maxBytes) {
    localError.value = 'File is too large. Maximum size is 5MB.'
    return
  }

  const allowedTypes = ['image/jpeg', 'image/png', 'image/jpg', 'application/pdf']
  if (!allowedTypes.includes(file.type)) {
    localError.value = 'Unsupported file type. Please upload a PDF or an image (JPG, PNG).'
    return
  }

  selectedFile.value = file
  localError.value = null
  uploading.value = true

  try {
    const path = await store.uploadAttachment(file)
    attachmentPath.value = path
  } catch (err) {
    localError.value = err.message || 'Failed to upload attachment.'
    selectedFile.value = null
    attachmentPath.value = null
  } finally {
    uploading.value = false
  }
}

function handleFileSelect(e) {
  const file = e.target.files?.[0]
  if (file) {
    validateAndUploadFile(file)
  }
}

function handleDrop(e) {
  isDragging.value = false
  const file = e.dataTransfer?.files?.[0]
  if (file) {
    validateAndUploadFile(file)
  }
}

async function handleSubmit() {
  if (!reason.value.trim()) {
    localError.value = 'Please provide a reason for absence.'
    return
  }

  submitting.value = true
  localError.value = null

  try {
    await store.submitLetter(props.event.id, reason.value, attachmentPath.value)
    emit('submitted')
    close()
  } catch (err) {
    localError.value = err.message || 'Failed to submit excuse letter.'
  } finally {
    submitting.value = false
  }
}
</script>

<style scoped>
.glass-card {
  background: rgba(20, 20, 20, 0.85);
  backdrop-filter: blur(28px) saturate(180%);
  -webkit-backdrop-filter: blur(28px) saturate(180%);
}

.upload-zone {
  border: 2px dashed rgba(255, 255, 255, 0.1);
  border-radius: 20px;
  background: rgba(255, 255, 255, 0.01);
  cursor: pointer;
  transition: all 0.25s ease;
}

.upload-zone:hover {
  border-color: rgba(255, 255, 255, 0.2);
  background: rgba(255, 255, 255, 0.02);
}

.upload-zone--active {
  border-color: #AAFF00;
  background: rgba(170, 255, 0, 0.05);
}

.upload-zone--has-file {
  border-color: rgba(170, 255, 0, 0.4);
  background: rgba(170, 255, 0, 0.02);
}

.premium-submit-btn {
  background: #AAFF00 !important;
  color: #050505 !important;
  font-weight: 700 !important;
  border-radius: 12px !important;
  box-shadow: 0 8px 20px -6px rgba(170, 255, 0, 0.4) !important;
}

.custom-scrollbar::-webkit-scrollbar {
  width: 4px;
}
.custom-scrollbar::-webkit-scrollbar-track {
  background: transparent;
}
.custom-scrollbar::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.1);
  border-radius: 10px;
}
.custom-scrollbar::-webkit-scrollbar-thumb:hover {
  background: rgba(255, 255, 255, 0.2);
}

.modal-fade-enter-active,
.modal-fade-leave-active {
  transition: all 0.4s cubic-bezier(0.22, 1, 0.36, 1);
}
.modal-fade-enter-from,
.modal-fade-leave-to {
  opacity: 0;
  transform: scale(0.9) translateY(20px);
}
</style>
