import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import AdminDashboard from '@/components/AdminDashboard.vue'
import { useAdminStore } from '@/stores/admin'

vi.mock('vue-router', () => ({
  useRouter: () => ({ push: vi.fn() }),
  RouterLink: { template: '<a><slot /></a>', props: ['to'] },
  RouterView: { template: '<div><slot /></div>' },
}))

const RouterLink = { template: '<a><slot /></a>', props: ['to'] }

describe('AdminDashboard', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    localStorage.clear()
    setActivePinia(createPinia())
  })

  it('renders all admin nav items', () => {
    const store = useAdminStore()
    store.setUser({ id: '1', email: 'admin@test.com', role: 'admin', is_active: true, is_verified: true, created_at: '' })

    const wrapper = mount(AdminDashboard, {
      global: { components: { RouterLink } },
    })

    const text = wrapper.text()
    expect(text).toContain('Articles')
    expect(text).toContain('Review')
    expect(text).toContain('Import')
    expect(text).toContain('Media')
    expect(text).toContain('Tags')
    expect(text).toContain('Analytics')
    expect(text).toContain('Users')
  })
})
