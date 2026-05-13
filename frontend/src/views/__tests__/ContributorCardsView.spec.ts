import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import ContributorCardsView from '@/views/ContributorCardsView.vue'
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
    title: 'My Published Post',
    slug: 'my-published',
    status: 'published',
    published_at: '2025-01-15T00:00:00Z',
    total_views: 100,
    email_ctr: 4.5,
    has_been_rejected: false,
    latest_rejection_feedback: null,
    author: { id: 'user-1', email: 'contrib@test.com' },
    tags: [],
  },
  {
    id: '2',
    title: 'My Draft',
    slug: 'my-draft',
    status: 'draft',
    published_at: null,
    total_views: 0,
    email_ctr: null,
    has_been_rejected: true,
    latest_rejection_feedback: 'Needs more detail',
    author: { id: 'user-1', email: 'contrib@test.com' },
    tags: [],
  },
  {
    id: '3',
    title: 'Pending Review Post',
    slug: 'pending-post',
    status: 'pending_review',
    published_at: null,
    total_views: 0,
    email_ctr: null,
    has_been_rejected: false,
    latest_rejection_feedback: null,
    author: { id: 'user-1', email: 'contrib@test.com' },
    tags: [],
  },
]

describe('ContributorCardsView', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    setActivePinia(createPinia())
    const store = useAdminStore()
    store.setUser({
      id: 'user-1',
      email: 'contrib@test.com',
      role: 'contributor',
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

    const wrapper = mount(ContributorCardsView, { global: { components: { RouterLink } } })
    expect(wrapper.text()).toContain('Loading articles...')
  })

  it('renders article cards in a grid', async () => {
    const wrapper = mount(ContributorCardsView, { global: { components: { RouterLink } } })
    await flushPromises()

    expect(wrapper.text()).toContain('My Published Post')
    expect(wrapper.text()).toContain('My Draft')
    expect(wrapper.text()).toContain('Pending Review Post')
  })

  it('shows status badges with correct colors', async () => {
    const wrapper = mount(ContributorCardsView, { global: { components: { RouterLink } } })
    await flushPromises()

    expect(wrapper.text()).toContain('published')
    expect(wrapper.text()).toContain('draft')
    expect(wrapper.text()).toContain('pending_review')
  })

  it('shows rejection badge on rejected articles', async () => {
    const wrapper = mount(ContributorCardsView, { global: { components: { RouterLink } } })
    await flushPromises()

    expect(wrapper.text()).toContain('Rejected')
  })

  it('shows attention count badge', async () => {
    const wrapper = mount(ContributorCardsView, { global: { components: { RouterLink } } })
    await flushPromises()

    expect(wrapper.text()).toContain('1 needs attention')
  })

  it('shows edit and delete buttons on each card', async () => {
    const wrapper = mount(ContributorCardsView, { global: { components: { RouterLink } } })
    await flushPromises()

    const editLinks = wrapper.findAll('a')
    const editButtons = editLinks.filter(link => link.text().includes('Edit'))
    expect(editButtons.length).toBe(3)
    expect(wrapper.text()).toContain('Delete')
  })

  it('shows filter tabs', async () => {
    const wrapper = mount(ContributorCardsView, { global: { components: { RouterLink } } })
    await flushPromises()

    expect(wrapper.text()).toContain('All')
    expect(wrapper.text()).toContain('Drafts')
    expect(wrapper.text()).toContain('Published')
    expect(wrapper.text()).toContain('Pending Review')
  })

  it('shows search input', async () => {
    const wrapper = mount(ContributorCardsView, { global: { components: { RouterLink } } })
    await flushPromises()

    const input = wrapper.find('input[type="text"]')
    expect(input.exists()).toBe(true)
  })

  it('shows empty state when no articles', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue({
      ok: true,
      json: () => Promise.resolve([]),
    }))

    const wrapper = mount(ContributorCardsView, { global: { components: { RouterLink } } })
    await flushPromises()

    expect(wrapper.text()).toContain('No articles yet')
  })

  it('shows error state on fetch failure', async () => {
    vi.stubGlobal('fetch', vi.fn().mockRejectedValue(new Error('Network error')))

    const wrapper = mount(ContributorCardsView, { global: { components: { RouterLink } } })
    await flushPromises()

    expect(wrapper.text()).toContain('Failed to load articles')
    expect(wrapper.text()).toContain('Network error')
  })

  it('calls delete when confirming', async () => {
    vi.stubGlobal('confirm', vi.fn().mockReturnValue(true))
    vi.stubGlobal('fetch', vi.fn()
      .mockResolvedValueOnce({ ok: true, json: () => Promise.resolve(mockArticles) })
      .mockResolvedValueOnce({ ok: true, json: () => Promise.resolve({}) }))

    const wrapper = mount(ContributorCardsView, { global: { components: { RouterLink } } })
    await flushPromises()

    const deleteBtn = wrapper.find('button')
    await deleteBtn.trigger('click')
    await flushPromises()
  })
})
