<template>
  <div class="min-h-screen bg-surface-950 flex items-center justify-center relative overflow-hidden">
    <div class="absolute top-1/4 left-1/4 w-72 h-72 bg-primary-600/10 rounded-full blur-3xl" />
    <div class="absolute bottom-1/4 right-1/4 w-72 h-72 bg-accent-600/10 rounded-full blur-3xl" />

    <div class="relative w-full max-w-md mx-4">
      <div class="rounded-2xl border border-white/10 bg-white/[0.03] backdrop-blur-sm p-8 shadow-2xl shadow-black/20">
        <!-- Logo -->
        <div class="flex items-center justify-center mb-8">
          <div class="w-12 h-12 rounded-xl bg-primary-600 flex items-center justify-center shadow-lg shadow-primary-600/25">
            <svg class="w-6 h-6 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
              <path stroke-linecap="round" stroke-linejoin="round" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
            </svg>
          </div>
        </div>

        <!-- Expired verification mode -->
        <template v-if="isExpiredVerification">
          <h1 class="text-xl font-display font-semibold text-white text-center mb-2">
            Link Expired
          </h1>
          <p class="text-sm text-slate-500 text-center mb-8">
            This verification link has expired. Click below to resend.
          </p>
          <button
            type="button"
            @click="handleResendVerification"
            :disabled="loading"
            class="w-full inline-flex items-center justify-center gap-2 px-4 py-3 bg-primary-600 hover:bg-primary-500 disabled:opacity-50 disabled:cursor-not-allowed text-white text-sm font-medium rounded-lg transition-all duration-200 shadow-lg shadow-primary-600/20 hover:shadow-primary-500/30 cursor-pointer"
          >
            <span v-if="loading">Sending...</span>
            <span v-else>Resend Verification</span>
          </button>
          <div class="mt-6 text-center">
            <a
              href="#"
              @click.prevent="activeTab = 'login'"
              class="text-sm text-slate-500 hover:text-primary-400 transition-colors duration-200 cursor-pointer"
            >Back to login</a>
          </div>
        </template>

        <!-- Setup mode -->
        <template v-else-if="isSetup">
          <h1 class="text-xl font-display font-semibold text-white text-center mb-2">
            Set Up Your Account
          </h1>
          <p class="text-sm text-slate-500 text-center mb-8">
            Create a password to activate your account
          </p>

          <div v-if="error" class="mb-6 border border-red-500/20 bg-red-500/10 rounded-lg p-4 flex items-start gap-3">
            <svg class="h-5 w-5 text-red-400 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <div>
              <p class="text-sm font-medium text-red-300">Setup Failed</p>
              <p class="text-sm text-red-400/80 mt-0.5">{{ error }}</p>
            </div>
          </div>

          <div v-if="setupSuccess" class="mb-6 border border-green-500/20 bg-green-500/10 rounded-lg p-4 flex items-start gap-3">
            <svg class="h-5 w-5 text-green-400 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
            </svg>
            <div>
              <p class="text-sm font-medium text-green-300">Account Activated!</p>
              <p class="text-sm text-green-400/80 mt-0.5">Redirecting to login...</p>
            </div>
          </div>

          <form v-if="!setupSuccess" @submit.prevent="handleSetup" class="space-y-5">
            <div>
              <label class="block text-sm font-medium text-slate-400 mb-2">Password</label>
              <input v-model="password" type="password" required
                class="w-full px-4 py-3 rounded-lg bg-white/5 border border-white/10 text-white text-sm placeholder-slate-600 focus:outline-none focus:border-primary-500/50 focus:ring-2 focus:ring-primary-500/20 transition-all duration-200"
                placeholder="••••••••" :disabled="loading" />
            </div>
            <div>
              <label class="block text-sm font-medium text-slate-400 mb-2">Confirm Password</label>
              <input v-model="confirmPassword" type="password" required
                class="w-full px-4 py-3 rounded-lg bg-white/5 border border-white/10 text-white text-sm placeholder-slate-600 focus:outline-none focus:border-primary-500/50 focus:ring-2 focus:ring-primary-500/20 transition-all duration-200"
                placeholder="••••••••" :disabled="loading" />
            </div>
            <button type="submit" :disabled="loading"
              class="w-full inline-flex items-center justify-center gap-2 px-4 py-3 bg-primary-600 hover:bg-primary-500 disabled:opacity-50 disabled:cursor-not-allowed text-white text-sm font-medium rounded-lg transition-all duration-200 shadow-lg shadow-primary-600/20 hover:shadow-primary-500/30 cursor-pointer">
              <span v-if="loading">Setting up...</span>
              <span v-else>Set Up Account</span>
            </button>
          </form>
        </template>

        <!-- Login + Register tabs -->
        <template v-else>
          <!-- Tab switcher -->
          <div class="flex gap-1 mb-8 p-1 rounded-lg bg-white/5 border border-white/5">
            <button
              data-test="login-tab"
              @click="activeTab = 'login'"
              :class="[
                'flex-1 py-2 text-sm font-medium rounded-md transition-all duration-200 cursor-pointer',
                activeTab === 'login' ? 'bg-primary-600 text-white shadow-lg shadow-primary-600/20' : 'text-slate-400 hover:text-white'
              ]"
            >Log in</button>
            <button
              data-test="register-tab"
              @click="activeTab = 'register'"
              :class="[
                'flex-1 py-2 text-sm font-medium rounded-md transition-all duration-200 cursor-pointer',
                activeTab === 'register' ? 'bg-primary-600 text-white shadow-lg shadow-primary-600/20' : 'text-slate-400 hover:text-white'
              ]"
            >Register</button>
          </div>

          <!-- Error state -->
          <div v-if="error" class="mb-6 border border-red-500/20 bg-red-500/10 rounded-lg p-4 flex items-start gap-3">
            <svg class="h-5 w-5 text-red-400 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <div>
              <p class="text-sm font-medium text-red-300">{{ activeTab === 'login' ? 'Login Failed' : 'Registration Failed' }}</p>
              <p class="text-sm text-red-400/80 mt-0.5">{{ error }}</p>
            </div>
          </div>

          <!-- Duplicate email hint -->
          <div v-if="duplicateHint" class="mb-6 border border-amber-500/20 bg-amber-500/10 rounded-lg p-4">
            <p class="text-sm text-amber-300">An account with this email may already exist.</p>
            <a href="#" @click.prevent="switchToLogin" class="text-sm text-primary-400 hover:text-primary-300 mt-1 inline-block">Log in instead</a>
          </div>

          <!-- Login form -->
          <form v-if="activeTab === 'login'" @submit.prevent="handleLogin" class="space-y-5">
            <div>
              <label class="block text-sm font-medium text-slate-400 mb-2">Email</label>
              <input v-model="email" type="email" required
                class="w-full px-4 py-3 rounded-lg bg-white/5 border border-white/10 text-white text-sm placeholder-slate-600 focus:outline-none focus:border-primary-500/50 focus:ring-2 focus:ring-primary-500/20 transition-all duration-200"
                placeholder="admin@example.com" :disabled="loading" />
            </div>
            <div>
              <label class="block text-sm font-medium text-slate-400 mb-2">Password</label>
              <input v-model="password" type="password" required
                class="w-full px-4 py-3 rounded-lg bg-white/5 border border-white/10 text-white text-sm placeholder-slate-600 focus:outline-none focus:border-primary-500/50 focus:ring-2 focus:ring-primary-500/20 transition-all duration-200"
                placeholder="••••••••" :disabled="loading" />
            </div>
            <button type="submit" :disabled="loading"
              class="w-full inline-flex items-center justify-center gap-2 px-4 py-3 bg-primary-600 hover:bg-primary-500 disabled:opacity-50 disabled:cursor-not-allowed text-white text-sm font-medium rounded-lg transition-all duration-200 shadow-lg shadow-primary-600/20 hover:shadow-primary-500/30 cursor-pointer">
              <svg v-if="loading" class="animate-spin h-4 w-4" viewBox="0 0 24 24" fill="none">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" />
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
              </svg>
              <span v-if="loading">Signing in...</span>
              <span v-else>Login</span>
            </button>
            <div class="text-center">
              <RouterLink data-test="forgot-password" to="/auth/forgot-password"
                class="text-sm text-slate-500 hover:text-primary-400 transition-colors duration-200 cursor-pointer">
                Forgot password?
              </RouterLink>
            </div>
          </form>

          <!-- Register form -->
          <form v-if="activeTab === 'register'" @submit.prevent="handleRegister" class="space-y-5">
            <div>
              <label class="block text-sm font-medium text-slate-400 mb-2">Email</label>
              <input v-model="email" type="email" required
                class="w-full px-4 py-3 rounded-lg bg-white/5 border border-white/10 text-white text-sm placeholder-slate-600 focus:outline-none focus:border-primary-500/50 focus:ring-2 focus:ring-primary-500/20 transition-all duration-200"
                placeholder="you@example.com" :disabled="loading" />
            </div>
            <div>
              <label class="block text-sm font-medium text-slate-400 mb-2">Password</label>
              <input v-model="password" type="password" required
                class="w-full px-4 py-3 rounded-lg bg-white/5 border border-white/10 text-white text-sm placeholder-slate-600 focus:outline-none focus:border-primary-500/50 focus:ring-2 focus:ring-primary-500/20 transition-all duration-200"
                placeholder="••••••••" :disabled="loading" />
              <!-- Password validation indicators -->
              <div class="mt-2 space-y-1 text-xs">
                <div :class="password.length >= 8 ? 'text-green-400' : 'text-slate-500'">
                  <span class="mr-1">{{ password.length >= 8 ? '✓' : '○' }}</span> At least 8 characters
                </div>
                <div :class="/[A-Z]/.test(password) ? 'text-green-400' : 'text-slate-500'">
                  <span class="mr-1">{{ /[A-Z]/.test(password) ? '✓' : '○' }}</span> One uppercase letter
                </div>
                <div :class="/[a-z]/.test(password) ? 'text-green-400' : 'text-slate-500'">
                  <span class="mr-1">{{ /[a-z]/.test(password) ? '✓' : '○' }}</span> One lowercase letter
                </div>
                <div :class="/[0-9]/.test(password) ? 'text-green-400' : 'text-slate-500'">
                  <span class="mr-1">{{ /[0-9]/.test(password) ? '✓' : '○' }}</span> One digit
                </div>
              </div>
            </div>
            <div>
              <label class="block text-sm font-medium text-slate-400 mb-2">Confirm Password</label>
              <input v-model="confirmPassword" type="password" required
                class="w-full px-4 py-3 rounded-lg bg-white/5 border border-white/10 text-white text-sm placeholder-slate-600 focus:outline-none focus:border-primary-500/50 focus:ring-2 focus:ring-primary-500/20 transition-all duration-200"
                placeholder="••••••••" :disabled="loading" />
              <div v-if="confirmPassword.length > 0" class="mt-1 text-xs" :class="password === confirmPassword ? 'text-green-400' : 'text-red-400'">
                {{ password === confirmPassword ? '✓ Passwords match' : '✗ Passwords do not match' }}
              </div>
            </div>
            <button type="submit" :disabled="loading || !isPasswordValid || password !== confirmPassword"
              class="w-full inline-flex items-center justify-center gap-2 px-4 py-3 bg-primary-600 hover:bg-primary-500 disabled:opacity-50 disabled:cursor-not-allowed text-white text-sm font-medium rounded-lg transition-all duration-200 shadow-lg shadow-primary-600/20 hover:shadow-primary-500/30 cursor-pointer">
              <span v-if="loading">Creating account...</span>
              <span v-else>Create Account</span>
            </button>
          </form>

          <!-- OAuth section -->
          <div class="mt-6 flex items-center gap-4">
            <div class="flex-1 h-px bg-white/10" />
            <span class="text-xs text-slate-500 uppercase">or continue with</span>
            <div class="flex-1 h-px bg-white/10" />
          </div>

          <div class="mt-6 grid grid-cols-2 gap-3">
            <button type="button" @click="handleOAuthLogin('google')"
              class="inline-flex items-center justify-center gap-2 px-4 py-3 bg-white/5 hover:bg-white/10 border border-white/10 text-white text-sm font-medium rounded-lg transition-all duration-200 cursor-pointer">
              <svg class="w-5 h-5" viewBox="0 0 24 24">
                <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92a5.06 5.06 0 0 1-2.2 3.32v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.1z"/>
                <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
                <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/>
                <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
              </svg>
              Google
            </button>
            <button type="button" @click="handleOAuthLogin('github')"
              class="inline-flex items-center justify-center gap-2 px-4 py-3 bg-white/5 hover:bg-white/10 border border-white/10 text-white text-sm font-medium rounded-lg transition-all duration-200 cursor-pointer">
              <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
                <path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 2.958.735.86-.238 1.782-.357 2.704-.36 1.526.003 2.854 1.166 2.854 2.609 0 1.868-1.112 3.395-2.656 3.508.209.453.396 1.349.396 2.721 0 1.967-.017 3.551-.017 4.037 0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z"/>
              </svg>
              GitHub
            </button>
          </div>

          <div class="mt-6 text-center">
            <RouterLink to="/" class="text-sm text-slate-500 hover:text-primary-400 transition-colors duration-200 cursor-pointer">
              Back to blog
            </RouterLink>
          </div>
        </template>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAdminStore } from '@/stores/admin'
