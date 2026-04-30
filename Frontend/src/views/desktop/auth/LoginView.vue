<template>
<<<<<<< HEAD
  <div class="login-page min-h-dvh flex flex-col overflow-auto" style="background: var(--color-bg);">
    <div class="flex-1 flex flex-col items-center justify-center px-8 relative z-10">
      <div class="w-full max-w-[340px] flex flex-col gap-6 login-form-area">
        <h1
          class="text-[22px] font-semibold leading-[1.4] tracking-[-0.3px] transition-all duration-700 ease-[cubic-bezier(0.22,1,0.36,1)] relative"
          style="color: var(--color-text-primary);"
          :class="isMounted ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-6'"
        >
          Welcome to the portal. Log in to access your dashboard.
        </h1>

        <form
          class="flex flex-col gap-3 transition-all duration-700 delay-100 ease-[cubic-bezier(0.22,1,0.36,1)] relative"
          :class="isMounted ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-6'"
          @submit.prevent="handleLogin"
        >
=======
  <div class="min-h-dvh flex font-[Manrope] w-full relative" style="background: linear-gradient(135deg, #eef7eb 0%, #f4f9f4 100%);">
    
    <!-- Left Section (Information & Branding) -->
    <div class="hidden lg:flex flex-1 flex-col justify-center px-16 xl:px-24">
      <div class="max-w-[480px]">
        <div class="flex items-center gap-3 mb-10">
          <img :src="surfaceAuraLogo" alt="Aura Logo" class="h-5 w-auto object-contain" />
          <span class="text-sm font-semibold tracking-tight text-gray-800">Powered by Aura Ai</span>
        </div>
        
        <p class="text-[11px] font-bold tracking-[0.15em] uppercase mb-4 text-gray-500">Desktop Workspace</p>
        
        <h1 class="text-[52px] xl:text-[60px] tracking-[-0.04em] leading-[1.05] mb-6 font-medium text-gray-900">
          Operate the full<br/>campus portal<br/>from one<br/>focused control<br/>room.
        </h1>
        
        <p class="text-gray-600 text-[15px] mb-8 max-w-md leading-relaxed">
          Desktop and mobile now live in separate folders, while auth,
          stores, and API services stay shared underneath.
        </p>

        <div class="flex flex-wrap gap-3">
          <span class="px-4 py-2 bg-white/50 backdrop-blur-sm rounded-3xl text-[11px] font-bold shadow-[0_2px_10px_rgba(0,0,0,0.02)] border border-white/60 text-gray-700">Shared Pinia stores</span>
          <span class="px-4 py-2 bg-white/50 backdrop-blur-sm rounded-3xl text-[11px] font-bold shadow-[0_2px_10px_rgba(0,0,0,0.02)] border border-white/60 text-gray-700">Shared API services</span>
          <span class="px-4 py-2 bg-white/50 backdrop-blur-sm rounded-3xl text-[11px] font-bold shadow-[0_2px_10px_rgba(0,0,0,0.02)] border border-white/60 text-gray-700">Desktop-only UI files</span>
        </div>
      </div>
    </div>

    <!-- Right Section (The Login Form) -->
    <div class="flex-1 flex flex-col items-center justify-center px-6 relative z-10 w-full lg:bg-transparent bg-gradient-to-br from-[#eef7eb] to-[#f4f9f4]">
      
      <!-- Mobile/Tablet top logo -->
      <div class="lg:hidden flex items-center justify-center gap-2 mb-8" :class="isMounted ? 'opacity-100' : 'opacity-0'">
        <img :src="surfaceAuraLogo" alt="Aura" class="h-8 w-auto object-contain" />
        <span class="text-[13px] font-medium tracking-tight text-gray-800">Powered by Aura Ai</span>
      </div>

      <div 
        class="w-full max-w-[420px] bg-white/95 backdrop-blur-xl p-8 xl:p-12 rounded-[2rem] shadow-[0_8px_40px_rgba(0,0,0,0.06)] border border-white transition-all duration-700 ease-[cubic-bezier(0.22,1,0.36,1)]"
        :class="isMounted ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-6'"
      >
        <div class="flex flex-col gap-2 mb-8">
          <p class="text-[10px] font-bold tracking-widest uppercase text-gray-500">Sign In</p>
          <h2 class="text-[32px] tracking-[-0.03em] font-bold text-gray-900 leading-tight">Welcome back</h2>
          <p class="text-[13px] text-gray-500 mt-1">Use your school account to open the web workspace.</p>
        </div>

        <!-- Form -->
        <form class="flex flex-col gap-4" @submit.prevent="handleLogin">
          
>>>>>>> Aura_update3
          <BaseInput
            id="email"
            v-model="email"
            type="email"
<<<<<<< HEAD
            placeholder="Gmail"
            autocomplete="email"
            tone="neutral"
            :disabled="isLoading"
=======
            placeholder="admin@yourdomain.com"
            autocomplete="email"
            tone="neutral"
            :disabled="isLoading"
            class="!rounded-[16px] border-gray-200 focus:border-black transition-colors"
>>>>>>> Aura_update3
          />

          <BaseInput
            id="password"
            v-model="password"
            type="password"
<<<<<<< HEAD
            placeholder="Password"
=======
            placeholder="••••••••••••"
>>>>>>> Aura_update3
            autocomplete="current-password"
            tone="neutral"
            :disabled="isLoading"
            @enter="handleLogin"
