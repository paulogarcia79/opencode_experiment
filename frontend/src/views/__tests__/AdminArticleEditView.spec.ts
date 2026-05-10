import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { ref } from 'vue'
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
}))

vi.mock('@/composables/useAutoSave', () => ({
  useAutoSave: vi.fn().mockReturnValue({
    status: ref('idle'),
    retry: vi.fn(),
  }),
}))

import { fetchAdminArticle, createArticle, updateArticle } from '@/composables/useAdminApi'
import { useAutoSave } from '@/composables/useAutoSave'

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
      description: 'A description',
      content: { type: 'doc', content: [] },
      status: 'draft',
      send_newsletter: false,
      tags: [{ name: 'Vue', slug: 'vue' }],
    })

    const wrapper = mount(AdminArticleEditView, {
      global: { components: { RouterLink, TipTapEditor, TagInput } },
    })
    await flushPromises()

    expect(wrapper.text()).toContain('Edit Article')
    expect(wrapper.text()).toContain('Update your existing article')
  })

  it('calls createArticle and redirects on new article submit', async () => {
    vi.mocked(createArticle).mockResolvedValue({ id: 'new-id', title: 'Test' })

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
      description: '',
      content: { type: 'doc', content: [] },
      status: 'draft',
      send_newsletter: true,
      tags: [],
    })
    vi.mocked(updateArticle).mockResolvedValue({ id: '123' })

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
      retry: vi.fn(),
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
})
