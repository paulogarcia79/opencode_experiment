import { describe, it, expect, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import { createRouter, createWebHistory } from 'vue-router'
import { useAdminStore } from '@/stores/admin'
import DashboardLayout from '@/components/DashboardLayout.vue'

describe('DashboardLayout verification prompt', () => {
  beforeEach(() => {
    localStorage.clear()
    setActivePinia(createPinia())
  })

  it('shows verification prompt when unverified', async () => {
    const router = createRouter({
      history: createWebHistory(),
      routes: [
        { path: '/', name: 'home', component: { template: '<div />' } },
        { path: '/contributor', component: DashboardLayout, meta: { requiresAuth: true, allowedRoles: ['admin', 'editor', 'contributor'] }, children: [{ path: '', name: 'contributor-articles', component: { template: '<div>Content</div>' } }] },
        { path: '/contributor/settings', name: 'contributor-settings', component: { template: '<div />' } },
      ],
    })
    router.push('/')
    await router.isReady()

    const store = useAdminStore()
    store.setToken('token')
    store.setUser({ id: '1', email: 'u@t.com', role: 'contributor', is_active: true, is_verified: false, created_at: '' })

    // Navigate to dashboard
    router.push('/contributor')
    await router.isReady()

    const wrapper = mount(DashboardLayout, {
      props: { homeRoute: '/contributor' },
      global: {
        plugins: [router],
        stubs: { RouterView: true, RouterLink: true },
      },
    })

    expect(wrapper.text()).toContain('Verify your email')
  })

  it('hides verification prompt when verified', async () => {
    const router = createRouter({
      history: createWebHistory(),
      routes: [
        { path: '/', name: 'home', component: { template: '<div />' } },
        { path: '/contributor', component: DashboardLayout, meta: { requiresAuth: true, allowedRoles: ['admin', 'editor', 'contributor'] }, children: [{ path: '', name: 'contributor-articles', component: { template: '<div>Content</div>' } }] },
        { path: '/contributor/settings', name: 'contributor-settings', component: { template: '<div />' } },
      ],
    })
    router.push('/')
    await router.isReady()

    const store = useAdminStore()
    store.setToken('token')
    store.setUser({ id: '1', email: 'u@t.com', role: 'contributor', is_active: true, is_verified: true, created_at: '' })

    router.push('/contributor')
    await router.isReady()

    const wrapper = mount(DashboardLayout, {
      props: { homeRoute: '/contributor' },
      global: {
        plugins: [router],
        stubs: { RouterView: true, RouterLink: true },
      },
    })

    expect(wrapper.text()).not.toContain('Verify your email')
  })
})
