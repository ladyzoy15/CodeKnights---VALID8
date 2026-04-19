<template>
  <section class="school-it-reports">
    <div class="school-it-reports__shell">
      <StandardHeader
        class="dashboard-enter dashboard-enter--1"
        :avatar-url="avatarUrl"
        :school-name="activeSchoolSettings?.school_name || activeUser?.school_name || ''"
        :display-name="displayName"
        :initials="initials"
        @logout="handleLogout"
      />

      <div class="school-it-reports__body">
        <header class="school-it-reports__header dashboard-enter dashboard-enter--2">
          <button class="school-it-reports__back" type="button" @click="goBack" aria-label="Go Back">
            <ArrowLeft :size="20" />
          </button>
          <div class="school-it-reports__header-copy">
            <h1 class="school-it-reports__title">Event Reports</h1>
            <p class="school-it-reports__subtitle">View and download school-scoped attendance reports for events across your campus.</p>
          </div>
        </header>

        <section class="school-it-reports__content dashboard-enter dashboard-enter--3">
          <div class="school-it-reports__toolbar">
            <div class="school-it-reports__search-shell">
              <input
                v-model="searchQuery"
                class="school-it-reports__search-input"
                type="text"
                placeholder="Search events by name or location"
              >
              <span class="school-it-reports__search-icon" aria-hidden="true">
                <Search :size="18" :stroke-width="2.5" />
              </span>
            </div>

            <button
              v-if="selectedEvent"
              class="school-it-reports__clear-btn"
              type="button"
              @click="clearSelection"
            >
              <X :size="16" />
              Clear Selection
            </button>
          </div>

          <div class="school-it-reports__table-wrap">
            <table class="school-it-reports__table">
              <thead>
                <tr>
                  <th>Event Name</th>
                  <th>Date</th>
                  <th>Location</th>
                  <th class="school-it-reports__cell--actions">Actions</th>
                </tr>
              </thead>
              <tbody>
                <tr
                  v-for="event in filteredEvents"
                  :key="event.id"
                  class="school-it-reports__table-row"
                  :class="{ 'school-it-reports__table-row--selected': Number(event.id) === selectedEventId }"
                  @click="viewEvent(event)"
                >
                  <td>
                    <div class="school-it-reports__event-name">{{ event.name }}</div>
                  </td>
                  <td>
                    <div class="school-it-reports__event-date">{{ formatDate(event.start_datetime) }}</div>
                  </td>
                  <td>
                    <div class="school-it-reports__event-loc">{{ event.location || 'Unspecified Location' }}</div>
                  </td>
                  <td class="school-it-reports__cell--actions">
                    <div class="school-it-reports__actions-tray">
                      <button class="school-it-reports__btn school-it-reports__btn--view" type="button" @click.stop="viewEvent(event)">
                        {{ Number(event.id) === selectedEventId ? 'Viewing' : 'View Report' }}
                      </button>
                      <button
                        class="school-it-reports__btn school-it-reports__btn--download"
                        type="button"
                        @click.stop="downloadReport(event, 'csv')"
                        :disabled="isDownloading === `${event.id}:csv`"
                      >
                        <Download :size="14" :stroke-width="2.5" />
                        {{ isDownloading === `${event.id}:csv` ? 'Exporting...' : 'CSV' }}
                      </button>
                    </div>
                  </td>
                </tr>
                <tr v-if="!filteredEvents.length">
                  <td colspan="4" class="school-it-reports__empty">
                    {{ isLoading ? 'Loading events...' : 'No events found matching your search.' }}
                  </td>
                </tr>
              </tbody>
            </table>
          </div>

          <section class="school-it-reports__detail">
            <template v-if="selectedEvent">
              <header class="school-it-reports__detail-header">
                <div class="school-it-reports__detail-copy">
                  <h2 class="school-it-reports__detail-title">{{ selectedEventReport?.event_name || selectedEvent.name }}</h2>
                  <p class="school-it-reports__detail-meta">
                    <span>{{ formatDate(selectedEvent.start_datetime) }}</span>
                    <span>•</span>
                    <span>{{ selectedEventReport?.event_location || selectedEvent.location || 'Unspecified Location' }}</span>
                  </p>
                </div>

                <div class="school-it-reports__detail-actions">
                  <button
                    class="school-it-reports__btn school-it-reports__btn--download"
                    type="button"
                    @click="downloadReport(selectedEvent, 'csv')"
                    :disabled="isDownloading === `${selectedEvent.id}:csv`"
                  >
                    <Download :size="14" :stroke-width="2.5" />
                    {{ isDownloading === `${selectedEvent.id}:csv` ? 'Exporting...' : 'Export CSV' }}
                  </button>
                  <button
                    class="school-it-reports__btn school-it-reports__btn--excel"
                    type="button"
                    @click="downloadReport(selectedEvent, 'excel')"
                    :disabled="isDownloading === `${selectedEvent.id}:excel`"
                  >
                    <FileSpreadsheet :size="14" :stroke-width="2.5" />
                    {{ isDownloading === `${selectedEvent.id}:excel` ? 'Exporting...' : 'Export Excel' }}
                  </button>
                </div>
              </header>

              <p v-if="selectionError" class="school-it-reports__banner school-it-reports__banner--error">
                {{ selectionError }}
              </p>

              <p v-else-if="isLoadingSelection" class="school-it-reports__banner">
                Loading attendance records for this event...
              </p>

              <template v-else-if="selectedEventReport">
                <div class="school-it-reports__stats-grid">
                  <article
                    v-for="card in summaryCards"
                    :key="card.id"
                    class="school-it-reports__stat-card"
                  >
                    <span class="school-it-reports__stat-label">{{ card.label }}</span>
                    <strong class="school-it-reports__stat-value">{{ card.value }}</strong>
                    <span class="school-it-reports__stat-meta">{{ card.meta }}</span>
                  </article>
                </div>

                <div class="school-it-reports__insights-grid">
                  <article class="school-it-reports__panel">
                    <header class="school-it-reports__panel-header">
                      <h3 class="school-it-reports__panel-title">Attendance Breakdown</h3>
                      <p class="school-it-reports__panel-copy">Final backend counts for this event.</p>
                    </header>

                    <div class="school-it-reports__segments">
                      <div
                        v-for="segment in overallSegments"
                        :key="segment.id"
                        class="school-it-reports__segment-row"
                      >
                        <div class="school-it-reports__segment-copy">
                          <span>{{ segment.label }}</span>
                          <strong>{{ segment.count }}</strong>
                        </div>
                        <div class="school-it-reports__segment-track">
                          <span
                            class="school-it-reports__segment-fill"
                            :class="`school-it-reports__segment-fill--${segment.id}`"
                            :style="{ width: `${segment.width}%` }"
                          />
                        </div>
                      </div>
                    </div>
                  </article>

                  <article class="school-it-reports__panel">
                    <header class="school-it-reports__panel-header">
                      <h3 class="school-it-reports__panel-title">Program Statistics</h3>
                      <p class="school-it-reports__panel-copy">Per-program attendance from the backend report.</p>
                    </header>

                    <div v-if="programBreakdownRows.length" class="school-it-reports__program-list">
                      <div
                        v-for="row in programBreakdownRows"
                        :key="row.program"
                        class="school-it-reports__program-row"
                      >
                        <div class="school-it-reports__program-header">
                          <div>
                            <strong>{{ row.program }}</strong>
                            <span>{{ row.total }} total students</span>
                          </div>
                          <strong>{{ row.attendanceRate }}%</strong>
                        </div>
                        <div class="school-it-reports__program-track">
                          <span
                            v-for="segment in row.segments"
                            :key="`${row.program}-${segment.id}`"
                            class="school-it-reports__program-fill"
                            :class="`school-it-reports__program-fill--${segment.id}`"
                            :style="{ width: `${segment.width}%` }"
                          />
                        </div>
                        <div class="school-it-reports__program-meta">
                          <span>Present {{ row.present }}</span>
                          <span>Late {{ row.late }}</span>
                          <span>Waiting {{ row.incomplete }}</span>
                          <span>Absent {{ row.absent }}</span>
                        </div>
                      </div>
                    </div>
                    <p v-else class="school-it-reports__panel-empty">
                      No program breakdown is available for this event yet.
                    </p>
                  </article>
                </div>

                <article class="school-it-reports__panel school-it-reports__panel--records">
                  <header class="school-it-reports__panel-header school-it-reports__panel-header--records">
                    <div class="school-it-reports__panel-copy-wrap">
                      <h3 class="school-it-reports__panel-title">Attendance List</h3>
                      <p class="school-it-reports__panel-copy">
                        Latest backend attendance record per student for this event.
                      </p>
                    </div>

                    <div class="school-it-reports__records-tools">
                      <div class="school-it-reports__search-shell school-it-reports__search-shell--records">
                        <input
                          v-model="attendeeQuery"
                          class="school-it-reports__search-input"
                          type="text"
                          placeholder="Search student name or ID"
                        >
                        <span class="school-it-reports__search-icon" aria-hidden="true">
                          <Search :size="18" :stroke-width="2.5" />
                        </span>
                      </div>

                      <div class="school-it-reports__filters">
                        <button
                          v-for="option in attendeeFilterOptions"
                          :key="option.id"
                          class="school-it-reports__filter-pill"
                          :class="{ 'school-it-reports__filter-pill--active': attendeeFilter === option.id }"
                          type="button"
                          @click="attendeeFilter = option.id"
                        >
                          {{ option.label }}
                        </button>
                      </div>
                    </div>
                  </header>

                  <div class="school-it-reports__records-wrap">
                    <table class="school-it-reports__records-table">
                      <thead>
                        <tr>
                          <th>Student ID</th>
                          <th>Name</th>
                          <th>Status</th>
                          <th>Sign In</th>
                          <th>Sign Out</th>
                          <th>Duration</th>
                          <th>Method</th>
                        </tr>
                      </thead>
                      <tbody>
                        <tr v-for="row in filteredAttendanceRows" :key="row.key">
                          <td>{{ row.studentId }}</td>
                          <td>{{ row.studentName }}</td>
                          <td>
                            <span class="school-it-reports__status-chip" :class="`school-it-reports__status-chip--${row.category}`">
                              {{ row.statusLabel }}
                            </span>
                          </td>
                          <td>{{ row.timeInLabel }}</td>
                          <td>{{ row.timeOutLabel }}</td>
                          <td>{{ row.durationLabel }}</td>
                          <td>{{ row.methodLabel }}</td>
                        </tr>
                        <tr v-if="!filteredAttendanceRows.length">
                          <td colspan="7" class="school-it-reports__empty">
                            {{ attendanceRows.length ? 'No attendance records matched the current filters.' : 'No attendance records have been recorded for this event yet.' }}
                          </td>
                        </tr>
                      </tbody>
                    </table>
                  </div>
                </article>
              </template>
            </template>

            <div v-else class="school-it-reports__placeholder">
              <h2>Select an Event</h2>
              <p>
                Choose an event above to load the live attendance summary, student sign-in list,
                and export actions for that event.
              </p>
            </div>
          </section>
        </section>
      </div>
    </div>
  </section>
