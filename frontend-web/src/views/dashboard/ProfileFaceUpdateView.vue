<template>
  <div class="face-update-page">
    <main class="face-update-shell">
      <!-- ── Step 1: Password Confirmation ───────────────────────────── -->
      <section v-if="step === 'password'" class="face-update-auth dashboard-enter dashboard-enter--1">
        <div class="auth-card">
          <div class="auth-icon-wrap">
            <ShieldCheck :size="48" stroke-width="1.5" />
          </div>
          <h1 class="face-update-auth__title">Security Check</h1>
          <p class="face-update-auth__copy">
            Please confirm your password to update your Face ID reference.
          </p>

          <form class="face-update-form" @submit.prevent="handlePasswordSubmit">
            <label class="face-update-field">
              <input
                v-model="currentPassword"
                class="face-update-input"
                :type="showPassword ? 'text' : 'password'"
                placeholder="Enter current password"
                autocomplete="current-password"
                :disabled="isVerifyingPassword"
              >
            </label>

            <p v-if="passwordError" class="face-update-feedback face-update-feedback--error">
              {{ passwordError }}
            </p>

            <div class="face-update-actions">
              <SecurityActionPill
                :icon="ArrowRight"
                label="Continue to Scan"
                type="submit"
                :loading="isVerifyingPassword"
                :disabled="isVerifyingPassword"
                :full-width="true"
              />

              <button
                type="button"
                class="face-update-cancel-btn"
                :disabled="isVerifyingPassword"
                @click="handleCancel"
              >
                Back to Security
              </button>
            </div>
          </form>
        </div>
      </section>

      <!-- ── Step 2: Face Scan / Upload ──────────────────────────────── -->
      <section v-else class="face-update-scan dashboard-enter dashboard-enter--2">
        <div class="scan-card">
          <div class="scan-header">
            <button class="scan-back-btn" @click="step = 'password'">
              <ArrowLeft :size="20" />
            </button>
            <h2 class="scan-title">{{ scanTitle }}</h2>
          </div>

          <div class="face-update-frame-container">
            <!-- Pulsing Ring -->
            <div class="face-update-ring" :class="{ 'face-update-ring--active': cameraState === 'ready' && !capturedPreview }"></div>
            
            <div class="face-update-frame">
              <!-- Scanning Beam -->
              <div v-if="statusState === 'detecting' || statusState === 'capturing'" class="face-update-beam"></div>

              <video
                v-show="cameraState === 'ready' && !capturedPreview"
                ref="videoEl"
                class="face-update-video"
                autoplay
                playsinline
                webkit-playsinline
                disablePictureInPicture
                disableRemotePlayback
                controlslist="nodownload noplaybackrate noremoteplayback"
                muted
              />

              <img
                v-if="capturedPreview"
                :src="capturedPreview"
                alt="Updated face preview"
                class="face-update-photo"
              >

              <div
                v-else-if="cameraState !== 'ready' && statusState !== 'submitting'"
                class="face-update-placeholder"
              >
                <UserRound :size="64" stroke-width="1.2" />
              </div>
              
              <!-- Submitting overlay -->
              <div v-if="statusState === 'submitting'" class="face-update-overlay">
                <LoaderCircle class="spinner" :size="48" />
              </div>
            </div>
          </div>

          <div class="scan-status">
            <div class="status-icon-wrap" :class="statusState">
              <Scan v-if="statusState === 'detecting' || statusState === 'idle'" class="pulse" :size="20" />
              <CheckCircle2 v-else-if="statusState === 'success'" :size="20" />
              <AlertCircle v-else-if="statusState === 'error'" :size="20" />
              <LoaderCircle v-else class="spinner" :size="20" />
            </div>
            <p class="status-message" :class="{ 'error': statusState === 'error', 'success': statusState === 'success' }">
              {{ statusMessage }}
            </p>
          </div>

          <!-- Action Buttons -->
          <div class="scan-actions">
            <button
              v-if="statusState === 'error'"
              class="scan-primary-btn"
              @click="retryEnrollment"
            >
              <RotateCcw :size="18" />
              Try Again
            </button>

            <div v-if="statusState !== 'submitting' && statusState !== 'success'" class="upload-option">
              <span class="upload-divider">OR</span>
              <button class="upload-btn" @click="triggerFileUpload" :disabled="isUploading">
                <Upload :size="18" />
                Upload a Photo
              </button>
              <input
                ref="fileInputEl"
                type="file"
                accept="image/jpeg,image/png"
                class="hidden-input"
                @change="handlePhotoUpload"
              >
            </div>
          </div>

          <!-- Tips Section -->
          <div v-if="statusState !== 'success'" class="scan-tips">
            <h3 class="tips-title">Registration Tips</h3>
            <ul class="tips-list">
              <li><div class="tip-dot"></div> Ensure your face is well-lit</li>
              <li><div class="tip-dot"></div> Remove masks or heavy glasses</li>
              <li><div class="tip-dot"></div> Keep a neutral expression</li>
            </ul>
          </div>
        </div>

        <div class="face-update-brand">
          <img :src="activeAuraLogo" alt="NEXUS AI" class="face-update-brand__logo">
          <span>Powered by NEXUS Ai</span>
        </div>
      </section>
    </main>
  </div>
