import { describe, it, expect, vi } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { nextTick } from 'vue'
import TagArticlesView from '@/views/TagArticlesView.vue'

const mockRoute = {
  params: {
    slug: 'docker',
  },
}

vi.mock('vue-router', () => ({
  useRoute: () => mockRoute,
}))

describe('TagArticlesView', () => {
  it('renders tag name and article count', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue({
      ok: true,
      json: () => Promise.resolve({
        name: 'Docker',
        slug: 'docker',
        articles: [
          { id: '1', title: 'Docker Guide', slug: 'docker-guide', description: 'Intro', content: {}, published_at: '2024-01-01' },
        ],
      }),
    }))

    const wrapper = mount(TagArticlesView, {
      global: { stubs: { RouterLink: { template: '<a><slot /></a>' } } },
    })
    await flushPromises()
    await nextTick()

    expect(wrapper.text()).toContain('Docker')
    expect(wrapper.text()).toContain('1 article tagged')
    expect(wrapper.text()).toContain('Docker Guide')
  })

  it('shows empty state when no articles', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue({
      ok: true,
      json: () => Promise.resolve({
        name: 'Empty',
        slug: 'empty',
        articles: [],
      }),
    }))

    const wrapper = mount(TagArticlesView, {
      global: { stubs: { RouterLink: { template: '<a><slot /></a>' } } },
    })
    await flushPromises()

    expect(wrapper.text()).toContain('No articles found')
  })

  it('shows error for unknown tag', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue({
      ok: false,
      status: 404,
    }))

    const wrapper = mount(TagArticlesView, {
      global: { stubs: { RouterLink: { template: '<a><slot /></a>' } } },
    })
    await flushPromises()

    expect(wrapper.text()).toContain('Tag not found')
  })
})
