<template>
  <div class="min-h-screen bg-surface-950">
    <ConfirmDialog />
    <!-- Navigation -->
    <nav class="border-b border-white/5 bg-surface-950/80 backdrop-blur-md sticky top-0 z-40">
      <div class="max-w-5xl mx-auto px-6 py-4 flex items-center justify-between">
        <div class="flex items-center gap-6">
          <RouterLink
            :to="homeRoute"
            class="flex items-center gap-2 text-lg font-display font-semibold text-white hover:text-primary-400 transition-colors duration-200 cursor-pointer"
          >
            <div class="w-7 h-7 rounded-md bg-primary-600 flex items-center justify-center">
              <svg class="w-3.5 h-3.5 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
              </svg>
            </div>
            Admin
          </RouterLink>
          <div class="hidden sm:flex items-center gap-1">
            <slot name="nav-items" />
          </div>
        </div>
        <RouterLink
          to="/"
          class="text-sm text-slate-500 hover:text-primary-400 transition-colors duration-200 cursor-pointer flex items-center gap-1"
        >
          <svg class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
          </svg>
          View Site
        </RouterLink>
      </div>
    </nav>

    <!-- Main Content -->
    <main class="max-w-5xl mx-auto px-6 py-8">
      <!-- Verification prompt -->
      <div v-if="showVerificationPrompt" class="flex flex-col items-center justify-center py-20">
        <div class="w-16 h-16 rounded-full bg-amber-500/10 flex items-center justify-center mb-6">
          <svg class="w-8 h-8 text-amber-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
            <path stroke-linecap="round" stroke-linejoin="round" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
          </svg>
        </div>
        <h2 class="text-xl font-display font-semibold text-white mb-2">Verify your email to access your dashboard</h2>
        <p class="text-sm text-slate-500 mb-6">Check your inbox for a verification link.</p>
        <button
          @click="handleResendVerification"
          :disabled="resending"
          class="px-4 py-2 bg-primary-600 hover:bg-primary-500 disabled:opacity-50 text-white text-sm font-medium rounded-lg transition-all duration-200 shadow-lg shadow-primary-600/20 cursor-pointer"
        >
          {{ resending ? 'Sending...' : 'Resend verification' }}
        </button>
      </div>
      <RouterView v-else />
    </main>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import { useAdminStore } from '@/stores/admin'
import { resendVerification } from '@/composables/useAdminApi'
import ConfirmDialog from '@/components/ConfirmDialog.vue'

const props = withDefaults(defineProps<{
  homeRoute?: string
}>(), {
  homeRoute: '/admin',
})

const store = useAdminStore()
const resending = ref(false)

const homeRoute = computed(() => props.homeRoute)

const showVerificationPrompt = computed(() => {
  if (!store.token) return false
  if (!store.user) return false
  return !store.user.is_verified
})

async function handleResendVerification() {
  if (resending.value) return
  resending.value = true
  try {
    await resendVerification()
  } catch {
    // silently fail
  } finally {
    resending.value = false
  }
}
</script>
