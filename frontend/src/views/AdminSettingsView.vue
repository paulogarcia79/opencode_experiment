<template>
  <div class="min-h-screen bg-surface-950">
    <div class="max-w-4xl mx-auto px-6 py-12">
      <h1 class="text-3xl font-display font-bold text-white mb-8">Settings</h1>

      <!-- Connected Accounts Section -->
      <div class="rounded-2xl border border-white/10 bg-white/[0.03] backdrop-blur-sm p-6">
        <h2 class="text-xl font-display font-semibold text-white mb-6">Connected Accounts</h2>

        <!-- Loading State -->
        <div v-if="loading" class="text-slate-400">Loading...</div>

        <!-- Error State -->
        <div v-else-if="error" class="border border-red-500/20 bg-red-500/10 rounded-lg p-4 text-red-300">
          {{ error }}
        </div>

        <!-- Accounts List -->
        <div v-else class="space-y-4">
          <div class="text-sm text-slate-400 mb-4">
            Email: <span class="text-slate-200">{{ account.email }}</span>
          </div>

          <!-- Google -->
          <div class="flex items-center justify-between p-4 rounded-lg bg-white/5 border border-white/10">
            <div class="flex items-center gap-3">
              <svg class="w-6 h-6" viewBox="0 0 24 24">
                <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92a5.06 5.06 0 0 1-2.2 3.32v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.1z"/>
                <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
                <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/>
                <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
              </svg>
              <div>
                <p class="text-white font-medium">Google</p>
                <p v-if="googleConnected" class="text-xs text-slate-400">Connected</p>
              </div>
            </div>
            <button
              v-if="googleConnected"
              @click="handleDisconnect('google')"
              :disabled="disconnecting"
              class="px-3 py-1.5 text-sm text-red-400 hover:text-red-300 border border-red-500/30 hover:border-red-500/50 rounded-lg transition-all cursor-pointer disabled:opacity-50"
            >
              Disconnect
            </button>
            <button
              v-else
              @click="handleConnect('google')"
              class="px-3 py-1.5 text-sm text-primary-400 hover:text-primary-300 border border-primary-500/30 hover:border-primary-500/50 rounded-lg transition-all cursor-pointer"
            >
              Connect
            </button>
          </div>

          <!-- GitHub -->
          <div class="flex items-center justify-between p-4 rounded-lg bg-white/5 border border-white/10">
            <div class="flex items-center gap-3">
              <svg class="w-6 h-6" fill="currentColor" viewBox="0 0 24 24">
                <path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 2.958.735.86-.238 1.782-.357 2.704-.36 1.526.003 2.854 1.166 2.854 2.609 0 1.868-1.112 3.395-2.656 3.508.209.453.396 1.349.396 2.721 0 1.967-.017 3.551-.017 4.037 0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z"/>
              </svg>
              <div>
                <p class="text-white font-medium">GitHub</p>
                <p v-if="githubConnected" class="text-xs text-slate-400">Connected</p>
              </div>
            </div>
            <button
              v-if="githubConnected"
              @click="handleDisconnect('github')"
              :disabled="disconnecting"
              class="px-3 py-1.5 text-sm text-red-400 hover:text-red-300 border border-red-500/30 hover:border-red-500/50 rounded-lg transition-all cursor-pointer disabled:opacity-50"
            >
              Disconnect
            </button>
            <button
              v-else
              @click="handleConnect('github')"
              class="px-3 py-1.5 text-sm text-primary-400 hover:text-primary-300 border border-primary-500/30 hover:border-primary-500/50 rounded-lg transition-all cursor-pointer"
            >
              Connect
            </button>
          </div>

          <!-- Disconnect Error -->
          <div v-if="disconnectError" class="border border-red-500/20 bg-red-500/10 rounded-lg p-4 text-red-300 text-sm">
            {{ disconnectError }}
          </div>

          <!-- Success Message -->
          <div v-if="successMessage" class="border border-green-500/20 bg-green-500/10 rounded-lg p-4 text-green-300 text-sm">
            {{ successMessage }}
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { fetchConnectedAccounts, disconnectOAuth, connectOAuth } from '@/composables/useAdminApi'

const route = useRoute()
const loading = ref(true)
const error = ref('')
const disconnecting = ref(false)
const disconnectError = ref('')
const successMessage = ref('')
const account = ref<{ email: string; is_verified: boolean; connected_providers: { provider: string; connected_at: string }[] }>({
  email: '',
  is_verified: false,
  connected_providers: [],
})

const googleConnected = computed(() => account.value.connected_providers.some(p => p.provider === 'google'))
const githubConnected = computed(() => account.value.connected_providers.some(p => p.provider === 'github'))

onMounted(async () => {
  // Check for success query param from OAuth callback
  const connectedProvider = route.query.connected as string
  if (connectedProvider) {
    successMessage.value = `Successfully connected ${connectedProvider}!`
  }

  try {
    account.value = await fetchConnectedAccounts()
  } catch (e: any) {
    error.value = e.message || 'Failed to load settings'
  } finally {
    loading.value = false
  }
})

async function handleDisconnect(provider: string) {
  disconnecting.value = true
  disconnectError.value = ''
  successMessage.value = ''

  try {
    await disconnectOAuth(provider)
    successMessage.value = `Disconnected from ${provider}`
    account.value = await fetchConnectedAccounts()
  } catch (e: any) {
    disconnectError.value = e.message || 'Failed to disconnect'
  } finally {
    disconnecting.value = false
  }
}

async function handleConnect(provider: string) {
  try {
    const data = await connectOAuth(provider)
    window.location.href = data.authorization_url
  } catch (e: any) {
    disconnectError.value = e.message || `Failed to connect ${provider}`
  }
}
</script>
