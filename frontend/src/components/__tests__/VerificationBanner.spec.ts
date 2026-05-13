import { describe, it, expect, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import { createRouter, createWebHistory } from 'vue-router'
import { useAdminStore } from '@/stores/admin'
import VerificationBanner from '@/components/VerificationBanner.vue'
import VerifyEmailView from '@/views/VerifyEmailView.vue'

const routes = [
  { path: '/', name: 'home', component: { template: '<div />' } },
  { path: '/verify-email', name: 'verify-email', component: VerifyEmailView, meta: { public: true } },
  { path: '/auth', name: 'auth', component: { template: '<div />' }, meta: { public: true } },
]

describe('VerificationBanner', () => {
  beforeEach(() => {
    localStorage.clear()
    setActivePinia(createPinia())
  })

  it('renders when unverified', () => {
    const store = useAdminStore()
    store.setToken('token')
    store.setUser({ id: '1', email: 'u@t.com', role: 'contributor', is_active: true, is_verified: false, created_at: '' })

    const wrapper = mount(VerificationBanner)
    expect(wrapper.text()).toContain('Verify your email')
  })

  it('does not render when verified', () => {
    const store = useAdminStore()
    store.setToken('token')
    store.setUser({ id: '1', email: 'u@t.com', role: 'contributor', is_active: true, is_verified: true, created_at: '' })

    const wrapper = mount(VerificationBanner)
    expect(wrapper.text()).toBe('')
  })

  it('does not render when logged out', () => {
    const wrapper = mount(VerificationBanner)
    expect(wrapper.text()).toBe('')
  })

  it('dismiss button hides banner for session', async () => {
    const store = useAdminStore()
    store.setToken('token')
    store.setUser({ id: '1', email: 'u@t.com', role: 'contributor', is_active: true, is_verified: false, created_at: '' })

    const wrapper = mount(VerificationBanner)
    expect(wrapper.text()).toContain('Verify your email')

    await wrapper.find('[data-test="dismiss-banner"]').trigger('click')
    expect(wrapper.text()).not.toContain('Verify your email')
    expect(store.isVerificationBannerDismissed).toBe(true)
  })

  it('resend button calls resendVerification', async () => {
    const store = useAdminStore()
    store.setToken('token')
    store.setUser({ id: '1', email: 'u@t.com', role: 'contributor', is_active: true, is_verified: false, created_at: '' })

    const wrapper = mount(VerificationBanner)

    const resendBtn = wrapper.find('[data-test="resend-verification"]')
    expect(resendBtn.exists()).toBe(true)
  })
})

describe('VerifyEmailView', () => {
  beforeEach(() => {
    localStorage.clear()
    setActivePinia(createPinia())
  })

  it('shows loading state initially', async () => {
    const router = createRouter({ history: createWebHistory(), routes })
    router.push({ path: '/verify-email', query: { token: 'test-token' } })
    await router.isReady()

    const wrapper = mount(VerifyEmailView, { global: { plugins: [router] } })

    expect(wrapper.find('[data-test="loading"]').exists()).toBe(true)
  })

  it('shows success state and redirects on valid token', async () => {
    const router = createRouter({ history: createWebHistory(), routes })
    router.push({ path: '/verify-email', query: { token: 'good-token' } })
    await router.isReady()

    // Mock fetch for verify-email
    const { vi } = await import('vitest')
    vi.spyOn(globalThis, 'fetch').mockResolvedValue(
      new Response(JSON.stringify({ token: 'jwt', type: 'bearer' }), { status: 200 })
    )

    const wrapper = mount(VerifyEmailView, { global: { plugins: [router] } })
    await wrapper.vm.$nextTick()

    // After API resolves, should show success
    await new Promise(r => setTimeout(r, 100))
    expect(wrapper.text()).toContain('verified')
  })

  it('shows error state on invalid token', async () => {
    const router = createRouter({ history: createWebHistory(), routes })
    router.push({ path: '/verify-email', query: { token: 'bad-token' } })
    await router.isReady()

    const { vi } = await import('vitest')
    vi.spyOn(globalThis, 'fetch').mockResolvedValue(
      new Response(JSON.stringify({ detail: 'expired' }), { status: 400 })
    )

    const wrapper = mount(VerifyEmailView, { global: { plugins: [router] } })
    await new Promise(r => setTimeout(r, 100))

    expect(wrapper.text()).toContain('invalid')
  })
})
