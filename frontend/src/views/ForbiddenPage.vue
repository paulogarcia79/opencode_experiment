<template>
  <div class="min-h-screen bg-surface-950 flex items-center justify-center">
    <div class="text-center">
      <h1 class="text-6xl font-display font-bold text-white mb-4">403</h1>
      <p class="text-xl text-slate-400 mb-8">You don't have access</p>
      <RouterLink
        :to="dashboardLink"
        class="inline-flex items-center gap-2 px-4 py-2.5 bg-primary-600 hover:bg-primary-500 text-white text-sm font-medium rounded-lg transition-all duration-200"
      >
        Back to Dashboard
      </RouterLink>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useAdminStore } from '@/stores/admin'

const store = useAdminStore()

const roleToDashboard: Record<string, string> = {
  admin: '/admin',
  editor: '/editor',
  contributor: '/contributor',
}

const dashboardLink = computed(() => {
  return roleToDashboard[store.user?.role ?? ''] || '/'
})
</script>
