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
            <h2 class="text-xl font-bold text-white">
              NEXUS Terms and Conditions
            </h2>
            <button 
              @click="close"
              class="p-2 rounded-full hover:bg-white/10 transition-colors text-white/50 hover:text-white"
            >
              <XIcon class="w-5 h-5" />
            </button>
          </div>

          <!-- Body (Scrollable) -->
          <div class="p-6 overflow-y-auto flex-1 font-[Manrope] text-[14px] leading-relaxed space-y-5 text-white/60 custom-scrollbar">
            <p class="font-medium text-white/80">These Terms and Conditions govern access to and use of the NEXUS platform by students, faculty, staff, administrators, governance officers, institutions, and other authorized users.</p>
            <p>By registering for, accessing, or using NEXUS, you agree to be bound by these Terms and Conditions.</p>

            <h3 class="font-bold text-[16px] mt-8 text-white/90 tracking-tight">NATURE OF THE SERVICE</h3>
            <p>NEXUS is a software platform intended to facilitate attendance management, identity verification, geofenced attendance validation, scheduling, dashboards, analytics, governance workflows, and related institutional functions.</p>

            <h3 class="font-bold text-[16px] mt-8 text-white/90 tracking-tight">ELIGIBILITY AND AUTHORITY</h3>
            <p>You may use NEXUS only if you are an authorized user of a participating institution, the information you provide is accurate, and you have the legal capacity to agree to these terms.</p>

            <h3 class="font-bold text-[16px] mt-8 text-white/90 tracking-tight">FACE REGISTRATION AND IDENTITY VERIFICATION</h3>
            <p>Where enabled, NEXUS may require face registration, face verification, or similar identity validation features. You acknowledge that your face embedding may be processed for attendance verification and security purposes.</p>

            <h3 class="font-bold text-[16px] mt-8 text-white/90 tracking-tight">ACCEPTABLE USE</h3>
            <p>You agree not to use NEXUS for unlawful purposes, impersonate others, or attempt to bypass security controls. False registration or spoofing of identity and location data is strictly prohibited.</p>

            <h3 class="font-bold text-[16px] mt-8 text-white/90 tracking-tight">INTELLECTUAL PROPERTY</h3>
            <p>All software, designs, and workflows forming part of NEXUS are owned by NEXUS Project and are protected by intellectual property laws.</p>
            
            <p class="pt-4 border-t border-white/5 text-[12px] italic">For the full legal text and detailed clauses, please contact auraautomessage@gmail.com.</p>
          </div>

          <!-- Footer -->
          <div class="p-6 border-t border-white/5 shrink-0 flex justify-end gap-3 bg-white/[0.02]">
            <BaseButton
              variant="primary"
              size="md"
              class="premium-agree-btn"
              @click="agree"
            >
              I Understand & Agree
            </BaseButton>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
import { X as XIcon } from 'lucide-vue-next'
import BaseButton from '@/components/ui/BaseButton.vue'

defineProps({
  isOpen: {
    type: Boolean,
    required: true
  }
})

const emit = defineEmits(['agree', 'close', 'decline'])

function close() {
  emit('decline')
  emit('close')
}

function agree() {
  emit('agree')
}
</script>

<style scoped>
.glass-card {
  background: rgba(20, 20, 20, 0.8);
  backdrop-filter: blur(24px) saturate(180%);
  -webkit-backdrop-filter: blur(24px) saturate(180%);
}

.premium-agree-btn {
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
