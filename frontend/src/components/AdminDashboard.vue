<template>
  <DashboardLayout home-route="/admin">
    <template #nav-items>
      <RouterLink
        to="/admin"
        exact-active-class="text-primary-400"
        class="text-sm text-slate-500 hover:text-white transition-colors duration-200 cursor-pointer px-3 py-1.5 rounded-lg hover:bg-white/5"
      >
        Articles
      </RouterLink>
      <RouterLink
        to="/admin/review"
        exact-active-class="text-primary-400"
        class="text-sm text-slate-500 hover:text-white transition-colors duration-200 cursor-pointer px-3 py-1.5 rounded-lg hover:bg-white/5 flex items-center gap-1.5"
      >
        Review
        <span
          v-if="pendingCount > 0"
          class="inline-flex items-center justify-center w-5 h-5 rounded-full bg-accent-500 text-white text-xs font-medium"
        >
          {{ pendingCount }}
        </span>
      </RouterLink>
      <RouterLink
        to="/admin/import"
        exact-active-class="text-primary-400"
        class="text-sm text-slate-500 hover:text-white transition-colors duration-200 cursor-pointer px-3 py-1.5 rounded-lg hover:bg-white/5"
      >
        Import
      </RouterLink>
      <RouterLink
        to="/admin/media"
        exact-active-class="text-primary-400"
        class="text-sm text-slate-500 hover:text-white transition-colors duration-200 cursor-pointer px-3 py-1.5 rounded-lg hover:bg-white/5"
      >
        Media
      </RouterLink>
      <RouterLink
        to="/admin/tags"
        exact-active-class="text-primary-400"
        class="text-sm text-slate-500 hover:text-white transition-colors duration-200 cursor-pointer px-3 py-1.5 rounded-lg hover:bg-white/5"
      >
        Tags
      </RouterLink>
      <RouterLink
        to="/admin/analytics"
        exact-active-class="text-primary-400"
        class="text-sm text-slate-500 hover:text-white transition-colors duration-200 cursor-pointer px-3 py-1.5 rounded-lg hover:bg-white/5"
      >
        Analytics
      </RouterLink>
      <RouterLink
        to="/admin/settings"
        exact-active-class="text-primary-400"
        class="text-sm text-slate-500 hover:text-white transition-colors duration-200 cursor-pointer px-3 py-1.5 rounded-lg hover:bg-white/5"
      >
        Settings
      </RouterLink>
      <RouterLink
        to="/admin/users"
        exact-active-class="text-primary-400"
        class="text-sm text-slate-500 hover:text-white transition-colors duration-200 cursor-pointer px-3 py-1.5 rounded-lg hover:bg-white/5"
      >
        Users
      </RouterLink>
    </template>
  </DashboardLayout>
</template>

<script setup lang="ts">
import { ref, onMounted, provide } from 'vue'
import DashboardLayout from '@/components/DashboardLayout.vue'
import { useAdminStore } from '@/stores/admin'

const store = useAdminStore()
const pendingCount = ref(0)

async function fetchPendingCount() {
  try {
    const API_BASE = import.meta.env.VITE_API_BASE_URL || ''
    const res = await fetch(`${API_BASE}/api/admin/articles/review/count`, {
      headers: { Authorization: `Bearer ${store.token}` },
    })
    if (res.ok) {
      const data = await res.json()
      pendingCount.value = data.pending_count ?? 0
    }
  } catch {
    console.error('Failed to fetch review count')
  }
}

onMounted(() => {
  if (store.user?.role === 'admin' || store.user?.role === 'editor') {
    fetchPendingCount()
  }
})

provide('refreshReviewCount', fetchPendingCount)
</script>
