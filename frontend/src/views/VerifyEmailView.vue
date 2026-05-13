<template>
  <div class="min-h-screen bg-surface-950 flex items-center justify-center relative overflow-hidden">
    <div class="absolute top-1/4 left-1/4 w-72 h-72 bg-primary-600/10 rounded-full blur-3xl" />
    <div class="absolute bottom-1/4 right-1/4 w-72 h-72 bg-accent-600/10 rounded-full blur-3xl" />

    <div class="relative w-full max-w-md mx-4">
      <div class="rounded-2xl border border-white/10 bg-white/[0.03] backdrop-blur-sm p-8 shadow-2xl shadow-black/20">
        <div class="flex items-center justify-center mb-8">
          <div class="w-12 h-12 rounded-xl bg-primary-600 flex items-center justify-center shadow-lg shadow-primary-600/25">
            <svg class="w-6 h-6 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
              <path stroke-linecap="round" stroke-linejoin="round" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
            </svg>
          </div>
        </div>

        <!-- Loading -->
        <div v-if="loading" data-test="loading" class="flex justify-center py-8">
          <svg class="animate-spin h-6 w-6 text-primary-400" viewBox="0 0 24 24" fill="none">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" />
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
          </svg>
        </div>

        <!-- Success -->
        <div v-if="success">
          <div class="flex justify-center mb-6">
            <div class="w-16 h-16 rounded-full bg-green-500/10 flex items-center justify-center">
              <svg class="w-8 h-8 text-green-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                <path stroke-linecap="round" stroke-linejoin="round" d="M5 13l4 4L19 7" />
              </svg>
            </div>
          </div>
          <h1 class="text-xl font-display font-semibold text-white text-center mb-2">
            Email Verified!
          </h1>
          <p class="text-sm text-slate-500 text-center">
            Your account is now verified. Redirecting...
          </p>
        </div>

        <!-- Error -->
        <div v-if="error">
          <div class="flex justify-center mb-6">
            <div class="w-16 h-16 rounded-full bg-red-500/10 flex items-center justify-center">
              <svg class="w-8 h-8 text-red-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                <path stroke-linecap="round" stroke-linejoin="round" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
          </div>
          <h1 class="text-xl font-display font-semibold text-white text-center mb-2">
            Verification Failed
          </h1>
          <p class="text-sm text-slate-500 text-center mb-8">
            This link is invalid or has expired.
          </p>
          <div class="text-center">
            <RouterLink
              to="/auth?tab=verify&expired=true"
              class="inline-flex items-center px-4 py-2 bg-primary-600 hover:bg-primary-500 text-white text-sm font-medium rounded-lg transition-all duration-200 shadow-lg shadow-primary-600/20 cursor-pointer"
            >
              Get a new link
            </RouterLink>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'

const route = useRoute()
const router = useRouter()
const loading = ref(true)
const success = ref(false)
const error = ref('')

onMounted(async () => {
  const token = route.query.token as string
  if (!token) {
    loading.value = false
    error.value = 'Missing verification token.'
    return
  }

  try {
    const res = await fetch('/api/auth/verify-email', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ token }),
    })

    if (res.ok) {
      loading.value = false
      success.value = true
      setTimeout(() => {
        router.push('/')
      }, 2000)
    } else {
      loading.value = false
      error.value = 'invalid'
    }
  } catch {
    loading.value = false
    error.value = 'invalid'
  }
})
</script>
