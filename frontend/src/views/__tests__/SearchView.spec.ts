import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import SearchView from '@/views/SearchView.vue'

const mockRoute = {
  query: {
    q: 'docker',
  },
}

vi.mock('vue-router', () => ({
  useRoute: () => mockRoute,
  useRouter: () => ({ replace: vi.fn() }),
}))

describe('SearchView', () => {
  beforeEach(() => {
    vi.useFakeTimers()
    vi.clearAllMocks()
    vi.stubGlobal('fetch', vi.fn())
  })

  afterEach(() => {
    vi.useRealTimers()
    vi.unstubAllGlobals()
  })

  it('renders search input with query from URL', async () => {
    const wrapper = mount(SearchView, {
      global: { stubs: { RouterLink: true } },
    })
    await flushPromises()
    const input = wrapper.find('input[type="search"]')
    expect(input.exists()).toBe(true)
    expect((input.element as HTMLInputElement).value).toBe('docker')
  })

  it('shows loading state while searching', async () => {
    vi.stubGlobal('fetch', vi.fn(() => new Promise(() => {})))

    const wrapper = mount(SearchView, {
      global: { stubs: { RouterLink: true } },
    })
    await flushPromises()
    vi.advanceTimersByTime(300)
    await flushPromises()

    expect(wrapper.text()).toContain('Searching')
  })

  it('renders search results', async () => {
    const mockResults = [
      { id: '1', title: 'Docker Guide', slug: 'docker-guide', description: 'Intro to Docker', published_at: '2024-01-01' },
      { id: '2', title: 'Kubernetes', slug: 'kubernetes', description: 'K8s basics', published_at: '2024-02-01' },
    ]
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue({
      ok: true,
      json: () => Promise.resolve(mockResults),
    }))

    const wrapper = mount(SearchView, {
      global: { stubs: { RouterLink: { template: '<a><slot /></a>' } } },
    })
    await flushPromises()
    vi.advanceTimersByTime(300)
    await flushPromises()

    expect(wrapper.text()).toContain('Docker Guide')
    expect(wrapper.text()).toContain('Kubernetes')
    expect(wrapper.text()).toContain('Intro to Docker')
  })

  it('shows empty state when no results', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue({
      ok: true,
      json: () => Promise.resolve([]),
    }))

    const wrapper = mount(SearchView, {
      global: { stubs: { RouterLink: true } },
    })
    await flushPromises()
    vi.advanceTimersByTime(300)
    await flushPromises()

    expect(wrapper.text()).toContain('No results')
  })

  it('shows error state on search failure', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue({
      ok: false,
      json: () => Promise.resolve({ detail: 'Server error' }),
    }))

    const wrapper = mount(SearchView, {
      global: { stubs: { RouterLink: true } },
    })
    await flushPromises()
    vi.advanceTimersByTime(300)
    await flushPromises()

    expect(wrapper.text()).toContain('Server error')
  })
})
