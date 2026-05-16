<template>
  <div class="login-page min-h-dvh flex flex-col font-[Manrope] overflow-auto" style="background: var(--color-bg);">
    <!-- Main centered content -->
    <div class="flex-1 flex flex-col items-center justify-center px-8 relative z-10">
      <div class="w-full max-w-[340px] flex flex-col gap-6 login-form-area">

        <!-- Heading -->
        <h1 
          class="text-[22px] font-semibold leading-[1.4] tracking-[-0.3px] transition-all duration-700 ease-[cubic-bezier(0.22,1,0.36,1)] relative"
          style="color: var(--color-text-primary);"
          :class="isMounted ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-6'"
        >
          Welcome to the portal. Log in to access your dashboard.
        </h1>

        <!-- Form -->
        <form 
          class="flex flex-col gap-3 transition-all duration-700 delay-100 ease-[cubic-bezier(0.22,1,0.36,1)] relative" 
          :class="isMounted ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-6'"
          @submit.prevent="handleLogin"
        >
          <!-- Email -->
          <BaseInput
            id="email"
            v-model="email"
            type="email"
            placeholder="Gmail"
            autocomplete="email"
            tone="neutral"
            :disabled="isLoading"
          />

          <!-- Password -->
          <BaseInput
            id="password"
            v-model="password"
            type="password"
            placeholder="Password"
            autocomplete="current-password"
            tone="neutral"
            :disabled="isLoading"
            @enter="handleLogin"
          />

          <!-- Error message -->
          <Transition name="fade">
            <p v-if="visibleMessage" class="text-red-500 text-xs text-center mt-1">
              {{ visibleMessage }}
            </p>
          </Transition>

          <div class="flex items-center justify-between px-1">
            <label class="remember-row" for="remember-me">
              <input
                id="remember-me"
                v-model="rememberMe"
                type="checkbox"
                class="remember-row__checkbox"
                :disabled="isLoading"
              >
              <span class="remember-row__label">Remember me</span>
            </label>

            <button 
              type="button"
              class="text-[13px] font-semibold transition-colors hover:opacity-70"
              style="color: var(--color-primary);"
              @click="handleForgotPassword"
            >
              Forgot Password?
            </button>
          </div>

          <!-- Login Button -->
          <BaseButton
            type="submit"
            variant="primary"
            size="md"
            class="mt-1 group"
            :loading="isLoading"
          >
            Log In
          </BaseButton>

          <!-- Divider -->
          <div class="flex items-center gap-4 my-1 opacity-40">
            <div class="h-[1px] flex-1 bg-current"></div>
            <span class="text-[11px] font-bold uppercase tracking-wider">or</span>
            <div class="h-[1px] flex-1 bg-current"></div>
          </div>

          <!-- Google Login Button -->
          <BaseButton
            type="button"
            variant="neutral"
            size="md"
            class="group flex items-center justify-center gap-2"
            :disabled="isLoading"
            @click="handleGoogleLogin('placeholder_token')"
          >
            <svg class="w-4 h-4" viewBox="0 0 24 24">
              <path fill="currentColor" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" />
              <path fill="currentColor" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-1 .67-2.28 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" />
              <path fill="currentColor" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l3.66-2.84z" />
              <path fill="currentColor" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" />
            </svg>
            Continue with Google
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

        <!-- Powered by Aura -->
        <div 
          class="flex flex-col items-center justify-center gap-2 mt-1 transition-all duration-700 delay-200 ease-[cubic-bezier(0.22,1,0.36,1)]"
          :class="isMounted ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-4'"
        >
          <div class="flex items-center justify-center gap-2">
            <img
              :src="surfaceAuraLogo"
              alt="Aura"
              class="h-8 w-auto object-contain"
            />
            <span class="text-[13px] font-medium tracking-tight" style="color: var(--color-text-primary);">
              Powered by Aura Ai
            </span>
          </div>
        </div>

      </div>
    </div>

    <!-- Footer -->
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
  </div>
</template>

<script setup>
import BaseInput from '@/components/ui/BaseInput.vue'
import BaseButton from '@/components/ui/BaseButton.vue'
import { surfaceAuraLogo } from '@/config/theme.js'
import { useLoginViewModel } from '@/composables/useLoginViewModel.js'

const {
  email,
  password,
  rememberMe,
  isMounted,
  isLoading,
  visibleMessage,
  handleLogin,
  handleGoogleLogin,
  handleForgotPassword,
  openQuickAttendance,
} = useLoginViewModel()
</script>

<style scoped>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

/* Ensure form area scrolls above keyboard on mobile */
.login-form-area {
  padding-bottom: env(safe-area-inset-bottom, 16px);
}

/* When keyboard is open (viewport shrinks), allow scrolling */
.login-page {
  -webkit-overflow-scrolling: touch;
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
}
</style>
