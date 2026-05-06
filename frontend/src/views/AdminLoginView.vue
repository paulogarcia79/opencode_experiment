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
              <path stroke-linecap="round" stroke-linejoin="round" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
            </svg>
          </div>
        </div>

        <h1 class="text-xl font-display font-semibold text-white text-center mb-2">
          Admin Login
        </h1>
        <p class="text-sm text-slate-500 text-center mb-8">
          Enter your API token to access the dashboard
        </p>

        <form @submit.prevent="login" class="space-y-5">
          <div>
            <label class="block text-sm font-medium text-slate-400 mb-2">API Token</label>
            <input
              v-model="token"
              type="password"
              required
              class="w-full px-4 py-3 rounded-lg bg-white/5 border border-white/10 text-white text-sm font-mono placeholder-slate-600 focus:outline-none focus:border-primary-500/50 focus:ring-2 focus:ring-primary-500/20 transition-all duration-200"
              placeholder="Bearer token"
            />
          </div>
          <button
            type="submit"
            class="w-full px-4 py-3 bg-primary-600 hover:bg-primary-500 text-white text-sm font-medium rounded-lg transition-all duration-200 shadow-lg shadow-primary-600/20 hover:shadow-primary-500/30 cursor-pointer"
          >
            Login
          </button>
        </form>

        <div class="mt-6 text-center">
          <RouterLink
            to="/"
            class="text-sm text-slate-500 hover:text-primary-400 transition-colors duration-200 cursor-pointer"
          >
            Back to blog
          </RouterLink>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAdminStore } from '@/stores/admin'

const token = ref('')
const router = useRouter()
const store = useAdminStore()

function login() {
  store.setToken(token.value)
  router.push('/admin')
}
</script>