</template>

<script setup>
import { useSchoolItEventReportsViewModel } from '@/composables/useSchoolItEventReportsViewModel.js'
import { ArrowLeft, Download, FileSpreadsheet, Search, X } from 'lucide-vue-next'
import StandardHeader from '@/components/desktop/dashboard/StandardHeader.vue'

const props = defineProps({
  preview: {
    type: Boolean,
    default: false,
  },
})

const {
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
} = useSchoolItEventReportsViewModel({ preview: props.preview })
</script>

<style scoped>
.school-it-reports {
  min-height: 100vh;
  padding: 30px 28px 120px;
  font-family: 'Manrope', sans-serif;
  background: var(--color-bg);
}

.school-it-reports__shell {
  width: 100%;
  max-width: 1120px;
  margin: 0 auto;
}

.school-it-reports__body {
  display: flex;
  flex-direction: column;
  gap: 24px;
  margin-top: 32px;
}

.school-it-reports__header {
  display: flex;
  align-items: flex-start;
  gap: 16px;
}

.school-it-reports__back {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: transparent;
  border: none;
  cursor: pointer;
  color: var(--color-text-primary);
  transition: background-color 0.2s;
  flex-shrink: 0;
}

.school-it-reports__back:hover {
  background: rgba(255, 255, 255, 0.38);
}

