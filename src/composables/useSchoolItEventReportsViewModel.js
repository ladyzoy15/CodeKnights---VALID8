import { computed, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuth } from '@/composables/useAuth.js'
import { useDashboardSession } from '@/composables/useDashboardSession.js'
import { useStoredAuthMeta } from '@/composables/useStoredAuthMeta.js'
import { filterWorkspaceEntitiesBySchool } from '@/services/workspaceScope.js'
import {
  getEventAttendance,
  getEventAttendanceReport,
  getEvents,
  resolveApiBaseUrl,
} from '@/services/backendApi.js'
import { useSchoolItPreviewStore } from '@/composables/useSchoolItPreviewStore.js'

export function useSchoolItEventReportsViewModel(options = { preview: false }) {
  const router = useRouter()
  const route = useRoute()
  const { logout } = useAuth()
  const authMeta = useStoredAuthMeta()
  const {
    currentUser,
    schoolSettings,
    apiBaseUrl,
    initializeDashboardSession,
    refreshSchoolSettings,
  } = useDashboardSession()
  const { state: previewState } = useSchoolItPreviewStore()

  // --- STATE ---
  const searchQuery = ref('')
  const attendeeQuery = ref('')
  const attendeeFilter = ref('all')
  const isDownloading = ref('')
  const eventsList = ref([])
  const isLoadingEvents = ref(true)
  const selectedEventId = ref(null)
  const selectedEventReport = ref(null)
  const selectedEventAttendanceRecords = ref([])
  const isLoadingSelection = ref(false)
  const selectionError = ref('')

  const attendeeFilterOptions = [
    { id: 'all', label: 'All' },
    { id: 'waiting', label: 'Waiting' },
    { id: 'present', label: 'Present' },
    { id: 'late', label: 'Late' },
    { id: 'absent', label: 'Absent' },
  ]

  const eventBundleCache = new Map()
  let latestSelectionRequest = 0

  // --- COMPUTED ---
  const activeUser = computed(() => (options.preview ? previewState.user : currentUser.value))
  const activeSchoolSettings = computed(() => (options.preview ? previewState.schoolSettings : schoolSettings.value))
  const schoolId = computed(() => Number(activeUser.value?.school_id ?? activeSchoolSettings.value?.school_id ?? authMeta.value?.schoolId))
  
  const activeEvents = computed(() => (
    options.preview
      ? (Array.isArray(previewState.events) ? previewState.events : [])
      : eventsList.value
  ))

  const filteredBySchoolEvents = computed(() => filterWorkspaceEntitiesBySchool(activeEvents.value, schoolId.value))

  const displayName = computed(() => {
    const first = activeUser.value?.first_name || authMeta.value?.firstName || ''
    const middle = activeUser.value?.middle_name || ''
    const last = activeUser.value?.last_name || authMeta.value?.lastName || ''
    return [first, middle, last].filter(Boolean).join(' ')
      || activeUser.value?.email?.split('@')[0]
      || authMeta.value?.email?.split('@')[0]
      || 'Campus Admin'
  })

  const initials = computed(() => {
    const parts = String(displayName.value || '').split(' ').filter(Boolean)
    if (parts.length >= 2) return `${parts[0][0]}${parts[parts.length - 1][0]}`.toUpperCase()
    return String(displayName.value || '').slice(0, 2).toUpperCase()
  })

  const avatarUrl = computed(() => activeUser.value?.avatar_url || '')

  const filteredEvents = computed(() => {
    const query = String(searchQuery.value || '').trim().toLowerCase()
    const baseList = [...filteredBySchoolEvents.value]
      .sort((left, right) => new Date(right?.start_datetime || 0).getTime() - new Date(left?.start_datetime || 0).getTime())

    if (!query) return baseList

    return baseList.filter((event) => {
      const haystack = [event?.name, event?.location].filter(Boolean).join(' ').toLowerCase()
      return haystack.includes(query)
    })
  })

  const selectedEvent = computed(() => (
    filteredBySchoolEvents.value.find((event) => Number(event?.id) === Number(selectedEventId.value)) || null
  ))

  const attendanceRows = computed(() => dedupeAttendanceRows(selectedEventAttendanceRecords.value))

  const filteredAttendanceRows = computed(() => {
    const query = String(attendeeQuery.value || '').trim().toLowerCase()

    return attendanceRows.value.filter((row) => {
      if (attendeeFilter.value !== 'all' && row.category !== attendeeFilter.value) {
        return false
      }

      if (!query) return true

      return [
        row.studentId,
        row.studentName,
        row.statusLabel,
        row.methodLabel,
      ].filter(Boolean).join(' ').toLowerCase().includes(query)
    })
  })

  const presentCount = computed(() => Math.max(
    Number(selectedEventReport.value?.attendees || 0) - Number(selectedEventReport.value?.late_attendees || 0),
    0,
  ))

  const summaryCards = computed(() => {
    const report = selectedEventReport.value
    if (!report) return []

    return [
      {
        id: 'participants',
        label: 'Total Participants',
        value: formatWholeNumber(report.total_participants),
        meta: 'Students inside the backend event scope',
      },
      {
        id: 'completed',
        label: 'Completed Attendance',
        value: formatWholeNumber(report.attendees),
        meta: 'Students with finalized sign-in and sign-out',
      },
      {
        id: 'late',
        label: 'Late Attendees',
        value: formatWholeNumber(report.late_attendees),
        meta: 'Marked late after the backend cutoff',
      },
      {
        id: 'waiting',
        label: 'Waiting for Sign Out',
        value: formatWholeNumber(report.incomplete_attendees),
        meta: 'Signed in but not fully finalized yet',
      },
      {
        id: 'absent',
        label: 'Absent',
        value: formatWholeNumber(report.absentees),
        meta: 'No completed attendance returned by the backend',
      },
      {
        id: 'rate',
        label: 'Attendance Rate',
        value: `${formatPercentage(report.attendance_rate)}%`,
        meta: 'Completed attendance versus total participants',
      },
    ]
  })

  const overallSegments = computed(() => {
    const report = selectedEventReport.value
    if (!report) return []

    const total = Math.max(Number(report.total_participants || 0), 1)
    return [
      {
        id: 'present',
        label: 'Present',
        count: presentCount.value,
        width: roundPercent((presentCount.value / total) * 100),
      },
      {
        id: 'late',
        label: 'Late',
        count: Number(report.late_attendees || 0),
        width: roundPercent((Number(report.late_attendees || 0) / total) * 100),
      },
      {
        id: 'waiting',
        label: 'Waiting',
        count: Number(report.incomplete_attendees || 0),
        width: roundPercent((Number(report.incomplete_attendees || 0) / total) * 100),
      },
      {
        id: 'absent',
        label: 'Absent',
        count: Number(report.absentees || 0),
        width: roundPercent((Number(report.absentees || 0) / total) * 100),
      },
    ].filter((segment) => segment.count > 0 || segment.id === 'present')
  })

  const programBreakdownRows = computed(() => {
    const rows = Array.isArray(selectedEventReport.value?.program_breakdown)
      ? selectedEventReport.value.program_breakdown
      : []

    return rows.map((row) => {
      const total = Math.max(Number(row?.total || 0), 0)
      const present = Number(row?.present || 0)
      const late = Number(row?.late || 0)
      const incomplete = Number(row?.incomplete || 0)
      const absent = Number(row?.absent || 0)

      return {
        program: row?.program || 'Unknown Program',
        total,
        present,
        late,
        incomplete,
        absent,
        attendanceRate: total > 0 ? roundPercent(((present + late) / total) * 100) : 0,
        segments: [
          { id: 'present', width: total > 0 ? roundPercent((present / total) * 100) : 0 },
          { id: 'late', width: total > 0 ? roundPercent((late / total) * 100) : 0 },
          { id: 'waiting', width: total > 0 ? roundPercent((incomplete / total) * 100) : 0 },
          { id: 'absent', width: total > 0 ? roundPercent((absent / total) * 100) : 0 },
        ].filter((segment) => segment.width > 0),
      }
    })
  })

  // --- METHODS ---
  const fetchEvents = async () => {
    isLoadingEvents.value = true

    if (options.preview) {
      isLoadingEvents.value = false
      return
    }

    try {
      const token = localStorage.getItem('aura_token') || ''
      eventsList.value = await getEvents(apiBaseUrl.value || resolveApiBaseUrl(), token)
    } catch (error) {
      selectionError.value = error?.message || 'Unable to load the event list right now.'
    } finally {
      isLoadingEvents.value = false
    }
  }

  const viewEvent = async (event, { updateRoute = true, force = false } = {}) => {
    const normalizedEventId = Number(event?.id)
    if (!Number.isFinite(normalizedEventId)) return null

    if (updateRoute && normalizeEventId(route.query.eventId) !== normalizedEventId) {
      router.replace({
        query: {
          ...route.query,
          eventId: String(normalizedEventId),
        },
      }).catch(() => null)
    }

    if (!force && selectedEventId.value === normalizedEventId && selectedEventReport.value) {
      return {
        report: selectedEventReport.value,
        records: selectedEventAttendanceRecords.value,
      }
    }

    selectedEventId.value = normalizedEventId
    attendeeQuery.value = ''
    attendeeFilter.value = 'all'
    selectionError.value = ''
    isLoadingSelection.value = true

    const requestId = ++latestSelectionRequest

    try {
      const bundle = await getEventReportBundle(event)
      if (requestId !== latestSelectionRequest) return null

      selectedEventReport.value = bundle.report
      selectedEventAttendanceRecords.value = bundle.records
      return bundle
    } catch (error) {
      if (requestId !== latestSelectionRequest) return null

      selectedEventReport.value = null
      selectedEventAttendanceRecords.value = []
      selectionError.value = resolveSelectionError(error)
      return null
    } finally {
      if (requestId === latestSelectionRequest) {
        isLoadingSelection.value = false
      }
    }
  }

  const syncSelectionFromRoute = async () => {
    const requestedEventId = normalizeEventId(route.query.eventId)

    if (!requestedEventId) {
      if (selectedEventId.value != null) {
        clearSelection({ updateRoute: false })
      }
      return
    }

    if (requestedEventId === Number(selectedEventId.value) && (selectedEventReport.value || isLoadingSelection.value)) {
      return
    }

    const event = filteredBySchoolEvents.value.find((entry) => Number(entry?.id) === requestedEventId)
    if (!event) {
      if (!isLoadingEvents.value) {
        clearSelection({ updateRoute: false })
      }
      return
    }

    await viewEvent(event, { updateRoute: false })
  }

  const getEventReportBundle = async (event) => {
    const normalizedEventId = Number(event?.id)
    if (!Number.isFinite(normalizedEventId)) {
      throw new Error('This event could not be opened.')
    }

    if (eventBundleCache.has(normalizedEventId)) {
      return eventBundleCache.get(normalizedEventId)
    }

    const bundle = options.preview
      ? buildPreviewBundle(event)
      : await fetchLiveEventBundle(normalizedEventId)

    eventBundleCache.set(normalizedEventId, bundle)
    return bundle
  }

  const fetchLiveEventBundle = async (eventId) => {
    const token = localStorage.getItem('aura_token') || ''
    const resolvedBaseUrl = apiBaseUrl.value || resolveApiBaseUrl()

    const [report, records] = await Promise.all([
      getEventAttendanceReport(resolvedBaseUrl, token, eventId),
      getEventAttendance(resolvedBaseUrl, token, eventId, { active_only: false }),
    ])

    return {
      report,
      records: Array.isArray(records) ? records : [],
    }
  }

  const clearSelection = ({ updateRoute = true } = {}) => {
    latestSelectionRequest += 1
    selectedEventId.value = null
    selectedEventReport.value = null
    selectedEventAttendanceRecords.value = []
    attendeeQuery.value = ''
    attendeeFilter.value = 'all'
    selectionError.value = ''
    isLoadingSelection.value = false

    if (updateRoute) {
      const nextQuery = { ...route.query }
      delete nextQuery.eventId
      router.replace({ query: nextQuery }).catch(() => null)
    }
  }

  const downloadReport = async (event, format = 'csv') => {
    const normalizedEventId = Number(event?.id)
    if (!Number.isFinite(normalizedEventId)) return

    const downloadKey = `${normalizedEventId}:${format}`
    if (isDownloading.value === downloadKey) return
    isDownloading.value = downloadKey

    try {
      const bundle = await viewEvent(event, {
        updateRoute: true,
        force: selectedEventId.value !== normalizedEventId,
      }) || await getEventReportBundle(event)

      const exportRows = dedupeAttendanceRows(bundle?.records || [])
      if (format === 'excel') {
        downloadExcelReport(event, bundle?.report, exportRows)
      } else {
        downloadCsvReport(event, bundle?.report, exportRows)
      }
    } catch (error) {
      selectionError.value = resolveSelectionError(error)
    } finally {
      isDownloading.value = ''
    }
  }

  const goBack = () => {
    if (options.preview) router.push({ name: 'PreviewSchoolItSchedule' })
    else router.push({ name: 'SchoolItSchedule' })
  }

  const handleLogout = async () => {
    await logout()
  }

  // --- LIFECYCLE ---
  onMounted(async () => {
    if (!options.preview) {
      await initializeDashboardSession().catch(() => null)
      if (!schoolSettings.value) {
        await refreshSchoolSettings().catch(() => null)
      }
    }
    await fetchEvents()
  })

  watch(
    [() => route.query.eventId, filteredBySchoolEvents, isLoadingEvents],
    () => {
      syncSelectionFromRoute().catch(() => null)
    },
    { immediate: true },
  )

  return {
    searchQuery,
    attendeeQuery,
    attendeeFilter,
    isDownloading,
    isLoadingEvents,
    selectedEventId,
    selectedEventReport,
    isLoadingSelection,
    selectionError,
    attendeeFilterOptions,
    avatarUrl,
    activeSchoolSettings,
    activeUser,
    displayName,
    initials,
    filteredEvents,
    selectedEvent,
    filteredAttendanceRows,
    summaryCards,
    overallSegments,
    programBreakdownRows,
    attendanceRows,
    viewEvent,
    clearSelection,
    downloadReport,
    goBack,
    handleLogout,
    formatDate,
  }
}

