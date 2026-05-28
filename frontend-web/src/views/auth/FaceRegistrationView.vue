<template>
  <div class="face-gate-page mesh-gradient relative overflow-hidden">
    <!-- Animated background elements -->
    <div class="absolute inset-0 overflow-hidden pointer-events-none">
      <div class="blob blob-1"></div>
      <div class="blob blob-2"></div>
    </div>

    <AttendancePermissionGate
      v-if="permissionState !== 'permissions_granted'"
      :permission-state="permissionState"
      :error-message="permissionError"
      :is-requesting="isPermissionRequesting"
      :camera-only="true"
      @request="requestPermissions"
      @retry="retryPermissions"
    />

    <div v-if="step === 'intro'" class="face-gate-shell face-gate-shell--intro relative z-10">
      <section class="intro-card glass-card">
        <span class="intro-chip">NEXUS Enrollment</span>
        <h1 class="intro-title">
          Hi {{ firstName }},<br>
          <span class="text-white/60">face is</span><br>
          unregistered<br>
          <span class="text-white/60">please</span> register<br>
          now.
        </h1>
        <p class="intro-copy">
          We use high-precision face scans to ensure secure and seamless attendance check-ins.
        </p>

        <button class="register-pill group" type="button" @click="beginEnrollment">
          <span class="register-pill__icon">
            <ArrowRight :size="20" class="group-hover:translate-x-1 transition-transform" />
          </span>
          <span class="register-pill__text">Begin Registration</span>
        </button>
      </section>
    </div>

    <div v-else class="face-gate-shell face-gate-shell--capture relative z-10">
      <section class="capture-card glass-card">
        <header class="capture-header">
          <span class="capture-chip">Face Setup</span>
          <Transition name="title-fade" mode="out-in">
            <h2 class="capture-title" :key="captureTitle">{{ captureTitle }}</h2>
          </Transition>
        </header>

        <FaceScanPanel
          class="face-gate-panel premium-scan-panel"
          :caption="panelCaption"
          :progress="scanProgress"
          :is-camera-ready="panelCameraReady"
          :face-image-url="panelFaceImageUrl"
          :show-error="showRetry"
          :error-text="statusMessage"
          :video-ref="setVideoEl"
          @retry="retryEnrollment"
        />

        <p v-if="showStatusMessage" class="capture-status" :class="statusClass">{{ statusText }}</p>
      </section>
    </div>

    <button v-if="step === 'intro'" class="signout-link text-white/40 hover:text-white" type="button" @click="logout">
      Sign Out
    </button>
  </div>
</template>

