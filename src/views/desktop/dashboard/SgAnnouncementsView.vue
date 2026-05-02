<template>
  <section class="sg-sub-page">
    <header class="sg-sub-header dashboard-enter dashboard-enter--1">
      <button class="sg-sub-back" type="button" @click="goBack">
        <ArrowLeft :size="20" />
      </button>
      <h1 class="sg-sub-title">Announcements</h1>
    </header>

    <div v-if="isLoading" class="sg-sub-loading dashboard-enter dashboard-enter--2">
      <p>Loading announcements...</p>
    </div>

    <div v-else-if="loadError" class="sg-sub-error dashboard-enter dashboard-enter--2">
      <p>{{ loadError }}</p>
      <button class="sg-sub-action" type="button" @click="reload">Try Again</button>
    </div>

    <template v-else>
      <div class="sg-sub-toolbar dashboard-enter dashboard-enter--2">
        <div class="sg-sub-search-shell">
          <input
            v-model="searchQuery"
            type="text"
            class="sg-sub-search-input"
            placeholder="Search announcements"
          />
          <Search :size="14" style="color: var(--color-text-muted);" />
        </div>
        <button class="sg-sub-action" type="button" @click="openCreate">
          <Plus :size="16" />
          <span>New</span>
        </button>
      </div>

      <div class="sg-sub-card dashboard-enter dashboard-enter--3">
        <h2 class="sg-sub-card-title">Announcements ({{ filteredAnnouncements.length }})</h2>
        <div v-if="filteredAnnouncements.length" class="sg-ann-list">
          <article
            v-for="ann in filteredAnnouncements"
            :key="ann.id"
            class="sg-ann-row"
          >
            <div class="sg-ann-info">
              <h3 class="sg-ann-title">{{ ann.title }}</h3>
              <p class="sg-ann-body">{{ ann.body }}</p>
              <div class="sg-ann-meta">
                <span class="sg-ann-status" :class="`sg-ann-status--${ann.status}`">{{ ann.status }}</span>
                <span class="sg-ann-date">{{ formatDate(ann.created_at) }}</span>
              </div>
            </div>
            <div class="sg-ann-actions">
              <button class="sg-ann-btn" type="button" @click="startEdit(ann)">
                <SquarePen :size="14" />
              </button>
              <button class="sg-ann-btn sg-ann-btn--danger" type="button" @click="handleDelete(ann)">
                <Trash2 :size="14" />
              </button>
            </div>
          </article>
        </div>
        <p v-else class="sg-sub-empty">No announcements yet.</p>
      </div>
    </template>

    <!-- Create/Edit Sheet -->
    <Transition name="sg-sheet">
      <div v-if="isFormOpen" class="sg-sheet-backdrop" @click.self="closeForm">
        <div class="sg-sheet">
          <form class="sg-ann-form" @submit.prevent="handleSave">
            <div class="sg-ann-form-header">
              <h2 class="sg-ann-form-title">{{ editingId ? 'Edit Announcement' : 'New Announcement' }}</h2>
              <p class="sg-ann-form-subtitle">
                {{ editingId ? 'Update the details of your announcement below.' : 'Create a new announcement for the student body.' }}
              </p>
            </div>

            <label class="sg-ann-field">
              <span class="sg-ann-field-label">
                <Type class="sg-ann-field-label-icon" :size="14" />
                Title
              </span>
              <input v-model="draft.title" class="sg-ann-field-input" type="text" placeholder="Enter a catchy title" />
            </label>

            <label class="sg-ann-field">
              <span class="sg-ann-field-label">
                <AlignLeft class="sg-ann-field-label-icon" :size="14" />
                Body
              </span>
              <textarea v-model="draft.body" class="sg-ann-field-input sg-ann-field-input--textarea" placeholder="Describe the announcement in detail..." rows="5" />
            </label>

            <label class="sg-ann-field">
              <span class="sg-ann-field-label">
                <Info class="sg-ann-field-label-icon" :size="14" />
                Status
              </span>
              <select v-model="draft.status" class="sg-ann-field-input">
                <option value="draft">Draft (Visible to council only)</option>
                <option value="published">Published (Visible to all students)</option>
                <option value="archived">Archived (Hidden from dashboard)</option>
              </select>
            </label>

            <div v-if="formError" class="sg-ann-form-error">
              <AlertCircle :size="16" />
              <span>{{ formError }}</span>
            </div>

            <div class="sg-ann-form-actions">
              <button class="sg-ann-form-cancel" type="button" @click="closeForm">Cancel</button>
              <button class="sg-sub-action sg-ann-btn-submit" type="submit" :disabled="isSaving || !draft.title.trim() || !draft.body.trim()">
                {{ isSaving ? 'Saving...' : (editingId ? 'Save Changes' : 'Post Announcement') }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </Transition>
  </section>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { useRouter } from 'vue-router'

const props = defineProps({
  preview: {
    type: Boolean,
    default: false,
  },
})
import { ArrowLeft, Search, Plus, SquarePen, Trash2, Type, AlignLeft, Info, AlertCircle } from 'lucide-vue-next'
import { useDashboardSession } from '@/composables/useDashboardSession.js'
import { useSgDashboard } from '@/composables/useSgDashboard.js'
import {
  getGovernanceAccess,
  getGovernanceAnnouncements,
  createGovernanceAnnouncement,
  updateGovernanceAnnouncement,
  deleteGovernanceAnnouncement,
} from '@/services/backendApi.js'
import { resolvePreferredGovernanceUnit } from '@/services/governanceScope.js'

const router = useRouter()
const { apiBaseUrl } = useDashboardSession()
const { isLoading: sgLoading } = useSgDashboard()

const isLoading = ref(true)
const loadError = ref('')
const announcements = ref([])
const searchQuery = ref('')
const isFormOpen = ref(false)
const isSaving = ref(false)
const formError = ref('')
const editingId = ref(null)
const draft = ref({ title: '', body: '', status: 'draft' })
const governanceUnitId = ref(null)

const filteredAnnouncements = computed(() => {
  const q = searchQuery.value.trim().toLowerCase()
  if (!q) return announcements.value
  return announcements.value.filter((a) =>
    [a.title, a.body, a.status].filter(Boolean).join(' ').toLowerCase().includes(q)
  )
})

function formatDate(d) {
  if (!d) return ''
  try { return new Date(d).toLocaleDateString(undefined, { year: 'numeric', month: 'short', day: 'numeric' }) }
  catch { return d }
}

function goBack() { 
  if (props.preview) {
    router.push('/exposed/sg')
    return
  }
  router.push('/sg') 
}

watch(
  [apiBaseUrl, () => sgLoading.value],
  async ([url]) => {
    if (!url || sgLoading.value) return
    await loadData(url)
  },
  { immediate: true }
)

async function loadData(url) {
  if (props.preview) {
    announcements.value = [
      { id: 1, title: 'Welcome to the New School Year', body: 'The student council welcomes all freshmen and returnees to Aura. Reach out if you need help!', status: 'published', created_at: new Date().toISOString() },
      { id: 2, title: 'Council Elections Validation', body: 'Please ensure your biometric data is properly enrolled before the upcoming council elections.', status: 'published', created_at: new Date(Date.now() - 86400000).toISOString() },
    ]
    isLoading.value = false
    return
  }

  isLoading.value = true
  loadError.value = ''
  try {
    const token = localStorage.getItem('aura_token') || ''
    const access = await getGovernanceAccess(url, token)
    const governanceUnit = resolvePreferredGovernanceUnit(access, {
      requiredPermissionCode: 'manage_announcements',
    })
    if (!governanceUnit) { loadError.value = 'No governance unit found.'; return }
    governanceUnitId.value = governanceUnit.governance_unit_id
    const list = await getGovernanceAnnouncements(url, token, governanceUnit.governance_unit_id)
    announcements.value = (list || []).sort((a, b) => new Date(b.created_at || 0) - new Date(a.created_at || 0))
  } catch (e) {
    loadError.value = e?.message || 'Unable to load announcements.'
  } finally { isLoading.value = false }
}

async function reload() { if (apiBaseUrl.value) await loadData(apiBaseUrl.value) }

function openCreate() {
  editingId.value = null
  draft.value = { title: '', body: '', status: 'draft' }
  formError.value = ''
  isFormOpen.value = true
}

function startEdit(ann) {
  editingId.value = ann.id
  draft.value = { title: ann.title, body: ann.body, status: ann.status || 'draft' }
  formError.value = ''
  isFormOpen.value = true
}

function closeForm() { isFormOpen.value = false; editingId.value = null }

async function handleSave() {
  if (props.preview) {
    alert('Edits are disabled in preview mode.')
    closeForm()
    return
  }
  if (isSaving.value || !draft.value.title.trim() || !draft.value.body.trim()) return
  isSaving.value = true
  formError.value = ''
  const token = localStorage.getItem('aura_token') || ''
  const payload = { title: draft.value.title.trim(), body: draft.value.body.trim(), status: draft.value.status }
  try {
    if (editingId.value) {
      await updateGovernanceAnnouncement(apiBaseUrl.value, token, editingId.value, payload)
    } else {
      await createGovernanceAnnouncement(apiBaseUrl.value, token, governanceUnitId.value, payload)
    }
    closeForm()
    await reload()
  } catch (e) { formError.value = e?.message || 'Unable to save.' }
  finally { isSaving.value = false }
}

async function handleDelete(ann) {
  if (!confirm('Delete this announcement?')) return
  try {
    const token = localStorage.getItem('aura_token') || ''
    await deleteGovernanceAnnouncement(apiBaseUrl.value, token, ann.id)
    await reload()
  } catch (e) { loadError.value = e?.message || 'Unable to delete.' }
}
</script>

<style scoped>

.sg-ann-list { display: flex; flex-direction: column; gap: 12px; }
.sg-ann-row { 
  display: flex; 
  justify-content: space-between; 
  align-items: flex-start; 
  gap: 16px; 
  padding: 18px 20px; 
  border-radius: 18px; 
  background: white; 
  border: 1px solid var(--color-surface-border);
  transition: all 0.2s ease;
  box-shadow: 0 2px 8px rgba(0,0,0,0.02);
}

.sg-ann-row:hover {
  border-color: var(--color-primary);
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(0,0,0,0.06);
}

.sg-ann-info { flex: 1; min-width: 0; }
.sg-ann-title { font-size: 16px; font-weight: 800; color: var(--color-text-primary); margin-bottom: 6px; }
.sg-ann-body { 
  font-size: 13.5px; 
  color: var(--color-text-muted); 
  line-height: 1.5; 
  overflow: hidden; 
  text-overflow: ellipsis; 
  display: -webkit-box; 
  -webkit-line-clamp: 2; 
  -webkit-box-orient: vertical; 
  overflow-wrap: break-word;
  word-break: break-word;
}
.sg-ann-meta { display: flex; gap: 12px; align-items: center; margin-top: 10px; }
.sg-ann-status { 
  font-size: 10px; 
  font-weight: 800; 
  padding: 4px 10px; 
  border-radius: 8px; 
  text-transform: uppercase; 
  letter-spacing: 0.05em;
}
.sg-ann-status--draft { background: #fef9c3; color: #854d0e; }
.sg-ann-status--published { background: #dcfce7; color: #166534; }
.sg-ann-status--archived { background: #f1f5f9; color: #475569; }
.sg-ann-date { font-size: 11px; font-weight: 600; color: var(--color-text-muted); opacity: 0.7; }
.sg-ann-actions { display: flex; gap: 8px; flex-shrink: 0; }
.sg-ann-btn { 
  background: var(--color-surface-border); 
  border: none; 
  color: var(--color-text-primary); 
  cursor: pointer; 
  padding: 8px; 
  border-radius: 10px; 
  transition: all 0.2s ease;
}
.sg-ann-btn:hover { background: var(--color-primary); color: white; transform: scale(1.1); }
.sg-ann-btn--danger:hover { background: #fee2e2; color: #ef4444; }

.sg-ann-form { 
  padding: 32px; 
  display: flex; 
  flex-direction: column; 
  gap: 24px; 
}

.sg-ann-form-header {
  margin-bottom: 8px;
}

.sg-ann-form-title { 
  font-size: 24px; 
  font-weight: 800; 
  color: var(--color-text-primary); 
  letter-spacing: -0.02em;
}

.sg-ann-form-subtitle {
  font-size: 14px;
  color: var(--color-text-muted);
  margin-top: 4px;
}

.sg-ann-field { 
  display: flex; 
  flex-direction: column; 
  gap: 8px; 
}

.sg-ann-field-label { 
  font-size: 13px; 
  font-weight: 700; 
  color: var(--color-text-primary);
  display: flex;
  align-items: center;
  gap: 6px;
}

.sg-ann-field-label-icon {
  color: var(--color-primary);
  opacity: 0.8;
}

.sg-ann-field-input { 
  background: var(--color-bg); 
  border: 2px solid transparent; 
  border-radius: 16px; 
  padding: 14px 18px; 
  font-size: 15px; 
  color: var(--color-text-primary); 
  outline: none; 
  font-family: inherit; 
  transition: all 0.2s ease;
  box-shadow: inset 0 2px 4px rgba(0,0,0,0.02);
}

.sg-ann-field-input:focus {
  border-color: var(--color-primary);
  background: white;
  box-shadow: 0 0 0 4px color-mix(in srgb, var(--color-primary), transparent 90%);
}

.sg-ann-field-input--textarea { 
  resize: vertical; 
  min-height: 120px; 
  line-height: 1.6;
}

.sg-ann-form-error { 
  font-size: 13px; 
  color: #ef4444; 
  background: #fef2f2;
  padding: 10px 14px;
  border-radius: 12px;
  border: 1px solid #fee2e2;
  display: flex;
  align-items: center;
  gap: 8px;
}

.sg-ann-form-actions { 
  display: flex; 
  justify-content: flex-end; 
  align-items: center;
  gap: 16px; 
  margin-top: 8px;
  padding-top: 24px;
  border-top: 1px solid var(--color-surface-border);
}

.sg-ann-form-cancel { 
  background: none; 
  border: none; 
  color: var(--color-text-muted); 
  font-size: 14px; 
  font-weight: 700; 
  cursor: pointer; 
  transition: color 0.2s ease;
  padding: 10px 16px;
  border-radius: 12px;
}

.sg-ann-form-cancel:hover {
  color: var(--color-text-primary);
  background: var(--color-surface-border);
}

.sg-ann-btn-submit {
  min-width: 120px;
  justify-content: center;
}
</style>
