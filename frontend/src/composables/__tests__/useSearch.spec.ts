import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { flushPromises } from '@vue/test-utils'
import { useSearch } from '@/composables/useSearch'

describe('useSearch', () => {
  beforeEach(() => {
    vi.useFakeTimers()
    vi.stubGlobal('fetch', vi.fn())
  })

  afterEach(() => {
    vi.useRealTimers()
    vi.unstubAllGlobals()
  })

  it('debounces fetch by 300ms', async () => {
    const mockFetch = vi.fn().mockResolvedValue({
      ok: true,
      json: () => Promise.resolve([]),
    })
    vi.stubGlobal('fetch', mockFetch)

    const { query, search } = useSearch()
    query.value = 'docker'
    search()

    // Immediately after search, fetch should not have been called
    expect(mockFetch).not.toHaveBeenCalled()

    // Advance by 299ms — still not called
    vi.advanceTimersByTime(299)
    expect(mockFetch).not.toHaveBeenCalled()

    // Advance by 1 more ms — now called
    vi.advanceTimersByTime(1)
    expect(mockFetch).toHaveBeenCalledTimes(1)
    expect(mockFetch).toHaveBeenCalledWith(
      expect.stringContaining('/api/articles/search?q=docker')
    )
  })

  it('returns results after fetch', async () => {
    const mockResults = [
      { id: '1', title: 'Docker Guide', slug: 'docker-guide', description: 'Intro', published_at: '2024-01-01' },
    ]
    const mockFetch = vi.fn().mockResolvedValue({
      ok: true,
      json: () => Promise.resolve(mockResults),
    })
    vi.stubGlobal('fetch', mockFetch)

    const { query, search, results } = useSearch()
    query.value = 'docker'
    search()

    vi.advanceTimersByTime(300)
    await flushPromises()

    expect(results.value).toEqual(mockResults)
  })

  it('shows loading state during fetch', async () => {
    let resolveJson: (value: unknown) => void
    const jsonPromise = new Promise((resolve) => {
      resolveJson = resolve
    })
    const mockFetch = vi.fn().mockResolvedValue({
      ok: true,
      json: () => jsonPromise,
    })
    vi.stubGlobal('fetch', mockFetch)

    const { query, search, loading } = useSearch()
    query.value = 'docker'
    search()

    vi.advanceTimersByTime(300)
    expect(loading.value).toBe(true)

    resolveJson!([{ id: '1', title: 'T', slug: 't', description: null, published_at: '' }])
    await flushPromises()

    expect(loading.value).toBe(false)
  })

  it('shows error state on fetch failure', async () => {
    const mockFetch = vi.fn().mockResolvedValue({
      ok: false,
      json: () => Promise.resolve({ detail: 'Server error' }),
    })
    vi.stubGlobal('fetch', mockFetch)

    const { query, search, error, results } = useSearch()
    query.value = 'docker'
    search()

    vi.advanceTimersByTime(300)
    await flushPromises()

    expect(error.value).toBe('Server error')
    expect(results.value).toEqual([])
  })
})