.school-it-reports__header-copy {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.school-it-reports__title {
  margin: 0;
  font-size: 26px;
  font-weight: 800;
  line-height: 1;
  letter-spacing: -0.04em;
  color: var(--color-text-primary);
}

.school-it-reports__subtitle {
  margin: 0;
  font-size: 15px;
  font-weight: 500;
  color: var(--color-text-muted);
}

.school-it-reports__content {
  display: flex;
  flex-direction: column;
  gap: 20px;
  background: var(--color-surface);
  border-radius: 32px;
  padding: 28px;
  border: 1px solid var(--color-surface-border);
  box-shadow: var(--aura-shadow-soft);
}

.school-it-reports__toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 14px;
  flex-wrap: wrap;
}

.school-it-reports__search-shell {
  display: flex;
  align-items: center;
  width: min(100%, 360px);
  height: 46px;
  border-radius: 999px;
  background: var(--color-field-surface);
  border: 1px solid var(--color-surface-border);
  padding: 0 6px 0 20px;
  transition: border-color 0.2s;
}

.school-it-reports__search-shell:focus-within {
  border-color: var(--color-primary, #0057B8);
}

.school-it-reports__search-input {
  flex: 1;
  min-width: 0;
  height: 100%;
  border: none;
  outline: none;
  font-size: 14px;
  color: var(--color-text-primary);
  background: transparent;
}

.school-it-reports__search-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 34px;
  height: 34px;
  border-radius: 50%;
  flex-shrink: 0;
  color: var(--color-text-muted, #9ca3af);
}

.school-it-reports__table-wrap {
  width: 100%;
  overflow-x: auto;
  -webkit-overflow-scrolling: touch;
}

.school-it-reports__table {
  width: 100%;
  min-width: 700px;
  border-collapse: separate;
  border-spacing: 0;
}

.school-it-reports__table th {
  text-align: left;
  padding: 12px 16px;
  font-size: 12px;
  font-weight: 700;
  color: var(--color-text-muted);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  border-bottom: 2px solid var(--color-surface-border);
}

.school-it-reports__table td {
  padding: 16px;
  vertical-align: middle;
  border-bottom: 1px solid var(--color-surface-border);
}

.school-it-reports__event-name {
  font-size: 15px;
  font-weight: 700;
  color: var(--color-primary, #0057B8);
}

.school-it-reports__event-date,
.school-it-reports__event-loc {
  font-size: 14px;
  font-weight: 500;
  color: var(--color-text-muted);
}

.school-it-reports__cell--actions {
  text-align: right;
  width: 220px;
}

.school-it-reports__actions-tray {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.school-it-reports__btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  height: 36px;
  padding: 0 16px;
  border-radius: 999px;
  font-size: 13px;
  font-weight: 700;
  cursor: pointer;
  border: none;
  transition: transform 0.1s, filter 0.2s;
}

.school-it-reports__btn:active {
  transform: scale(0.96);
}

.school-it-reports__btn--view {
  background: var(--color-primary, #0057B8);
  color: var(--color-primary-text, #ffffff);
}

.school-it-reports__btn--download {
  background: var(--color-text-always-dark, #111827);
  color: #ffffff;
}

.school-it-reports__btn--excel {
  background: var(--color-secondary, #FFD400);
  color: var(--color-secondary-text, #111827);
}

.school-it-reports__btn--download:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.school-it-reports__empty {
  text-align: center !important;
  color: var(--color-text-muted);
  padding: 40px !important;
  font-size: 14px;
  font-weight: 500;
}

.school-it-reports__clear-btn,
.school-it-reports__filter-pill {
  border: none;
  cursor: pointer;
  font: inherit;
}

.school-it-reports__clear-btn {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  min-height: 42px;
  padding: 0 16px;
  border-radius: 999px;
  background: var(--color-field-surface);
  color: var(--color-text-primary);
  border: 1px solid var(--color-surface-border);
  box-shadow: var(--aura-shadow-soft);
}

.school-it-reports__table-row {
  transition: background-color 0.2s ease;
}

.school-it-reports__table-row:hover {
  background: var(--color-field-surface);
}

.school-it-reports__table-row--selected {
  background: color-mix(in srgb, var(--color-primary) 15%, transparent);
}

.school-it-reports__detail {
  display: flex;
  flex-direction: column;
  gap: 20px;
  border-radius: 28px;
  background: var(--color-field-surface);
  border: 1px solid var(--color-surface-border);
  padding: 24px;
}

.school-it-reports__detail-header,
.school-it-reports__panel-header,
.school-it-reports__records-tools {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
  flex-wrap: wrap;
}

.school-it-reports__detail-copy,
.school-it-reports__panel-copy-wrap {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.school-it-reports__detail-title,
.school-it-reports__panel-title {
  margin: 0;
  color: var(--color-text-primary);
}

.school-it-reports__detail-title {
  font-size: 22px;
  font-weight: 800;
}

.school-it-reports__panel-title {
  font-size: 18px;
  font-weight: 800;
}

.school-it-reports__detail-meta,
.school-it-reports__panel-copy {
  margin: 0;
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
  color: var(--color-text-muted);
  font-size: 14px;
}

.school-it-reports__detail-actions,
.school-it-reports__filters {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
}

.school-it-reports__banner,
.school-it-reports__placeholder {
  border-radius: 24px;
  padding: 18px 20px;
  background: color-mix(in srgb, var(--color-primary) 10%, transparent);
  color: var(--color-text-primary);
}

.school-it-reports__banner--error {
  background: color-mix(in srgb, #ef4444 12%, white);
  color: #991b1b;
}

.school-it-reports__placeholder {
  text-align: center;
}

.school-it-reports__placeholder h2 {
  margin: 0 0 10px;
}

.school-it-reports__placeholder p {
  margin: 0;
  color: var(--color-text-muted);
  line-height: 1.7;
}

.school-it-reports__stats-grid,
.school-it-reports__insights-grid {
  display: grid;
  gap: 14px;
}

.school-it-reports__stats-grid {
  grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
}

.school-it-reports__insights-grid {
  grid-template-columns: repeat(2, minmax(0, 1fr));
}

.school-it-reports__stat-card,
.school-it-reports__panel {
  border-radius: 24px;
  background: var(--color-surface);
  border: 1px solid var(--color-surface-border);
  box-shadow: var(--aura-shadow-soft);
}

.school-it-reports__stat-card {
  display: flex;
  flex-direction: column;
  gap: 8px;
  min-height: 134px;
  padding: 18px;
}

.school-it-reports__stat-label {
  font-size: 12px;
  font-weight: 800;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: var(--color-text-muted);
}

.school-it-reports__stat-value {
  font-size: 28px;
  line-height: 1;
  color: var(--color-primary, #0057B8);
}

.school-it-reports__stat-meta {
  font-size: 13px;
  line-height: 1.55;
  color: var(--color-text-muted);
}

.school-it-reports__panel {
  padding: 22px;
}

.school-it-reports__segments,
.school-it-reports__program-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.school-it-reports__segment-row,
.school-it-reports__program-row {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.school-it-reports__segment-copy,
.school-it-reports__program-meta {
  font-size: 13px;
  color: var(--color-text-muted);
}

.school-it-reports__segment-copy strong,
.school-it-reports__program-header strong {
  color: var(--color-text-primary);
}

.school-it-reports__segment-track,
.school-it-reports__program-track {
  position: relative;
  width: 100%;
  height: 12px;
  overflow: hidden;
  border-radius: 999px;
  background: var(--color-surface-border);
}

.school-it-reports__segment-fill,
.school-it-reports__program-fill {
  display: block;
  height: 100%;
  border-radius: 999px;
}

.school-it-reports__segment-fill--present,
.school-it-reports__program-fill--present {
  background: var(--color-primary, #0057B8);
}

.school-it-reports__segment-fill--late,
.school-it-reports__program-fill--late {
  background: #f59e0b;
}

.school-it-reports__segment-fill--waiting,
.school-it-reports__program-fill--waiting {
  background: #64748b;
}

.school-it-reports__segment-fill--absent,
.school-it-reports__program-fill--absent {
  background: #ef4444;
}

.school-it-reports__panel-empty {
  margin: 0;
  color: var(--color-text-muted);
  line-height: 1.7;
}

.school-it-reports__panel--records {
  overflow: hidden;
}

.school-it-reports__panel-header--records {
  margin-bottom: 18px;
}

.school-it-reports__search-shell--records {
  width: min(100%, 320px);
}

.school-it-reports__filters {
  justify-content: flex-end;
}

.school-it-reports__filter-pill {
  min-height: 38px;
  padding: 0 14px;
  border-radius: 999px;
  background: var(--color-field-surface);
  color: var(--color-text-muted);
  font-size: 13px;
  font-weight: 700;
}

.school-it-reports__filter-pill--active {
  background: var(--color-secondary, #FFD400);
  color: var(--color-secondary-text, #111827);
}

.school-it-reports__records-wrap {
  overflow-x: auto;
}

.school-it-reports__records-table {
  width: 100%;
  min-width: 720px;
  border-collapse: separate;
  border-spacing: 0;
}

.school-it-reports__records-table th,
.school-it-reports__records-table td {
  padding: 16px;
  vertical-align: middle;
  border-bottom: 1px solid var(--color-surface-border);
}

.school-it-reports__records-table th {
  text-align: left;
  font-size: 12px;
  font-weight: 700;
  color: var(--color-text-muted);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.school-it-reports__status-chip {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-height: 30px;
  padding: 0 12px;
  border-radius: 999px;
  font-size: 12px;
  font-weight: 800;
}

.school-it-reports__status-chip--present {
  background: color-mix(in srgb, var(--color-primary) 15%, transparent);
  color: var(--color-primary);
}

.school-it-reports__status-chip--late {
  background: rgba(245, 158, 11, 0.16);
  color: #f59e0b;
}

.school-it-reports__status-chip--waiting {
  background: var(--color-field-surface);
  color: var(--color-text-muted);
}

.school-it-reports__status-chip--absent {
  background: rgba(239, 68, 68, 0.16);
  color: #ef4444;
}

@media (max-width: 960px) {
  .school-it-reports__insights-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 720px) {
  .school-it-reports__content,
  .school-it-reports__detail {
    padding: 20px;
  }

  .school-it-reports__toolbar,
  .school-it-reports__records-tools {
    align-items: stretch;
  }

  .school-it-reports__search-shell,
  .school-it-reports__search-shell--records {
    width: 100%;
  }

  .school-it-reports__stats-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 560px) {
  .school-it-reports__stats-grid {
    grid-template-columns: 1fr;
  }

  .school-it-reports__detail-title {
    font-size: 20px;
  }
}
</style>
