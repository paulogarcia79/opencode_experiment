import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import EditorDashboard from '@/components/EditorDashboard.vue'
import { useAdminStore } from '@/stores/admin'

vi.mock('vue-router', () => ({
  useRouter: () => ({ push: vi.fn() }),
  RouterLink: { template: '<a><slot /></a>', props: ['to'] },
  RouterView: { template: '<div><slot /></div>' },
}))

const RouterLink = { template: '<a><slot /></a>', props: ['to'] }

describe('EditorDashboard', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    localStorage.clear()
    setActivePinia(createPinia())
  })

  it('renders editor nav items: Articles, Review, Import, Settings', () => {
    const store = useAdminStore()
    store.setUser({ id: '1', email: 'editor@test.com', role: 'editor', is_active: true, is_verified: true, created_at: '' })

    const wrapper = mount(EditorDashboard, {
      global: { components: { RouterLink } },
    })

    const text = wrapper.text()
    expect(text).toContain('Articles')
    expect(text).toContain('Review')
    expect(text).toContain('Import')
    expect(text).toContain('Settings')
  })

  it('does not show admin-only nav items', () => {
    const store = useAdminStore()
    store.setUser({ id: '1', email: 'editor@test.com', role: 'editor', is_active: true, is_verified: true, created_at: '' })

    const wrapper = mount(EditorDashboard, {
      global: { components: { RouterLink } },
    })

    const text = wrapper.text()
    expect(text).not.toContain('Users')
    expect(text).not.toContain('Media')
    expect(text).not.toContain('Tags')
    expect(text).not.toContain('Analytics')
  })
})
