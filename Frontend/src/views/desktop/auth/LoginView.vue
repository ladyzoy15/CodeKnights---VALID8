<template>
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
          
          <BaseInput
            id="email"
            v-model="email"
            type="email"
            placeholder="admin@yourdomain.com"
            autocomplete="email"
            tone="neutral"
            :disabled="isLoading"
            class="!rounded-[16px] border-gray-200 focus:border-black transition-colors"
          />

          <BaseInput
            id="password"
            v-model="password"
            type="password"
            placeholder="••••••••••••"
            autocomplete="current-password"
            tone="neutral"
            :disabled="isLoading"
            @enter="handleLogin"
            class="!rounded-[16px] border-gray-200 focus:border-black transition-colors mt-[-4px]"
          />

          <Transition name="fade">
            <p v-if="visibleMessage" class="text-red-500 text-[12px] text-center mt-1 font-medium bg-red-50 py-2 rounded-lg">
              {{ visibleMessage }}
            </p>
          </Transition>

          <label class="flex items-center gap-2 mt-[-4px] cursor-pointer w-max" for="remember-me">
            <input
              id="remember-me"
              v-model="rememberMe"
              type="checkbox"
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
  </div>
</template>

<script setup>
import { onBeforeMount, onUnmounted } from 'vue'
import BaseInput from '@/components/ui/BaseInput.vue'
import BaseButton from '@/components/ui/BaseButton.vue'
import { surfaceAuraLogo, applyLightOverride, removeLightOverride } from '@/config/theme.js'
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

onBeforeMount(() => {
  // Desktop split layout looks best strictly in light mode
  applyLightOverride()
})

onUnmounted(() => {
  removeLightOverride()
})
</script>

<style scoped>
.fade-enter-active,
.fade-leave-active {
  transition: all 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
  transform: translateY(-5px);
}
</style>
