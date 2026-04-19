<!--
|||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||
Purpose: Common Dashboard Header with User Info and Logout
-->
<template>
  <header ref="headerEl" class="standard-header">
    <button
      ref="profileEl"
      class="standard-header__profile"
      :class="{ 'standard-header__profile--expanded': isExpanded }"
      type="button"
      aria-label="Account actions"
      @click="toggleExpanded"
    >
      <span class="standard-header__profile-main">
        <span class="standard-header__avatar-wrap">
          <img
            v-if="avatarUrl"
            :src="avatarUrl"
            :alt="avatarAlt"
            class="standard-header__avatar"
          >
          <span
            v-else
            class="standard-header__avatar standard-header__avatar--fallback"
          >
            {{ initials }}
          </span>
          <span class="standard-header__status-dot" aria-hidden="true" />
        </span>

        <span class="standard-header__profile-copy">
          <span class="standard-header__eyebrow">Welcome Back</span>
          <span class="standard-header__name">{{ schoolLabel }}</span>
        </span>
      </span>

      <span class="standard-header__signout" @click.stop="emit('logout')">
        <LogOut :size="18" color="#D92D20" :stroke-width="2.4" />
        <span class="standard-header__signout-label">Sign Out</span>
      </span>
    </button>

    <div class="standard-header__actions">
      <button
        class="standard-header__action-btn"
        type="button"
        aria-label="Toggle Theme"
        @click="toggleDarkMode"
      >
        <Moon :size="18" :stroke-width="2" :color="isDarkMode ? 'var(--color-primary)' : 'currentColor'" />
      </button>

      <div class="standard-header__action-wrap">
        <button
          class="standard-header__action-btn"
          type="button"
          aria-label="Notifications"
          @click="toggleNotifications"
        >
          <Bell :size="18" :stroke-width="2" />
          <span v-if="hasUnread" class="standard-header__unread-dot" />
        </button>

        <Transition name="notif-dropdown">
          <div v-if="showNotifications" class="standard-header__notif-dropdown">
            <div class="notif-header">
              <span class="notif-title">Notifications</span>
              <button class="notif-mark-read" @click="markAllRead">Mark all read</button>
            </div>
            <div class="notif-list">
              <div v-for="notif in notifications" :key="notif.id" class="notif-item" :class="{ 'notif-item--unread': !notif.read }">
                <div class="notif-icon-wrap" :style="{ background: notif.iconBg }">
                  <component :is="notif.icon" :size="14" />
                </div>
                <div class="notif-content">
                  <p class="notif-text">{{ notif.title }}</p>
                  <p class="notif-meta">{{ notif.time }}</p>
                </div>
              </div>
              <p v-if="!notifications.length" class="notif-empty">No notifications</p>
            </div>
          </div>
        </Transition>
      </div>
    </div>
  </header>
</template>

<script setup>
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import { Bell, LogOut, Moon, Calendar, Megaphone, CheckCircle, Clock } from 'lucide-vue-next'
import { isDarkMode, toggleDarkMode } from '@/config/theme.js'

const props = defineProps({
  avatarUrl: {
    type: String,
    default: '',
  },
  schoolName: {
    type: String,
    default: '',
  },
  displayName: {
    type: String,
    default: 'School IT',
  },
  initials: {
    type: String,
    default: 'SI',
  },
})

const emit = defineEmits(['logout', 'toggle-notifications'])

const showNotifications = ref(false)
const notifications = ref([
  {
    id: 1,
    title: 'New Student Batch Imported',
    time: '1 hour ago',
    read: false,
    icon: CheckCircle,
    iconBg: 'rgba(0, 200, 100, 0.15)',
  },
  {
    id: 2,
    title: 'System update scheduled for 12 AM',
    time: '4 hours ago',
    read: false,
    icon: Clock,
    iconBg: 'rgba(255, 140, 0, 0.15)',
  },
  {
    id: 3,
    title: 'Orientation reminder sent to Engineering',
    time: '2 days ago',
    read: true,
    icon: Megaphone,
    iconBg: 'rgba(255, 212, 0, 0.2)',
  },
])

const hasUnread = computed(() => notifications.value.some(n => !n.read))

