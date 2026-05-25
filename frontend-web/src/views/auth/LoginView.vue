<template>
  <div class="login-page min-h-dvh flex flex-col font-[Manrope] mesh-gradient overflow-hidden relative">
    <!-- Animated background elements -->
    <div class="absolute inset-0 overflow-hidden pointer-events-none">
      <div class="blob blob-1"></div>
      <div class="blob blob-2"></div>
      <div class="blob blob-3"></div>
    </div>

    <!-- Main centered content -->
    <div class="flex-1 flex flex-col items-center justify-center px-6 relative z-10">
      <div 
        class="w-full max-w-[400px] glass-card rounded-[32px] p-8 md:p-10 flex flex-col gap-8 transition-all duration-1000 ease-[cubic-bezier(0.22,1,0.36,1)]"
        :class="isMounted ? 'opacity-100 translate-y-0 scale-100' : 'opacity-0 translate-y-12 scale-95'"
      >
        <!-- Logo & Brand -->
        <div class="flex flex-col items-center gap-2">
          <div class="w-24 h-24 mb-4 flex items-center justify-center">
            <img src="/logos/nexus_logo.png" alt="NEXUS Logo" class="w-full h-full object-contain relative z-10" />
          </div>
          <h1 class="text-3xl font-extrabold text-white tracking-tight mb-2 text-center">Welcome to NEXUS</h1>
          <p class="text-white/40 text-[15px] font-medium">Institutional Operating System</p>
        </div>

        <!-- Heading -->
        <div class="text-center">
          <h1 class="text-[20px] font-semibold leading-tight text-white/90">
            Log In
          </h1>
          <p class="text-[14px] text-white/50 mt-2">
            Enter your credentials to access the portal
          </p>
        </div>

        <!-- Form -->
        <form 
          class="flex flex-col gap-4" 
          @submit.prevent="handleLogin"
        >
          <!-- Email -->
          <div class="group relative">
            <BaseInput
              id="email"
              v-model="email"
              type="email"
              placeholder="Email Address"
              autocomplete="email"
              tone="neutral"
              class="premium-input"
              :disabled="isLoading || googleLoading"
            />
          </div>

          <!-- Password -->
          <div class="group relative">
            <BaseInput
              id="password"
              v-model="password"
              type="password"
              placeholder="Password"
              autocomplete="current-password"
              tone="neutral"
              class="premium-input"
              :disabled="isLoading || googleLoading"
            />
          </div>

          <!-- Forgot Password Link -->
          <div class="flex justify-end -mt-1">
            <a
              href="#"
              class="text-[12px] font-medium text-white/40 hover:text-[var(--color-primary)] transition-colors"
              @click.prevent="goToForgotPassword"
            >
              Forgot password?
            </a>
          </div>

          <!-- Error message -->
          <Transition name="fade">
            <p v-if="visibleMessage" class="text-red-400 text-xs text-center font-medium">
              {{ visibleMessage }}
            </p>
          </Transition>

          <!-- Login Button -->
          <BaseButton
            type="submit"
            variant="primary"
            size="lg"
            class="mt-2 premium-login-btn"
            :loading="isLoading"
            :disabled="googleLoading"
          >
            Log In
          </BaseButton>

          <!-- Google Sign-In -->
          <div class="flex items-center gap-4 my-2" aria-hidden="true">
            <div class="flex-1 h-px bg-white/10"></div>
            <span class="text-[11px] uppercase tracking-[0.15em] text-white/30 font-bold">OR</span>
            <div class="flex-1 h-px bg-white/10"></div>
          </div>

          <div class="google-btn-wrapper">
            <GoogleSignInButton @credential="handleGoogleCredential" />
          </div>
        </form>

        <!-- PWA Install -->
        <Transition name="fade">
          <div
            v-if="showPwaInstallCta"
            class="pwa-card rounded-2xl p-4 border border-white/5 bg-white/[0.02] flex flex-col gap-3"
          >
            <div class="flex items-center gap-3">
              <div class="w-8 h-8 rounded-lg bg-[var(--color-primary)]/20 flex items-center justify-center text-[var(--color-primary)]">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <path d="M21 15V19C21 19.5304 20.7893 20.4142 20.4142 20.4142C20.0391 20.7893 19.5304 21 19 21H5C4.46957 21 3.96086 20.7893 3.58579 20.4142C3.21071 20.0391 3 19.5304 3 19V15" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                  <path d="M7 10L12 15L17 10" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                  <path d="M12 15V3" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                </svg>
              </div>
              <div class="flex-1">
                <p class="text-[12px] font-bold text-white/90">{{ pwaInstallButtonLabel }}</p>
                <p class="text-[10px] text-white/40 leading-tight mt-0.5">{{ pwaInstallHelpText }}</p>
              </div>
            </div>
            <BaseButton
              v-if="canPromptPwaInstall"
              type="button"
              variant="secondary"
              size="sm"
              class="w-full glass-secondary-btn"
              @click="handlePwaInstall"
            >
              Install NEXUS App
            </BaseButton>
          </div>
        </Transition>
      </div>

      <!-- Footer Info -->
      <div 
        class="mt-8 flex flex-col items-center gap-4 transition-all duration-1000 delay-300"
        :class="isMounted ? 'opacity-100' : 'opacity-0'"
      >
        <div class="flex items-center gap-2 px-4 py-2 rounded-full bg-white/[0.03] border border-white/[0.05]">
          <span class="text-[11px] font-bold tracking-[0.05em] text-white/30 uppercase">Powered by</span>
          <span class="text-[11px] font-bold text-[var(--color-primary)] uppercase">NEXUS v1.0</span>
        </div>
        
        <a
          href="https://nexus-landing-page-iota.vercel.app/"
          target="_blank"
          rel="noopener noreferrer"
          class="text-[12px] font-semibold text-white/40 hover:text-white transition-colors"
        >
          Explore NEXUS Platform
        </a>
      </div>
    </div>

    <!-- Terms Modal -->
    <TermsModal 
      :isOpen="showTermsModal" 
      @agree="handleAgree"
      @decline="handleDecline" 
    />
  </div>
