import { describe, it, expect, vi } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import HomeView from '@/views/HomeView.vue'

vi.mock('vue-router', () => ({
  useRouter: () => ({ push: vi.fn() }),
}))

vi.mock('@/composables/useApi', () => ({
  fetchArticles: vi.fn().mockResolvedValue([]),
}))

vi.mock('@/composables/useHead', () => ({
  useHead: vi.fn(),
}))

describe('HomeView', () => {
  it('renders hero section', async () => {
    const wrapper = mount(HomeView, {
      global: { stubs: { RouterLink: true } },
    })
    await flushPromises()

    expect(wrapper.text()).toContain('Exploring code')
  })
})
