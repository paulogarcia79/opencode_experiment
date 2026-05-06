import { useAdminStore } from '@/stores/admin'

const API_BASE = import.meta.env.VITE_API_BASE_URL || ''

export function getAuthHeaders(): Record<string, string> {
  const store = useAdminStore()
  return store.token ? { Authorization: `Bearer ${store.token}` } : {}
}

export async function fetchAdminArticles() {
  const res = await fetch(`${API_BASE}/api/admin/articles`, { headers: getAuthHeaders() })
  if (!res.ok) throw new Error('Failed to fetch articles')
  return res.json()
}

export async function fetchAdminArticle(id: string) {
  const res = await fetch(`${API_BASE}/api/admin/articles/${id}`, { headers: getAuthHeaders() })
  if (!res.ok) throw new Error('Failed to fetch article')
  return res.json()
}

export async function createArticle(data: any) {
  const res = await fetch(`${API_BASE}/api/admin/articles`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', ...getAuthHeaders() },
    body: JSON.stringify(data),
  })
  if (!res.ok) throw new Error('Failed to create article')
  return res.json()
}

export async function updateArticle(id: string, data: any) {
  const res = await fetch(`${API_BASE}/api/articles/${id}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json', ...getAuthHeaders() },
    body: JSON.stringify(data),
  })
  if (!res.ok) throw new Error('Failed to update article')
  return res.json()
}

export async function deleteArticle(id: string) {
  const res = await fetch(`${API_BASE}/api/articles/${id}`, {
    method: 'DELETE',
    headers: getAuthHeaders(),
  })
  if (!res.ok) throw new Error('Failed to delete article')
}