// --- HELPER FUNCTIONS (Internal) ---

function buildPreviewBundle(event) {
  const summary = event?.attendance_summary && typeof event.attendance_summary === 'object'
    ? event.attendance_summary
    : {}

  const totalParticipants = Number(summary.total_attendance_records || 0)
  const lateAttendees = Number(summary.late_count || 0)
  const presentAttendees = Number(summary.present_count || 0)
  const incompleteAttendees = Number(summary.incomplete_count || 0)
  const absentees = Number(summary.absent_count || 0)
  const attendees = presentAttendees + lateAttendees

  return {
    report: {
      event_name: event?.name || 'Preview Event',
      event_date: formatDate(event?.start_datetime),
      event_location: event?.location || 'Preview Campus',
      total_participants: totalParticipants,
      attendees,
      late_attendees: lateAttendees,
      incomplete_attendees: incompleteAttendees,
      absentees,
      attendance_rate: totalParticipants > 0 ? roundPercent((attendees / totalParticipants) * 100) : 0,
      programs: [],
      program_breakdown: [],
    },
    records: Array.isArray(event?.attendances) ? event.attendances : [],
  }
}

function downloadCsvReport(event, report, rows) {
  const csvLines = [
    ['Event', report?.event_name || event?.name || 'Event'],
    ['Date', report?.event_date || formatDate(event?.start_datetime)],
    ['Location', report?.event_location || event?.location || 'N/A'],
    [],
    ['Summary'],
    ['Total Participants', formatWholeNumber(report?.total_participants || 0)],
    ['Completed Attendance', formatWholeNumber(report?.attendees || 0)],
    ['Late Attendees', formatWholeNumber(report?.late_attendees || 0)],
    ['Waiting for Sign Out', formatWholeNumber(report?.incomplete_attendees || 0)],
    ['Absent', formatWholeNumber(report?.absentees || 0)],
    ['Attendance Rate', `${formatPercentage(report?.attendance_rate || 0)}%`],
    [],
    ['Student ID', 'Student Name', 'Status', 'Sign In', 'Sign Out', 'Duration', 'Method'],
    ...rows.map((row) => [
      row.studentId,
      row.studentName,
      row.statusLabel,
      row.timeInLabel,
      row.timeOutLabel,
      row.durationLabel,
      row.methodLabel,
    ]),
  ]

  const csvContent = `\uFEFF${csvLines.map((line) => line.map(toCsvField).join(',')).join('\r\n')}`
  const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' })
  triggerFileDownload(blob, `${sanitizeFilename(event?.name || report?.event_name || 'event_report')}.csv`)
}

