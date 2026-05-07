import { getAuthHeaders } from './useAdminApi'

const API_BASE = import.meta.env.VITE_API_BASE_URL || ''

export interface UploadImageResult {
  id: string
  url: string
  original_name: string
  size_bytes: number
  mime_type: string
}

export async function uploadImage(file: File): Promise<UploadImageResult> {
  const formData = new FormData()
  formData.append('file', file)

  const res = await fetch(`${API_BASE}/api/admin/images`, {
    method: 'POST',
    headers: getAuthHeaders(),
    body: formData,
  })

  if (!res.ok) {
    const error = await res.json().catch(() => ({ detail: 'Upload failed' }))
    throw new Error(error.detail || 'Upload failed')
  }

  return res.json()
}
