import { ref, watch } from 'vue'

const API_BASE = import.meta.env.VITE_API_BASE_URL || ''

export interface SearchResult {
  id: string
  title: string
  slug: string
  description: string | null
  published_at: string
}

export function useSearch() {
  const query = ref('')
  const results = ref<SearchResult[]>([])
  const loading = ref(false)
  const error = ref('')
  const searched = ref(false)

  let debounceTimer: ReturnType<typeof setTimeout> | null = null

  async function doSearch() {
    const q = query.value.trim()
    if (q.length < 2) {
      results.value = []
      return
    }

    loading.value = true
    error.value = ''
    searched.value = true

    try {
      const res = await fetch(`${API_BASE}/api/articles/search?q=${encodeURIComponent(q)}`)
      if (!res.ok) {
        const data = await res.json().catch(() => ({ detail: 'Search failed' }))
        throw new Error(data.detail || 'Search failed')
      }
      results.value = await res.json()
    } catch (e: any) {
      error.value = e.message || 'Search failed'
      results.value = []
    } finally {
      loading.value = false
    }
  }

  function search() {
    if (debounceTimer) {
      clearTimeout(debounceTimer)
    }
    debounceTimer = setTimeout(() => {
      doSearch()
    }, 300)
  }

  // Watch for query changes and auto-search
  watch(query, () => {
    search()
  })

  return {
    query,
    results,
    loading,
    error,
    searched,
    search,
  }
}
