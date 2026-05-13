import { describe, it, expect, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import { createRouter, createWebHistory } from 'vue-router'
import AuthView from '@/views/AuthView.vue'

function makeRouter(query = {}) {
  const router = createRouter({
    history: createWebHistory(),
    routes: [
      { path: '/', name: 'home', component: { template: '<div />' } },
      { path: '/auth', name: 'auth', component: AuthView, meta: { public: true } },
      { path: '/auth/forgot-password', name: 'auth-forgot-password', component: { template: '<div />' } },
      { path: '/admin', name: 'admin-articles', component: { template: '<div />' } },
    ],
  })
  // Navigate with query
  router.push({ path: '/auth', query })
  return router
}

describe('AuthView', () => {
  beforeEach(() => {
    localStorage.clear()
    setActivePinia(createPinia())
  })

  it('renders login tab by default', async () => {
    const router = makeRouter()
    await router.isReady()
    const wrapper = mount(AuthView, {
      global: { plugins: [router] },
    })

    expect(wrapper.text()).toContain('Login')
    expect(wrapper.find('input[type="email"]').exists()).toBe(true)
    expect(wrapper.find('input[type="password"]').exists()).toBe(true)
  })

  it('renders register tab when clicked', async () => {
    const router = makeRouter()
    await router.isReady()
    const wrapper = mount(AuthView, {
      global: { plugins: [router] },
    })

    const registerLink = wrapper.find('[data-test="register-tab"]')
    await registerLink.trigger('click')

    // Should now show registration form
    expect(wrapper.find('input[type="email"]').exists()).toBe(true)
    // Should have two password fields (password + confirm)
    const passwordFields = wrapper.findAll('input[type="password"]')
    expect(passwordFields.length).toBeGreaterThanOrEqual(2)
  })

  it('shows OAuth buttons on both tabs', async () => {
    const router = makeRouter()
    await router.isReady()
    const wrapper = mount(AuthView, {
      global: { plugins: [router] },
    })

    // Login tab has OAuth
    expect(wrapper.text()).toContain('Google')
    expect(wrapper.text()).toContain('GitHub')

    // Switch to register tab
    await wrapper.find('[data-test="register-tab"]').trigger('click')
    expect(wrapper.text()).toContain('Google')
    expect(wrapper.text()).toContain('GitHub')
  })

  it('renders setup mode when ?setup query param is present', async () => {
    const router = makeRouter({ setup: 'test-token-123' })
    await router.isReady()
    const wrapper = mount(AuthView, {
      global: { plugins: [router] },
    })

    expect(wrapper.text()).toContain('Set Up Your Account')
  })

  it('renders expired verification mode when ?tab=verify&expired=true', async () => {
    const router = makeRouter({ tab: 'verify', expired: 'true' })
    await router.isReady()
    const wrapper = mount(AuthView, {
      global: { plugins: [router] },
    })

    expect(wrapper.text()).toContain('expired')
  })

  it('shows "Forgot password?" link on login tab', async () => {
    const router = makeRouter()
    await router.isReady()
    const wrapper = mount(AuthView, {
      global: { plugins: [router] },
    })

    const forgotLink = wrapper.find('[data-test="forgot-password"]')
    expect(forgotLink.exists()).toBe(true)
  })
})
