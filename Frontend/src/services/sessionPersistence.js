import { Capacitor } from '@capacitor/core'
import { clearStoredAuthMeta, getStoredAuthMeta } from '@/services/localAuth.js'
import { getStoredRememberMePreference } from '@/services/userPreferences.js'

/**
 * XSS HARDENING CHECKLIST & CSP ENFORCEMENT (Audit Finding 6)
 * ----------------------------------------------------------
 * Since JWT tokens and user roles are stored in localStorage for hybrid web/native compatibility,
 * the following security measures are strictly enforced across the application:
 * 1. CSP Enforcement: index.html defines a strict Content-Security-Policy restricting script execution
 *    to 'self' and blocked frame-ancestors to prevent clickjacking/XSS token harvesting.
 * 2. Vue Template Escaping: All dynamic user inputs are rendered using Vue's double-mustache syntax ({{ }})
 *    which automatically HTML-escapes content. v-html is strictly prohibited for user-generated content.
 * 3. Sanitization: Any rich text input must be sanitized via DOMPurify before rendering or submission.
 * 4. Automatic Session Expiry: Tokens contain strict exp claims verified on every backend request.
 */
const SESSION_TOKEN_STORAGE_KEY = 'aura_token'
const USER_ROLES_STORAGE_KEY = 'aura_user_roles'
const DASHBOARD_CACHE_STORAGE_KEY = 'aura_dashboard_cache_v1'
const NATIVE_RUNTIME_SESSION_KEY = 'aura_native_runtime_session'

function normalizeRoleKey(role = '') {
  const normalizedRole = String(role || '')
    .trim()
    .toLowerCase()
    .replace(/_/g, '-')

  return normalizedRole === 'campus-admin' ? 'school-it' : normalizedRole
}

function getStoredRoleKeys(meta = getStoredAuthMeta()) {
  if (!Array.isArray(meta?.roles)) return []
  return meta.roles.map((role) => normalizeRoleKey(role)).filter(Boolean)
}

export function shouldPersistStoredSession(meta = getStoredAuthMeta()) {
  if (getStoredRememberMePreference()) {
    return true
  }
  return !getStoredRoleKeys(meta).includes('school-it')
}

export function clearStoredSessionArtifacts() {
  if (typeof window === 'undefined' || typeof window.localStorage === 'undefined') {
    return
  }

  window.localStorage.removeItem(SESSION_TOKEN_STORAGE_KEY)
  window.localStorage.removeItem(USER_ROLES_STORAGE_KEY)
  window.localStorage.removeItem(DASHBOARD_CACHE_STORAGE_KEY)
  window.sessionStorage?.removeItem?.(NATIVE_RUNTIME_SESSION_KEY)
  clearStoredAuthMeta()
}

export function markCurrentRuntimeSession() {
  if (typeof window === 'undefined' || typeof window.sessionStorage === 'undefined') {
    return
  }

  try {
    window.sessionStorage.setItem(NATIVE_RUNTIME_SESSION_KEY, '1')
  } catch {
    // Ignore sessionStorage failures and keep auth usable.
  }
}

function hasCurrentRuntimeSession() {
  if (typeof window === 'undefined' || typeof window.sessionStorage === 'undefined') {
    return false
  }

  try {
    return window.sessionStorage.getItem(NATIVE_RUNTIME_SESSION_KEY) === '1'
  } catch {
    return false
  }
}

export function bootstrapStoredSessionPersistence() {
  if (!Capacitor.isNativePlatform()) return
  if (shouldPersistStoredSession()) return
  if (hasCurrentRuntimeSession()) return

  clearStoredSessionArtifacts()
}

export function readStoredSessionToken() {
  bootstrapStoredSessionPersistence()

  if (typeof window === 'undefined' || typeof window.localStorage === 'undefined') {
    return ''
  }

  return String(window.localStorage.getItem(SESSION_TOKEN_STORAGE_KEY) || '')
}

export function hasStoredSessionToken() {
  return Boolean(readStoredSessionToken())
}
