<template>
  <div class="reset-password-page min-h-dvh flex flex-col font-[Manrope] mesh-gradient overflow-hidden relative">
    <!-- Animated background elements -->
    <div class="absolute inset-0 overflow-hidden pointer-events-none">
      <div class="blob blob-1"></div>
      <div class="blob blob-2"></div>
    </div>

    <div class="flex-1 flex flex-col items-center justify-center px-6 relative z-10">
      <div 
        class="w-full max-w-[400px] glass-card rounded-[32px] p-8 md:p-10 flex flex-col gap-8 transition-all duration-1000 ease-[cubic-bezier(0.22,1,0.36,1)]"
        :class="isMounted ? 'opacity-100 translate-y-0 scale-100' : 'opacity-0 translate-y-12 scale-95'"
      >
        <!-- Logo & Brand -->
        <div class="flex flex-col items-center gap-2">
          <img
            :src="surfaceAuraLogo"
            alt="NEXUS"
            class="h-12 w-auto object-contain brightness-0 invert"
          />
        </div>

        <!-- Heading -->
        <div class="text-center">
          <h1 class="text-[20px] font-semibold leading-tight text-white/90">
            Reset your password
          </h1>
          <p class="text-[14px] text-white/50 mt-2 leading-relaxed">
            Please enter your new password below.
          </p>
        </div>

        <form 
          class="flex flex-col gap-4" 
          @submit.prevent="handleSubmit"
        >
          <div class="group relative">
            <BaseInput
              id="password"
              v-model="newPassword"
              type="password"
              placeholder="New Password"
              tone="neutral"
              class="premium-input"
              :disabled="isLoading || isSuccess"
            />
          </div>

          <div class="group relative">
            <BaseInput
              id="confirmPassword"
              v-model="confirmPassword"
              type="password"
              placeholder="Confirm New Password"
              tone="neutral"
              class="premium-input"
              :disabled="isLoading || isSuccess"
            />
          </div>

          <Transition name="fade">
            <p v-if="message" :class="messageClass">
              {{ message }}
            </p>
          </Transition>

          <BaseButton
            type="submit"
            variant="primary"
            size="lg"
            class="mt-2 premium-action-btn"
            :loading="isLoading"
            :disabled="isSuccess"
          >
            {{ isSuccess ? 'Password Reset!' : 'Update Password' }}
          </BaseButton>

          <BaseButton
            type="button"
            variant="secondary"
            size="lg"
            class="glass-secondary-btn"
            :disabled="isLoading"
            @click="goToLogin"
          >
            Back to Login
          </BaseButton>
        </form>
      </div>

      <!-- Footer Info -->
      <div 
        class="mt-8 flex flex-col items-center gap-4 transition-all duration-1000 delay-300"
        :class="isMounted ? 'opacity-100' : 'opacity-0'"
      >
        <div class="flex items-center gap-2 px-4 py-2 rounded-full bg-white/[0.03] border border-white/[0.05]">
          <span class="text-[11px] font-bold tracking-[0.05em] text-white/30 uppercase">Powered by</span>
          <span class="text-[11px] font-bold text-[var(--color-primary)] uppercase">NEXUS Ai v1.0</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeMount } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import BaseInput from '@/components/ui/BaseInput.vue'
import BaseButton from '@/components/ui/BaseButton.vue'
import { applyTheme, loadUnbrandedTheme, surfaceAuraLogo } from '@/config/theme.js'
import { confirmPasswordReset, resolveApiBaseUrl } from '@/services/backendApi.js'

const newPassword = ref('')
const confirmPassword = ref('')
const isLoading = ref(false)
const message = ref('')
const isSuccess = ref(false)
const isMounted = ref(false)
const router = useRouter()
const route = useRoute()

const token = computed(() => route.query.token)

const messageClass = computed(() => {
  return isSuccess.value 
    ? 'text-green-400 text-xs text-center font-medium mt-1'
    : 'text-red-400 text-xs text-center font-medium mt-1'
})

onBeforeMount(() => {
  applyTheme(loadUnbrandedTheme())
})

onMounted(() => {
  setTimeout(() => {
    isMounted.value = true
  }, 50)

  if (!token.value) {
    message.value = 'Missing reset token. Please use the link from your email.'
  }
})

async function handleSubmit() {
  if (!token.value) {
    message.value = 'Invalid or missing reset token.'
    return
  }

  if (newPassword.value.length < 8) {
    message.value = 'Password must be at least 8 characters long.'
    isSuccess.value = false
    return
  }

  if (newPassword.value !== confirmPassword.value) {
    message.value = 'Passwords do not match.'
    isSuccess.value = false
    return
  }

  isLoading.value = true
  message.value = ''
  isSuccess.value = false

  try {
    await confirmPasswordReset(resolveApiBaseUrl(), token.value, newPassword.value)
    
    message.value = 'Your password has been reset successfully. You can now log in with your new password.'
    isSuccess.value = true
    
    setTimeout(() => {
      router.push({ name: 'Login' })
    }, 4000)
  } catch (error) {
    message.value = error?.message || 'Failed to reset password. The link may be invalid or expired.'
    isSuccess.value = false
  } finally {
    isLoading.value = false
  }
}

function goToLogin() {
  router.push({ name: 'Login' })
}
</script>

<style scoped>
.reset-password-page {
  --color-primary: #AAFF00;
  --color-primary-glow: rgba(170, 255, 0, 0.4);
}

/* Background Blobs */
.blob {
  position: absolute;
  width: 500px;
  height: 500px;
  background: radial-gradient(circle, var(--color-primary-glow) 0%, transparent 70%);
  filter: blur(80px);
  opacity: 0.15;
  z-index: 1;
}

.blob-1 { top: -10%; left: -10%; animation: float 20s infinite alternate; }
.blob-2 { bottom: -10%; right: -10%; animation: float 25s infinite alternate-reverse; }

@keyframes float {
  0% { transform: translate(0, 0) rotate(0deg); }
  100% { transform: translate(100px, 50px) rotate(30deg); }
}

/* Premium Component Overrides */
.premium-input :deep(.base-input) {
  background: rgba(255, 255, 255, 0.05) !important;
  border: 1px solid rgba(255, 255, 255, 0.1) !important;
  color: white !important;
  height: 56px !important;
  border-radius: 16px !important;
}

.premium-input :deep(.base-input:focus) {
  background: rgba(255, 255, 255, 0.08) !important;
  border-color: var(--color-primary) !important;
  box-shadow: 0 0 20px var(--color-primary-glow) !important;
}

.premium-input :deep(.base-input::placeholder) {
  color: rgba(255, 255, 255, 0.3) !important;
}

.premium-action-btn {
  background: var(--color-primary) !important;
  color: #050505 !important;
  height: 56px !important;
  border-radius: 16px !important;
  box-shadow: 0 10px 30px -10px var(--color-primary-glow) !important;
  transition: all 0.3s cubic-bezier(0.22, 1, 0.36, 1) !important;
}

.premium-action-btn:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.glass-secondary-btn {
  background: rgba(255, 255, 255, 0.05) !important;
  border: 1px solid rgba(255, 255, 255, 0.1) !important;
  color: white !important;
  height: 56px !important;
  border-radius: 16px !important;
}

.glass-secondary-btn:hover {
  background: rgba(255, 255, 255, 0.1) !important;
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