<script setup>
import { computed, nextTick, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import { ArrowRight } from 'lucide-vue-next'
import { useAuth } from '@/composables/useAuth.js'
import { useDashboardSession } from '@/composables/useDashboardSession.js'
import { applyTheme, loadTheme } from '@/config/theme.js'
import { registerStudentFace } from '@/services/backendApi.js'
import { initFaceScanDetector, resetFaceScanDetector } from '@/composables/useFaceScanDetector.js'
import { getStoredAuthMeta, patchStoredAuthMeta } from '@/services/localAuth.js'
import FaceScanPanel from '@/components/attendance/FaceScanPanel.vue'
import AttendancePermissionGate from '@/components/attendance/AttendancePermissionGate.vue'
import { useAttendancePermissions } from '@/composables/useAttendancePermissions.js'

const router = useRouter()
const { logout } = useAuth()
const {
  apiBaseUrl,
  currentUser,
  initializeDashboardSession,
  needsFaceRegistration,
  schoolSettings,
} = useDashboardSession()

const step = ref('intro')
const statusState = ref('idle')
const statusMessage = ref('')
const capturedPreview = ref('')
const videoEl = ref(null)
const mediaStream = ref(null)
const videoReady = ref(false)
const cameraState = ref('idle')

let detectorInstance = null
let detectRaf = null
let captureTimeout = null
let detectStartedAt = 0
let detectionStreak = 0
let redirectTimeout = null

const firstName = computed(() => currentUser.value?.first_name?.trim() || 'there')
const schoolName = computed(() => (
  currentUser.value?.school_name?.trim() ||
  schoolSettings.value?.school_name?.trim() ||
  getStoredAuthMeta()?.schoolName ||
  'Your school'
))
const captureTitle = computed(() => {
  if (statusState.value === 'success') return 'All set!'
  if (statusState.value === 'submitting' || statusState.value === 'capturing') return 'Registering...'
  if (statusState.value === 'starting') return 'Preparing camera'
  if (statusState.value === 'detecting') return 'Scanning...'
  if (statusState.value === 'error') return 'Try again'
  return 'Register your face'
})
const panelCaption = computed(() => {
  if (statusState.value === 'success') return 'Face registered.'
  if (statusState.value === 'submitting' || statusState.value === 'capturing') return 'Hold still...'
  if (statusState.value === 'starting') return 'Warming up camera...'
  if (statusState.value === 'error') return 'Registration failed.'
  return 'Keep your face centered.'
})
const showRetry = computed(() => statusState.value === 'error')
const statusClass = computed(() => ({
  'capture-status--error': statusState.value === 'error',
  'capture-status--success': statusState.value === 'success',
}))
const panelCameraReady = computed(() => cameraState.value === 'ready' && !capturedPreview.value)
const panelFaceImageUrl = computed(() =>
  capturedPreview.value ||
  currentUser.value?.avatar_url ||
  currentUser.value?.profile_photo_url ||
  ''
)
const showStatusMessage = computed(() =>
  Boolean(statusText.value) && statusState.value === 'success'
)
const statusText = computed(() => {
  if (statusState.value === 'success') {
    return 'Face registered successfully. Redirecting to your dashboard...'
  }

  return statusMessage.value
})
const scanProgress = computed(() => {
  if (statusState.value === 'success') return 100
  if (statusState.value === 'submitting') return 88
  if (statusState.value === 'capturing') return 72
  if (statusState.value === 'detecting') return 46
  if (statusState.value === 'starting') return 18
  if (statusState.value === 'error') return 64
  return panelCameraReady.value ? 28 : 12
})

const faceDetectorWasmBaseUrl =
  import.meta.env.VITE_FACE_DETECTOR_WASM_URL ||
  'https://cdn.jsdelivr.net/npm/@mediapipe/tasks-vision@latest/wasm'
const faceDetectorModelUrl =
  import.meta.env.VITE_FACE_DETECTOR_MODEL_URL ||
  'https://storage.googleapis.com/mediapipe-models/face_detector/blaze_face_short_range/float16/1/blaze_face_short_range.tflite'
const faceDetectorMinConfidence = Number(import.meta.env.VITE_FACE_DETECTOR_MIN_CONFIDENCE ?? 0.5)
const faceDetectorSuppression = Number(import.meta.env.VITE_FACE_DETECTOR_SUPPRESSION ?? 0.3)
const faceDetectorIntervalMs = Number(import.meta.env.VITE_FACE_DETECTOR_INTERVAL_MS ?? 200)
const detectTimeoutMs = Number(import.meta.env.VITE_FACE_ENROLL_DETECT_TIMEOUT_MS ?? 12000)
const captureDelayMs = Number(import.meta.env.VITE_FACE_ENROLL_CAPTURE_DELAY_MS ?? 450)

const setVideoEl = (el) => {
  videoEl.value = el
}

const {
  permissionState,
  errorMessage: permissionError,
  isRequesting: isPermissionRequesting,
  checkExistingPermissions,
  requestPermissions,
  retryPermissions,
} = useAttendancePermissions({ cameraOnly: true })

function applyRegistrationTheme() {
  const authMeta = getStoredAuthMeta()
  const fallbackSettings = {
    school_name: currentUser.value?.school_name || authMeta?.schoolName || null,
    school_code: currentUser.value?.school_code || authMeta?.schoolCode || null,
    logo_url: schoolSettings.value?.logo_url || authMeta?.logoUrl || null,
    primary_color: schoolSettings.value?.primary_color || authMeta?.primaryColor || '#AAFF00',
    secondary_color: schoolSettings.value?.secondary_color || authMeta?.secondaryColor || '#AAFF00',
    accent_color: schoolSettings.value?.accent_color || authMeta?.accentColor || '#000000',
  }

  applyTheme(loadTheme(fallbackSettings))
}

watch(
  () => needsFaceRegistration.value,
  (required) => {
    if (!required) {
      router.replace({ name: 'Home' })
    }
  }
)

watch(
  () => [
    currentUser.value?.school_name,
    currentUser.value?.school_code,
    schoolSettings.value?.primary_color,
    schoolSettings.value?.secondary_color,
    schoolSettings.value?.accent_color,
    schoolSettings.value?.logo_url,
  ],
  () => {
    applyRegistrationTheme()
  },
  { immediate: true }
)

onMounted(() => {
  applyRegistrationTheme()
  if (!needsFaceRegistration.value) {
    router.replace({ name: 'Home' })
    return
  }
  checkExistingPermissions()
})

onBeforeUnmount(() => {
  clearTimers()
  stopFaceDetection()
  stopCamera()
  resetFaceScanDetector()
  detectorInstance = null
})

async function beginEnrollment() {
  step.value = 'capture'
  await nextTick()
  await startEnrollmentFlow()
}

async function retryEnrollment() {
  capturedPreview.value = ''
  await startEnrollmentFlow()
}

async function startEnrollmentFlow() {
  clearTimers()
  stopFaceDetection()
  stopCamera()

  statusState.value = 'starting'
  statusMessage.value = 'Starting camera...'
  videoReady.value = false
  detectionStreak = 0

  const cameraReady = await startCamera()
  if (!cameraReady) {
    setRegistrationError(
      cameraState.value === 'denied'
        ? 'Camera access is required to register your face.'
        : 'Camera is unavailable on this device.'
    )
    return
  }

  const detectorReady = await ensureFaceDetector()
  if (!detectorReady) {
    statusState.value = 'capturing'
    statusMessage.value = 'Hold still while we capture your face.'
    captureTimeout = setTimeout(() => {
      captureAndRegister()
    }, captureDelayMs + 500)
    return
  }

  statusState.value = 'detecting'
  statusMessage.value = 'Center your face inside the frame.'
  detectStartedAt = 0
  startFaceDetection()
}

async function ensureFaceDetector() {
  if (detectorInstance) return true

  try {
    detectorInstance = await initFaceScanDetector({
      wasmBaseUrl: faceDetectorWasmBaseUrl,
      modelAssetPath: faceDetectorModelUrl,
      minDetectionConfidence: faceDetectorMinConfidence,
      minSuppressionThreshold: faceDetectorSuppression,
      runningMode: 'VIDEO',
    })
    return Boolean(detectorInstance)
  } catch {
    detectorInstance = null
    resetFaceScanDetector()
    return false
  }
}

async function startCamera() {
  if (!navigator?.mediaDevices?.getUserMedia) {
    cameraState.value = 'unsupported'
    return false
  }

  cameraState.value = 'requesting'

  try {
    mediaStream.value = await navigator.mediaDevices.getUserMedia({
      video: {
        facingMode: 'user',
        width: { ideal: 720 },
        height: { ideal: 720 },
      },
      audio: false,
    })
  } catch {
    cameraState.value = 'denied'
    return false
  }

  const el = videoEl.value
  if (!el) {
    cameraState.value = 'unsupported'
    return false
  }

  el.srcObject = mediaStream.value
  el.muted = true
  el.autoplay = true
  el.playsInline = true

  try {
    await el.play().catch(() => null)
  } catch {
    // Ignore autoplay issues; ready state watcher below handles availability.
  }

  const ready = await waitForVideoReady(el)
  if (!ready) {
    cameraState.value = 'unsupported'
    return false
  }

  cameraState.value = 'ready'
  videoReady.value = true
  return true
}

function waitForVideoReady(el) {
  if (el.readyState >= 2) return Promise.resolve(true)

  return new Promise((resolve) => {
    let settled = false
    const finish = (nextValue) => {
      if (settled) return
      settled = true
      clearTimeout(timer)
      el.removeEventListener('loadeddata', handleReady)
      el.removeEventListener('canplay', handleReady)
      el.removeEventListener('error', handleError)
      resolve(nextValue)
    }

    const handleReady = () => finish(true)
    const handleError = () => finish(false)
    const timer = setTimeout(() => finish(false), 8000)

    el.addEventListener('loadeddata', handleReady, { once: true })
    el.addEventListener('canplay', handleReady, { once: true })
    el.addEventListener('error', handleError, { once: true })
  })
}

function startFaceDetection() {
  stopFaceDetection()
  detectStartedAt = 0
  detectionStreak = 0

  const detect = (now) => {
    if (!videoEl.value || !detectorInstance || statusState.value === 'submitting') return

    if (!detectStartedAt) detectStartedAt = now
    if (now - detectStartedAt > detectTimeoutMs) {
      setRegistrationError('No face detected. Please try again in a brighter area.')
      return
    }

    try {
      const result = detectorInstance.detectForVideo(videoEl.value, now)
      const hasFace = Array.isArray(result?.detections) && result.detections.length > 0
      detectionStreak = hasFace ? detectionStreak + 1 : 0

      if (detectionStreak >= 2) {
        statusState.value = 'capturing'
        statusMessage.value = 'Face detected. Registering...'
        stopFaceDetection()
        captureTimeout = setTimeout(() => {
          captureAndRegister()
        }, captureDelayMs)
        return
      }
    } catch {
      setRegistrationError('Face detection failed. Please try again.')
      return
    }

    captureTimeout = setTimeout(() => {
      detectRaf = requestAnimationFrame(detect)
    }, faceDetectorIntervalMs)
  }

  detectRaf = requestAnimationFrame(detect)
}

function stopFaceDetection() {
  if (detectRaf) cancelAnimationFrame(detectRaf)
  detectRaf = null
  if (captureTimeout) clearTimeout(captureTimeout)
  captureTimeout = null
}

function stopCamera() {
  if (mediaStream.value) {
    mediaStream.value.getTracks().forEach((track) => track.stop())
    mediaStream.value = null
  }
  if (videoEl.value) {
    videoEl.value.srcObject = null
  }
  videoReady.value = false
  cameraState.value = 'idle'
}

function clearTimers() {
  if (captureTimeout) clearTimeout(captureTimeout)
  captureTimeout = null
  if (redirectTimeout) clearTimeout(redirectTimeout)
  redirectTimeout = null
}

function captureVideoFrame() {
  const el = videoEl.value
  if (!el || el.videoWidth <= 0 || el.videoHeight <= 0) {
    throw new Error('Unable to capture a face image.')
  }

  const size = Math.min(el.videoWidth, el.videoHeight)
  const sx = Math.max(0, (el.videoWidth - size) / 2)
  const sy = Math.max(0, (el.videoHeight - size) / 2)
  const canvas = document.createElement('canvas')
  canvas.width = 720
  canvas.height = 720
  const ctx = canvas.getContext('2d')
  if (!ctx) {
    throw new Error('Unable to prepare the face image.')
  }

  ctx.drawImage(el, sx, sy, size, size, 0, 0, canvas.width, canvas.height)
  return canvas.toDataURL('image/jpeg', 0.92)
}

async function captureAndRegister() {
  try {
    statusState.value = 'submitting'
    statusMessage.value = 'Registering your face...'

    const imageDataUrl = captureVideoFrame()
    capturedPreview.value = imageDataUrl

    stopCamera()

    const token = localStorage.getItem('nexus_token')
    await registerStudentFace(apiBaseUrl.value, token, imageDataUrl)

    patchStoredAuthMeta({
      faceReferenceEnrolled: true,
    })

    await initializeDashboardSession(true)
    if (needsFaceRegistration.value) {
      throw new Error('Face registration was saved, but the account is still marked as unregistered.')
    }

    statusState.value = 'success'
    statusMessage.value = 'Face registered successfully. Redirecting to your dashboard...'
    redirectTimeout = setTimeout(() => {
      router.replace({ name: 'Home' })
    }, 900)
  } catch (error) {
    setRegistrationError(error?.message || 'Unable to register your face right now.')
  }
}

function setRegistrationError(message) {
  clearTimers()
  stopFaceDetection()
  stopCamera()
  statusState.value = 'error'
  statusMessage.value = message
}
</script>

<style scoped>
.face-gate-page {
  --color-primary: #AAFF00;
  --color-primary-glow: rgba(170, 255, 0, 0.4);
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  padding: 34px 24px;
}

/* Background Blobs */
.blob {
  position: absolute;
  width: 500px;
  height: 500px;
  background: radial-gradient(circle, var(--color-primary-glow) 0%, transparent 70%);
  filter: blur(80px);
  opacity: 0.15;
}
.blob-1 { top: -10%; left: -10%; animation: float 20s infinite alternate; }
.blob-2 { bottom: -10%; right: -10%; animation: float 25s infinite alternate-reverse; }

@keyframes float {
  0% { transform: translate(0, 0) rotate(0deg); }
  100% { transform: translate(100px, 50px) rotate(30deg); }
}

.face-gate-shell {
  width: min(100%, 480px);
}

.intro-card,
.capture-card {
  width: 100%;
  padding: 40px;
}

.intro-chip,
.capture-chip {
  display: inline-flex;
  padding: 6px 14px;
  border-radius: 999px;
  background: rgba(170, 255, 0, 0.1);
  color: var(--color-primary);
  font-size: 11px;
  font-weight: 800;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  margin-bottom: 24px;
}

.intro-title {
  font-size: clamp(32px, 8vw, 48px);
  line-height: 1.1;
  font-weight: 800;
  letter-spacing: -0.04em;
  color: white;
  margin-bottom: 24px;
}

.intro-copy {
  font-size: 15px;
  line-height: 1.6;
  color: white/50;
  margin-bottom: 40px;
}

.register-pill {
  display: flex;
  align-items: center;
  gap: 16px;
  background: var(--color-primary);
  color: #050505;
  padding: 6px 24px 6px 6px;
  border-radius: 999px;
  border: none;
  font-weight: 700;
  cursor: pointer;
  box-shadow: 0 10px 20px -5px var(--color-primary-glow);
}

.register-pill__icon {
  width: 48px;
  height: 48px;
  background: #050505;
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.capture-header {
  margin-bottom: 32px;
}

.capture-title {
  font-size: 28px;
  font-weight: 800;
  color: white;
}

.capture-status {
  margin-top: 24px;
  font-size: 14px;
  font-weight: 600;
  color: white/40;
  text-align: center;
}

.capture-status--error { color: #ff5555; }
.capture-status--success { color: var(--color-primary); }

.signout-link {
  margin-top: 32px;
  border: none;
  background: transparent;
  font-size: 13px;
  font-weight: 700;
  cursor: pointer;
}

/* Scan Panel Overrides */
.premium-scan-panel :deep(.scan-ring-base) {
  stroke: rgba(255, 255, 255, 0.05) !important;
}
.premium-scan-panel :deep(.scan-ring-progress) {
  stroke: var(--color-primary) !important;
  filter: drop-shadow(0 0 8px var(--color-primary-glow));
}
.premium-scan-panel :deep(.scan-media) {
  background: rgba(0,0,0,0.3) !important;
  border: 1px solid rgba(255,255,255,0.1) !important;
}
.premium-scan-panel :deep(.step-caption) {
  color: white/60 !important;
  font-weight: 600 !important;
}
</style>
