<template>
  <header class="border-b border-white/5 bg-surface-950/80 backdrop-blur-md sticky top-0 z-[60]">
    <div class="max-w-4xl mx-auto px-6 py-4">
      <div class="flex items-center justify-between">
        <!-- Logo -->
        <RouterLink to="/" class="group flex items-center gap-3 cursor-pointer">
          <div class="w-8 h-8 rounded-lg bg-primary-600 flex items-center justify-center shadow-lg shadow-primary-600/20">
            <svg class="w-4 h-4 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
              <path stroke-linecap="round" stroke-linejoin="round" d="M13 10V3L4 14h7v7l9-11h-7z" />
            </svg>
          </div>
          <div>
            <h1 class="text-lg font-display font-semibold text-white tracking-tight group-hover:text-primary-400 transition-colors duration-200">
              Tech & Games Blog
            </h1>
          </div>
        </RouterLink>

        <!-- Desktop right section: search + auth -->
        <div class="hidden sm:flex items-center gap-3">
          <form @submit.prevent="handleSearch" class="flex items-center">
            <div class="relative">
              <svg class="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                <path stroke-linecap="round" stroke-linejoin="round" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
              <input
                v-model="searchQuery"
                type="search"
                placeholder="Search..."
                class="w-48 lg:w-64 bg-white/5 border border-white/10 rounded-lg pl-9 pr-3 py-1.5 text-sm text-white placeholder-slate-500 focus:outline-none focus:border-primary-500 focus:ring-1 focus:ring-primary-500"
              />
            </div>
          </form>

          <!-- Auth: logged out -->
          <RouterLink
            v-if="!store.token"
            to="/auth"
            class="px-4 py-1.5 bg-primary-600 hover:bg-primary-500 text-white text-sm font-medium rounded-lg transition-all duration-200 shadow-lg shadow-primary-600/20 hover:shadow-primary-500/30 cursor-pointer"
          >
            Log in / Sign up
          </RouterLink>

          <!-- Auth: logged in -->
          <div v-else class="relative">
            <button
              data-test="user-pill"
              @click="dropdownOpen = !dropdownOpen"
              class="flex items-center gap-2 px-3 py-1.5 bg-white/5 hover:bg-white/10 border border-white/10 rounded-lg text-sm text-slate-300 transition-all duration-200 cursor-pointer"
            >
              <span class="max-w-[120px] truncate">{{ store.user?.email }}</span>
              <svg class="w-3 h-3 text-slate-500" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                <path stroke-linecap="round" stroke-linejoin="round" d="M19 9l-7 7-7-7" />
              </svg>
            </button>
            <div
              v-if="dropdownOpen"
              class="absolute right-0 mt-2 w-48 rounded-lg border border-white/10 bg-surface-900 shadow-xl shadow-black/40 py-1 z-50"
            >
              <RouterLink
                data-test="dash-link"
                :to="dashboardPath"
                class="block px-4 py-2 text-sm text-slate-300 hover:text-white hover:bg-white/5 transition-colors duration-150 cursor-pointer"
                @click="dropdownOpen = false"
              >
                Dashboard
              </RouterLink>
              <RouterLink
                :to="settingsPath"
                class="block px-4 py-2 text-sm text-slate-300 hover:text-white hover:bg-white/5 transition-colors duration-150 cursor-pointer"
                @click="dropdownOpen = false"
              >
                Settings
              </RouterLink>
              <hr class="border-white/5 my-1" />
              <button
                data-test="logout-button"
                @click="handleLogout"
                class="w-full text-left px-4 py-2 text-sm text-slate-400 hover:text-white hover:bg-white/5 transition-colors duration-150 cursor-pointer"
              >
                Log out
              </button>
            </div>
          </div>
        </div>

        <!-- Mobile hamburger -->
        <button
          data-test="hamburger"
          class="sm:hidden p-2 text-slate-400 hover:text-white transition-colors cursor-pointer"
          @click="drawerOpen = !drawerOpen"
        >
          <svg v-if="!drawerOpen" class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
            <path stroke-linecap="round" stroke-linejoin="round" d="M4 6h16M4 12h16M4 18h16" />
          </svg>
          <svg v-else class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
            <path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>

      <!-- Mobile drawer -->
      <div v-if="drawerOpen" data-test="mobile-drawer" class="sm:hidden mt-4 pt-4 border-t border-white/5">
        <form @submit.prevent="handleSearch" class="mb-4">
          <div class="relative">
            <svg class="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
              <path stroke-linecap="round" stroke-linejoin="round" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
            <input
              v-model="searchQuery"
              type="search"
              placeholder="Search..."
              class="w-full bg-white/5 border border-white/10 rounded-lg pl-9 pr-3 py-2 text-sm text-white placeholder-slate-500 focus:outline-none focus:border-primary-500"
            />
          </div>
        </form>

        <div v-if="!store.token">
          <RouterLink
            to="/auth"
            @click="drawerOpen = false"
            class="flex items-center gap-2 px-3 py-2 text-slate-300 hover:text-white rounded-lg hover:bg-white/5 transition-colors cursor-pointer"
          >
            <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
              <path stroke-linecap="round" stroke-linejoin="round" d="M11 16l-4-4m0 0l4-4m-4 4h14m-5 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h7a3 3 0 013 3v1" />
            </svg>
            Log in / Sign up
          </RouterLink>
        </div>

        <div v-else class="space-y-1">
          <span class="block px-3 py-1 text-xs text-slate-500 uppercase tracking-wider">{{ store.user?.email }}</span>
          <RouterLink
            :to="dashboardPath"
            @click="drawerOpen = false"
            class="flex items-center gap-2 px-3 py-2 text-slate-300 hover:text-white rounded-lg hover:bg-white/5 transition-colors cursor-pointer"
          >
            Dashboard
          </RouterLink>
          <RouterLink
            :to="settingsPath"
            @click="drawerOpen = false"
            class="flex items-center gap-2 px-3 py-2 text-slate-300 hover:text-white rounded-lg hover:bg-white/5 transition-colors cursor-pointer"
          >
            Settings
          </RouterLink>
          <button
            @click="handleLogout"
            class="flex items-center gap-2 px-3 py-2 text-slate-400 hover:text-white rounded-lg hover:bg-white/5 transition-colors cursor-pointer"
          >
            Log out
          </button>
        </div>
      </div>
    </div>
  </header>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAdminStore } from '@/stores/admin'

const store = useAdminStore()
const router = useRouter()
const searchQuery = ref('')
const dropdownOpen = ref(false)
const drawerOpen = ref(false)

const rolePrefix = computed(() => {
  const role = store.user?.role
  if (role === 'admin') return '/admin'
  if (role === 'editor') return '/editor'
  return '/contributor'
})

const dashboardPath = computed(() => rolePrefix.value)
const settingsPath = computed(() => `${rolePrefix.value}/settings`)

function handleSearch() {
  const q = searchQuery.value.trim()
  if (q) {
    drawerOpen.value = false
    router.push({ path: '/search', query: { q } })
  }
}

function handleLogout() {
  store.clearToken()
  dropdownOpen.value = false
  drawerOpen.value = false
  router.push('/')
}
</script>
