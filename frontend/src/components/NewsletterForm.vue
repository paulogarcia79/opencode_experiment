<template>
  <div class="rounded-xl border border-white/5 bg-white/[0.02] p-6">
    <div class="flex items-start gap-4">
      <div class="w-10 h-10 rounded-lg bg-primary-600/15 flex items-center justify-center flex-shrink-0">
        <svg class="w-5 h-5 text-primary-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
        </svg>
      </div>
      <div class="flex-1 min-w-0">
        <h3 class="text-base font-display font-semibold text-white">Subscribe to the newsletter</h3>
        <p class="mt-1 text-sm text-slate-500">Get notified when new articles are published.</p>

        <form @submit.prevent="handleSubmit" class="mt-4">
          <div class="flex flex-col sm:flex-row gap-3">
            <input
              v-model="email"
              type="email"
              required
              placeholder="your@email.com"
              class="flex-1 px-4 py-2.5 rounded-lg bg-white/5 border border-white/10 text-white text-sm font-mono placeholder-slate-600 focus:outline-none focus:border-primary-500/50 focus:ring-2 focus:ring-primary-500/20 transition-all duration-200"
              :disabled="state === 'loading'"
            />
            <button
              type="submit"
              :disabled="state === 'loading' || !email"
              class="inline-flex items-center justify-center gap-2 px-5 py-2.5 bg-primary-600 hover:bg-primary-500 disabled:opacity-50 disabled:cursor-not-allowed text-white text-sm font-medium rounded-lg transition-all duration-200 shadow-lg shadow-primary-600/20 hover:shadow-primary-500/30 cursor-pointer whitespace-nowrap"
            >
              <svg v-if="state === 'loading'" class="animate-spin h-4 w-4" viewBox="0 0 24 24" fill="none">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" />
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
              </svg>
              <span v-if="state === 'loading'">Subscribing...</span>
              <span v-else>Subscribe</span>
            </button>
          </div>
        </form>

        <!-- Success State -->
        <div
          v-if="state === 'success'"
          class="mt-4 flex items-start gap-3 p-4 rounded-lg border border-emerald-500/20 bg-emerald-500/10"
          role="alert"
        >
          <svg class="h-5 w-5 text-emerald-400 mt-0.5 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
          </svg>
          <div>
            <p class="font-medium text-emerald-300 text-sm">Success</p>
            <p class="text-sm text-emerald-400/80 mt-0.5">{{ message }}</p>
          </div>
        </div>

        <!-- Error State -->
        <div
          v-if="state === 'error'"
          class="mt-4 flex items-start gap-3 p-4 rounded-lg border border-red-500/20 bg-red-500/10"
          role="alert"
        >
          <svg class="h-5 w-5 text-red-400 mt-0.5 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <div>
            <p class="font-medium text-red-300 text-sm">Error</p>
            <p class="text-sm text-red-400/80 mt-0.5">{{ message }}</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { subscribeToNewsletter } from '@/composables/useApi'

const email = ref('')
const state = ref<'idle' | 'loading' | 'success' | 'error'>('idle')
const message = ref('')

async function handleSubmit() {
  state.value = 'loading'
  message.value = ''

  try {
    const result = await subscribeToNewsletter(email.value)
    state.value = 'success'
    message.value = result.message || 'Check your email to confirm your subscription.'
    email.value = ''
  } catch (e: any) {
    state.value = 'error'
    message.value = e.message || 'Something went wrong. Please try again.'
  }
}
</script>
