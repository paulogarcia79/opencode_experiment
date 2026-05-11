import { useAdminStore } from '@/stores/admin'

const API_BASE = import.meta.env.VITE_API_BASE_URL || ''

export function getAuthHeaders(): Record<string, string> {
  const store = useAdminStore()
  return store.token ? { Authorization: `Bearer ${store.token}` } : {}
}

export async function login(email: string, password: string) {
  const res = await fetch(`${API_BASE}/api/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password }),
  })
  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}))
    throw new Error(errorData.detail || 'Login failed')
  }
  return res.json()
}

export async function fetchAnalytics(range: string = '30d') {
  const res = await fetch(`${API_BASE}/api/admin/analytics?range=${range}`, {
    headers: getAuthHeaders(),
  })
  if (!res.ok) throw new Error('Failed to fetch analytics')
  return res.json()
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

export async function fetchAdminImages() {
  const res = await fetch(`${API_BASE}/api/admin/images`, { headers: getAuthHeaders() })
  if (!res.ok) throw new Error('Failed to fetch images')
  return res.json()
}

export async function deleteImage(id: string) {
  const res = await fetch(`${API_BASE}/api/admin/images/${id}`, {
    method: 'DELETE',
    headers: getAuthHeaders(),
  })
  if (!res.ok) throw new Error('Failed to delete image')
}

export async function sendPreviewEmail(id: string) {
  const res = await fetch(`${API_BASE}/api/admin/articles/${id}/preview-email`, {
    method: 'POST',
    headers: getAuthHeaders(),
  })
  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}))
    throw new Error(errorData.detail || 'Failed to send preview email')
  }
  return res.json()
}

export async function forgotPassword(email: string) {
  const res = await fetch(`${API_BASE}/api/auth/forgot-password`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email }),
  })
  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}))
    throw new Error(errorData.detail || 'Failed to send reset link')
  }
  return res.json()
}

export async function resetPassword(token: string, newPassword: string) {
  const res = await fetch(`${API_BASE}/api/auth/reset-password`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ token, new_password: newPassword }),
  })
  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}))
    throw new Error(errorData.detail || 'Failed to reset password')
  }
  return res.json()
}

export interface RevisionListItem {
  version_number: number
  change_type: string
  title: string
  created_at: string
}

export interface Revision {
  version_number: number
  change_type: string
  title: string
  content: Record<string, unknown>
  description: string | null
  tag_names: string[]
  created_at: string
}

export async function fetchRevisions(articleId: string): Promise<RevisionListItem[]> {
  const res = await fetch(`${API_BASE}/api/admin/articles/${articleId}/revisions`, {
    headers: getAuthHeaders(),
  })
  if (!res.ok) throw new Error('Failed to fetch revisions')
  return res.json()
}

export async function fetchRevision(articleId: string, versionNumber: number): Promise<Revision> {
  const res = await fetch(`${API_BASE}/api/admin/articles/${articleId}/revisions/${versionNumber}`, {
    headers: getAuthHeaders(),
  })
  if (!res.ok) throw new Error('Failed to fetch revision')
  return res.json()
}

export async function restoreRevision(articleId: string, versionNumber: number) {
  const res = await fetch(`${API_BASE}/api/admin/articles/${articleId}/revisions/${versionNumber}/restore`, {
    method: 'POST',
    headers: getAuthHeaders(),
  })
  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}))
    throw new Error(errorData.detail || 'Failed to restore revision')
  }
  return res.json()
}
