import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import AdminMediaView from '@/views/AdminMediaView.vue'

// Mock the API composables
vi.mock('@/composables/useAdminApi', () => ({
  fetchAdminImages: vi.fn(),
  deleteImage: vi.fn(),
}))

vi.mock('@/composables/useImageUpload', () => ({
  uploadImage: vi.fn(),
}))

import { fetchAdminImages, deleteImage } from '@/composables/useAdminApi'

describe('AdminMediaView', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
  })

  it('renders loading state initially', () => {
    vi.mocked(fetchAdminImages).mockImplementation(() => new Promise(() => {}))
    
    const wrapper = mount(AdminMediaView)
    expect(wrapper.text()).toContain('Loading images...')
  })

  it('renders image grid after loading', async () => {
    const mockImages = [
      {
        id: '1',
        url: '/uploads/test1.png',
        original_name: 'test1.png',
        size_bytes: 1024,
        mime_type: 'image/png',
        created_at: '2025-01-01T00:00:00Z',
      },
      {
        id: '2',
        url: '/uploads/test2.png',
        original_name: 'test2.png',
        size_bytes: 2048,
        mime_type: 'image/png',
        created_at: '2025-01-02T00:00:00Z',
      },
    ]
    vi.mocked(fetchAdminImages).mockResolvedValue(mockImages)

    const wrapper = mount(AdminMediaView)
    await flushPromises()

    expect(wrapper.findAll('img').length).toBe(2)
    expect(wrapper.text()).toContain('test1.png')
    expect(wrapper.text()).toContain('test2.png')
    expect(wrapper.text()).toContain('1.0 KB')
    expect(wrapper.text()).toContain('2.0 KB')
  })

  it('shows empty state when no images', async () => {
    vi.mocked(fetchAdminImages).mockResolvedValue([])

    const wrapper = mount(AdminMediaView)
    await flushPromises()

    expect(wrapper.text()).toContain('No images yet')
  })

  it('shows error state on fetch failure', async () => {
    vi.mocked(fetchAdminImages).mockRejectedValue(new Error('Network error'))

    const wrapper = mount(AdminMediaView)
    await flushPromises()

    expect(wrapper.text()).toContain('Failed to load images')
    expect(wrapper.text()).toContain('Network error')
  })

  it('opens delete confirmation dialog', async () => {
    const mockImages = [
      {
        id: '1',
        url: '/uploads/test1.png',
        original_name: 'test1.png',
        size_bytes: 1024,
        mime_type: 'image/png',
        created_at: '2025-01-01T00:00:00Z',
      },
    ]
    vi.mocked(fetchAdminImages).mockResolvedValue(mockImages)

    const wrapper = mount(AdminMediaView)
    await flushPromises()

    // Click delete button
    const deleteBtn = wrapper.find('button[title="Delete"]')
    await deleteBtn.trigger('click')
    await flushPromises()

    expect(wrapper.text()).toContain('Delete Image')
    expect(wrapper.text()).toContain('test1.png')
    expect(wrapper.text()).toContain('This action cannot be undone')
  })

  it('calls deleteImage when confirming deletion', async () => {
    const mockImages = [
      {
        id: '1',
        url: '/uploads/test1.png',
        original_name: 'test1.png',
        size_bytes: 1024,
        mime_type: 'image/png',
        created_at: '2025-01-01T00:00:00Z',
      },
    ]
    vi.mocked(fetchAdminImages).mockResolvedValue(mockImages)
    vi.mocked(deleteImage).mockResolvedValue(undefined)

    const wrapper = mount(AdminMediaView)
    await flushPromises()

    // Open delete dialog
    const deleteBtn = wrapper.find('button[title="Delete"]')
    await deleteBtn.trigger('click')
    await flushPromises()

    // Click confirm delete
    const confirmBtn = wrapper.findAll('button').find(btn => btn.text() === 'Delete')
    await confirmBtn?.trigger('click')
    await flushPromises()

    expect(deleteImage).toHaveBeenCalledWith('1')
  })
})
