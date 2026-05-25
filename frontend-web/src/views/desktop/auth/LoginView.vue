<template>
  <div class="min-h-dvh flex font-[Manrope] bg-[#F7F7F9] text-[#111111] overflow-hidden relative selection:bg-black selection:text-white">
    <!-- Left Column (Brand & Context) -->
    <div class="hidden lg:flex flex-1 flex-col justify-between p-12 xl:p-16 relative z-10 transition-all duration-700 ease-out"
         :class="isMounted ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-4'">
      
      <!-- Top Brand -->
      <div class="flex items-center gap-3">
        <div class="w-14 h-14 flex items-center justify-center">
          <img src="/logos/nexus_logo_black.png" alt="NEXUS Logo" class="w-full h-full object-contain opacity-90" />
        </div>
        <span class="text-sm font-bold tracking-wide text-black/60">Powered by NEXUS</span>
      </div>

      <!-- Main Copy -->
      <div class="max-w-xl">
        <div class="text-[10px] font-bold tracking-[0.2em] uppercase text-black/40 mb-6">Desktop Workspace</div>
        <h1 class="text-5xl xl:text-6xl font-medium tracking-tight leading-[1.1] mb-6">
          Operate the full campus portal from one focused control room.
        </h1>
        <p class="text-lg text-black/50 leading-relaxed font-medium">
          Desktop and mobile now live in separate folders, while auth stores and API services stay shared underneath.
        </p>
      </div>

      <!-- Bottom Pills -->
      <div class="flex flex-wrap gap-3">
        <div class="px-4 py-2 rounded-full border border-black/10 text-xs font-semibold text-black/50 bg-white/50 shadow-sm">Shared Pinia stores</div>
        <div class="px-4 py-2 rounded-full border border-black/10 text-xs font-semibold text-black/50 bg-white/50 shadow-sm">Shared API services</div>
        <div class="px-4 py-2 rounded-full border border-black/10 text-xs font-semibold text-black/50 bg-white/50 shadow-sm">Desktop-only UI files</div>
      </div>
    </div>

    <!-- Right Column (Login Form Card) -->
    <div class="w-full lg:w-[45%] xl:w-[40%] flex-shrink-0 flex items-center justify-center p-6 lg:p-12 relative z-10">
      
      <div class="w-full max-w-[420px] bg-white rounded-[32px] p-8 sm:p-10 shadow-[0_8px_30px_rgb(0,0,0,0.04)] border border-black/[0.03] transition-all duration-700 delay-100 ease-out"
           :class="isMounted ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-8'">
        
        <!-- Mobile Logo (visible only on smaller screens if they hit this desktop route) -->
        <div class="lg:hidden flex items-center gap-3 mb-10">
          <div class="w-12 h-12 flex items-center justify-center bg-black rounded-[14px] p-2">
            <img src="/logos/nexus_logo.png" alt="NEXUS Logo" class="w-full h-full object-contain" />
          </div>
          <span class="text-lg font-bold tracking-tight">NEXUS</span>
        </div>

        <div class="mb-8">
          <div class="text-[10px] font-bold tracking-[0.2em] uppercase text-black/40 mb-3">Sign In</div>
          <h2 class="text-3xl font-semibold tracking-tight mb-2">Welcome back</h2>
          <p class="text-sm text-black/50 font-medium">Use your school account to open the web workspace.</p>
        </div>

        <form @submit.prevent="handleLogin" class="space-y-5">
          <div class="space-y-4">
            <div class="relative">
              <input
                v-model="email"
                placeholder="School email"
                type="email"
                autocomplete="email"
                class="light-input"
                :disabled="isLoading || googleLoading"
              />
            </div>
            <div class="relative">
              <input
                v-model="password"
                placeholder="Password"
                type="password"
                autocomplete="current-password"
                class="light-input pr-12"
                :disabled="isLoading || googleLoading"
              />
              <button 
                type="button"
                tabindex="-1"
                class="absolute right-4 top-1/2 -translate-y-1/2 text-black/20 hover:text-black/60 transition-colors"
              >
                <!-- Eye icon static just for visual match -->
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <path d="M2 12s3-7 10-7 10 7 10 7-3 7-10 7-10-7-10-7Z" />
                  <circle cx="12" cy="12" r="3" />
                </svg>
              </button>
            </div>
          </div>

          <div class="flex justify-between items-center -mt-2">
            <div></div> <!-- spacer -->
            <button
              type="button"
              class="text-xs font-semibold text-black/40 hover:text-black transition-colors"
              @click="goToForgotPassword"
            >
              Forgot Password?
            </button>
          </div>

          <Transition name="fade">
            <p v-if="visibleMessage" class="text-xs font-bold text-red-500 text-center py-3 bg-red-50 rounded-xl">
              {{ visibleMessage }}
            </p>
          </Transition>

          <button
            type="submit"
            class="w-full bg-[#111] text-white font-semibold text-[13px] py-4 rounded-[16px] hover:bg-black hover:scale-[0.99] active:scale-[0.97] transition-all disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:scale-100 mt-2"
            :disabled="isLoading || googleLoading"
          >
            <span v-if="isLoading">Authenticating...</span>
            <span v-else>Log In</span>
          </button>

          <div class="pt-4 flex flex-col gap-3">
            <div class="google-btn-wrapper light-google">
              <GoogleSignInButton @credential="handleGoogleCredential" />
            </div>
          </div>
        </form>
      </div>

      <!-- Footer Info below card -->
      <div class="absolute bottom-6 left-0 w-full flex justify-center lg:hidden">
        <a
          href="https://nexus-landing-page-iota.vercel.app/"
          target="_blank"
          rel="noopener noreferrer"
          class="text-[11px] font-bold text-black/30 hover:text-black/60 transition-colors uppercase tracking-widest"
        >
          Documentation
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
.light-input {
  width: 100%;
  background: white;
  border: 1px solid rgba(0, 0, 0, 0.1);
  border-radius: 16px;
  padding: 16px 16px;
  color: #111;
  font-size: 14px;
  font-weight: 500;
  transition: all 0.2s ease;
  outline: none;
}

.light-input::placeholder {
  color: rgba(0, 0, 0, 0.3);
  font-weight: 500;
}

.light-input:focus {
  border-color: rgba(0, 0, 0, 0.3);
  box-shadow: 0 0 0 4px rgba(0, 0, 0, 0.04);
}

.light-input:disabled {
  background: #FAFAFA;
  color: #999;
  cursor: not-allowed;
}

.fade-enter-active, .fade-leave-active { transition: opacity 0.3s ease; }
.fade-enter-from, .fade-leave-to { opacity: 0; }

:deep(.light-google iframe) {
  border-radius: 16px !important;
}

:deep(.light-google) {
  background: white;
  border-radius: 16px;
  overflow: hidden;
  border: 1px solid rgba(0,0,0,0.1);
}
</style>
