import { describe, it, expect, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import { createRouter, createWebHistory } from 'vue-router'
import App from '@/App.vue'

const routes = [
  { path: '/', name: 'home', component: { template: '<div>Home Page</div>' } },
  { path: '/auth', name: 'auth', component: { template: '<div />' }, meta: { public: true } },
  { path: '/admin', name: 'admin-articles', component: { template: '<div />' } },
]

describe('App.vue integration', () => {
  beforeEach(() => {
    localStorage.clear()
    setActivePinia(createPinia())
  })

  it('renders SiteHeader globally', async () => {
    const router = createRouter({ history: createWebHistory(), routes })
    router.push('/')
    await router.isReady()

    const wrapper = mount(App, {
      global: { plugins: [router], stubs: { ToastContainer: true } },
    })

    expect(wrapper.findComponent({ name: 'SiteHeader' }).exists()).toBe(true)
  })

  it('renders VerificationBanner', async () => {
    const router = createRouter({ history: createWebHistory(), routes })
    router.push('/')
    await router.isReady()

    const wrapper = mount(App, {
      global: { plugins: [router], stubs: { ToastContainer: true } },
    })

    expect(wrapper.findComponent({ name: 'VerificationBanner' }).exists()).toBe(true)
  })

  it('renders RouterView content', async () => {
    const router = createRouter({ history: createWebHistory(), routes })
    router.push('/')
    await router.isReady()

    const wrapper = mount(App, {
      global: { plugins: [router], stubs: { ToastContainer: true } },
    })

    expect(wrapper.text()).toContain('Home Page')
  })
})
