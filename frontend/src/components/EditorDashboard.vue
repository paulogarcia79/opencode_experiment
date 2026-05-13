<template>
  <DashboardLayout home-route="/editor">
    <template #nav-items>
      <RouterLink
        to="/editor"
        exact-active-class="text-primary-400"
        class="text-sm text-slate-500 hover:text-white transition-colors duration-200 cursor-pointer px-3 py-1.5 rounded-lg hover:bg-white/5"
      >
        Articles
      </RouterLink>
      <RouterLink
        to="/editor/review"
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
        to="/editor/import"
        exact-active-class="text-primary-400"
        class="text-sm text-slate-500 hover:text-white transition-colors duration-200 cursor-pointer px-3 py-1.5 rounded-lg hover:bg-white/5"
      >
        Import
      </RouterLink>
      <RouterLink
        to="/editor/settings"
        exact-active-class="text-primary-400"
        class="text-sm text-slate-500 hover:text-white transition-colors duration-200 cursor-pointer px-3 py-1.5 rounded-lg hover:bg-white/5"
      >
        Settings
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
  fetchPendingCount()
})

provide('refreshReviewCount', fetchPendingCount)
</script>
