import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import DashboardLayout from '@/components/DashboardLayout.vue'
import { useAdminStore } from '@/stores/admin'

const mockPush = vi.fn()
vi.mock('vue-router', () => ({
  useRouter: () => ({ push: mockPush }),
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

  it('has logout button that clears token and redirects to login', async () => {
    const store = useAdminStore()
    store.setToken('test-token')

    const wrapper = mount(DashboardLayout, {
      global: { components: { RouterLink } },
    })

    expect(wrapper.find('button').exists()).toBe(true)
    await wrapper.find('button').trigger('click')
    expect(store.token).toBe('')
    expect(mockPush).toHaveBeenCalledWith('/admin/login')
  })

  it('renders View Site link', () => {
    const wrapper = mount(DashboardLayout, {
      global: { components: { RouterLink } },
    })
    expect(wrapper.text()).toContain('View Site')
  })
})
