import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import AdminTagsView from '@/views/AdminTagsView.vue'

describe('AdminTagsView', () => {
  beforeEach(() => {
    vi.stubGlobal('localStorage', {
      getItem: vi.fn().mockReturnValue('dev-token'),
    })
  })

  it('renders tags table with article counts', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue({
      ok: true,
      json: () => Promise.resolve([
        { id: '1', name: 'docker', slug: 'docker', article_count: 3, created_at: '2024-01-01T00:00:00Z' },
        { id: '2', name: 'vue', slug: 'vue', article_count: 1, created_at: '2024-02-01T00:00:00Z' },
      ]),
    }))

    const wrapper = mount(AdminTagsView)
    await flushPromises()

    expect(wrapper.text()).toContain('docker')
    expect(wrapper.text()).toContain('vue')
    expect(wrapper.text()).toContain('3')
    expect(wrapper.text()).toContain('1')
  })

  it('shows confirmation dialog when deleting a tag', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue({
      ok: true,
      json: () => Promise.resolve([
        { id: '1', name: 'docker', slug: 'docker', article_count: 3, created_at: '2024-01-01T00:00:00Z' },
      ]),
    }))

    const wrapper = mount(AdminTagsView)
    await flushPromises()

    const deleteBtn = wrapper.find('button[title="Delete"]')
    await deleteBtn.trigger('click')
    await flushPromises()

    expect(wrapper.text()).toContain('Delete Tag')
    expect(wrapper.text()).toContain('used by 3 articles')
  })

  it('deletes tag after confirming', async () => {
    vi.stubGlobal('fetch', vi.fn()
      .mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve([
          { id: '1', name: 'docker', slug: 'docker', article_count: 0, created_at: '2024-01-01T00:00:00Z' },
        ]),
      })
      .mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve([]),
      })
    )

    const wrapper = mount(AdminTagsView)
    await flushPromises()

    const deleteBtn = wrapper.find('button[title="Delete"]')
    await deleteBtn.trigger('click')
    await flushPromises()

    const confirmBtn = wrapper.findAll('button').find(btn => btn.text() === 'Delete')
    await confirmBtn?.trigger('click')
    await flushPromises()

    expect(wrapper.text()).not.toContain('docker')
  })
})
