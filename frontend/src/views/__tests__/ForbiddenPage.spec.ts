import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import ForbiddenPage from '@/views/ForbiddenPage.vue'
import { useAdminStore } from '@/stores/admin'

vi.mock('vue-router', () => ({
  RouterLink: { template: '<a><slot /></a>', props: ['to'] },
}))

const RouterLink = { template: '<a><slot /></a>', props: ['to'] }

describe('ForbiddenPage', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    localStorage.clear()
    setActivePinia(createPinia())
  })

  it('shows 403 message', () => {
    const wrapper = mount(ForbiddenPage, {
      global: { components: { RouterLink } },
    })
    expect(wrapper.text()).toContain('403')
    expect(wrapper.text()).toContain("You don't have access")
  })

  it('shows link to admin dashboard for admin role', () => {
    const store = useAdminStore()
    store.setUser({ id: '1', email: 'admin@test.com', role: 'admin', is_active: true, is_verified: true, created_at: '' })

    const wrapper = mount(ForbiddenPage, {
      global: { components: { RouterLink } },
    })

    const link = wrapper.findComponent(RouterLink)
    expect(link.props('to')).toBe('/admin')
  })

  it('shows link to editor dashboard for editor role', () => {
    const store = useAdminStore()
    store.setUser({ id: '1', email: 'editor@test.com', role: 'editor', is_active: true, is_verified: true, created_at: '' })

    const wrapper = mount(ForbiddenPage, {
      global: { components: { RouterLink } },
    })

    const link = wrapper.findComponent(RouterLink)
    expect(link.props('to')).toBe('/editor')
  })

  it('shows link to contributor dashboard for contributor role', () => {
    const store = useAdminStore()
    store.setUser({ id: '1', email: 'contrib@test.com', role: 'contributor', is_active: true, is_verified: true, created_at: '' })

    const wrapper = mount(ForbiddenPage, {
      global: { components: { RouterLink } },
    })

    const link = wrapper.findComponent(RouterLink)
    expect(link.props('to')).toBe('/contributor')
  })
})
