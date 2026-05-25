<template>
  <div
    class="app-boot-loader"
    role="status"
    aria-live="polite"
    aria-label="Loading NEXUS"
  >
    <div class="app-boot-loader__viewport">
      <div class="app-boot-loader__content">
        <!-- Logo Wrapper with Glow -->
        <div class="app-boot-loader__logo-wrapper">
          <div class="app-boot-loader__glow"></div>
          <img
            src="/logos/nexus_logo_white.png"
            alt="NEXUS Logo"
            class="app-boot-loader__logo"
          />
          <!-- Premium Rotating Gradient Ring -->
          <div class="app-boot-loader__ring"></div>
        </div>

        <!-- Sleek Loading Text -->
        <div class="app-boot-loader__text-container">
          <h1 class="app-boot-loader__brand">NEXUS</h1>
          <p class="app-boot-loader__status">Initializing secure portal...</p>
        </div>
      </div>
    </div>

    <span class="app-boot-loader__sr-only">Loading NEXUS</span>
  </div>
</template>

<script setup>
import { onMounted, onBeforeUnmount } from 'vue'
import { markBootSplashPlaybackReady } from '@/services/bootSplash.js'

let playbackReadyTimer = null
const PLAYBACK_READY_DELAY_MS = 300 // Small buffer to let the animation start smoothly before marking ready

onMounted(() => {
  playbackReadyTimer = window.setTimeout(() => {
    markBootSplashPlaybackReady()
  }, PLAYBACK_READY_DELAY_MS)
})

onBeforeUnmount(() => {
  if (playbackReadyTimer) {
    window.clearTimeout(playbackReadyTimer)
    playbackReadyTimer = null
  }
})
</script>

<style scoped>
.app-boot-loader {
  display: grid;
  place-items: center;
  width: 100%;
  height: 100%;
  background: #050505;
  font-family: 'Manrope', sans-serif;
  overflow: hidden;
}

.app-boot-loader__viewport {
  width: min(100vw, 430px);
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.app-boot-loader__content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 32px;
}

.app-boot-loader__logo-wrapper {
  position: relative;
  width: 120px;
  height: 120px;
  display: grid;
  place-items: center;
}

.app-boot-loader__logo {
  width: 64px;
  height: 64px;
  object-fit: contain;
  z-index: 2;
  animation: logo-breathe 3s ease-in-out infinite;
}

.app-boot-loader__glow {
  position: absolute;
  width: 80px;
  height: 80px;
  border-radius: 50%;
  background: radial-gradient(circle, rgba(255, 255, 255, 0.15) 0%, transparent 70%);
  filter: blur(10px);
  z-index: 1;
  animation: glow-pulse 3s ease-in-out infinite;
}

.app-boot-loader__ring {
  position: absolute;
  inset: 0;
  border-radius: 50%;
  padding: 2.5px;
  background: linear-gradient(135deg, rgba(255,255,255,0.4) 0%, rgba(255,255,255,0.05) 50%, rgba(255,255,255,0.3) 100%);
  -webkit-mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
  -webkit-mask-composite: xor;
  mask-composite: exclude;
  pointer-events: none;
  z-index: 3;
  animation: ring-spin 2s linear infinite;
}

.app-boot-loader__text-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  text-align: center;
}

.app-boot-loader__brand {
  margin: 0;
  font-size: 20px;
  font-weight: 800;
  letter-spacing: 0.25em;
  color: #ffffff;
  text-transform: uppercase;
  text-indent: 0.25em; /* Perfectly centers tracking */
  animation: text-fade 2.5s ease-in-out infinite alternate;
}

.app-boot-loader__status {
  margin: 0;
  font-size: 13px;
  font-weight: 500;
  color: rgba(255, 255, 255, 0.45);
  letter-spacing: 0.02em;
}

.app-boot-loader__sr-only {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border: 0;
}

/* Animations */
@keyframes logo-breathe {
  0%, 100% {
    transform: scale(1);
    opacity: 0.95;
  }
  50% {
    transform: scale(1.08);
    opacity: 1;
    filter: drop-shadow(0 0 8px rgba(255, 255, 255, 0.3));
  }
}

@keyframes glow-pulse {
  0%, 100% {
    transform: scale(1);
    opacity: 0.6;
  }
  50% {
    transform: scale(1.3);
    opacity: 1;
  }
}

@keyframes ring-spin {
  to {
    transform: rotate(360deg);
  }
}

@keyframes text-fade {
  0% {
    opacity: 0.7;
  }
  100% {
    opacity: 1;
    text-shadow: 0 0 12px rgba(255, 255, 255, 0.2);
  }
}
</style>
