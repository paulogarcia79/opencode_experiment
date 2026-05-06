const API_BASE = import.meta.env.VITE_API_BASE_URL || ''

export async function fetchArticles() {
  const res = await fetch(`${API_BASE}/api/articles`)
  if (!res.ok) throw new Error('Failed to fetch articles')
  return res.json()
}

export async function fetchArticle(slug: string) {
  const res = await fetch(`${API_BASE}/api/articles/${slug}`)
  if (!res.ok) throw new Error('Article not found')
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
