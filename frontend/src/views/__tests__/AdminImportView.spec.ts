import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import AdminImportView from '@/views/AdminImportView.vue'

vi.mock('@/composables/useMarkdownImport', () => ({
  importMarkdownFiles: vi.fn(),
}))

const RouterLink = {
  template: '<a :href="to"><slot /></a>',
  props: ['to'],
}

import { importMarkdownFiles } from '@/composables/useMarkdownImport'

describe('AdminImportView', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
  })

  it('renders page header and drop zone', () => {
    const wrapper = mount(AdminImportView, { global: { components: { RouterLink } } })

    expect(wrapper.text()).toContain('Import Articles')
    expect(wrapper.text()).toContain('Drag & drop Markdown files')
  })

  it('shows file input button for browse upload', () => {
    const wrapper = mount(AdminImportView, { global: { components: { RouterLink } } })

    const browseButton = wrapper.find('button')
    expect(browseButton.exists()).toBe(true)
    expect(browseButton.text()).toContain('Browse files')
  })

  it('shows loading state during import', async () => {
    vi.mocked(importMarkdownFiles).mockImplementation(() => new Promise(() => {}))

    const wrapper = mount(AdminImportView, { global: { components: { RouterLink } } })

    const file = new File(['# Test'], 'test.md', { type: 'text/markdown' })
    Object.defineProperty(wrapper.find('input[type="file"]').element, 'files', {
      value: [file],
    })
    await wrapper.find('input[type="file"]').trigger('change')

    expect(wrapper.text()).toContain('Importing')
  })

  it('shows results with success and error counts', async () => {
    const mockResult = {
      successes: [
        { id: 'abc-123', title: 'Good Article', slug: 'good-article' },
        { id: 'def-456', title: 'Another Article', slug: 'another-article' },
      ],
      errors: [
        { filename: 'bad.md', error: 'Invalid frontmatter' },
      ],
      total: 3,
    }
    vi.mocked(importMarkdownFiles).mockResolvedValue(mockResult)

    const wrapper = mount(AdminImportView, { global: { components: { RouterLink } } })

    const file = new File(['# Test'], 'test.md', { type: 'text/markdown' })
    Object.defineProperty(wrapper.find('input[type="file"]').element, 'files', {
      value: [file],
    })
    await wrapper.find('input[type="file"]').trigger('change')
    await flushPromises()

    expect(wrapper.text()).toContain('Imported')
    expect(wrapper.text()).toContain('Failed')
  })

  it('shows links to imported articles', async () => {
    const mockResult = {
      successes: [
        { id: 'abc-123', title: 'Good Article', slug: 'good-article' },
      ],
      errors: [],
      total: 1,
    }
    vi.mocked(importMarkdownFiles).mockResolvedValue(mockResult)

    const wrapper = mount(AdminImportView, { global: { components: { RouterLink } } })

    const file = new File(['# Test'], 'test.md', { type: 'text/markdown' })
    Object.defineProperty(wrapper.find('input[type="file"]').element, 'files', {
      value: [file],
    })
    await wrapper.find('input[type="file"]').trigger('change')
    await flushPromises()

    const link = wrapper.find('a[href="/admin/articles/abc-123/edit"]')
    expect(link.exists()).toBe(true)
    expect(link.text()).toContain('Good Article')
  })

  it('shows collapsible error list with filename and reason', async () => {
    const mockResult = {
      successes: [],
      errors: [
        { filename: 'bad.md', error: 'Invalid frontmatter' },
        { filename: 'empty.md', error: 'No content found' },
      ],
      total: 2,
    }
    vi.mocked(importMarkdownFiles).mockResolvedValue(mockResult)

    const wrapper = mount(AdminImportView, { global: { components: { RouterLink } } })

    const file = new File(['# Test'], 'test.md', { type: 'text/markdown' })
    Object.defineProperty(wrapper.find('input[type="file"]').element, 'files', {
      value: [file],
    })
    await wrapper.find('input[type="file"]').trigger('change')
    await flushPromises()

    // Click to expand errors
    const expandBtn = wrapper.findAll('button').find(btn => btn.text().includes('Failed imports'))
    await expandBtn?.trigger('click')
    await flushPromises()

    expect(wrapper.text()).toContain('bad.md')
    expect(wrapper.text()).toContain('Invalid frontmatter')
    expect(wrapper.text()).toContain('empty.md')
    expect(wrapper.text()).toContain('No content found')
  })

  it('shows Back to Articles link', async () => {
    const mockResult = {
      successes: [],
      errors: [],
      total: 0,
    }
    vi.mocked(importMarkdownFiles).mockResolvedValue(mockResult)

    const wrapper = mount(AdminImportView, { global: { components: { RouterLink } } })

    const file = new File(['# Test'], 'test.md', { type: 'text/markdown' })
    Object.defineProperty(wrapper.find('input[type="file"]').element, 'files', {
      value: [file],
    })
    await wrapper.find('input[type="file"]').trigger('change')
    await flushPromises()

    const backLink = wrapper.find('a[href="/admin"]')
    expect(backLink.exists()).toBe(true)
    expect(backLink.text()).toContain('Back to Articles')
  })

  it('shows error message on import failure', async () => {
    vi.mocked(importMarkdownFiles).mockRejectedValue(new Error('Network error'))

    const wrapper = mount(AdminImportView, { global: { components: { RouterLink } } })

    const file = new File(['# Test'], 'test.md', { type: 'text/markdown' })
    Object.defineProperty(wrapper.find('input[type="file"]').element, 'files', {
      value: [file],
    })
    await wrapper.find('input[type="file"]').trigger('change')
    await flushPromises()

    expect(wrapper.text()).toContain('Network error')
  })
})