<<<<<<< HEAD
          />

          <Transition name="fade">
            <p v-if="visibleMessage" class="text-red-500 text-xs text-center mt-1">
=======
            class="!rounded-[16px] border-gray-200 focus:border-black transition-colors mt-[-4px]"
          />

          <Transition name="fade">
            <p v-if="visibleMessage" class="text-red-500 text-[12px] text-center mt-1 font-medium bg-red-50 py-2 rounded-lg">
>>>>>>> Aura_update3
              {{ visibleMessage }}
            </p>
          </Transition>

<<<<<<< HEAD
          <label class="remember-row" for="remember-me">
=======
          <label class="flex items-center gap-2 mt-[-4px] cursor-pointer w-max" for="remember-me">
>>>>>>> Aura_update3
            <input
              id="remember-me"
              v-model="rememberMe"
              type="checkbox"
<<<<<<< HEAD
              class="remember-row__checkbox"
              :disabled="isLoading"
            >
            <span class="remember-row__label">Remember me</span>
          </label>

          <BaseButton
            type="submit"
            variant="primary"
            size="md"
            class="mt-1 group"
            :loading="isLoading"
          >
            Log In
          </BaseButton>

          <BaseButton
            type="button"
            variant="secondary"
            size="md"
            class="group"
            :disabled="isLoading"
            @click="openQuickAttendance"
          >
            Quick Attendance
          </BaseButton>
        </form>

        <div
          class="flex flex-col items-center justify-center gap-2 mt-1 transition-all duration-700 delay-200 ease-[cubic-bezier(0.22,1,0.36,1)]"
          :class="isMounted ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-4'"
        >
          <div class="flex items-center justify-center gap-2">
            <img
              :src="surfaceAuraLogo"
              alt="Aura"
              class="h-8 w-auto object-contain"
            >
            <span class="text-[13px] font-medium tracking-tight" style="color: var(--color-text-primary);">
              Powered by Aura Ai
            </span>
          </div>
        </div>
      </div>
    </div>

    <footer
      class="pb-8 flex justify-center transition-all duration-1000 delay-300 ease-out relative z-10"
      :class="isMounted ? 'opacity-100' : 'opacity-0'"
    >
      <a
        href="#"
        class="text-[12px] font-medium transition-colors"
        style="color: var(--color-text-secondary);"
      >
        Learn more about Aura Project
      </a>
    </footer>
=======
              class="w-4 h-4 accent-black rounded cursor-pointer"
              :disabled="isLoading"
            >
            <span class="text-[13px] font-semibold text-gray-700 select-none">Remember me</span>
          </label>

          <div class="flex flex-col gap-2 mt-2">
            <BaseButton
              type="submit"
              variant="primary"
              size="md"
              class="w-full !rounded-full !bg-black !text-white h-[48px] font-semibold tracking-wide hover:!bg-gray-800 transition-colors shadow-md"
              :loading="isLoading"
            >
              Log In
            </BaseButton>

            <BaseButton
              type="button"
              variant="secondary"
              size="md"
              class="w-full !rounded-full !bg-white !text-black border border-gray-200 h-[48px] font-semibold tracking-wide hover:!bg-gray-50 transition-colors"
              :disabled="isLoading"
              @click="openQuickAttendance"
            >
              Quick Attendance
            </BaseButton>
          </div>
        </form>
      </div>
    </div>
>>>>>>> Aura_update3
  </div>
</template>

<script setup>
<<<<<<< HEAD
import BaseInput from '@/components/ui/BaseInput.vue'
import BaseButton from '@/components/ui/BaseButton.vue'
import { surfaceAuraLogo } from '@/config/theme.js'
=======
import { onBeforeMount, onUnmounted } from 'vue'
import BaseInput from '@/components/ui/BaseInput.vue'
import BaseButton from '@/components/ui/BaseButton.vue'
import { surfaceAuraLogo, applyLightOverride, removeLightOverride } from '@/config/theme.js'
>>>>>>> Aura_update3
import { useLoginViewModel } from '@/composables/useLoginViewModel.js'

const {
  email,
  password,
  rememberMe,
  isMounted,
  isLoading,
  visibleMessage,
  handleLogin,
  openQuickAttendance,
} = useLoginViewModel()
<<<<<<< HEAD
=======

onBeforeMount(() => {
  // Desktop split layout looks best strictly in light mode
  applyLightOverride()
})

onUnmounted(() => {
  removeLightOverride()
})
>>>>>>> Aura_update3
</script>

<style scoped>
.fade-enter-active,
.fade-leave-active {
<<<<<<< HEAD
  transition: opacity 0.3s ease;
=======
  transition: all 0.3s ease;
>>>>>>> Aura_update3
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
<<<<<<< HEAD
}

.login-page {
  font-family: 'Manrope', sans-serif;
  -webkit-overflow-scrolling: touch;
}

.login-form-area {
  padding-bottom: env(safe-area-inset-bottom, 16px);
}

.remember-row {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 2px 4px 0;
  color: var(--color-text-primary);
  font-size: 13px;
  font-weight: 600;
}

.remember-row__checkbox {
  width: 16px;
  height: 16px;
  accent-color: var(--color-primary);
}

.remember-row__label {
  line-height: 1.2;
=======
  transform: translateY(-5px);
>>>>>>> Aura_update3
}
</style>
