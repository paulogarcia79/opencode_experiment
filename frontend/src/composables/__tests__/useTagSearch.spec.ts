import { describe, it, expect, vi, beforeEach } from 'vitest'
import { useTagSearch } from '@/composables/useTagSearch'

describe('useTagSearch', () => {
  beforeEach(() => {
    vi.restoreAllMocks()
  })

  it('returns empty suggestions for empty query', async () => {
    const { suggestions, fetchSuggestions } = useTagSearch()

    await fetchSuggestions('')

    expect(suggestions.value).toEqual([])
  })

  it('fetches and returns tag suggestions', async () => {
    const mockTags = [
      { name: 'Vue', slug: 'vue' },
      { name: 'Vue 3', slug: 'vue-3' },
    ]
    vi.spyOn(globalThis, 'fetch').mockResolvedValue(
      new Response(JSON.stringify(mockTags), { status: 200 })
    )

    const { suggestions, fetchSuggestions } = useTagSearch()

    await fetchSuggestions('vue')

    expect(suggestions.value).toEqual(mockTags)
    expect(globalThis.fetch).toHaveBeenCalledWith(
      '/api/admin/tags?q=vue',
      expect.objectContaining({ headers: expect.any(Object) })
    )
  })

  it('sets loading to true during fetch', async () => {
    vi.spyOn(globalThis, 'fetch').mockImplementation(
      () => new Promise((resolve) => setTimeout(() => resolve(new Response('[]', { status: 200 })), 10))
    )

    const { suggestions, loading, fetchSuggestions } = useTagSearch()

    const promise = fetchSuggestions('test')
    expect(loading.value).toBe(true)

    await promise
    expect(loading.value).toBe(false)
  })

  it('resets suggestions to empty on fetch error', async () => {
    vi.spyOn(globalThis, 'fetch').mockRejectedValue(new Error('Network error'))

    const { suggestions, fetchSuggestions } = useTagSearch()

    await fetchSuggestions('test')

    expect(suggestions.value).toEqual([])
  })

  it('resets suggestions to empty on non-ok response', async () => {
    vi.spyOn(globalThis, 'fetch').mockResolvedValue(
      new Response('Not Found', { status: 404 })
    )

    const { suggestions, fetchSuggestions } = useTagSearch()

    await fetchSuggestions('test')

    expect(suggestions.value).toEqual([])
  })

  it('handles non-array response gracefully', async () => {
    vi.spyOn(globalThis, 'fetch').mockResolvedValue(
      new Response(JSON.stringify({ error: 'not an array' }), { status: 200 })
    )

    const { suggestions, fetchSuggestions } = useTagSearch()

    await fetchSuggestions('test')

    expect(suggestions.value).toEqual([])
  })
})
