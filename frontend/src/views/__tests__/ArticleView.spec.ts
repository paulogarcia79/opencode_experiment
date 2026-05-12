import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import ArticleView from '@/views/ArticleView.vue'

const mockParams = { slug: 'test-article' }

vi.mock('vue-router', () => ({
  useRoute: () => ({ params: mockParams }),
}))

const RouterLink = {
  template: '<a :href="to"><slot /></a>',
  props: ['to'],
}

vi.mock('@/composables/useApi', () => ({
  fetchArticle: vi.fn(),
}))

vi.mock('@/composables/useHead', () => ({
  useHead: vi.fn(),
}))

vi.mock('@/composables/useReadingTime', () => ({
  estimateReadingTime: vi.fn().mockReturnValue(3),
  formatReadingTime: vi.fn().mockReturnValue('3 min read'),
}))

vi.mock('@/components/TipTapRenderer.vue', () => ({
  default: { template: '<div data-testid="tiptap-renderer" />' },
}))

vi.mock('@/components/NewsletterForm.vue', () => ({
  default: { template: '<div data-testid="newsletter-form" />' },
}))

vi.mock('@/components/ShareButtons.vue', () => ({
  default: {
    template: '<div data-testid="share-buttons" />',
    props: ['url', 'title', 'description'],
  },
}))

import { fetchArticle } from '@/composables/useApi'
import { useHead } from '@/composables/useHead'

describe('ArticleView', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('shows loading state while fetching', () => {
    vi.mocked(fetchArticle).mockImplementation(() => new Promise(() => {}))

    const wrapper = mount(ArticleView, {
      global: { components: { RouterLink } },
    })

    expect(wrapper.text()).toContain('Loading article...')
  })

  it('shows error state on fetch failure', async () => {
    vi.mocked(fetchArticle).mockRejectedValue(new Error('Article not found'))

    const wrapper = mount(ArticleView, {
      global: { stubs: { RouterLink: true } },
    })
    await flushPromises()

    expect(wrapper.text()).toContain('Error loading article')
    expect(wrapper.text()).toContain('Article not found')
  })

  it('renders article title, date, and reading time on success', async () => {
    vi.mocked(fetchArticle).mockResolvedValue({
      id: '1',
      title: 'Test Article',
      slug: 'test-article',
      description: 'A test article',
      content: { type: 'doc', content: [] },
      published_at: '2025-01-15T00:00:00Z',
    })

    const wrapper = mount(ArticleView, { global: { components: { RouterLink } } })
    await flushPromises()

    expect(wrapper.text()).toContain('Test Article')
    expect(wrapper.text()).toContain('3 min read')
    expect(wrapper.text()).toContain('test-article')
  })

  it('renders tags as RouterLinks when present', async () => {
    vi.mocked(fetchArticle).mockResolvedValue({
      id: '1',
      title: 'Test Article',
      slug: 'test-article',
      description: 'A test article',
      content: { type: 'doc', content: [] },
      published_at: '2025-01-15T00:00:00Z',
      tags: [
        { name: 'Vue', slug: 'vue' },
        { name: 'TypeScript', slug: 'typescript' },
      ],
    })

    const wrapper = mount(ArticleView, { global: { components: { RouterLink } } })
    await flushPromises()

    const links = wrapper.findAll('a')
    const tagLinks = links.filter(link => link.attributes('href')?.startsWith('/tags/'))
    expect(tagLinks.length).toBe(2)
    expect(tagLinks[0].text()).toBe('Vue')
    expect(tagLinks[1].text()).toBe('TypeScript')
  })

  it('does not render tags when article has no tags', async () => {
    vi.mocked(fetchArticle).mockResolvedValue({
      id: '1',
      title: 'Test Article',
      slug: 'test-article',
      description: 'A test article',
      content: { type: 'doc', content: [] },
      published_at: '2025-01-15T00:00:00Z',
      tags: [],
    })

    const wrapper = mount(ArticleView, { global: { components: { RouterLink } } })
    await flushPromises()

    const tagSection = wrapper.findAll('a').filter(a => a.text() === 'Vue' || a.text() === 'TypeScript')
    expect(tagSection.length).toBe(0)
  })

  it('renders ShareButtons with correct props', async () => {
    vi.mocked(fetchArticle).mockResolvedValue({
      id: '1',
      title: 'Test Article',
      slug: 'test-article',
      description: 'A test article',
      content: { type: 'doc', content: [] },
      published_at: '2025-01-15T00:00:00Z',
    })

    const wrapper = mount(ArticleView, { global: { components: { RouterLink } } })
    await flushPromises()

    expect(wrapper.find('[data-testid="share-buttons"]').exists()).toBe(true)
  })

  it('renders NewsletterForm component', async () => {
    vi.mocked(fetchArticle).mockResolvedValue({
      id: '1',
      title: 'Test Article',
      slug: 'test-article',
      description: 'A test article',
      content: { type: 'doc', content: [] },
      published_at: '2025-01-15T00:00:00Z',
    })

    const wrapper = mount(ArticleView, { global: { components: { RouterLink } } })
    await flushPromises()

    expect(wrapper.find('[data-testid="newsletter-form"]').exists()).toBe(true)
  })

  it('calls useHead with correct meta data on success', async () => {
    vi.mocked(fetchArticle).mockResolvedValue({
      id: '1',
      title: 'Test Article',
      slug: 'test-article',
      description: 'A test article',
      content: { type: 'doc', content: [] },
      published_at: '2025-01-15T00:00:00Z',
    })

    mount(ArticleView, { global: { components: { RouterLink } } })
    await flushPromises()

    expect(useHead).toHaveBeenCalledWith(
      expect.objectContaining({
        title: 'Test Article',
        description: 'A test article',
        ogTitle: 'Test Article',
        ogType: 'article',
        twitterTitle: 'Test Article',
      })
    )
  })
})