import { login, register, setupAccount, resendVerification } from '@/composables/useAdminApi'

const router = useRouter()
const route = useRoute()
const store = useAdminStore()

const activeTab = ref<'login' | 'register'>('login')
const email = ref('')
const password = ref('')
const confirmPassword = ref('')
const loading = ref(false)
const error = ref('')
const duplicateHint = ref(false)
const setupSuccess = ref(false)

const isSetup = computed(() => !!route.query.setup)
const isExpiredVerification = computed(() => route.query.tab === 'verify' && route.query.expired === 'true')

const isPasswordValid = computed(() => {
  return password.value.length >= 8 &&
    /[A-Z]/.test(password.value) &&
    /[a-z]/.test(password.value) &&
    /[0-9]/.test(password.value)
})

function getDashboardForRole(role: string | undefined): string {
  const dashboards: Record<string, string> = { admin: '/admin', editor: '/editor', contributor: '/contributor' }
  return dashboards[role ?? ''] || '/admin'
}

function switchToLogin() {
  activeTab.value = 'login'
  duplicateHint.value = false
  error.value = ''
}

async function handleLogin() {
  if (loading.value) return
  loading.value = true
  error.value = ''
  duplicateHint.value = false

  try {
    const data = await login(email.value, password.value)
    store.setToken(data.token)
    await store.fetchMe()
    router.push(getDashboardForRole(store.user?.role))
  } catch (e: unknown) {
    error.value = e instanceof Error ? e.message : 'Something went wrong'
  } finally {
    loading.value = false
  }
}

