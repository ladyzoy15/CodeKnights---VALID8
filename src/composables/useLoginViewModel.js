import { computed, onBeforeMount, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuth } from '@/composables/useAuth.js'
import { applyTheme, loadUnbrandedTheme } from '@/config/theme.js'
import { consumeSessionExpiredNotice } from '@/services/sessionExpiry.js'

export function useLoginViewModel() {
  const email = ref('')
  const password = ref('')
  const isMounted = ref(false)
  const sessionNotice = ref('')
  const onboardingData = ref(null)
  const showOnboarding = ref(false)

  const router = useRouter()
  const { login, loginWithGoogleAuth, isLoading, error } = useAuth()
  const visibleMessage = computed(() => error.value || sessionNotice.value)

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
    await login(email.value, password.value)
  }

  async function handleGoogleLogin(idToken) {
    const result = await loginWithGoogleAuth(idToken)
    if (result?.needsOnboarding) {
      onboardingData.value = {
        ...result.payload,
        id_token: idToken
      }
      showOnboarding.value = true
    }
  }

  async function handleOnboardingSubmit(schoolId) {
    if (!onboardingData.value?.id_token) return
    
    const result = await loginWithGoogleAuth(onboardingData.value.id_token, schoolId)
    if (result?.success) {
      showOnboarding.value = false
      onboardingData.value = null
    }
  }

  function openQuickAttendance() {
    router.push({ name: 'QuickAttendance' })
  }

  return {
    email,
    password,
    isMounted,
    isLoading,
    visibleMessage,
    showOnboarding,
    onboardingData,
    handleLogin,
    handleGoogleLogin,
    handleOnboardingSubmit,
    openQuickAttendance,
  }
}

