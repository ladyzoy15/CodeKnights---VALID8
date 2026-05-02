function normalizeContext(value = '') {
  return String(value || '')
    .trim()
    .toLowerCase()
    .replace(/[\s-]+/g, '_')
}

function getRoutePath(routeOrPath = '') {
  if (routeOrPath && typeof routeOrPath === 'object') {
    return String(routeOrPath.path || '')
  }
  return String(routeOrPath || '')
}

export function isGovernancePreviewPath(path = '') {
  const normalizedPath = getRoutePath(path)
  return normalizedPath.startsWith('/exposed/governance') || normalizedPath.startsWith('/exposed/sg')
}

function resolveContextFromPath(path = '') {
  const normalizedPath = getRoutePath(path)

  if (normalizedPath.startsWith('/exposed/admin')) return 'admin_preview'
  if (normalizedPath.startsWith('/exposed/workspace')) return 'workspace_preview'
  if (normalizedPath.startsWith('/exposed/sg')) return 'sg_preview'
  if (normalizedPath.startsWith('/exposed/dashboard')) return 'dashboard_preview'
  if (normalizedPath.startsWith('/admin')) return 'admin'
  if (normalizedPath.startsWith('/workspace')) return 'workspace'
  if (normalizedPath.startsWith('/sg')) return 'sg'
  if (normalizedPath.startsWith('/dashboard')) return 'dashboard'
  return 'dashboard'
}

export function resolveWorkspaceContext(routeOrPath = null) {
  if (routeOrPath && typeof routeOrPath === 'object') {
    const matchedRecords = Array.isArray(routeOrPath.matched) ? [...routeOrPath.matched].reverse() : []
    const matchedContext = matchedRecords
      .map((record) => normalizeContext(record?.meta?.workspaceContext))
      .find(Boolean)

    if (matchedContext) {
      return matchedContext
    }

    const metaContext = normalizeContext(routeOrPath?.meta?.workspaceContext)
    if (metaContext) {
      return metaContext
    }
  }

  return resolveContextFromPath(routeOrPath)
}

export function isPreviewWorkspaceContext(routeOrContext = null) {
  const context = normalizeContext(
    typeof routeOrContext === 'string'
      ? routeOrContext
      : resolveWorkspaceContext(routeOrContext)
  )
  return context.endsWith('_preview')
}

export function hasGovernancePreviewAccess(routeOrContext = null) {
  const context = normalizeContext(
    typeof routeOrContext === 'string'
      ? routeOrContext
      : resolveWorkspaceContext(routeOrContext)
  )
  return context === 'sg_preview' || context === 'governance_preview'
}

export function isGovernanceWorkspaceContext(routeOrContext = null) {
  const context = normalizeContext(
    typeof routeOrContext === 'string'
      ? routeOrContext
      : resolveWorkspaceContext(routeOrContext)
  )
  return context === 'sg' || context === 'sg_preview' || context === 'governance' || context === 'governance_preview'
}

export function isCouncilWorkspaceContext(routeOrContext = null) {
  return isGovernanceWorkspaceContext(routeOrContext)
}

export function resolveStudentHomeLocation(routeOrPath = null) {
  return isPreviewWorkspaceContext(routeOrPath)
    ? { name: 'PreviewHome' }
    : { name: 'Home' }
}

export function isGatherWelcomePath(path = '') {
  const normalizedPath = getRoutePath(path)
  return normalizedPath.includes('/gather') && !normalizedPath.includes('/attendance')
}

export function resolveGatherWelcomeLocation(routeOrPath = null) {
  const context = resolveWorkspaceContext(routeOrPath)
  switch (context) {
    case 'dashboard_preview':
      return { name: 'PreviewGatherWelcome' }
    case 'sg':
    case 'governance':
      return { name: 'SgGatherWelcome' }
    default:
      return { name: 'GatherWelcome' }
  }
}

export function resolveGatherAttendanceLocation(routeOrPath = null) {
  const context = resolveWorkspaceContext(routeOrPath)
  switch (context) {
    case 'dashboard_preview':
      return { name: 'PreviewGatherAttendance' }
    case 'sg':
    case 'governance':
      return { name: 'SgGatherAttendance' }
    default:
      return { name: 'GatherAttendance' }
  }
}

export function resolveGatherEntryLocation(routeOrPath = null) {
  const context = resolveWorkspaceContext(routeOrPath)
  switch (context) {
    case 'dashboard_preview':
      return { name: 'PreviewGatherWelcome' }
    case 'sg':
    case 'governance':
      return { name: 'SgGatherWelcome' }
    default:
      return { name: 'GatherWelcome' }
  }
}

