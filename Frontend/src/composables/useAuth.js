import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { loginForAccessToken, loginWithGoogle as apiLoginWithGoogle, requestPasswordReset as apiRequestPasswordReset, resolveApiBaseUrl } from '@/services/backendApi.js'
import {
    clearDashboardSession,
    getDefaultAuthenticatedRoute,
    initializeDashboardSession,
    sessionUsesLimitedMode,
    sessionNeedsFaceRegistration,
} from '@/composables/useDashboardSession.js'
import { hasPrivilegedPendingFace, storeAuthMeta } from '@/services/localAuth.js'
import { markCurrentRuntimeSession } from '@/services/sessionPersistence.js'
import { clearSessionExpiredNotice } from '@/services/sessionExpiry.js'
import { storeRememberMePreference } from '@/services/userPreferences.js'

export function useAuth() {
    const router = useRouter()
    const isLoading = ref(false)
    const error = ref(null)

    async function handlePostLogin(tokenPayload, { rememberMe = false } = {}) {
        const accessToken = tokenPayload?.access_token
        if (!accessToken) {
            throw new Error('The API did not return an access token.')
        }

        localStorage.setItem('aura_token', accessToken)
        localStorage.setItem('aura_user_roles', JSON.stringify(tokenPayload?.roles ?? []))
        const authMeta = storeAuthMeta(tokenPayload)
        storeRememberMePreference(rememberMe)
        markCurrentRuntimeSession()

        if (authMeta.mustChangePassword) {
            router.push({ name: 'ChangePassword' })
            return
        }

        if (hasPrivilegedPendingFace(authMeta)) {
            router.push({ name: 'PrivilegedFaceVerification' })
            return
        }

        const initializedSession = await initializeDashboardSession(true)
        if (!initializedSession?.user || sessionUsesLimitedMode()) {
            throw new Error('The backend did not return a complete user session. Please try again once the backend is stable.')
        }
        router.push(
            sessionNeedsFaceRegistration()
                ? { name: 'FaceRegistration' }
                : getDefaultAuthenticatedRoute()
        )
    }

    async function login(email, password, { rememberMe = false } = {}) {
        isLoading.value = true
        error.value = null

        try {
            if (!email || !password) {
                throw new Error('Please enter your email and password.')
            }

            clearSessionExpiredNotice()

            const apiBaseUrl = resolveApiBaseUrl()
            const tokenPayload = await loginForAccessToken(apiBaseUrl, {
                username: email,
                password,
                rememberMe,
            })

            await handlePostLogin(tokenPayload, { rememberMe })
        } catch (err) {
            clearDashboardSession()
            error.value = err?.message || 'Login failed. Please try again.'
        } finally {
            isLoading.value = false
        }
    }

    async function loginWithGoogle(idToken) {
        isLoading.value = true
        error.value = null

        try {
            if (!idToken) {
                throw new Error('Google ID token is missing.')
            }

            clearSessionExpiredNotice()
            const apiBaseUrl = resolveApiBaseUrl()
            const tokenPayload = await apiLoginWithGoogle(apiBaseUrl, { idToken })

            await handlePostLogin(tokenPayload, { rememberMe: true })
        } catch (err) {
            clearDashboardSession()
            error.value = err?.message || 'Google login failed.'
        } finally {
            isLoading.value = false
        }
    }

    async function requestPasswordReset(email) {
        isLoading.value = true
        error.value = null

        try {
            if (!email) {
                throw new Error('Please enter your email address.')
            }

            const apiBaseUrl = resolveApiBaseUrl()
            const response = await apiRequestPasswordReset(apiBaseUrl, { email })
            return response
        } catch (err) {
            error.value = err?.message || 'Password reset request failed.'
            throw err
        } finally {
            isLoading.value = false
        }
    }

    function logout() {
        clearDashboardSession()
        router.push({ name: 'Login' })
    }

    return { login, loginWithGoogle, requestPasswordReset, logout, isLoading, error }
}
