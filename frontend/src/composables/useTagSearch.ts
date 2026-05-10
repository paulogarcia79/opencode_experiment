import { ref } from 'vue'

const API_BASE = import.meta.env.VITE_API_BASE_URL || ''

export interface TagSuggestion {
  name: string
  slug: string
}

export function useTagSearch() {
  const suggestions = ref<TagSuggestion[]>([])
  const loading = ref(false)

  async function fetchSuggestions(query: string) {
    if (query.length < 1) {
      suggestions.value = []
      return
    }

    loading.value = true
    try {
      const res = await fetch(`${API_BASE}/api/admin/tags?q=${encodeURIComponent(query)}`, {
        headers: {
          Authorization: `Bearer ${localStorage.getItem('admin_token') || ''}`,
        },
      })
      if (res.ok) {
        const data = await res.json()
        suggestions.value = Array.isArray(data) ? data : []
      }
    } catch {
      suggestions.value = []
    } finally {
      loading.value = false
    }
  }

  return {
    suggestions,
    loading,
    fetchSuggestions,
  }
}
