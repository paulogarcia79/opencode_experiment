<template>
  <DashboardLayout home-route="/contributor">
    <template #nav-items>
      <RouterLink
        to="/contributor"
        exact-active-class="text-primary-400"
        class="text-sm text-slate-500 hover:text-white transition-colors duration-200 cursor-pointer px-3 py-1.5 rounded-lg hover:bg-white/5"
      >
        Articles
      </RouterLink>
      <RouterLink
        to="/contributor/import"
        exact-active-class="text-primary-400"
        class="text-sm text-slate-500 hover:text-white transition-colors duration-200 cursor-pointer px-3 py-1.5 rounded-lg hover:bg-white/5"
      >
        Import
      </RouterLink>
      <RouterLink
        to="/contributor/settings"
        exact-active-class="text-primary-400"
        class="text-sm text-slate-500 hover:text-white transition-colors duration-200 cursor-pointer px-3 py-1.5 rounded-lg hover:bg-white/5"
      >
        Settings
      </RouterLink>
    </template>
  </DashboardLayout>
</template>

<script setup lang="ts">
import DashboardLayout from '@/components/DashboardLayout.vue'
</script>