function downloadExcelReport(event, report, rows) {
  const html = `
    <html>
      <head>
        <meta charset="utf-8">
        <style>
          body { font-family: Arial, sans-serif; padding: 24px; }
          h1 { margin-bottom: 6px; }
          p { margin-top: 0; color: #555; }
          table { border-collapse: collapse; width: 100%; margin-top: 18px; }
          th, td { border: 1px solid #d1d5db; padding: 8px 10px; text-align: left; }
          th { background: #f3f4f6; font-weight: 700; }
          .meta td:first-child { font-weight: 700; width: 220px; }
        </style>
      </head>
      <body>
        <h1>${escapeHtml(report?.event_name || event?.name || 'Event Report')}</h1>
        <p>${escapeHtml(report?.event_date || formatDate(event?.start_datetime))} | ${escapeHtml(report?.event_location || event?.location || 'N/A')}</p>
        <table class="meta">
          <tbody>
            <tr><td>Total Participants</td><td>${escapeHtml(formatWholeNumber(report?.total_participants || 0))}</td></tr>
            <tr><td>Completed Attendance</td><td>${escapeHtml(formatWholeNumber(report?.attendees || 0))}</td></tr>
            <tr><td>Late Attendees</td><td>${escapeHtml(formatWholeNumber(report?.late_attendees || 0))}</td></tr>
            <tr><td>Waiting for Sign Out</td><td>${escapeHtml(formatWholeNumber(report?.incomplete_attendees || 0))}</td></tr>
            <tr><td>Absent</td><td>${escapeHtml(formatWholeNumber(report?.absentees || 0))}</td></tr>
            <tr><td>Attendance Rate</td><td>${escapeHtml(`${formatPercentage(report?.attendance_rate || 0)}%`)}</td></tr>
          </tbody>
        </table>
        <table>
          <thead>
            <tr>
              <th>Student ID</th>
              <th>Student Name</th>
              <th>Status</th>
              <th>Sign In</th>
              <th>Sign Out</th>
              <th>Duration</th>
              <th>Method</th>
            </tr>
          </thead>
          <tbody>
            ${rows.map((row) => `
              <tr>
                <td>${escapeHtml(row.studentId)}</td>
                <td>${escapeHtml(row.studentName)}</td>
                <td>${escapeHtml(row.statusLabel)}</td>
                <td>${escapeHtml(row.timeInLabel)}</td>
                <td>${escapeHtml(row.timeOutLabel)}</td>
                <td>${escapeHtml(row.durationLabel)}</td>
                <td>${escapeHtml(row.methodLabel)}</td>
              </tr>
            `).join('')}
          </tbody>
        </table>
      </body>
    </html>
  `

  const blob = new Blob([`\uFEFF${html}`], {
    type: 'application/vnd.ms-excel;charset=utf-8;',
  })
  triggerFileDownload(blob, `${sanitizeFilename(event?.name || report?.event_name || 'event_report')}.xls`)
}

