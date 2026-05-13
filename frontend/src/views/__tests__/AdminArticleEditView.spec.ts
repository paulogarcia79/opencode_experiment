import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { ref } from 'vue'
import { createPinia, setActivePinia } from 'pinia'
import AdminArticleEditView from '@/views/AdminArticleEditView.vue'

const mockParams = { id: 'new' }
const mockPush = vi.fn()
const mockReplace = vi.fn()

vi.mock('vue-router', () => ({
  useRoute: () => ({ params: mockParams }),
  useRouter: () => ({ push: mockPush, replace: mockReplace }),
  RouterLink: { template: '<a :href="to"><slot /></a>', props: ['to'] },
}))

vi.mock('@/composables/useAdminApi', () => ({
  fetchAdminArticle: vi.fn(),
  createArticle: vi.fn(),
  updateArticle: vi.fn(),
  sendPreviewEmail: vi.fn(),
  fetchUsers: vi.fn(),
  reassignArticle: vi.fn(),
}))

vi.mock('@/composables/useAutoSave', () => ({
  useAutoSave: vi.fn().mockReturnValue({
    status: ref('idle'),
    retry: vi.fn(),
    markFormTouched: vi.fn(),
  }),
}))

import { fetchAdminArticle, createArticle, updateArticle, sendPreviewEmail, fetchUsers, reassignArticle } from '@/composables/useAdminApi'
import { useAutoSave } from '@/composables/useAutoSave'
import { useAdminStore } from '@/stores/admin'

const RouterLink = {
  template: '<a :href="to"><slot /></a>',
  props: ['to'],
}

const TipTapEditor = {
  template: '<div data-testid="tiptap-editor" />',
  props: ['modelValue'],
}

const TagInput = {
  template: '<div data-testid="tag-input" />',
  props: ['modelValue'],
}

