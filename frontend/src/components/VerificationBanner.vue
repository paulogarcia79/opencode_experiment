<template>
  <div
    v-if="showBanner"
    class="border-b border-amber-500/20 bg-amber-500/10"
  >
    <div class="max-w-4xl mx-auto px-6 py-3 flex items-center justify-between gap-4">
      <div class="flex items-center gap-2">
        <svg class="w-4 h-4 text-amber-400 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
          <path stroke-linecap="round" stroke-linejoin="round" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
        </svg>
        <span class="text-sm text-amber-300">Verify your email to unlock full access.</span>
      </div>
      <div class="flex items-center gap-2">
        <button
          data-test="resend-verification"
          @click="handleResend"
          :disabled="resending"
          class="text-sm text-primary-400 hover:text-primary-300 font-medium transition-colors cursor-pointer"
        >
          {{ resending ? 'Sending...' : 'Resend verification' }}
        </button>
        <button
          data-test="dismiss-banner"
          @click="handleDismiss"
          class="p-1 text-slate-500 hover:text-white transition-colors cursor-pointer"
        >
          <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
            <path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useAdminStore } from '@/stores/admin'
import { resendVerification } from '@/composables/useAdminApi'

const store = useAdminStore()
const resending = ref(false)

const showBanner = computed(() => {
  if (!store.token) return false
  if (!store.user) return false
  if (store.user.is_verified) return false
  if (store.isVerificationBannerDismissed) return false
  return true
})

function handleDismiss() {
  store.isVerificationBannerDismissed = true
}

async function handleResend() {
  if (resending.value) return
  resending.value = true
  try {
    await resendVerification()
  } catch {
    // silently fail — the user can try again
  } finally {
    resending.value = false
  }
}
</script>