function toggleNotifications() {
  showNotifications.value = !showNotifications.value
}

function markAllRead() {
  notifications.value = notifications.value.map(n => ({ ...n, read: true }))
}

const isExpanded = ref(false)
const headerEl = ref(null)
const profileEl = ref(null)

const schoolLabel = computed(() => abbreviateSchoolName(props.schoolName || props.displayName))
const avatarAlt = computed(() => props.displayName || schoolLabel.value)

function toggleExpanded() {
  isExpanded.value = !isExpanded.value
}

function collapseExpanded(event) {
  if (!isExpanded.value) return
  const profile = profileEl.value
  if (profile instanceof HTMLElement && event.target instanceof Node && !profile.contains(event.target)) {
    isExpanded.value = false
  }
}

function abbreviateSchoolName(value) {
  const input = String(value || '').trim()
  if (!input) return 'School IT'

  const words = input.match(/[A-Za-z0-9]+/g) || []
  if (!words.length) return input

  const firstWord = words[0] || ''
  if (/^[A-Z]{2,10}$/.test(firstWord)) {
    return `${firstWord.split('').join('.')}.`
  }

  const stopwords = new Set(['of', 'the', 'and', 'for', 'at', 'in', 'on', 'de', 'la'])
  const significantWords = words.filter((word) => !stopwords.has(word.toLowerCase()))
  const sourceWords = significantWords.length >= 2 ? significantWords : words

  if (sourceWords.length === 1) {
    return sourceWords[0]
  }

  return `${sourceWords.map((word) => word[0].toUpperCase()).join('.')}.`
}

function handleClickOutside(event) {
  if (showNotifications.value) {
    const actions = headerEl.value?.querySelector('.standard-header__actions')
    if (actions && !actions.contains(event.target)) {
      showNotifications.value = false
    }
  }
  if (!isExpanded.value) return
  const profile = profileEl.value
  if (profile instanceof HTMLElement && event.target instanceof Node && !profile.contains(event.target)) {
    isExpanded.value = false
  }
}

onMounted(() => {
  window.addEventListener('pointerdown', handleClickOutside, true)
})

onBeforeUnmount(() => {
  window.removeEventListener('pointerdown', handleClickOutside, true)
})
</script>