export function resolveChatLocation(routeOrPath = null) {
  const context = resolveWorkspaceContext(routeOrPath)
  switch (context) {
    case 'admin':
      return { name: 'AdminAuraChat' }
    case 'admin_preview':
      return { name: 'PreviewAdminAuraChat' }
    case 'workspace':
      return { name: 'SchoolItAuraChat' }
    case 'workspace_preview':
      return { name: 'PreviewSchoolItAuraChat' }
    case 'sg':
    case 'governance':
      return { name: 'SgAuraChat' }
    case 'sg_preview':
    case 'governance_preview':
      return { name: 'PreviewSgAuraChat' }
    case 'dashboard_preview':
      return { name: 'PreviewDashboardAuraChat' }
    default:
      return { name: 'AuraChat' }
  }
}

export function resolveWorkspaceHomeLocation(routeOrPath = null) {
  const context = resolveWorkspaceContext(routeOrPath)
  switch (context) {
    case 'admin':
      return { name: 'AdminHome' }
    case 'admin_preview':
      return { name: 'PreviewAdminHome' }
    case 'workspace':
      return { name: 'SchoolItHome' }
    case 'workspace_preview':
      return { name: 'PreviewSchoolItHome' }
    case 'sg':
    case 'governance':
      return { name: 'SgDashboard' }
    case 'sg_preview':
    case 'governance_preview':
      return { name: 'PreviewSgDashboard' }
    default:
      return resolveStudentHomeLocation(routeOrPath)
  }
}

export function resolveGovernanceWorkspaceLocation(routeOrPath = null) {
  return isPreviewWorkspaceContext(routeOrPath)
    ? { name: 'PreviewSgDashboard' }
    : { name: 'SgDashboard' }
}

export function resolveCouncilWorkspaceLocation(routeOrPath = null) {
  return resolveGovernanceWorkspaceLocation(routeOrPath)
}

export function resolveEventListLocation(routeOrPath = null) {
  switch (resolveWorkspaceContext(routeOrPath)) {
    case 'sg':
      return { name: 'SgEvents' }
    case 'workspace':
      return { name: 'SchoolItSchedule' }
    case 'workspace_preview':
      return { name: 'PreviewSchoolItSchedule' }
    case 'sg_preview':
    case 'dashboard_preview':
      return { name: 'PreviewDashboardSchedule' }
    default:
      return { name: 'Schedule' }
  }
}

export function resolveEventDetailLocation(routeOrPath = null, eventId = null) {
  const normalizedEventId = Number(eventId)
  const params = Number.isFinite(normalizedEventId)
    ? { id: String(normalizedEventId) }
    : {}

  switch (resolveWorkspaceContext(routeOrPath)) {
    case 'sg':
      return { name: 'SgEventDetail', params }
    case 'workspace':
      return { name: 'SchoolItEventDetail', params }
    case 'workspace_preview':
      return { name: 'PreviewSchoolItEventDetail', params }
    case 'sg_preview':
    case 'dashboard_preview':
      return { name: 'PreviewEventDetail', params }
    default:
      return { name: 'EventDetail', params }
  }
}

export function resolveAttendanceLocation(routeOrPath = null, eventId = null) {
  const normalizedEventId = Number(eventId)
  const params = Number.isFinite(normalizedEventId)
    ? { id: String(normalizedEventId) }
    : {}

  switch (resolveWorkspaceContext(routeOrPath)) {
    case 'dashboard_preview':
      return { name: 'PreviewAttendance', params }
    case 'workspace_preview':
    case 'sg_preview':
    case 'admin_preview':
      return resolveEventDetailLocation(routeOrPath, eventId)
    default:
      return {
        name: 'Attendance',
        params,
      }
  }
}

export function resolveBackFallbackLocation(routeOrPath = null, options = {}) {
  const currentPath = getRoutePath(routeOrPath)

  if (currentPath.includes('/attendance')) {
    return resolveEventDetailLocation(routeOrPath, options?.eventId)
  }

  if (currentPath.includes('/schedule/') || currentPath.includes('/events/')) {
    return resolveEventListLocation(routeOrPath)
  }

  return resolveStudentHomeLocation(routeOrPath)
}

export function withPreservedGovernancePreviewQuery(route = null, target = null) {
  if (!route || !target) return target
  const query = route.query || {}

  if (!query.preview && !query.unit && !query.variant) return target

  const targetObj = typeof target === 'string' ? { path: target } : { ...target }
  targetObj.query = { ...query, ...(targetObj.query || {}) }
  return targetObj
}

export function hasNavigableHistory(routeOrPath = null) {
  if (typeof window === 'undefined') return false

  const currentPath = getRoutePath(routeOrPath)
  const backTarget = window.history.state?.back

  return Boolean(backTarget && backTarget !== currentPath)
}
