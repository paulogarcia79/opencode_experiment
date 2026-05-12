import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import AdminLoginView from '@/views/AdminLoginView.vue'
import { useAdminStore } from '@/stores/admin'

const mockPush = vi.fn()
const mockRoute = { query: {} }
vi.mock('vue-router', () => ({
  useRouter: () => ({ push: mockPush, replace: mockPush }),
  useRoute: () => mockRoute,
  RouterLink: { template: '<a><slot /></a>', props: ['to'] },
}))

vi.mock('@/composables/useAdminApi', () => ({
  login: vi.fn(),
}))

import { login } from '@/composables/useAdminApi'

const RouterLink = { template: '<a><slot /></a>', props: ['to'] }

describe('AdminLoginView', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    localStorage.clear()
    setActivePinia(createPinia())
  })

  it('renders login form with email and password fields', () => {
    const wrapper = mount(AdminLoginView, { global: { components: { RouterLink } } })
    
    expect(wrapper.find('input[type="email"]').exists()).toBe(true)
    expect(wrapper.find('input[type="password"]').exists()).toBe(true)
    expect(wrapper.text()).toContain('Admin Login')
  })

  it('shows error state on login failure', async () => {
    vi.mocked(login).mockRejectedValue(new Error('Incorrect email or password'))

    const wrapper = mount(AdminLoginView, { global: { components: { RouterLink } } })
    
    await wrapper.find('input[type="email"]').setValue('admin@example.com')
    await wrapper.find('input[type="password"]').setValue('wrong')
    await wrapper.find('form').trigger('submit.prevent')
    await flushPromises()

    expect(wrapper.text()).toContain('Login Failed')
    expect(wrapper.text()).toContain('Incorrect email or password')
  })

  it('shows loading state during submission', async () => {
    vi.mocked(login).mockImplementation(() => new Promise((resolve) => setTimeout(() => resolve({ token: 'test' }), 50)))

    const wrapper = mount(AdminLoginView, { global: { components: { RouterLink } } })
    
    await wrapper.find('input[type="email"]').setValue('admin@example.com')
    await wrapper.find('input[type="password"]').setValue('pass')
    wrapper.find('form').trigger('submit.prevent')
    await flushPromises()

    expect(wrapper.find('button[type="submit"]').text()).toContain('Signing in...')
  })

  it('stores token and redirects on successful login', async () => {
    vi.mocked(login).mockResolvedValue({ token: 'new-jwt-token' })
    const store = useAdminStore()

    const wrapper = mount(AdminLoginView, { global: { components: { RouterLink } } })
    
    await wrapper.find('input[type="email"]').setValue('admin@example.com')
    await wrapper.find('input[type="password"]').setValue('pass')
    await wrapper.find('form').trigger('submit.prevent')
    await flushPromises()

    expect(login).toHaveBeenCalledWith('admin@example.com', 'pass')
    expect(store.token).toBe('new-jwt-token')
    expect(mockPush).toHaveBeenCalledWith('/admin')
  })
})