<style scoped>
.standard-header{width:100%;display:grid;grid-template-columns:minmax(0,1fr) auto;align-items:center;gap:clamp(10px,3.6vw,16px)}
.standard-header__profile{display:flex;align-items:center;min-width:0;max-width:min(100%,clamp(162px,56vw,228px));min-height:52px;padding:7px clamp(10px,2.8vw,12px) 7px 7px;border:1px solid var(--aura-glass-border);border-radius:999px;background:var(--color-surface);color:var(--color-text-always-dark);transition:max-width .3s ease,padding .3s ease,box-shadow .24s ease,transform .18s ease;cursor:pointer;overflow:hidden;justify-self:start;box-shadow:var(--aura-shadow-soft)}
.standard-header__profile--expanded{max-width:min(100%,clamp(220px,76vw,292px))}
.standard-header__profile-main{display:flex;align-items:center;gap:10px;min-width:0;flex:1}
.standard-header__avatar-wrap{position:relative;display:inline-flex;flex-shrink:0}
.standard-header__avatar{width:38px;height:38px;border-radius:999px;object-fit:cover;flex-shrink:0}
.standard-header__avatar--fallback{display:inline-flex;align-items:center;justify-content:center;background:var(--color-nav);color:var(--color-nav-text);font-size:13px;font-weight:700}
.standard-header__status-dot{position:absolute;right:0;bottom:0;width:10px;height:10px;border-radius:999px;background:var(--color-primary);border:2px solid var(--color-surface)}
.standard-header__profile-copy{display:flex;flex-direction:column;align-items:flex-start;min-width:0;line-height:1;text-align:left}
.standard-header__eyebrow{font-size:10px;font-weight:500;color:var(--color-text-muted);white-space:nowrap}
.standard-header__name{margin-top:2px;max-width:100%;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;font-size:12px;font-weight:700;line-height:1.08;color:var(--color-text-always-dark);letter-spacing:-.02em}
.standard-header__signout{display:inline-flex;align-items:center;overflow:hidden;max-width:0;min-width:0;opacity:0;margin-left:0;white-space:nowrap;transition:max-width .3s ease,opacity .25s ease,margin .3s ease;color:#D92D20;cursor:pointer;flex-shrink:1}
.standard-header__signout-label{margin-left:8px;min-width:0;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;font-size:13px;font-weight:500;letter-spacing:-.02em}
.standard-header__profile--expanded .standard-header__signout{max-width:min(36vw,118px);opacity:1;margin-left:clamp(8px,2.4vw,16px)}
.standard-header__actions{display:flex;align-items:center;gap:8px;justify-self:end}
.standard-header__action-btn{width:42px;height:42px;border:1px solid var(--aura-glass-border);border-radius:999px;background:var(--color-surface);color:var(--color-text-always-dark);display:inline-grid;place-items:center;transition:transform .16s ease;flex-shrink:0;line-height:0;box-shadow:var(--aura-shadow-soft)}
.standard-header__action-btn:active{transform:scale(.95)}
.standard-header__action-btn :deep(svg){display:block}

@media (max-width: 420px){
  .standard-header{gap:10px}
  .standard-header__profile{max-width:min(100%,clamp(150px,58vw,204px))}
  .standard-header__profile--expanded{max-width:min(100%,clamp(204px,74vw,252px))}
}

@media (max-width: 360px){
  .standard-header__profile{padding-right:8px;min-height:50px;max-width:min(100%,clamp(142px,60vw,188px))}
  .standard-header__profile--expanded{max-width:min(100%,clamp(188px,76vw,234px))}
  .standard-header__profile-main{gap:8px}
  .standard-header__avatar{width:36px;height:36px}
  .standard-header__avatar--fallback{font-size:12px}
  .standard-header__name{font-size:11px}
  .standard-header__profile--expanded .standard-header__signout{max-width:32px;margin-left:6px}
  .standard-header__signout-label{display:none}
  .standard-header__action-btn{width:40px;height:40px}
  .standard-header__actions{gap:6px}
}
.standard-header__action-wrap{position:relative}
.standard-header__unread-dot{position:absolute;top:8px;right:8px;width:8px;height:8px;border-radius:999px;background:var(--color-primary);border:2px solid var(--color-surface)}
.standard-header__notif-dropdown{position:absolute;top:calc(100% + 12px);right:0;width:320px;max-height:420px;border-radius:20px;background:var(--color-surface);border:1px solid var(--aura-glass-border);box-shadow:var(--aura-shadow-premium);overflow:hidden;z-index:1000}
.notif-header{display:flex;align-items:center;justify-content:space-between;padding:16px 18px 12px;border-bottom:1px solid var(--color-surface-border)}
.notif-title{font-size:14px;font-weight:700;color:var(--color-text-primary)}
.notif-mark-read{font-size:12px;font-weight:600;color:var(--color-primary);background:none;border:none;cursor:pointer;padding:4px 8px;border-radius:8px}
.notif-list{max-height:340px;overflow-y:auto;padding:8px}
.notif-item{display:flex;align-items:flex-start;gap:12px;padding:12px 14px;border-radius:14px;cursor:pointer;transition:background .15s ease}
.notif-item:hover{background:var(--color-field-surface)}
.notif-item--unread{background:color-mix(in srgb,var(--color-primary) 6%,transparent)}
.notif-icon-wrap{width:32px;height:32px;border-radius:10px;display:flex;align-items:center;justify-content:center;flex-shrink:0}
.notif-content{flex:1;min-width:0}
.notif-text{font-size:13px;font-weight:600;color:var(--color-text-primary);line-height:1.4;margin:0}
.notif-meta{font-size:11px;font-weight:500;color:var(--color-text-muted);margin:4px 0 0}
.notif-empty{text-align:center;font-size:13px;font-weight:500;color:var(--color-text-muted);padding:32px 16px}
.notif-dropdown-enter-active{transition:all .25s cubic-bezier(.16,1,.3,1)}
.notif-dropdown-leave-active{transition:all .2s ease}
.notif-dropdown-enter-from,.notif-dropdown-leave-to{opacity:0;transform:translateY(-8px) scale(.96)}
</style>