function dedupeAttendanceRows(records) {
  const latestByStudent = new Map()

  for (const record of Array.isArray(records) ? records : []) {
    const key = resolveAttendanceStudentKey(record)
    const existing = latestByStudent.get(key)
    if (!existing || getAttendanceSortTimestamp(record) > getAttendanceSortTimestamp(existing)) {
      latestByStudent.set(key, record)
    }
  }

  return Array.from(latestByStudent.values())
    .map((record) => buildAttendanceRow(record))
    .sort((left, right) => left.studentName.localeCompare(right.studentName))
}

function buildAttendanceRow(record) {
  const attendance = record?.attendance || {}
  const category = resolveAttendanceCategory(attendance)

  return {
    key: `${resolveAttendanceStudentKey(record)}:${attendance.id ?? attendance.time_in ?? record?.student_name ?? 'row'}`,
    studentId: String(record?.student_id || 'N/A').trim() || 'N/A',
    studentName: String(record?.student_name || 'Unknown Student').trim() || 'Unknown Student',
    statusLabel: resolveAttendanceStatusLabel(attendance),
    category,
    timeInLabel: formatDateTime(attendance.time_in, category === 'absent' ? 'No sign-in record' : 'Not recorded'),
    timeOutLabel: attendance.time_out
      ? formatDateTime(attendance.time_out, 'Not recorded')
      : category === 'waiting'
      ? 'Waiting for sign out'
      : category === 'absent'
      ? 'No sign-out record'
      : 'Not recorded',
    durationLabel: formatDuration(attendance.duration_minutes),
    methodLabel: resolveMethodLabel(attendance.method),
  }
}

