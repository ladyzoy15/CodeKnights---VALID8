<template>
  <div class="mobile-app-layout">
    <main class="mobile-app-layout__main">
      <AppLayoutOutlet />
    </main>

    <!-- AI Assistant Floating UI -->
    <div class="mobile-app-layout__ai-trigger">
      <AuraChatFab />
    </div>
    <AuraChatWindow />

    <MobileBottomNav />
  </div>
</template>

<script setup>
import MobileBottomNav from '@/components/mobile/navigation/MobileBottomNav.vue'
import AppLayoutOutlet from '@/layouts/shared/AppLayoutOutlet.vue'
import AuraChatFab from '@/components/mobile/ai/AuraChatFab.vue'
import AuraChatWindow from '@/components/mobile/ai/AuraChatWindow.vue'
import { useProtectedShellSession } from '@/layouts/shared/useProtectedShellSession.js'

useProtectedShellSession()
</script>

<style scoped>
.mobile-app-layout {
  min-height: 100vh;
  background: var(--color-bg);
  font-family: 'Manrope', sans-serif;
}

.mobile-app-layout__main {
  min-height: 100vh;
  padding-bottom: 112px;
}

.mobile-app-layout__ai-trigger {
  position: fixed;
  right: 16px;
  bottom: 80px; /* Above bottom nav */
  z-index: 100;
}
</style>

