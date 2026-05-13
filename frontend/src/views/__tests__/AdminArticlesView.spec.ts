import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import AdminArticlesView from '@/views/AdminArticlesView.vue'
import { useAdminStore } from '@/stores/admin'

const mockPush = vi.fn()
const mockReplace = vi.fn()
vi.mock('vue-router', () => ({
  useRouter: () => ({ push: mockPush, replace: mockReplace }),
  useRoute: () => ({ query: {} }),
  RouterLink: { template: '<a :href="to"><slot /></a>', props: ['to'] },
}))

const RouterLink = { template: '<a :href="to"><slot /></a>', props: ['to'] }

const mockArticles = [
  {
    id: '1',
    title: 'Published Article',
    slug: 'published-article',
    status: 'published',
    published_at: '2025-01-15T00:00:00Z',
    total_views: 100,
    email_ctr: 4.5,
    content: { type: 'doc' },
    description: null,
    send_newsletter: true,
    scheduled_for: null,
    search_text: null,
    submitted_at: null,
    created_at: '2025-01-15T00:00:00Z',
    updated_at: '2025-01-15T00:00:00Z',
    author: { id: 'user-1', email: 'admin@example.com' },
    tags: [],
  },
  {
    id: '2',
    title: 'Draft Article',
    slug: 'draft-article',
    status: 'draft',
    published_at: null,
    total_views: 0,
    email_ctr: null,
    content: { type: 'doc' },
    description: null,
    send_newsletter: true,
    scheduled_for: null,
    search_text: null,
    submitted_at: null,
    created_at: '2025-01-15T00:00:00Z',
    updated_at: '2025-01-15T00:00:00Z',
    author: { id: 'user-1', email: 'admin@example.com' },
    tags: [],
  },
]

describe('AdminArticlesView', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    setActivePinia(createPinia())
    const store = useAdminStore()
    store.setUser({
      id: 'user-1',
      email: 'admin@example.com',
      role: 'admin',
      is_active: true,
      is_verified: true,
      created_at: '2025-01-01T00:00:00Z',
    })
    store.setToken('test-token')
    vi.stubGlobal('confirm', vi.fn())
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue({
      ok: true,
      json: () => Promise.resolve(mockArticles),
    }))
  })

  it('shows loading state while fetching', () => {
    vi.stubGlobal('fetch', vi.fn().mockImplementation(() => new Promise(() => {})))

    const wrapper = mount(AdminArticlesView, { global: { components: { RouterLink } } })
    expect(wrapper.text()).toContain('Loading articles...')
  })

  it('shows empty state when no articles', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue({
      ok: true,
      json: () => Promise.resolve([]),
    }))

    const wrapper = mount(AdminArticlesView, { global: { components: { RouterLink } } })
    await flushPromises()

    expect(wrapper.text()).toContain('No items to display')
  })

  it('renders article list with title and status', async () => {
    const wrapper = mount(AdminArticlesView, { global: { components: { RouterLink } } })
    await flushPromises()

    expect(wrapper.text()).toContain('Published Article')
    expect(wrapper.text()).toContain('Draft Article')
    expect(wrapper.text()).toContain('published')
    expect(wrapper.text()).toContain('draft')
  })

  it('shows edit and delete buttons on articles', async () => {
    const wrapper = mount(AdminArticlesView, { global: { components: { RouterLink } } })
    await flushPromises()

    expect(wrapper.text()).toContain('Edit')
    expect(wrapper.text()).toContain('Delete')
  })

  it('expands row to show detail card on click', async () => {
    const wrapper = mount(AdminArticlesView, { global: { components: { RouterLink } } })
    await flushPromises()

    const rows = wrapper.findAll('tbody tr')
    // Click first data row (not expanded row)
    await rows[0].trigger('click')
    await flushPromises()

    expect(wrapper.text()).toContain('Views')
    expect(wrapper.text()).toContain('Email CTR')
  })

  it('shows filter tabs', async () => {
    const wrapper = mount(AdminArticlesView, { global: { components: { RouterLink } } })
    await flushPromises()

    expect(wrapper.text()).toContain('All')
    expect(wrapper.text()).toContain('Drafts')
    expect(wrapper.text()).toContain('Published')
    expect(wrapper.text()).toContain('Pending Review')
  })

  it('calls delete when confirming', async () => {
    vi.stubGlobal('confirm', vi.fn().mockReturnValue(true))
    vi.stubGlobal('fetch', vi.fn()
      .mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve(mockArticles),
      })
      .mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve({}),
      }))

    const wrapper = mount(AdminArticlesView, { global: { components: { RouterLink } } })
    await flushPromises()

    const deleteBtn = wrapper.find('button')
    await deleteBtn.trigger('click')
    await flushPromises()
  })

  it('shows error state on fetch failure', async () => {
    vi.stubGlobal('fetch', vi.fn().mockRejectedValue(new Error('Network error')))

    const wrapper = mount(AdminArticlesView, { global: { components: { RouterLink } } })
    await flushPromises()

    expect(wrapper.text()).toContain('Failed to load articles')
    expect(wrapper.text()).toContain('Network error')
  })
})