</template>

<script setup>
import { computed, ref, onBeforeMount, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import BaseInput from '@/components/ui/BaseInput.vue'
import BaseButton from '@/components/ui/BaseButton.vue'
import TermsModal from '@/components/auth/TermsModal.vue'
import GoogleSignInButton from '@/components/auth/GoogleSignInButton.vue'
import { useAuth } from '@/composables/useAuth.js'
import { useGoogleLogin } from '@/composables/useGoogleLogin.js'
import { applyTheme, loadUnbrandedTheme, surfaceAuraLogo } from '@/config/theme.js'
import {
  canPromptPwaInstall,
  hasManualPwaInstallInstructions,
  installPwaApp,
  isPwaInstalled,
  pwaInstallButtonLabel,
  pwaInstallError,
  pwaInstallHelpText,
} from '@/services/pwaInstall.js'
import { consumeSessionExpiredNotice } from '@/services/sessionExpiry.js'

const email = ref('')
const password = ref('')
const showTermsModal = ref(false)
const isMounted = ref(false)
const sessionNotice = ref('')
const router = useRouter()

const { login, logout, isLoading, error } = useAuth()
const {
  loginWithGoogleCredential,
  isLoading: googleLoading,
  error: googleError,
} = useGoogleLogin()
const visibleMessage = computed(() => error.value || googleError.value || sessionNotice.value)
const showPwaInstallCta = computed(() => (
  canPromptPwaInstall.value
  || hasManualPwaInstallInstructions.value
  || isPwaInstalled.value
  || Boolean(pwaInstallError.value)
))

const nextRoute = ref(null)

onBeforeMount(() => {
  applyTheme(loadUnbrandedTheme())
})

onMounted(() => {
  sessionNotice.value = consumeSessionExpiredNotice()

  setTimeout(() => {
    isMounted.value = true
  }, 50)
})

async function handleLogin() {
  if (isLoading.value || googleLoading.value) return

  // TEMPORARY TESTING BYPASS: If you type "test" in both fields, it will skip the backend
  if (email.value === 'test' && password.value === 'test') {
    nextRoute.value = { name: 'PreviewHome' }
    showTermsModal.value = true
    return
  }

  const route = await login(email.value, password.value, { preventRedirect: true })
  
  if (route) {
    // Login succeeded, token stored, session initialized.
    // Pause routing and show Terms Modal.
    nextRoute.value = route
    showTermsModal.value = true
  }
}

async function handlePwaInstall() {
  await installPwaApp()
}

async function handleGoogleCredential(credential) {
  const route = await loginWithGoogleCredential(credential, { preventRedirect: true })

  if (route) {
    nextRoute.value = route
    showTermsModal.value = true
  }
}

function handleAgree() {
  showTermsModal.value = false
  localStorage.setItem('nexus_terms_agreed', 'true')
  if (nextRoute.value) {
    router.push(nextRoute.value)
  }
}

function handleDecline() {
  showTermsModal.value = false
  // Log them out and clear session
  logout()
}

function goToForgotPassword() {
  router.push({ name: 'ForgotPassword' })
}
</script>

<style scoped>
/* Logo style updated to preserve texture */

.login-page {
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
.blob-3 { top: 40%; left: 30%; width: 300px; height: 300px; opacity: 0.1; animation: float 15s infinite ease-in-out; }

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

.premium-login-btn {
  background: var(--color-primary) !important;
  color: #050505 !important;
  height: 56px !important;
  border-radius: 16px !important;
  box-shadow: 0 10px 30px -10px var(--color-primary-glow) !important;
  transition: all 0.3s cubic-bezier(0.22, 1, 0.36, 1) !important;
}

.premium-login-btn:hover {
  transform: translateY(-2px) !important;
  box-shadow: 0 15px 40px -10px var(--color-primary-glow) !important;
  filter: brightness(1.1) !important;
}

.premium-login-btn:active {
  transform: scale(0.98) !important;
}

.google-btn-wrapper :deep(button) {
  height: 56px !important;
  border-radius: 16px !important;
  background: rgba(255, 255, 255, 0.03) !important;
  border: 1px solid rgba(255, 255, 255, 0.1) !important;
  color: white !important;
  transition: all 0.2s ease !important;
}

.google-btn-wrapper :deep(button:hover) {
  background: rgba(255, 255, 255, 0.06) !important;
  border-color: rgba(255, 255, 255, 0.2) !important;
}

.glass-secondary-btn {
  background: rgba(255, 255, 255, 0.05) !important;
  border: 1px solid rgba(255, 255, 255, 0.1) !important;
  color: white !important;
  border-radius: 12px !important;
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

/* Responsive adjustments */
@media (max-width: 640px) {
  .glass-card {
    background: transparent;
    border: none;
    box-shadow: none;
    backdrop-filter: none;
    padding: 0;
  }
}
</style>
