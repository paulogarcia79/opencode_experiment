import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import ResetPasswordView from '@/views/ResetPasswordView.vue'

const mockPush = vi.fn()
const mockRouteQuery = vi.fn(() => ({ token: 'test-reset-token' }))
vi.mock('vue-router', () => ({
  useRouter: () => ({ push: mockPush }),
  useRoute: () => ({ query: mockRouteQuery() }),
}))

vi.mock('@/composables/useAdminApi', () => ({
  resetPassword: vi.fn(),
}))

import { resetPassword } from '@/composables/useAdminApi'

describe('ResetPasswordView', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    setActivePinia(createPinia())
  })

  it('renders password and confirm password inputs', () => {
    const wrapper = mount(ResetPasswordView)
    
    expect(wrapper.findAll('input[type="password"]').length).toBe(2)
    expect(wrapper.find('button[type="submit"]').exists()).toBe(true)
    expect(wrapper.text()).toContain('Reset Password')
  })

  it('calls resetPassword API with token and new password on submission', async () => {
    vi.mocked(resetPassword).mockResolvedValue(undefined)

    const wrapper = mount(ResetPasswordView)
    
    await wrapper.findAll('input[type="password"]')[0].setValue('NewPass123!')
    await wrapper.findAll('input[type="password"]')[1].setValue('NewPass123!')
    await wrapper.find('form').trigger('submit.prevent')
    await flushPromises()

    expect(resetPassword).toHaveBeenCalledWith('test-reset-token', 'NewPass123!')
  })

  it('shows error when passwords do not match', async () => {
    const wrapper = mount(ResetPasswordView)
    
    await wrapper.findAll('input[type="password"]')[0].setValue('NewPass123!')
    await wrapper.findAll('input[type="password"]')[1].setValue('DifferentPass!')
    await wrapper.find('form').trigger('submit.prevent')
    await flushPromises()

    expect(wrapper.text()).toContain('Passwords do not match')
    expect(resetPassword).not.toHaveBeenCalled()
  })

  it('shows error state on API failure', async () => {
    vi.mocked(resetPassword).mockRejectedValue(new Error('Invalid or expired token'))

    const wrapper = mount(ResetPasswordView)
    
    await wrapper.findAll('input[type="password"]')[0].setValue('NewPass123!')
    await wrapper.findAll('input[type="password"]')[1].setValue('NewPass123!')
    await wrapper.find('form').trigger('submit.prevent')
    await flushPromises()

    expect(wrapper.text()).toContain('Reset Failed')
    expect(wrapper.text()).toContain('Invalid or expired token')
  })

  it('shows loading state during submission', async () => {
    vi.mocked(resetPassword).mockImplementation(() => new Promise((resolve) => setTimeout(resolve, 50)))

    const wrapper = mount(ResetPasswordView)
    
    await wrapper.findAll('input[type="password"]')[0].setValue('NewPass123!')
    await wrapper.findAll('input[type="password"]')[1].setValue('NewPass123!')
    wrapper.find('form').trigger('submit.prevent')
    await flushPromises()

    expect(wrapper.find('button[type="submit"]').text()).toContain('Resetting...')
  })

  it('redirects to login on success', async () => {
    vi.mocked(resetPassword).mockResolvedValue(undefined)

    const wrapper = mount(ResetPasswordView)
    
    await wrapper.findAll('input[type="password"]')[0].setValue('NewPass123!')
    await wrapper.findAll('input[type="password"]')[1].setValue('NewPass123!')
    await wrapper.find('form').trigger('submit.prevent')
    await flushPromises()

    expect(mockPush).toHaveBeenCalledWith('/auth')
  })
})
