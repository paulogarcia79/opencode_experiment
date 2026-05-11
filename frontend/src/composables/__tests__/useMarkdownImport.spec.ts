import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { createPinia, setActivePinia } from 'pinia'
import { useAdminStore } from '@/stores/admin'
import { importMarkdownFiles } from '@/composables/useMarkdownImport'

describe('useMarkdownImport', () => {
  beforeEach(() => {
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

  it('imports markdown files successfully', async () => {
    const mockResponse = {
      successes: [
        { id: 'abc-123', title: 'Test Article', slug: 'test-article' },
      ],
      errors: [],
      total: 1,
    }

    const mockFetch = vi.fn().mockResolvedValue({
      ok: true,
      json: () => Promise.resolve(mockResponse),
    })
    vi.stubGlobal('fetch', mockFetch)

    const store = useAdminStore()
    store.token = 'test-token'

    const file = new File(['# Test'], 'test.md', { type: 'text/markdown' })
    const result = await importMarkdownFiles([file])

    expect(result).toEqual(mockResponse)
    expect(mockFetch).toHaveBeenCalledWith(
      expect.stringContaining('/api/admin/articles/import'),
      expect.objectContaining({
        method: 'POST',
        headers: expect.objectContaining({
          Authorization: 'Bearer test-token',
        }),
        body: expect.any(FormData),
      })
    )
  })

  it('handles partial failures', async () => {
    const mockResponse = {
      successes: [
        { id: 'abc-123', title: 'Good Article', slug: 'good-article' },
      ],
      errors: [
        { filename: 'bad.md', error: 'Invalid frontmatter' },
      ],
      total: 2,
    }

    const mockFetch = vi.fn().mockResolvedValue({
      ok: true,
      json: () => Promise.resolve(mockResponse),
    })
    vi.stubGlobal('fetch', mockFetch)

    const store = useAdminStore()
    store.token = 'test-token'

    const files = [
      new File(['# Good'], 'good.md', { type: 'text/markdown' }),
      new File(['bad content'], 'bad.md', { type: 'text/markdown' }),
    ]
    const result = await importMarkdownFiles(files)

    expect(result.successes).toHaveLength(1)
    expect(result.errors).toHaveLength(1)
    expect(result.errors[0].filename).toBe('bad.md')
  })

  it('throws error on API failure', async () => {
    const mockFetch = vi.fn().mockResolvedValue({
      ok: false,
      json: () => Promise.resolve({ detail: 'Unauthorized' }),
    })
    vi.stubGlobal('fetch', mockFetch)

    const store = useAdminStore()
    store.token = 'test-token'

    const file = new File(['# Test'], 'test.md', { type: 'text/markdown' })
    await expect(importMarkdownFiles([file])).rejects.toThrow('Unauthorized')
  })

  it('throws generic error when response json fails', async () => {
    const mockFetch = vi.fn().mockResolvedValue({
      ok: false,
      json: () => Promise.reject(new Error('Invalid JSON')),
    })
    vi.stubGlobal('fetch', mockFetch)

    const store = useAdminStore()
    store.token = 'test-token'

    const file = new File(['# Test'], 'test.md', { type: 'text/markdown' })
    await expect(importMarkdownFiles([file])).rejects.toThrow('Import failed')
  })
})