function resolveAttendanceStudentKey(record) {
  const numericProfileId = Number(record?.attendance?.student_id)
  if (Number.isFinite(numericProfileId)) return `profile:${numericProfileId}`

  const studentId = String(record?.student_id || '').trim()
  if (studentId) return `student:${studentId}`

  return `name:${String(record?.student_name || '').trim().toLowerCase()}`
}

function resolveAttendanceCategory(attendance = {}) {
  const completionState = String(attendance?.completion_state || '').toLowerCase()
  const displayStatus = String(attendance?.display_status || attendance?.status || '').toLowerCase()

  if (completionState !== 'completed') return 'waiting'
  if (displayStatus === 'late') return 'late'
  if (displayStatus === 'absent') return 'absent'
  return 'present'
}

function resolveAttendanceStatusLabel(attendance = {}) {
  const category = resolveAttendanceCategory(attendance)
  if (category === 'waiting') return 'Waiting for Sign Out'
  if (category === 'late') return 'Late'
  if (category === 'absent') return 'Absent'
  return 'Present'
}

function resolveMethodLabel(method) {
  const normalized = String(method || '').trim().toLowerCase()
  if (normalized === 'face_scan') return 'Face Scan'
  if (normalized === 'manual') return 'Manual'
  return normalized ? normalized.replace(/_/g, ' ') : 'Unknown'
}

