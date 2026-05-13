import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import ContributorDashboard from '@/components/ContributorDashboard.vue'
import { useAdminStore } from '@/stores/admin'

vi.mock('vue-router', () => ({
  useRouter: () => ({ push: vi.fn() }),
  RouterLink: { template: '<a><slot /></a>', props: ['to'] },
  RouterView: { template: '<div><slot /></div>' },
}))

const RouterLink = { template: '<a><slot /></a>', props: ['to'] }

describe('ContributorDashboard', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    localStorage.clear()
    setActivePinia(createPinia())
  })

  it('renders contributor nav items: Articles, Import, Settings', () => {
    const store = useAdminStore()
    store.setUser({ id: '1', email: 'contrib@test.com', role: 'contributor', is_active: true, is_verified: true, created_at: '' })

    const wrapper = mount(ContributorDashboard, {
      global: { components: { RouterLink } },
    })

    const text = wrapper.text()
    expect(text).toContain('Articles')
    expect(text).toContain('Import')
    expect(text).toContain('Settings')
  })

  it('does not show admin/editor-only nav items', () => {
    const store = useAdminStore()
    store.setUser({ id: '1', email: 'contrib@test.com', role: 'contributor', is_active: true, is_verified: true, created_at: '' })

    const wrapper = mount(ContributorDashboard, {
      global: { components: { RouterLink } },
    })

    const text = wrapper.text()
    expect(text).not.toContain('Users')
    expect(text).not.toContain('Media')
    expect(text).not.toContain('Tags')
    expect(text).not.toContain('Analytics')
    expect(text).not.toContain('Review')
  })
})
