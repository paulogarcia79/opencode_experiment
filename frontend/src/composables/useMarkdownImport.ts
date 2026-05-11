import { getAuthHeaders } from './useAdminApi'

const API_BASE = import.meta.env.VITE_API_BASE_URL || ''

export interface ImportSuccessItem {
  id: string
  title: string
  slug: string
}

export interface ImportErrorItem {
  filename: string
  error: string
}

export interface ImportResult {
  successes: ImportSuccessItem[]
  errors: ImportErrorItem[]
  total: number
}

export async function importMarkdownFiles(files: File[]): Promise<ImportResult> {
  const formData = new FormData()
  for (const file of files) {
    formData.append('files', file)
  }

  const res = await fetch(`${API_BASE}/api/admin/articles/import`, {
    method: 'POST',
    headers: getAuthHeaders(),
    body: formData,
  })

  if (!res.ok) {
    const error = await res.json().catch(() => ({ detail: 'Import failed' }))
    throw new Error(error.detail || 'Import failed')
  }

  return res.json()
}
