const API_BASE = import.meta.env.VITE_API_BASE_URL || ''

export async function fetchArticles() {
  const res = await fetch(`${API_BASE}/api/articles`)
  if (!res.ok) throw new Error('Failed to fetch articles')
  return res.json()
}

export async function fetchArticle(slug: string) {
  const headers: Record<string, string> = {}
  try {
    const { useAdminStore } = await import('@/stores/admin')
    const store = useAdminStore()
    if (store.token) {
      headers.Authorization = `Bearer ${store.token}`
    }
  } catch {
    // store not available (e.g., SSR), proceed without auth
  }
  const res = await fetch(`${API_BASE}/api/articles/${slug}`, { headers })
  if (!res.ok) throw new Error('Article not found')
  return res.json()
}

export async function fetchArticlePreview(slug: string) {
  const headers: Record<string, string> = {}
  try {
    const { useAdminStore } = await import('@/stores/admin')
    const store = useAdminStore()
    if (store.token) {
      headers.Authorization = `Bearer ${store.token}`
    }
  } catch {
    // store not available
  }
  const res = await fetch(`${API_BASE}/api/admin/articles/preview/${slug}`, { headers })
  if (!res.ok) throw new Error('Preview not found or unauthorized')
  return res.json()
}

export async function subscribeToNewsletter(email: string) {
  const res = await fetch(`${API_BASE}/api/subscribers`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email }),
  })
  if (!res.ok) throw new Error('Subscription failed')
  return res.json()
}

export async function confirmSubscription(token: string) {
  const res = await fetch(`${API_BASE}/api/subscribers/confirm?token=${token}`)
  if (!res.ok) throw new Error('Confirmation failed')
  return res.json()
}

export async function unsubscribeFromNewsletter(token: string) {
  const res = await fetch(`${API_BASE}/api/subscribers/unsubscribe?token=${token}`)
  if (!res.ok) throw new Error('Unsubscribe failed')
  return res.json()
}
