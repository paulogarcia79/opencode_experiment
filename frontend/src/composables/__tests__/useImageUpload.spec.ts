import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { createPinia, setActivePinia } from 'pinia'
import { useAdminStore } from '@/stores/admin'
import { uploadImage } from '@/composables/useImageUpload'

describe('useImageUpload', () => {
  beforeEach(() => {
    // Mock localStorage
    const localStorageMock = {
      getItem: vi.fn(),
      setItem: vi.fn(),
      removeItem: vi.fn(),
    }
    vi.stubGlobal('localStorage', localStorageMock)

    setActivePinia(createPinia())
    vi.stubGlobal('fetch', vi.fn())
  })

  afterEach(() => {
    vi.unstubAllGlobals()
  })

  it('uploads an image successfully', async () => {
    const mockResponse = {
      id: 'test-id',
      url: '/uploads/test.png',
      original_name: 'test.png',
      size_bytes: 1234,
      mime_type: 'image/png',
    }

    const mockFetch = vi.fn().mockResolvedValue({
      ok: true,
      json: () => Promise.resolve(mockResponse),
    })
    vi.stubGlobal('fetch', mockFetch)

    const store = useAdminStore()
    store.token = 'test-token'

    const file = new File(['test'], 'test.png', { type: 'image/png' })
    const result = await uploadImage(file)

    expect(result).toEqual(mockResponse)
    expect(mockFetch).toHaveBeenCalledWith(
      expect.stringContaining('/api/admin/images'),
      expect.objectContaining({
        method: 'POST',
        headers: expect.objectContaining({
          Authorization: 'Bearer test-token',
        }),
        body: expect.any(FormData),
      })
    )
  })

  it('throws error on upload failure', async () => {
    const mockFetch = vi.fn().mockResolvedValue({
      ok: false,
      json: () => Promise.resolve({ detail: 'Invalid file type' }),
    })
    vi.stubGlobal('fetch', mockFetch)

    const store = useAdminStore()
    store.token = 'test-token'

    const file = new File(['test'], 'test.txt', { type: 'text/plain' })
    await expect(uploadImage(file)).rejects.toThrow('Invalid file type')
  })

  it('throws generic error when response json fails', async () => {
    const mockFetch = vi.fn().mockResolvedValue({
      ok: false,
      json: () => Promise.reject(new Error('Invalid JSON')),
    })
    vi.stubGlobal('fetch', mockFetch)

    const store = useAdminStore()
    store.token = 'test-token'

    const file = new File(['test'], 'test.png', { type: 'image/png' })
    await expect(uploadImage(file)).rejects.toThrow('Upload failed')
  })
})
