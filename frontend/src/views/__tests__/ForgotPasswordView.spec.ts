import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import ForgotPasswordView from '@/views/ForgotPasswordView.vue'

const mockPush = vi.fn()
vi.mock('vue-router', () => ({
  useRouter: () => ({ push: mockPush }),
  RouterLink: { template: '<a><slot /></a>', props: ['to'] },
}))

vi.mock('@/composables/useAdminApi', () => ({
  forgotPassword: vi.fn(),
}))

import { forgotPassword } from '@/composables/useAdminApi'

const RouterLink = { template: '<a><slot /></a>', props: ['to'] }

describe('ForgotPasswordView', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    setActivePinia(createPinia())
  })

  it('renders email input and submit button', () => {
    const wrapper = mount(ForgotPasswordView, { global: { components: { RouterLink } } })
    
    expect(wrapper.find('input[type="email"]').exists()).toBe(true)
    expect(wrapper.find('button[type="submit"]').exists()).toBe(true)
    expect(wrapper.text()).toContain('Forgot Password')
  })

  it('calls forgotPassword API on form submission', async () => {
    vi.mocked(forgotPassword).mockResolvedValue(undefined)

    const wrapper = mount(ForgotPasswordView, { global: { components: { RouterLink } } })
    
    await wrapper.find('input[type="email"]').setValue('admin@example.com')
    await wrapper.find('form').trigger('submit.prevent')
    await flushPromises()

    expect(forgotPassword).toHaveBeenCalledWith('admin@example.com')
  })

  it('shows success message after submission', async () => {
    vi.mocked(forgotPassword).mockResolvedValue(undefined)

    const wrapper = mount(ForgotPasswordView, { global: { components: { RouterLink } } })
    
    await wrapper.find('input[type="email"]').setValue('admin@example.com')
    await wrapper.find('form').trigger('submit.prevent')
    await flushPromises()

    expect(wrapper.text()).toContain('Check your email')
  })

  it('shows error state on API failure', async () => {
    vi.mocked(forgotPassword).mockRejectedValue(new Error('Network error'))

    const wrapper = mount(ForgotPasswordView, { global: { components: { RouterLink } } })
    
    await wrapper.find('input[type="email"]').setValue('admin@example.com')
    await wrapper.find('form').trigger('submit.prevent')
    await flushPromises()

    expect(wrapper.text()).toContain('Request Failed')
    expect(wrapper.text()).toContain('Network error')
  })

  it('shows loading state during submission', async () => {
    vi.mocked(forgotPassword).mockImplementation(() => new Promise((resolve) => setTimeout(resolve, 50)))

    const wrapper = mount(ForgotPasswordView, { global: { components: { RouterLink } } })
    
    await wrapper.find('input[type="email"]').setValue('admin@example.com')
    wrapper.find('form').trigger('submit.prevent')
    await flushPromises()

    expect(wrapper.find('button[type="submit"]').text()).toContain('Sending...')
  })
})