function getAttendanceSortTimestamp(record) {
  const attendance = record?.attendance || {}
  const timestamp = new Date(attendance?.time_out || attendance?.time_in || 0).getTime()
  return Number.isFinite(timestamp) ? timestamp : 0
}

function normalizeEventId(value) {
  const rawValue = Array.isArray(value) ? value[0] : value
  const normalized = Number(rawValue)
  return Number.isFinite(normalized) ? normalized : null
}

function formatDate(isoString) {
  if (!isoString) return 'Unspecified Date'
  const normalizedValue = String(isoString)
  const date = /^\d{4}-\d{2}-\d{2}$/.test(normalizedValue)
    ? new Date(`${normalizedValue}T00:00:00`)
    : new Date(normalizedValue)
  if (Number.isNaN(date.getTime())) return String(isoString)
  return new Intl.DateTimeFormat('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
  }).format(date)
}

function formatDateTime(value, fallback = 'Not recorded') {
  if (!value) return fallback
  const parsed = new Date(value)
  if (Number.isNaN(parsed.getTime())) return String(value)

  return new Intl.DateTimeFormat('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
    hour: 'numeric',
    minute: '2-digit',
  }).format(parsed)
}

function formatDuration(value) {
  const minutes = Number(value)
  if (!Number.isFinite(minutes) || minutes <= 0) return 'Not available'
  if (minutes < 60) return `${Math.round(minutes)}m`

  const hours = Math.floor(minutes / 60)
  const remainingMinutes = Math.round(minutes % 60)
  return remainingMinutes > 0 ? `${hours}h ${remainingMinutes}m` : `${hours}h`
}

function roundPercent(value) {
  const normalized = Number(value)
  if (!Number.isFinite(normalized)) return 0
  return Math.max(0, Math.min(100, Math.round(normalized)))
}

function formatPercentage(value) {
  const normalized = Number(value)
  return Number.isFinite(normalized) ? normalized.toFixed(2).replace(/\.00$/, '') : '0'
}

function formatWholeNumber(value) {
  const normalized = Number(value)
  if (!Number.isFinite(normalized)) return '0'
  return Math.round(normalized).toLocaleString('en-US')
}

function sanitizeFilename(value) {
  return String(value || 'event_report')
    .trim()
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, '_')
    .replace(/^_+|_+$/g, '')
    || 'event_report'
}

function toSpreadsheetSafeText(value) {
  const text = String(value ?? '')
  return /^[=+\-@]/.test(text) ? `'${text}` : text
}

function toCsvField(value) {
  return `"${toSpreadsheetSafeText(value).replace(/"/g, '""')}"`
}

function triggerFileDownload(blob, filename) {
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = filename
  link.style.display = 'none'
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  window.setTimeout(() => URL.revokeObjectURL(url), 1000)
}

function escapeHtml(value) {
  return toSpreadsheetSafeText(value)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;')
}

function resolveSelectionError(error) {
  return error?.message || 'Unable to load the attendance report for this event right now.'
}
