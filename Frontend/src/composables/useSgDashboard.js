import { ref, watch, computed } from 'vue'
import { useDashboardSession } from '@/composables/useDashboardSession.js'
import { getGovernanceAccess } from '@/services/backendApi.js'
import { resolvePreferredGovernanceUnit } from '@/services/governanceScope.js'

// Global state cache for instant navigation without loading skeletons
const cachedIsLoading = ref(true)
const cachedError = ref('')
const cachedPermissions = ref([])
const cachedOfficerPosition = ref('')
const cachedAcronym = ref('SSG')
const cachedUnitName = ref('Student Government')
const cachedActiveUnitId = ref(null)
let hasFetched = false

/**
 * Composable for the SG Dashboard.
 */
export function useSgDashboard(preview = false) {
  const { dashboardState, apiBaseUrl, token } = useDashboardSession()

  const isLoading = preview ? ref(false) : cachedIsLoading
  const error = preview ? ref('') : cachedError
  const permissionCodes = preview ? ref([]) : cachedPermissions
  const officerPosition = preview ? ref('President') : cachedOfficerPosition
  const acronym = preview ? ref('SSG') : cachedAcronym
  const unitName = preview ? ref('Supreme Student Government') : cachedUnitName
  const activeUnitId = preview ? ref(1) : cachedActiveUnitId

  const currentUser = computed(() => dashboardState.user)
  const schoolSettings = computed(() => dashboardState.schoolSettings)

  const officerName = computed(() => {
    const user = currentUser.value
    if (!user) return ''
    return [user.first_name, user.last_name].filter(Boolean).join(' ').trim() || user.email || 'Officer'
  })

  const schoolName = computed(() => schoolSettings.value?.school_name || 'University')
  const schoolLogo = computed(() => schoolSettings.value?.logo_url || null)

  if (preview) {
    return {
      isLoading, error, permissionCodes, officerPosition,
      officerName, acronym, unitName, currentUser, schoolSettings, schoolName, schoolLogo,
      activeUnitId,
    }
  }

  watch(
    [apiBaseUrl, token, () => dashboardState.initialized],
    async ([url, authToken, isInit]) => {
      if (!isInit || !url || !authToken) return

      if (hasFetched) {
        getGovernanceAccess(url, authToken).then(access => updateCache(access, dashboardState.user)).catch(() => {})
        return
      }

      cachedIsLoading.value = true
      cachedError.value = ''

      try {
        const access = await getGovernanceAccess(url, authToken)
        updateCache(access, dashboardState.user)
        hasFetched = true
      } catch (err) {
        cachedError.value = err?.message || 'Unable to load SG governance data.'
      } finally {
        cachedIsLoading.value = false
      }
    },
    { immediate: true }
  )

  function updateCache(access, user) {
    const governanceUnit = resolvePreferredGovernanceUnit(access)

    if (!governanceUnit) {
      cachedPermissions.value = []
      cachedOfficerPosition.value = ''
      cachedAcronym.value = 'SG'
      cachedUnitName.value = 'Student Government'
      cachedActiveUnitId.value = null
      cachedError.value = 'You do not have access to a governance unit.'
      return
    }

    const unitPerms = Array.isArray(governanceUnit.permission_codes) ? governanceUnit.permission_codes : []
    const topPerms = Array.isArray(access.permission_codes) ? access.permission_codes : []
    cachedPermissions.value = [...new Set([...unitPerms, ...topPerms])]

    cachedActiveUnitId.value = governanceUnit.governance_unit_id ?? null
    cachedAcronym.value = governanceUnit.unit_code || 'SG'
    cachedUnitName.value = governanceUnit.unit_name || 'Student Government'

    const ssgProfile = user?.ssg_profile
    let rawPos = 
      governanceUnit?.position_title || 
      governanceUnit?.member?.position_title || 
      governanceUnit?.role || 
      governanceUnit?.member?.role || 
      ssgProfile?.position_title || 
      ssgProfile?.role || 
      ''
    
    if (rawPos) {
      cachedOfficerPosition.value = String(rawPos).charAt(0).toUpperCase() + String(rawPos).slice(1)
    } else {
      cachedOfficerPosition.value = ''
    }
  }

  return {
    isLoading, error, permissionCodes, officerPosition,
    officerName, acronym, unitName, currentUser, schoolSettings, schoolName, schoolLogo,
    activeUnitId,
  }
}
