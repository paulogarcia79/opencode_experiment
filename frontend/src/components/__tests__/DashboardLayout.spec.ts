import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import DashboardLayout from '@/components/DashboardLayout.vue'

vi.mock('vue-router', () => ({
  useRouter: () => ({ push: vi.fn() }),
  RouterLink: { template: '<a><slot /></a>', props: ['to'] },
  RouterView: { template: '<div class="router-view"><slot /></div>' },
}))

const RouterLink = { template: '<a><slot /></a>', props: ['to'] }

describe('DashboardLayout', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    localStorage.clear()
    setActivePinia(createPinia())
  })

  it('renders nav items via slot', () => {
    const wrapper = mount(DashboardLayout, {
      global: { components: { RouterLink } },
      slots: { 'nav-items': '<a href="/admin/articles">Articles</a>' },
    })
    expect(wrapper.text()).toContain('Articles')
  })

  it('renders content via default slot (RouterView)', () => {
    const wrapper = mount(DashboardLayout, {
      global: { components: { RouterLink } },
    })
    expect(wrapper.html()).toContain('routerview')
  })

  it('renders View Site link', () => {
    const wrapper = mount(DashboardLayout, {
      global: { components: { RouterLink } },
    })
    expect(wrapper.text()).toContain('View Site')
  })
})
