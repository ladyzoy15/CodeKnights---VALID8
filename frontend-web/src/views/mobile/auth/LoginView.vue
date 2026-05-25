<template>
  <div class="login-page min-h-dvh flex flex-col font-[Manrope] bg-[#0a0a0a] text-white overflow-hidden relative">
    
    <div class="flex-1 flex flex-col items-center justify-center p-6 relative z-10">
      <div 
        class="w-full max-w-[400px] transition-all duration-700 ease-out"
        :class="isMounted ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-4'"
      >
        <!-- Logo Section -->
        <div class="flex flex-col items-center mb-10">
          <div class="w-20 h-20 mb-6 flex items-center justify-center">
            <img src="/logos/nexus_logo.png" alt="NEXUS Logo" class="w-full h-full object-contain" />
          </div>
          <h1 class="text-xl font-bold tracking-tight mb-1">NEXUS</h1>
          <p class="text-white/40 text-[11px] font-bold tracking-[0.2em] uppercase">Institutional OS</p>
        </div>

        <!-- Login Form -->
        <form @submit.prevent="handleLogin" class="space-y-6">
          <div class="space-y-3">
            <input
              v-model="email"
              placeholder="Email Address"
              type="email"
              autocomplete="email"
              class="flat-input"
              :disabled="isLoading || googleLoading"
            />
            <input
              v-model="password"
              placeholder="Password"
              type="password"
              autocomplete="current-password"
              class="flat-input"
              :disabled="isLoading || googleLoading"
            />
          </div>

          <div class="flex justify-end">
            <button
              type="button"
              class="text-[10px] font-bold text-white/30 hover:text-white transition-colors uppercase tracking-[0.15em]"
              @click="goToForgotPassword"
            >
              Forgot Password?
            </button>
          </div>

          <Transition name="fade">
            <p v-if="visibleMessage" class="text-[11px] font-bold text-red-400 text-center py-3 bg-red-500/5 border border-red-500/10 rounded-lg">
              {{ visibleMessage }}
            </p>
          </Transition>

          <button
            type="submit"
            class="w-full flat-btn font-bold text-xs tracking-[0.2em] uppercase py-4 rounded-xl transition-all"
            :disabled="isLoading || googleLoading"
          >
            <span v-if="isLoading">Authenticating...</span>
            <span v-else>Log In</span>
          </button>

          <div class="relative py-4">
            <div class="absolute inset-0 flex items-center"><div class="w-full border-t border-white/[0.05]"></div></div>
            <div class="relative flex justify-center text-[9px] uppercase tracking-[0.3em] font-bold text-white/10">
              <span class="bg-[#0a0a0a] px-4">Secure Access</span>
            </div>
          </div>

          <div class="google-btn-wrapper flat-google">
            <GoogleSignInButton @credential="handleGoogleCredential" />
          </div>
        </form>

        <!-- PWA/Install Section -->
        <Transition name="fade">
          <div v-if="showPwaInstallCta" class="mt-8 p-5 rounded-2xl border border-white/[0.05] bg-white/[0.01] flex flex-col gap-4">
            <div class="flex items-center gap-4">
              <div class="w-6 h-6 flex items-center justify-center text-white/20">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <path d="M12 15V3M12 15L7 10M12 15L17 10M4 21H20" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                </svg>
              </div>
              <div class="flex-1">
                <p class="text-[10px] font-bold text-white/40 uppercase tracking-widest">{{ pwaInstallButtonLabel }}</p>
              </div>
            </div>
            <button
              v-if="canPromptPwaInstall"
              type="button"
              class="w-full py-3 rounded-xl border border-white/5 text-[9px] font-bold uppercase tracking-[0.2em] text-white/60 hover:bg-white/5 transition-colors"
              @click="handlePwaInstall"
            >
              Install App
            </button>
          </div>
        </Transition>
      </div>

      <!-- Footer Info -->
      <div 
        class="mt-10 flex flex-col items-center gap-4 transition-all duration-1000 delay-300"
        :class="isMounted ? 'opacity-100' : 'opacity-0'"
      >
        <div class="text-[9px] font-bold tracking-[0.2em] text-white/10 uppercase text-center leading-relaxed">
          NEXUS v1.0 &copy; 2026<br/>
          Smart Institutional Platform
        </div>
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
import TermsModal from '@/components/auth/TermsModal.vue'
import GoogleSignInButton from '@/components/auth/GoogleSignInButton.vue'
import { useAuth } from '@/composables/useAuth.js'
import { useGoogleLogin } from '@/composables/useGoogleLogin.js'
import { applyTheme, loadUnbrandedTheme } from '@/config/theme.js'
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

  if (email.value === 'test' && password.value === 'test') {
    nextRoute.value = { name: 'PreviewHome' }
    showTermsModal.value = true
    return
  }

  const route = await login(email.value, password.value, { preventRedirect: true })
  if (route) {
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
  if (nextRoute.value) router.push(nextRoute.value)
}

function handleDecline() {
  showTermsModal.value = false
  logout()
}

function goToForgotPassword() {
  router.push({ name: 'ForgotPassword' })
}
</script>

<style scoped>
.logo-container {
  display: flex;
  align-items: center;
  justify-content: center;
}

.flat-input {
  width: 100%;
  background: #111;
  border: 1px solid #1a1a1a;
  border-radius: 12px;
  padding: 16px;
  color: white;
  font-size: 14px;
  transition: all 0.2s ease;
  appearance: none;
}

.flat-input:focus {
  outline: none;
  border-color: #333;
  background: #151515;
}

.flat-btn {
  background: white;
  color: black;
  border: none;
}

.flat-btn:active {
  transform: scale(0.98);
}

.flat-btn:disabled {
  background: #222;
  color: #444;
}

.fade-enter-active, .fade-leave-active { transition: opacity 0.3s ease; }
.fade-enter-from, .fade-leave-to { opacity: 0; }

:deep(.flat-google iframe) {
  border-radius: 12px !important;
}
</style>