describe('AdminArticleEditView', () => {
  beforeEach(() => {
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
    vi.clearAllMocks()
    mockParams.id = 'new'
  })

  it('shows "New Article" header in create mode', () => {
    const wrapper = mount(AdminArticleEditView, {
      global: { components: { RouterLink, TipTapEditor, TagInput } },
    })

    expect(wrapper.text()).toContain('New Article')
    expect(wrapper.text()).toContain('Create a new blog post')
  })

  it('loads article and shows "Edit Article" header in edit mode', async () => {
    mockParams.id = '123'
    vi.mocked(fetchAdminArticle).mockResolvedValue({
      id: '123',
      title: 'Existing Article',
      slug: 'existing-article',
      description: 'A description',
      content: { type: 'doc', content: [] },
      status: 'draft',
      send_newsletter: false,
      published_at: null,
      scheduled_for: null,
      search_text: null,
      created_at: '2025-01-15T00:00:00Z',
      updated_at: '2025-01-15T00:00:00Z',
      author: { id: 'user-1', email: 'admin@example.com' },
      tags: [{ id: '1', name: 'Vue', slug: 'vue' }],
    })

    const wrapper = mount(AdminArticleEditView, {
      global: { components: { RouterLink, TipTapEditor, TagInput } },
    })
    await flushPromises()

    expect(wrapper.text()).toContain('Edit Article')
    expect(wrapper.text()).toContain('Update your existing article')
  })

  it('calls createArticle and redirects on new article submit', async () => {
    vi.mocked(createArticle).mockResolvedValue({
      id: 'new-id',
      title: 'Test',
      slug: 'test',
      content: { type: 'doc' },
      description: null,
      status: 'draft',
      send_newsletter: true,
      published_at: null,
      scheduled_for: null,
      search_text: null,
      created_at: '2025-01-15T00:00:00Z',
      updated_at: '2025-01-15T00:00:00Z',
      author: { id: 'user-1', email: 'admin@example.com' },
      tags: [],
    })

    const wrapper = mount(AdminArticleEditView, {
      global: { components: { RouterLink, TipTapEditor, TagInput } },
    })

    await wrapper.find('input[type="text"]').setValue('Test Article')
    await wrapper.find('form').trigger('submit.prevent')
    await flushPromises()

    expect(createArticle).toHaveBeenCalledWith(
      expect.objectContaining({ title: 'Test Article' })
    )
    expect(mockPush).toHaveBeenCalledWith('/admin/articles/new-id/edit')
    expect(wrapper.text()).toContain('Article created successfully')
  })

  it('calls updateArticle on edit mode submit', async () => {
    mockParams.id = '123'
    vi.mocked(fetchAdminArticle).mockResolvedValue({
      id: '123',
      title: 'Existing',
      slug: 'existing',
      description: '',
      content: { type: 'doc', content: [] },
      status: 'draft',
      send_newsletter: true,
      published_at: null,
      scheduled_for: null,
      search_text: null,
      created_at: '2025-01-15T00:00:00Z',
      updated_at: '2025-01-15T00:00:00Z',
      author: { id: 'user-1', email: 'admin@example.com' },
      tags: [],
    })
    vi.mocked(updateArticle).mockResolvedValue({
      id: '123',
      title: 'Existing',
      slug: 'existing',
      content: { type: 'doc', content: [] },
      description: '',
      status: 'draft',
      send_newsletter: true,
      published_at: null,
      scheduled_for: null,
      search_text: null,
      created_at: '2025-01-15T00:00:00Z',
      updated_at: '2025-01-15T00:00:00Z',
      author: { id: 'user-1', email: 'admin@example.com' },
      tags: [],
    })

    const wrapper = mount(AdminArticleEditView, {
      global: { components: { RouterLink, TipTapEditor, TagInput } },
    })
    await flushPromises()

    await wrapper.find('form').trigger('submit.prevent')
    await flushPromises()

    expect(updateArticle).toHaveBeenCalledWith('123', expect.any(Object))
    expect(wrapper.text()).toContain('Article updated successfully')
  })

  it('shows auto-save status indicators', async () => {
    vi.mocked(useAutoSave).mockReturnValue({
      status: ref('saved'),
      error: ref<string | null>(null),
      lastSavedAt: ref<Date | null>(null),
      retry: vi.fn(),
      markFormTouched: vi.fn(),
    })

    const wrapper = mount(AdminArticleEditView, {
      global: { components: { RouterLink, TipTapEditor, TagInput } },
    })

    expect(wrapper.text()).toContain('Saved')
  })

  it('shows newsletter checkbox only when status is published', async () => {
    const wrapper = mount(AdminArticleEditView, {
      global: { components: { RouterLink, TipTapEditor, TagInput } },
    })

    // Default status is draft - newsletter checkbox should not be visible
    expect(wrapper.text()).not.toContain('Send newsletter')

    // Toggle to published - need to find and click the checkbox
    const checkboxes = wrapper.findAll('input[type="checkbox"]')
    const publishCheckbox = checkboxes[0]
    await publishCheckbox.setValue(true)
    await flushPromises()

    expect(wrapper.text()).toContain('Send newsletter')
  })

  it('calls sendPreviewEmail and shows success message', async () => {
    mockParams.id = '123'
    vi.mocked(fetchAdminArticle).mockResolvedValue({
      id: '123',
      title: 'Existing',
      slug: 'existing',
      description: '',
      content: { type: 'doc', content: [] },
      status: 'draft',
      send_newsletter: true,
      published_at: null,
      scheduled_for: null,
      search_text: null,
      created_at: '2025-01-15T00:00:00Z',
      updated_at: '2025-01-15T00:00:00Z',
      author: { id: 'user-1', email: 'admin@example.com' },
      tags: [],
    })
    vi.mocked(sendPreviewEmail).mockResolvedValue({ message: 'Preview sent successfully' })

    const wrapper = mount(AdminArticleEditView, {
      global: { components: { RouterLink, TipTapEditor, TagInput } },
    })
    await flushPromises()

    // Find and click the Send Preview button
    const buttons = wrapper.findAll('button')
    const previewBtn = buttons.find(btn => btn.text() === 'Send Preview')
    expect(previewBtn).toBeDefined()
    
    await previewBtn!.trigger('click')
    await flushPromises()

    expect(sendPreviewEmail).toHaveBeenCalledWith('123')
    expect(wrapper.text()).toContain('Preview sent successfully')
  })

  it('shows error state when sendPreviewEmail fails', async () => {
    mockParams.id = '123'
    vi.mocked(fetchAdminArticle).mockResolvedValue({
      id: '123',
      title: 'Existing',
      slug: 'existing',
      description: '',
      content: { type: 'doc', content: [] },
      status: 'draft',
      send_newsletter: true,
      published_at: null,
      scheduled_for: null,
      search_text: null,
      created_at: '2025-01-15T00:00:00Z',
      updated_at: '2025-01-15T00:00:00Z',
      author: { id: 'user-1', email: 'admin@example.com' },
      tags: [],
    })
    vi.mocked(sendPreviewEmail).mockRejectedValue(new Error('Network error'))

    const wrapper = mount(AdminArticleEditView, {
      global: { components: { RouterLink, TipTapEditor, TagInput } },
    })
    await flushPromises()

    const buttons = wrapper.findAll('button')
    const previewBtn = buttons.find(btn => btn.text() === 'Send Preview')
    
    await previewBtn!.trigger('click')
    await flushPromises()

    expect(wrapper.text()).toContain('Network error')
  })

  it('shows Change Author dropdown for admin when editing', async () => {
    mockParams.id = '123'
    vi.mocked(fetchAdminArticle).mockResolvedValue({
      id: '123',
      title: 'Existing',
      slug: 'existing',
      description: '',
      content: { type: 'doc', content: [] },
      status: 'draft',
      send_newsletter: true,
      published_at: null,
      scheduled_for: null,
      search_text: null,
      created_at: '2025-01-15T00:00:00Z',
      updated_at: '2025-01-15T00:00:00Z',
      author: { id: 'user-1', email: 'admin@example.com' },
      tags: [],
    })
    vi.mocked(fetchUsers).mockResolvedValue([
      { id: 'user-1', email: 'admin@example.com', role: 'admin', is_active: true, is_verified: true, created_at: '2025-01-01T00:00:00Z' },
      { id: 'user-2', email: 'editor@example.com', role: 'editor', is_active: true, is_verified: true, created_at: '2025-01-01T00:00:00Z' },
    ])

    const wrapper = mount(AdminArticleEditView, {
      global: { components: { RouterLink, TipTapEditor, TagInput } },
    })
    await flushPromises()

    expect(wrapper.text()).toContain('Change Author')
    expect(wrapper.find('select').exists()).toBe(true)
  })

  it('hides Change Author dropdown for editor', async () => {
    const store = useAdminStore()
    store.setUser({
      id: 'user-1',
      email: 'editor@example.com',
      role: 'editor',
      is_active: true,
      is_verified: true,
      created_at: '2025-01-01T00:00:00Z',
    })

    mockParams.id = '123'
    vi.mocked(fetchAdminArticle).mockResolvedValue({
      id: '123',
      title: 'Existing',
      slug: 'existing',
      description: '',
      content: { type: 'doc', content: [] },
      status: 'draft',
      send_newsletter: true,
      published_at: null,
      scheduled_for: null,
      search_text: null,
      created_at: '2025-01-15T00:00:00Z',
      updated_at: '2025-01-15T00:00:00Z',
      author: { id: 'user-1', email: 'editor@example.com' },
      tags: [],
    })

    const wrapper = mount(AdminArticleEditView, {
      global: { components: { RouterLink, TipTapEditor, TagInput } },
    })
    await flushPromises()

    expect(wrapper.text()).not.toContain('Change Author')
  })

  it('calls reassignArticle when selecting user and confirming', async () => {
    mockParams.id = '123'
    vi.mocked(fetchAdminArticle).mockResolvedValue({
      id: '123',
      title: 'Existing',
      slug: 'existing',
      description: '',
      content: { type: 'doc', content: [] },
      status: 'draft',
      send_newsletter: true,
      published_at: null,
      scheduled_for: null,
      search_text: null,
      created_at: '2025-01-15T00:00:00Z',
      updated_at: '2025-01-15T00:00:00Z',
      author: { id: 'user-1', email: 'admin@example.com' },
      tags: [],
    })
    vi.mocked(fetchUsers).mockResolvedValue([
      { id: 'user-2', email: 'editor@example.com', role: 'editor', is_active: true, is_verified: true, created_at: '2025-01-01T00:00:00Z' },
    ])
    vi.mocked(reassignArticle).mockResolvedValue({ message: 'Article reassigned' })
    vi.stubGlobal('confirm', vi.fn().mockReturnValue(true))

    const wrapper = mount(AdminArticleEditView, {
      global: { components: { RouterLink, TipTapEditor, TagInput } },
    })
    await flushPromises()

    const select = wrapper.find('select')
    await select.setValue('user-2')

    const reassignBtn = wrapper.findAll('button').find(btn => btn.text() === 'Reassign')
    await reassignBtn!.trigger('click')
    await flushPromises()

    expect(reassignArticle).toHaveBeenCalledWith('123', 'user-2')
    expect(wrapper.text()).toContain('Article reassigned to editor@example.com')
  })

  it('shows error when reassign fails', async () => {
    mockParams.id = '123'
    vi.mocked(fetchAdminArticle).mockResolvedValue({
      id: '123',
      title: 'Existing',
      slug: 'existing',
      description: '',
      content: { type: 'doc', content: [] },
      status: 'draft',
      send_newsletter: true,
      published_at: null,
      scheduled_for: null,
      search_text: null,
      created_at: '2025-01-15T00:00:00Z',
      updated_at: '2025-01-15T00:00:00Z',
      author: { id: 'user-1', email: 'admin@example.com' },
      tags: [],
    })
    vi.mocked(fetchUsers).mockResolvedValue([
      { id: 'user-2', email: 'inactive@example.com', role: 'contributor', is_active: false, is_verified: true, created_at: '2025-01-01T00:00:00Z' },
    ])
    vi.mocked(reassignArticle).mockRejectedValue(new Error('Target user is inactive'))
    vi.stubGlobal('confirm', vi.fn().mockReturnValue(true))

    const wrapper = mount(AdminArticleEditView, {
      global: { components: { RouterLink, TipTapEditor, TagInput } },
    })
    await flushPromises()

    const select = wrapper.find('select')
    await select.setValue('user-2')

    const reassignBtn = wrapper.findAll('button').find(btn => btn.text() === 'Reassign')
    await reassignBtn!.trigger('click')
    await flushPromises()

    expect(wrapper.text()).toContain('Target user is inactive')
  })
})
