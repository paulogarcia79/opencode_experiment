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
              <path stroke-linecap="round" stroke-linejoin="round" d="M15 7a2 2 0 012 2m4 0a6 6 0 01-7.743 5.743L11 17H9v2H7v2H4a1 1 0 01-1-1v-2a6 6 0 016-6h6.243M3 3l18 18" />
            </svg>
          </div>
        </div>

        <h1 class="text-xl font-display font-semibold text-white text-center mb-2">
          Reset Password
        </h1>
        <p class="text-sm text-slate-500 text-center mb-8">
          Enter your new password below
        </p>

        <!-- Error State -->
        <div v-if="error" class="mb-6 border border-red-500/20 bg-red-500/10 rounded-lg p-4 flex items-start gap-3">
          <svg class="h-5 w-5 text-red-400 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <div>
            <p class="text-sm font-medium text-red-300">Reset Failed</p>
            <p class="text-sm text-red-400/80 mt-0.5">{{ error }}</p>
          </div>
        </div>

        <form @submit.prevent="handleSubmit" class="space-y-5">
          <div>
            <label class="block text-sm font-medium text-slate-400 mb-2">New Password</label>
            <input
              v-model="password"
              type="password"
              required
              class="w-full px-4 py-3 rounded-lg bg-white/5 border border-white/10 text-white text-sm placeholder-slate-600 focus:outline-none focus:border-primary-500/50 focus:ring-2 focus:ring-primary-500/20 transition-all duration-200"
              placeholder="••••••••"
              :disabled="loading"
            />
          </div>
          <div>
            <label class="block text-sm font-medium text-slate-400 mb-2">Confirm Password</label>
            <input
              v-model="confirmPassword"
              type="password"
              required
              class="w-full px-4 py-3 rounded-lg bg-white/5 border border-white/10 text-white text-sm placeholder-slate-600 focus:outline-none focus:border-primary-500/50 focus:ring-2 focus:ring-primary-500/20 transition-all duration-200"
              placeholder="••••••••"
              :disabled="loading"
            />
          </div>
          <button
            type="submit"
            :disabled="loading"
            class="w-full inline-flex items-center justify-center gap-2 px-4 py-3 bg-primary-600 hover:bg-primary-500 disabled:opacity-50 disabled:cursor-not-allowed text-white text-sm font-medium rounded-lg transition-all duration-200 shadow-lg shadow-primary-600/20 hover:shadow-primary-500/30 cursor-pointer"
          >
            <svg v-if="loading" class="animate-spin h-4 w-4" viewBox="0 0 24 24" fill="none">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" />
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
            </svg>
            <span v-if="loading">Resetting...</span>
            <span v-else>Reset Password</span>
          </button>
        </form>

        <div class="mt-6 text-center">
          <RouterLink
            to="/auth"
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
import { ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { resetPassword } from '@/composables/useAdminApi'

const route = useRoute()
const router = useRouter()

const password = ref('')
const confirmPassword = ref('')
const loading = ref(false)
const error = ref('')

async function handleSubmit() {
  if (loading.value) return
  
  loading.value = true
  error.value = ''
  
  if (password.value !== confirmPassword.value) {
    error.value = 'Passwords do not match'
    loading.value = false
    return
  }

  const token = route.query.token as string
  if (!token) {
    error.value = 'Missing reset token. Please request a new link.'
    loading.value = false
    return
  }
  
  try {
    await resetPassword(token, password.value)
    router.push('/auth')
  } catch (e: any) {
    error.value = e.message || 'Something went wrong'
  } finally {
    loading.value = false
  }
}
</script>
