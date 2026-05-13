<template>
  <SiteHeader />
  <VerificationBanner />
  <router-view />
  <ToastContainer />
</template>

<script setup lang="ts">
import { watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAdminStore } from '@/stores/admin'
import { exchangeOAuthCode } from '@/composables/useAdminApi'
import SiteHeader from '@/components/SiteHeader.vue'
import VerificationBanner from '@/components/VerificationBanner.vue'
import ToastContainer from '@/components/ToastContainer.vue'

const router = useRouter()
const route = useRoute()
const store = useAdminStore()

function getDashboardForRole(role: string | undefined): string {
  const dashboards: Record<string, string> = { admin: '/admin', editor: '/editor', contributor: '/contributor' }
  return dashboards[role ?? ''] || '/admin'
}

watch(() => route.query.oauth_code, async (code) => {
  if (!code || store.token) return
  try {
    const data = await exchangeOAuthCode(code as string)
    store.setToken(data.token)
    await store.fetchMe()
    router.replace(getDashboardForRole(store.user?.role))
  } catch (e) {
    console.error('OAuth login failed:', e)
    router.replace('/auth')
  }
}, { immediate: true })
</script>

<style>
/* Global dark theme styles */
html {
  scroll-behavior: smooth;
}

::selection {
  background-color: rgba(124, 58, 237, 0.4);
  color: #fff;
}

/* Custom scrollbar */
::-webkit-scrollbar {
  width: 8px;
}
::-webkit-scrollbar-track {
  background: #0f0f23;
}
::-webkit-scrollbar-thumb {
  background: #3f3f5f;
  border-radius: 4px;
}
::-webkit-scrollbar-thumb:hover {
  background: #5b5b7a;
}

/* Focus visible styles */
*:focus-visible {
  outline: 2px solid #7c3aed;
  outline-offset: 2px;
}
</style>