</template>

<script setup>
import { computed, nextTick, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import { 
  ArrowLeft, 
  ArrowRight, 
  Eye, 
  EyeOff, 
  UserRound, 
  ShieldCheck, 
  Scan, 
  CheckCircle2, 
  AlertCircle, 
  LoaderCircle,
  RotateCcw,
  Upload
} from 'lucide-vue-next'
import SecurityActionPill from '@/components/security/SecurityActionPill.vue'
import { activeAuraLogo, applyTheme, loadTheme } from '@/config/theme.js'
import { useDashboardSession } from '@/composables/useDashboardSession.js'
import { initFaceScanDetector, resetFaceScanDetector } from '@/composables/useFaceScanDetector.js'
import {
  registerStudentFace,
  registerStudentFaceUpload,
  resolveApiBaseUrl,
  verifyPasswordForUser,
} from '@/services/backendApi.js'
import { getStoredAuthMeta } from '@/services/localAuth.js'

const router = useRouter()
const {
  currentUser,
  schoolSettings,
  markCurrentUserFaceRegistered,
} = useDashboardSession()

const step = ref('password')
const currentPassword = ref('')
const showPassword = ref(false)
const isVerifyingPassword = ref(false)
const passwordError = ref('')
const statusState = ref('idle') // idle, starting, detecting, capturing, submitting, success, error
const statusMessage = ref('')
const capturedPreview = ref('')
const videoEl = ref(null)
const fileInputEl = ref(null)
const mediaStream = ref(null)
const cameraState = ref('idle')
const isUploading = ref(false)

let detectorInstance = null
let detectRaf = null
let captureTimeout = null
let detectStartedAt = 0
let detectionStreak = 0
let redirectTimeout = null

const faceDetectorWasmBaseUrl =
  import.meta.env.VITE_FACE_DETECTOR_WASM_URL ||
  'https://cdn.jsdelivr.net/npm/@mediapipe/tasks-vision@latest/wasm'
const faceDetectorModelUrl =
  import.meta.env.VITE_FACE_DETECTOR_MODEL_URL ||
  'https://storage.googleapis.com/mediapipe-models/face_detector/blaze_face_short_range/float16/1/blaze_face_short_range.tflite'
const faceDetectorMinConfidence = Number(import.meta.env.VITE_FACE_DETECTOR_MIN_CONFIDENCE ?? 0.5)
const faceDetectorSuppression = Number(import.meta.env.VITE_FACE_DETECTOR_SUPPRESSION ?? 0.3)
const faceDetectorIntervalMs = Number(import.meta.env.VITE_FACE_DETECTOR_INTERVAL_MS ?? 120)
const detectTimeoutMs = Number(import.meta.env.VITE_FACE_ENROLL_DETECT_TIMEOUT_MS ?? 12000)
const captureDelayMs = Number(import.meta.env.VITE_FACE_ENROLL_CAPTURE_DELAY_MS ?? 450)

const authEmail = computed(() =>
  currentUser.value?.email || getStoredAuthMeta()?.email || ''
)
const authUserId = computed(() => Number(currentUser.value?.id ?? getStoredAuthMeta()?.userId ?? NaN))

const scanTitle = computed(() => {
  if (statusState.value === 'success') return 'Success'
  if (statusState.value === 'error') return 'Scan Failed'
  return 'Face Registration'
})

function applySecurityTheme() {
  const authMeta = getStoredAuthMeta()
  applyTheme(loadTheme({
    school_name: currentUser.value?.school_name || authMeta?.schoolName || null,
    school_code: currentUser.value?.school_code || authMeta?.schoolCode || null,
    logo_url: schoolSettings.value?.logo_url || authMeta?.logoUrl || null,
    primary_color: schoolSettings.value?.primary_color || authMeta?.primaryColor || '#AAFF00',
    secondary_color: schoolSettings.value?.secondary_color || authMeta?.secondaryColor || '#FFD400',
    accent_color: schoolSettings.value?.accent_color || authMeta?.accentColor || '#000000',
  }))
}

watch(
  () => [
    currentUser.value?.school_name,
    currentUser.value?.school_code,
    schoolSettings.value?.logo_url,
    schoolSettings.value?.primary_color,
    schoolSettings.value?.secondary_color,
    schoolSettings.value?.accent_color,
  ],
  () => {
    applySecurityTheme()
  },
  { immediate: true }
)

onMounted(() => {
  applySecurityTheme()
})

onBeforeUnmount(() => {
  clearTimers()
  stopFaceDetection()
  stopCamera()
  resetFaceScanDetector()
  detectorInstance = null
})

async function handlePasswordSubmit() {
  passwordError.value = ''

  if (!currentPassword.value.trim()) {
    passwordError.value = 'Enter your current password before updating Face ID.'
    return
  }

  if (!authEmail.value) {
    passwordError.value = 'Unable to verify your account password right now.'
    return
  }

  isVerifyingPassword.value = true

  try {
    await verifyPasswordForUser(resolveApiBaseUrl(), {
      email: authEmail.value,
      password: currentPassword.value,
      expectedUserId: authUserId.value,
    })

    step.value = 'scan'
    await nextTick()
    await startEnrollmentFlow()
  } catch (error) {
    passwordError.value = error?.message || 'Password confirmation failed.'
  } finally {
    isVerifyingPassword.value = false
  }
}

function handleCancel() {
  router.push({ name: 'ProfileSecurity' })
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
  statusMessage.value = 'Preparing camera...'

  const cameraReady = await startCamera()
  if (!cameraReady) {
    setEnrollmentError(
      cameraState.value === 'denied'
        ? 'Camera access is required to update Face ID.'
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
  statusMessage.value = 'Position your face in the center of the frame.'
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
    // Ignore autoplay issues.
  }

  const ready = await waitForVideoReady(el)
  if (!ready) {
    cameraState.value = 'unsupported'
    return false
  }

  cameraState.value = 'ready'
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
      setEnrollmentError('No face detected. Please try again in a brighter area.')
      return
    }

    try {
      const result = detectorInstance.detectForVideo(videoEl.value, now)
      const hasFace = Array.isArray(result?.detections) && result.detections.length > 0
      detectionStreak = hasFace ? detectionStreak + 1 : 0

      if (detectionStreak >= 2) {
        statusState.value = 'capturing'
        statusMessage.value = 'Face detected. Updating Face ID...'
        stopFaceDetection()
        captureTimeout = setTimeout(() => {
          captureAndRegister()
        }, captureDelayMs)
        return
      }
    } catch {
      setEnrollmentError('Face detection failed. Please try again.')
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
    statusMessage.value = 'Updating your Face ID...'

    const imageDataUrl = captureVideoFrame()
    capturedPreview.value = imageDataUrl
    stopCamera()

    const token = localStorage.getItem('nexus_token')
    await registerStudentFace(resolveApiBaseUrl(), token, imageDataUrl)

    markCurrentUserFaceRegistered()
    statusState.value = 'success'
    statusMessage.value = 'Face ID updated successfully.'
    redirectTimeout = setTimeout(() => {
      router.replace({ name: 'ProfileSecurity', query: { done: 'face' } })
    }, 1500)
  } catch (error) {
    setEnrollmentError(error?.message || 'Unable to update your Face ID right now.')
  }
}

function triggerFileUpload() {
  fileInputEl.value?.click()
}

async function handlePhotoUpload(event) {
  const file = event.target.files?.[0]
  if (!file) return

  stopFaceDetection()
  stopCamera()
  
  isUploading.value = true
  statusState.value = 'submitting'
  statusMessage.value = 'Uploading photo...'

  // Preview the file
  const reader = new FileReader()
  reader.onload = (e) => {
    capturedPreview.value = e.target.result
  }
  reader.readAsDataURL(file)

  try {
    const token = localStorage.getItem('nexus_token')
    await registerStudentFaceUpload(resolveApiBaseUrl(), token, file)

    markCurrentUserFaceRegistered()
    statusState.value = 'success'
    statusMessage.value = 'Photo uploaded and Face ID updated.'
    redirectTimeout = setTimeout(() => {
      router.replace({ name: 'ProfileSecurity', query: { done: 'face' } })
    }, 1500)
  } catch (error) {
    setEnrollmentError(error?.message || 'Unable to register face from photo.')
  } finally {
    isUploading.value = false
  }
}

function setEnrollmentError(message) {
  clearTimers()
  stopFaceDetection()
  stopCamera()
  statusState.value = 'error'
  statusMessage.value = message
}
</script>

<style scoped>
.face-update-page {
  min-height: 100vh;
  background: var(--color-bg, #ebebeb);
  padding: 24px;
  font-family: 'Manrope', sans-serif;
  display: flex;
  align-items: center;
  justify-content: center;
}

.face-update-shell {
  width: min(100%, 420px);
}

/* ── Auth Card ── */
.auth-card {
  background: rgba(255, 255, 255, 0.85);
  backdrop-filter: blur(12px);
  border-radius: 32px;
  padding: 40px 32px;
  box-shadow: 0 12px 40px rgba(0,0,0,0.06);
  text-align: center;
  border: 1px solid rgba(255, 255, 255, 0.5);
}

.auth-icon-wrap {
  width: 80px;
  height: 80px;
  background: var(--color-primary, #aaff00);
  color: var(--color-primary-text, #0a0a0a);
  border-radius: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 24px;
}

.face-update-auth__title {
  margin: 0 0 12px;
  font-size: 28px;
  font-weight: 800;
  letter-spacing: -0.04em;
  color: #0a0a0a;
}

.face-update-auth__copy {
  margin: 0 0 32px;
  font-size: 15px;
  line-height: 1.5;
  color: #555550;
}

.face-update-cancel-btn {
  background: transparent;
  border: none;
  color: #6d6d69;
  font-size: 14px;
  font-weight: 500;
  margin-top: 12px;
  cursor: pointer;
}

/* ── Scan Card ── */
.scan-card {
  background: rgba(255, 255, 255, 0.85);
  backdrop-filter: blur(12px);
  border-radius: 32px;
  padding: 32px;
  box-shadow: 0 12px 40px rgba(0,0,0,0.06);
  border: 1px solid rgba(255, 255, 255, 0.5);
}

.scan-header {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 32px;
}

.scan-back-btn {
  width: 40px;
  height: 40px;
  border-radius: 12px;
  background: #f4f4f1;
  border: none;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
}

.scan-title {
  margin: 0;
  font-size: 20px;
  font-weight: 700;
  letter-spacing: -0.02em;
}

/* ── Camera Frame ── */
.face-update-frame-container {
  position: relative;
  width: 260px;
  height: 260px;
  margin: 0 auto 24px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.face-update-ring {
  position: absolute;
  inset: 0;
  border: 2px dashed rgba(0, 0, 0, 0.1);
  border-radius: 50%;
  transition: all 0.5s ease;
}

.face-update-ring--active {
  border: 3px solid var(--color-primary, #aaff00);
  animation: pulse-ring 2s infinite;
}

@keyframes pulse-ring {
  0% { transform: scale(1); opacity: 0.8; }
  50% { transform: scale(1.05); opacity: 0.4; }
  100% { transform: scale(1); opacity: 0.8; }
}

.face-update-frame {
  width: 220px;
  height: 220px;
  border-radius: 50%;
  overflow: hidden;
  position: relative;
  background: #000;
  box-shadow: 0 8px 24px rgba(0,0,0,0.2);
}

.face-update-video,
.face-update-photo {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.face-update-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f4f4f1;
  color: #8d8d88;
}

/* ── Scanning Beam ── */
.face-update-beam {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 4px;
  background: linear-gradient(90deg, transparent, var(--color-primary, #aaff00), transparent);
  box-shadow: 0 0 15px var(--color-primary, #aaff00);
  z-index: 10;
  animation: scan-beam 2.5s infinite ease-in-out;
}

@keyframes scan-beam {
  0% { top: 0%; }
  50% { top: 100%; }
  100% { top: 0%; }
}

.face-update-overlay {
  position: absolute;
  inset: 0;
  background: rgba(0,0,0,0.4);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  z-index: 20;
}

/* ── Status ── */
.scan-status {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  margin-bottom: 24px;
}

.status-icon-wrap {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f4f4f1;
  color: #555550;
}

.status-icon-wrap.success { background: #e7f7ed; color: #2ecc71; }
.status-icon-wrap.error { background: #fdeaea; color: #e74c3c; }

.status-message {
  margin: 0;
  font-size: 14px;
  font-weight: 500;
  color: #555550;
}

.status-message.error { color: #e74c3c; }
.status-message.success { color: #2ecc71; }

/* ── Actions ── */
.scan-actions {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.scan-primary-btn {
  width: 100%;
  min-height: 56px;
  background: var(--color-primary, #aaff00);
  color: var(--color-primary-text, #0a0a0a);
  border: none;
  border-radius: 16px;
  font-weight: 700;
  font-size: 15px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  cursor: pointer;
}

.upload-option {
  text-align: center;
}

.upload-divider {
  display: block;
  font-size: 10px;
  font-weight: 800;
  color: #b5b5b0;
  margin-bottom: 12px;
  letter-spacing: 0.1em;
}

.upload-btn {
  background: transparent;
  border: 1.5px solid #dcdcd8;
  border-radius: 16px;
  min-height: 50px;
  width: 100%;
  color: #171717;
  font-weight: 600;
  font-size: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  cursor: pointer;
}

.hidden-input {
  display: none;
}

/* ── Tips ── */
.scan-tips {
  margin-top: 32px;
  padding-top: 24px;
  border-top: 1px solid #f0f0ed;
  text-align: left;
}

.tips-title {
  margin: 0 0 12px;
  font-size: 13px;
  font-weight: 700;
  color: #8d8d88;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.tips-list {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.tips-list li {
  font-size: 13px;
  color: #555550;
  display: flex;
  align-items: center;
  gap: 8px;
}

.tip-dot {
  width: 4px;
  height: 4px;
  border-radius: 50%;
  background: var(--color-primary, #aaff00);
}

/* ── Brand ── */
.face-update-brand {
  margin-top: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  opacity: 0.6;
}

.face-update-brand__logo {
  height: 24px;
}

.face-update-brand span {
  font-size: 12px;
  font-weight: 600;
  color: #111;
}

/* ── Helpers ── */
.spinner { animation: spin 1s linear infinite; }
.pulse { animation: pulse 1.5s ease-in-out infinite; }

@keyframes spin { to { transform: rotate(360deg); } }
@keyframes pulse {
  0% { transform: scale(1); opacity: 1; }
  50% { transform: scale(1.1); opacity: 0.7; }
  100% { transform: scale(1); opacity: 1; }
}

.face-update-field {
  position: relative;
  display: block;
}

.face-update-input {
  width: 100%;
  min-height: 56px;
  padding: 0 20px;
  border-radius: 16px;
  border: 1.5px solid #dcdcd8;
  background: #fdfdfc;
  font-size: 15px;
  outline: none;
}

.face-update-input:focus {
  border-color: var(--color-primary, #aaff00);
  box-shadow: 0 0 0 4px color-mix(in srgb, var(--color-primary, #aaff00) 15%, transparent);
}

.face-update-input::-ms-reveal,
.face-update-input::-ms-clear {
  display: none;
}

.face-update-visibility {
  position: absolute;
  right: 16px;
  top: 50%;
  transform: translateY(-50%);
  background: none;
  border: none;
  color: #8d8d88;
}

.face-update-actions {
  margin-top: 12px;
}
</style>
