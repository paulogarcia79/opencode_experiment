import { describe, it, expect, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import { createRouter, createWebHistory } from 'vue-router'
import SiteHeader from '@/components/SiteHeader.vue'
import { useAdminStore } from '@/stores/admin'

const routes = [
  { path: '/', name: 'home', component: { template: '<div />' } },
  { path: '/auth', name: 'auth', component: { template: '<div />' } },
  { path: '/search', name: 'search', component: { template: '<div />' } },
  { path: '/admin', name: 'admin-articles', component: { template: '<div />' } },
  { path: '/admin/settings', name: 'admin-settings', component: { template: '<div />' } },
  { path: '/editor', name: 'editor-articles', component: { template: '<div />' } },
  { path: '/editor/settings', name: 'editor-settings', component: { template: '<div />' } },
  { path: '/contributor', name: 'contributor-articles', component: { template: '<div />' } },
  { path: '/contributor/settings', name: 'contributor-settings', component: { template: '<div />' } },
]

describe('SiteHeader', () => {
  beforeEach(() => {
    localStorage.clear()
    setActivePinia(createPinia())
  })

  it('shows "Log in / Sign up" button when logged out', async () => {
    const router = createRouter({ history: createWebHistory(), routes })
    router.push('/')
    await router.isReady()

    const wrapper = mount(SiteHeader, { global: { plugins: [router] } })

    expect(wrapper.text()).toContain('Log in')
  })

  it('shows user pill with email when logged in', async () => {
    const router = createRouter({ history: createWebHistory(), routes })
    router.push('/')
    await router.isReady()

    const store = useAdminStore()
    store.setToken('fake-token')
    store.setUser({ id: '1', email: 'user@test.com', role: 'contributor', is_active: true, is_verified: true, created_at: '' })

    const wrapper = mount(SiteHeader, { global: { plugins: [router] } })

    expect(wrapper.text()).toContain('user@test.com')
  })

  it('dropdown shows Dashboard, Settings, and Log out', async () => {
    const router = createRouter({ history: createWebHistory(), routes })
    router.push('/')
    await router.isReady()

    const store = useAdminStore()
    store.setToken('fake-token')
    store.setUser({ id: '1', email: 'editor@test.com', role: 'editor', is_active: true, is_verified: true, created_at: '' })

    const wrapper = mount(SiteHeader, { global: { plugins: [router] } })

    await wrapper.find('[data-test="user-pill"]').trigger('click')

    expect(wrapper.text()).toContain('Dashboard')
    expect(wrapper.text()).toContain('Settings')
    expect(wrapper.text()).toContain('Log out')
  })

  it('Dashboard link resolves to role-specific path', async () => {
    const router = createRouter({ history: createWebHistory(), routes })
    router.push('/')
    await router.isReady()

    const store = useAdminStore()
    store.setToken('fake-token')
    store.setUser({ id: '1', email: 'contrib@test.com', role: 'contributor', is_active: true, is_verified: true, created_at: '' })

    const wrapper = mount(SiteHeader, { global: { plugins: [router] } })

    await wrapper.find('[data-test="user-pill"]').trigger('click')

    const dashboardLink = wrapper.find('[data-test="dash-link"]')
    expect(dashboardLink.attributes('href')).toBe('/contributor')
  })

  it('logout clears store and redirects to /', async () => {
    const router = createRouter({ history: createWebHistory(), routes })
    router.push('/')
    await router.isReady()

    const store = useAdminStore()
    store.setToken('fake-token')
    store.setUser({ id: '1', email: 'user@test.com', role: 'contributor', is_active: true, is_verified: true, created_at: '' })

    const wrapper = mount(SiteHeader, { global: { plugins: [router] } })

    await wrapper.find('[data-test="user-pill"]').trigger('click')
    await wrapper.find('[data-test="logout-button"]').trigger('click')

    expect(store.token).toBe('')
    expect(router.currentRoute.value.path).toBe('/')
  })

  it('mobile hamburger renders', async () => {
    const router = createRouter({ history: createWebHistory(), routes })
    router.push('/')
    await router.isReady()

    const wrapper = mount(SiteHeader, { global: { plugins: [router] } })

    const hamburger = wrapper.find('[data-test="hamburger"]')
    expect(hamburger.exists()).toBe(true)
  })
})