async function handleRegister() {
  if (loading.value) return
  loading.value = true
  error.value = ''
  duplicateHint.value = false

  try {
    const result = await register(email.value, password.value, confirmPassword.value)
    if ('duplicate' in result && result.duplicate) {
      duplicateHint.value = true
      loading.value = false
      return
    }
    // Registration auto-login stays on / — handled by guard redirect
  } catch (e: unknown) {
    error.value = e instanceof Error ? e.message : 'Registration failed'
  } finally {
    loading.value = false
  }
}

async function handleSetup() {
  if (loading.value) return
  loading.value = true
  error.value = ''

  const token = route.query.setup as string
  if (!token) {
    error.value = 'Missing setup token. Please request a new invite.'
    loading.value = false
    return
  }

  if (password.value.length < 8) {
    error.value = 'Password must be at least 8 characters'
    loading.value = false
    return
  }

  if (password.value !== confirmPassword.value) {
    error.value = 'Passwords do not match'
    loading.value = false
    return
  }

  try {
    await setupAccount(token, password.value)
    setupSuccess.value = true
    setTimeout(() => {
      router.push('/auth')
    }, 2000)
  } catch (e: unknown) {
    error.value = e instanceof Error ? e.message : 'Something went wrong'
  } finally {
    loading.value = false
  }
}

async function handleResendVerification() {
  if (loading.value) return
  loading.value = true
  error.value = ''

  try {
    await resendVerification()
    error.value = ''
  } catch (e: unknown) {
    error.value = e instanceof Error ? e.message : 'Failed to resend'
  } finally {
    loading.value = false
  }
}

function handleOAuthLogin(provider: string) {
  window.location.href = `/api/auth/oauth/${provider}`
}
</script>
