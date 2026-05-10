import { describe, it, expect, vi } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import HomeView from '@/views/HomeView.vue'

const mockPush = vi.fn()

vi.mock('vue-router', () => ({
  useRouter: () => ({ push: mockPush }),
}))

vi.mock('@/composables/useApi', () => ({
  fetchArticles: vi.fn().mockResolvedValue([]),
}))

vi.mock('@/composables/useHead', () => ({
  useHead: vi.fn(),
}))

describe('HomeView search input', () => {
  it('navigates to /search?q=term on submit', async () => {
    const wrapper = mount(HomeView, {
      global: { stubs: { RouterLink: true } },
    })
    await flushPromises()

    const input = wrapper.find('input[type="search"]')
    await input.setValue('docker')
    await wrapper.find('form').trigger('submit.prevent')

    expect(mockPush).toHaveBeenCalledWith({ path: '/search', query: { q: 'docker' } })
  })
})
