<template>
  <div class="min-h-screen bg-surface-950 flex items-center justify-center relative overflow-hidden">
    <!-- Background decorations -->
    <div class="absolute top-1/4 left-1/4 w-72 h-72 bg-primary-600/10 rounded-full blur-3xl" />
    <div class="absolute bottom-1/4 right-1/4 w-72 h-72 bg-accent-600/10 rounded-full blur-3xl" />

    <div class="relative w-full max-w-md mx-4">
      <!-- Card -->
      <div class="rounded-2xl border border-white/10 bg-white/[0.03] backdrop-blur-sm p-8 shadow-2xl shadow-black/20">
        <!-- Logo -->
        <div class="flex items-center justify-center mb-8">
          <div class="w-12 h-12 rounded-xl bg-primary-600 flex items-center justify-center shadow-lg shadow-primary-600/25">
            <svg class="w-6 h-6 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
              <path stroke-linecap="round" stroke-linejoin="round" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
            </svg>
          </div>
        </div>

        <h1 class="text-xl font-display font-semibold text-white text-center mb-2">
          Check Your Inbox
        </h1>
        <p class="text-sm text-slate-500 text-center mb-8">
          We've sent a verification link to <strong class="text-slate-300">{{ email }}</strong>. Click the link to activate your account.
        </p>

        <!-- Success State -->
        <div v-if="resendSuccess" class="mb-6 border border-green-500/20 bg-green-500/10 rounded-lg p-4 flex items-start gap-3">
          <svg class="h-5 w-5 text-green-400 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
          </svg>
          <p class="text-sm text-green-300">Verification email resent successfully!</p>
        </div>

        <!-- Error State -->
        <div v-if="error" class="mb-6 border border-red-500/20 bg-red-500/10 rounded-lg p-4 flex items-start gap-3">
          <svg class="h-5 w-5 text-red-400 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <p class="text-sm text-red-300">{{ error }}</p>
        </div>

        <button
          type="button"
          @click="handleResend"
          :disabled="loading"
          class="w-full inline-flex items-center justify-center gap-2 px-4 py-3 bg-primary-600 hover:bg-primary-500 disabled:opacity-50 disabled:cursor-not-allowed text-white text-sm font-medium rounded-lg transition-all duration-200 shadow-lg shadow-primary-600/20 hover:shadow-primary-500/30 cursor-pointer"
        >
          <svg v-if="loading" class="animate-spin h-4 w-4" viewBox="0 0 24 24" fill="none">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" />
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
          </svg>
          <span v-if="loading">Sending...</span>
          <span v-else>Resend Verification Email</span>
        </button>

        <div class="mt-6 text-center">
          <RouterLink
            to="/admin/login"
            class="text-sm text-slate-500 hover:text-primary-400 transition-colors duration-200 cursor-pointer"
          >
            Back to login
          </RouterLink>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { resendVerification } from '@/composables/useAdminApi'

const route = useRoute()
const email = ref('')
const loading = ref(false)
const error = ref('')
const resendSuccess = ref(false)

onMounted(() => {
  email.value = (route.query.email as string) || ''
})

async function handleResend() {
  if (loading.value || !email.value) return

  loading.value = true
  error.value = ''
  resendSuccess.value = false

  try {
    await resendVerification(email.value)
    resendSuccess.value = true
  } catch (e: any) {
    error.value = e.message || 'Failed to resend verification email'
  } finally {
    loading.value = false
  }
}
</script>
