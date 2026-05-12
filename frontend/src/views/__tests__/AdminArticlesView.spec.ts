import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import AdminArticlesView from '@/views/AdminArticlesView.vue'

vi.mock('@/composables/useAdminApi', () => ({
  fetchAdminArticles: vi.fn(),
  fetchArticlePerformance: vi.fn().mockResolvedValue([]),
  deleteArticle: vi.fn(),
  getAuthHeaders: vi.fn(() => ({ Authorization: 'Bearer test-token' })),
}))

vi.mock('vue-router', () => ({
  RouterLink: { template: '<a :href="to"><slot /></a>', props: ['to'] },
}))

import { fetchAdminArticles, deleteArticle } from '@/composables/useAdminApi'

const RouterLink = {
  template: '<a :href="to"><slot /></a>',
  props: ['to'],
}

describe('AdminArticlesView', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    vi.stubGlobal('confirm', vi.fn())
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue({
      ok: true,
      json: () => Promise.resolve([]),
    }))
  })

  it('shows loading state while fetching', () => {
    vi.mocked(fetchAdminArticles).mockImplementation(() => new Promise(() => {}))

    const wrapper = mount(AdminArticlesView, { global: { components: { RouterLink } } })

    expect(wrapper.text()).toContain('Loading articles...')
  })

  it('shows empty state when no articles', async () => {
    vi.mocked(fetchAdminArticles).mockResolvedValue([])

    const wrapper = mount(AdminArticlesView, { global: { components: { RouterLink } } })
    await flushPromises()

    expect(wrapper.text()).toContain('No articles yet')
  })

  it('renders article list with title, status, date, and actions', async () => {
    const mockArticles = [
      {
        id: '1',
        title: 'Published Article',
        slug: 'published-article',
        status: 'published',
        published_at: '2025-01-15T00:00:00Z',
      },
      {
        id: '2',
        title: 'Draft Article',
        slug: 'draft-article',
        status: 'draft',
        published_at: null,
      },
    ]
    vi.mocked(fetchAdminArticles).mockResolvedValue(mockArticles)

    const wrapper = mount(AdminArticlesView, { global: { components: { RouterLink } } })
    await flushPromises()

    expect(wrapper.text()).toContain('Published Article')
    expect(wrapper.text()).toContain('Draft Article')
    expect(wrapper.text()).toContain('published')
    expect(wrapper.text()).toContain('draft')
    expect(wrapper.findAll('button').length).toBeGreaterThanOrEqual(2)
  })

  it('calls deleteArticle when confirming deletion', async () => {
    const mockArticles = [
      { id: '1', title: 'Test', slug: 'test', status: 'draft', published_at: null },
    ]
    vi.mocked(fetchAdminArticles).mockResolvedValue(mockArticles)
    vi.mocked(deleteArticle).mockResolvedValue(undefined)
    vi.mocked(globalThis.confirm).mockReturnValue(true)

    const wrapper = mount(AdminArticlesView, { global: { components: { RouterLink } } })
    await flushPromises()

    const deleteButtons = wrapper.findAll('button')
    const deleteBtn = deleteButtons.find(btn => btn.text().includes('Delete'))
    await deleteBtn?.trigger('click')
    await flushPromises()

    expect(deleteArticle).toHaveBeenCalledWith('1')
  })

  it('shows error state on fetch failure', async () => {
    vi.mocked(fetchAdminArticles).mockRejectedValue(new Error('Network error'))

    const wrapper = mount(AdminArticlesView, { global: { components: { RouterLink } } })
    await flushPromises()

    expect(wrapper.text()).toContain('Failed to load articles')
    expect(wrapper.text()).toContain('Network error')
  })
})
