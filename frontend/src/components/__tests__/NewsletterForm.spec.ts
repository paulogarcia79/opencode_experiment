import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import NewsletterForm from '@/components/NewsletterForm.vue'

vi.mock('@/composables/useApi', () => ({
  subscribeToNewsletter: vi.fn(),
}))

import { subscribeToNewsletter } from '@/composables/useApi'

describe('NewsletterForm', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('renders initial idle state with email input', () => {
    const wrapper = mount(NewsletterForm)

    expect(wrapper.find('input[type="email"]').exists()).toBe(true)
    expect(wrapper.find('button').text()).toBe('Subscribe')
    expect(wrapper.find('[role="alert"]').exists()).toBe(false)
  })

  it('calls subscribeToNewsletter on form submit', async () => {
    vi.mocked(subscribeToNewsletter).mockResolvedValue({ message: 'Check your email' })

    const wrapper = mount(NewsletterForm)
    const input = wrapper.find('input[type="email"]')
    await input.setValue('test@example.com')
    await wrapper.find('form').trigger('submit.prevent')
    await flushPromises()

    expect(subscribeToNewsletter).toHaveBeenCalledWith('test@example.com')
  })

  it('shows loading state during submission', async () => {
    vi.mocked(subscribeToNewsletter).mockImplementation(
      () => new Promise((resolve) => setTimeout(() => resolve({ message: 'OK' }), 50))
    )

    const wrapper = mount(NewsletterForm)
    await wrapper.find('input[type="email"]').setValue('test@example.com')
    wrapper.find('form').trigger('submit.prevent')
    await flushPromises()

    expect(wrapper.find('button').text()).toBe('Subscribing...')
    expect(wrapper.find('button').attributes('disabled')).toBeDefined()
  })

  it('shows success state with message on success', async () => {
    vi.mocked(subscribeToNewsletter).mockResolvedValue({ message: 'Check your email to confirm' })

    const wrapper = mount(NewsletterForm)
    await wrapper.find('input[type="email"]').setValue('test@example.com')
    await wrapper.find('form').trigger('submit.prevent')
    await flushPromises()

    expect(wrapper.text()).toContain('Success')
    expect(wrapper.text()).toContain('Check your email to confirm')
  })

  it('shows error state with message on failure', async () => {
    vi.mocked(subscribeToNewsletter).mockRejectedValue(new Error('Email already subscribed'))

    const wrapper = mount(NewsletterForm)
    await wrapper.find('input[type="email"]').setValue('existing@example.com')
    await wrapper.find('form').trigger('submit.prevent')
    await flushPromises()

    expect(wrapper.text()).toContain('Error')
    expect(wrapper.text()).toContain('Email already subscribed')
  })

  it('clears email input after successful subscription', async () => {
    vi.mocked(subscribeToNewsletter).mockResolvedValue({ message: 'OK' })

    const wrapper = mount(NewsletterForm)
    const input = wrapper.find('input[type="email"]')
    await input.setValue('test@example.com')
    await wrapper.find('form').trigger('submit.prevent')
    await flushPromises()

    expect((input.element as HTMLInputElement).value).toBe('')
  })
})
