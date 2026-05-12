import { describe, it, expect, beforeEach, vi } from 'vitest'
import { createPinia, setActivePinia } from 'pinia'
import {
  getAuthHeaders,
  login,
  fetchAdminArticles,
  fetchAdminArticle,
  createArticle,
  updateArticle,
  deleteArticle,
  fetchAdminImages,
  deleteImage,
  sendPreviewEmail,
  fetchRevisions,
  fetchRevision,
  restoreRevision,
  fetchUsers,
  inviteUser,
  updateUserRole,
  toggleUserActive,
} from '@/composables/useAdminApi'
import { useAdminStore } from '@/stores/admin'

describe('login', () => {
  beforeEach(() => {
    localStorage.clear()
    setActivePinia(createPinia())
  })

  it('posts to login endpoint with email and password on success', async () => {
    const mockData = { token: 'jwt-token', type: 'bearer' }
    const fetchSpy = vi.spyOn(globalThis, 'fetch').mockResolvedValue(
      new Response(JSON.stringify(mockData), { status: 200 })
    )

    const result = await login('admin@example.com', 'password')

    expect(result).toEqual(mockData)
    expect(fetchSpy).toHaveBeenCalledWith(
      '/api/auth/login',
      expect.objectContaining({
        method: 'POST',
        headers: expect.objectContaining({ 'Content-Type': 'application/json' }),
        body: JSON.stringify({ email: 'admin@example.com', password: 'password' }),
      })
    )
    fetchSpy.mockRestore()
  })

  it('throws extracted error detail on error response', async () => {
    vi.spyOn(globalThis, 'fetch').mockResolvedValue(
      new Response(JSON.stringify({ detail: 'Incorrect email or password' }), { status: 401 })
    )

    await expect(login('wrong@example.com', 'pass')).rejects.toThrow('Incorrect email or password')
    vi.restoreAllMocks()
  })
})

describe('getAuthHeaders', () => {
  beforeEach(() => {
    localStorage.clear()
    setActivePinia(createPinia())
  })

  it('returns empty object when no token', () => {
    expect(getAuthHeaders()).toEqual({})
  })

  it('returns Authorization header when token exists', () => {
    const store = useAdminStore()
    store.setToken('test-token')
    expect(getAuthHeaders()).toEqual({ Authorization: 'Bearer test-token' })
  })
})

describe('fetchAdminArticles', () => {
  beforeEach(() => {
    localStorage.clear()
    setActivePinia(createPinia())
  })

  it('fetches articles with auth headers on success', async () => {
    const mockData = [{ id: '1', title: 'Test' }]
    const fetchSpy = vi.spyOn(globalThis, 'fetch').mockResolvedValue(
      new Response(JSON.stringify(mockData), { status: 200 })
    )

    const result = await fetchAdminArticles()

    expect(result).toEqual(mockData)
    expect(fetchSpy).toHaveBeenCalledWith(
      '/api/admin/articles',
      expect.objectContaining({ headers: expect.any(Object) })
    )
    fetchSpy.mockRestore()
  })

  it('throws on error response', async () => {
    vi.spyOn(globalThis, 'fetch').mockResolvedValue(
      new Response('Not Found', { status: 404 })
    )

    await expect(fetchAdminArticles()).rejects.toThrow('Failed to fetch articles')
    vi.restoreAllMocks()
  })
})

describe('fetchAdminArticle', () => {
  beforeEach(() => {
    localStorage.clear()
    setActivePinia(createPinia())
  })

  it('fetches single article on success', async () => {
    const mockData = { id: '1', title: 'Test Article' }
    const fetchSpy = vi.spyOn(globalThis, 'fetch').mockResolvedValue(
      new Response(JSON.stringify(mockData), { status: 200 })
    )

    const result = await fetchAdminArticle('1')

    expect(result).toEqual(mockData)
    expect(fetchSpy).toHaveBeenCalledWith(
      '/api/admin/articles/1',
      expect.objectContaining({ headers: expect.any(Object) })
    )
    fetchSpy.mockRestore()
  })

  it('throws on error response', async () => {
    vi.spyOn(globalThis, 'fetch').mockResolvedValue(
      new Response('Not Found', { status: 404 })
    )

    await expect(fetchAdminArticle('1')).rejects.toThrow('Failed to fetch article')
    vi.restoreAllMocks()
  })
})

describe('createArticle', () => {
  beforeEach(() => {
    localStorage.clear()
    setActivePinia(createPinia())
  })

  it('creates article with POST on success', async () => {
    const mockData = { id: '1', title: 'New Article' }
    const fetchSpy = vi.spyOn(globalThis, 'fetch').mockResolvedValue(
      new Response(JSON.stringify(mockData), { status: 201 })
    )

    const result = await createArticle({ title: 'New Article', content: {} })

    expect(result).toEqual(mockData)
    expect(fetchSpy).toHaveBeenCalledWith(
      '/api/admin/articles',
      expect.objectContaining({
        method: 'POST',
        headers: expect.objectContaining({ 'Content-Type': 'application/json' }),
        body: JSON.stringify({ title: 'New Article', content: {} }),
      })
    )
    fetchSpy.mockRestore()
  })

  it('throws on error response', async () => {
    vi.spyOn(globalThis, 'fetch').mockResolvedValue(
      new Response('Bad Request', { status: 400 })
    )

    await expect(createArticle({ title: '' })).rejects.toThrow('Failed to create article')
    vi.restoreAllMocks()
  })
})

describe('updateArticle', () => {
  beforeEach(() => {
    localStorage.clear()
    setActivePinia(createPinia())
  })

  it('updates article with PUT on success', async () => {
    const mockData = { id: '1', title: 'Updated' }
    const fetchSpy = vi.spyOn(globalThis, 'fetch').mockResolvedValue(
      new Response(JSON.stringify(mockData), { status: 200 })
    )

    const result = await updateArticle('1', { title: 'Updated' })

    expect(result).toEqual(mockData)
    expect(fetchSpy).toHaveBeenCalledWith(
      '/api/articles/1',
      expect.objectContaining({
        method: 'PUT',
        body: JSON.stringify({ title: 'Updated' }),
      })
    )
    fetchSpy.mockRestore()
  })

  it('throws on error response', async () => {
    vi.spyOn(globalThis, 'fetch').mockResolvedValue(
      new Response('Not Found', { status: 404 })
    )

    await expect(updateArticle('1', { title: 'Updated' })).rejects.toThrow('Failed to update article')
    vi.restoreAllMocks()
  })
})

describe('deleteArticle', () => {
  beforeEach(() => {
    localStorage.clear()
    setActivePinia(createPinia())
  })

  it('deletes article with DELETE on success', async () => {
    const fetchSpy = vi.spyOn(globalThis, 'fetch').mockResolvedValue(
      new Response(null, { status: 204 })
    )

    await deleteArticle('1')

    expect(fetchSpy).toHaveBeenCalledWith(
      '/api/articles/1',
      expect.objectContaining({ method: 'DELETE' })
    )
    fetchSpy.mockRestore()
  })

  it('throws on error response', async () => {
    vi.spyOn(globalThis, 'fetch').mockResolvedValue(
      new Response('Not Found', { status: 404 })
    )

    await expect(deleteArticle('1')).rejects.toThrow('Failed to delete article')
    vi.restoreAllMocks()
  })
})

describe('fetchAdminImages', () => {
  beforeEach(() => {
    localStorage.clear()
    setActivePinia(createPinia())
  })

  it('fetches images with auth headers on success', async () => {
    const mockData = [{ id: '1', url: '/uploads/test.png' }]
    const fetchSpy = vi.spyOn(globalThis, 'fetch').mockResolvedValue(
      new Response(JSON.stringify(mockData), { status: 200 })
    )

    const result = await fetchAdminImages()

    expect(result).toEqual(mockData)
    expect(fetchSpy).toHaveBeenCalledWith(
      '/api/admin/images',
      expect.objectContaining({ headers: expect.any(Object) })
    )
    fetchSpy.mockRestore()
  })

  it('throws on error response', async () => {
    vi.spyOn(globalThis, 'fetch').mockResolvedValue(
      new Response('Not Found', { status: 404 })
    )

    await expect(fetchAdminImages()).rejects.toThrow('Failed to fetch images')
    vi.restoreAllMocks()
  })
})

describe('deleteImage', () => {
  beforeEach(() => {
    localStorage.clear()
    setActivePinia(createPinia())
  })

  it('deletes image with DELETE on success', async () => {
    const fetchSpy = vi.spyOn(globalThis, 'fetch').mockResolvedValue(
      new Response(null, { status: 204 })
    )

    await deleteImage('1')

    expect(fetchSpy).toHaveBeenCalledWith(
      '/api/admin/images/1',
      expect.objectContaining({ method: 'DELETE' })
    )
    fetchSpy.mockRestore()
  })

  it('throws on error response', async () => {
    vi.spyOn(globalThis, 'fetch').mockResolvedValue(
      new Response('Not Found', { status: 404 })
    )

    await expect(deleteImage('1')).rejects.toThrow('Failed to delete image')
    vi.restoreAllMocks()
  })
})

describe('sendPreviewEmail', () => {
  beforeEach(() => {
    localStorage.clear()
    setActivePinia(createPinia())
  })

  it('posts to preview-email endpoint on success', async () => {
    const mockData = { message: 'Preview sent successfully' }
    const fetchSpy = vi.spyOn(globalThis, 'fetch').mockResolvedValue(
      new Response(JSON.stringify(mockData), { status: 200 })
    )

    const result = await sendPreviewEmail('1')

    expect(result).toEqual(mockData)
    expect(fetchSpy).toHaveBeenCalledWith(
      '/api/admin/articles/1/preview-email',
      expect.objectContaining({
        method: 'POST',
        headers: expect.any(Object),
      })
    )
    fetchSpy.mockRestore()
  })

  it('throws extracted error detail on error response', async () => {
    vi.spyOn(globalThis, 'fetch').mockResolvedValue(
      new Response(JSON.stringify({ detail: 'Article not found' }), { status: 404 })
    )

    await expect(sendPreviewEmail('1')).rejects.toThrow('Article not found')
    vi.restoreAllMocks()
  })
})

describe('fetchRevisions', () => {
  beforeEach(() => {
    localStorage.clear()
    setActivePinia(createPinia())
  })

  it('fetches revisions with auth headers on success', async () => {
    const mockData = [{ version_number: 1, change_type: 'save', title: 'V1', created_at: '2025-01-15T09:00:00' }]
    const fetchSpy = vi.spyOn(globalThis, 'fetch').mockResolvedValue(
      new Response(JSON.stringify(mockData), { status: 200 })
    )

    const result = await fetchRevisions('1')

    expect(result).toEqual(mockData)
    expect(fetchSpy).toHaveBeenCalledWith(
      '/api/admin/articles/1/revisions',
      expect.objectContaining({ headers: expect.any(Object) })
    )
    fetchSpy.mockRestore()
  })

  it('throws on error response', async () => {
    vi.spyOn(globalThis, 'fetch').mockResolvedValue(
      new Response('Not Found', { status: 404 })
    )

    await expect(fetchRevisions('1')).rejects.toThrow('Failed to fetch revisions')
    vi.restoreAllMocks()
  })
})

describe('fetchRevision', () => {
  beforeEach(() => {
    localStorage.clear()
    setActivePinia(createPinia())
  })

  it('fetches single revision on success', async () => {
    const mockData = { version_number: 1, change_type: 'save', title: 'V1', content: {}, description: null, tag_names: [], created_at: '2025-01-15T09:00:00' }
    const fetchSpy = vi.spyOn(globalThis, 'fetch').mockResolvedValue(
      new Response(JSON.stringify(mockData), { status: 200 })
    )

    const result = await fetchRevision('1', 1)

    expect(result).toEqual(mockData)
    expect(fetchSpy).toHaveBeenCalledWith(
      '/api/admin/articles/1/revisions/1',
      expect.objectContaining({ headers: expect.any(Object) })
    )
    fetchSpy.mockRestore()
  })

  it('throws on error response', async () => {
    vi.spyOn(globalThis, 'fetch').mockResolvedValue(
      new Response('Not Found', { status: 404 })
    )

    await expect(fetchRevision('1', 1)).rejects.toThrow('Failed to fetch revision')
    vi.restoreAllMocks()
  })
})

describe('restoreRevision', () => {
  beforeEach(() => {
    localStorage.clear()
    setActivePinia(createPinia())
  })

  it('restores revision with POST on success', async () => {
    const mockData = { id: '1', title: 'Restored' }
    const fetchSpy = vi.spyOn(globalThis, 'fetch').mockResolvedValue(
      new Response(JSON.stringify(mockData), { status: 200 })
    )

    const result = await restoreRevision('1', 1)

    expect(result).toEqual(mockData)
    expect(fetchSpy).toHaveBeenCalledWith(
      '/api/admin/articles/1/revisions/1/restore',
      expect.objectContaining({ method: 'POST', headers: expect.any(Object) })
    )
    fetchSpy.mockRestore()
  })

  it('throws extracted error detail on error response', async () => {
    vi.spyOn(globalThis, 'fetch').mockResolvedValue(
      new Response(JSON.stringify({ detail: 'Revision not found' }), { status: 404 })
    )

    await expect(restoreRevision('1', 999)).rejects.toThrow('Revision not found')
    vi.restoreAllMocks()
  })
})

describe('fetchUsers', () => {
  beforeEach(() => {
    localStorage.clear()
    setActivePinia(createPinia())
  })

  it('fetches users with auth headers on success', async () => {
    const mockData = [
      { id: '1', email: 'admin@example.com', role: 'admin', is_active: true, is_verified: true, created_at: '2025-01-15T00:00:00Z' },
    ]
    const fetchSpy = vi.spyOn(globalThis, 'fetch').mockResolvedValue(
      new Response(JSON.stringify(mockData), { status: 200 })
    )

    const result = await fetchUsers()

    expect(result).toEqual(mockData)
    expect(fetchSpy).toHaveBeenCalledWith(
      '/api/admin/users',
      expect.objectContaining({ headers: expect.any(Object) })
    )
    fetchSpy.mockRestore()
  })

  it('throws on error response', async () => {
    vi.spyOn(globalThis, 'fetch').mockResolvedValue(
      new Response('Not Found', { status: 404 })
    )

    await expect(fetchUsers()).rejects.toThrow('Failed to fetch users')
    vi.restoreAllMocks()
  })
})

describe('inviteUser', () => {
  beforeEach(() => {
    localStorage.clear()
    setActivePinia(createPinia())
  })

  it('sends invite with POST on success', async () => {
    const mockData = { message: 'Invite sent to user@example.com' }
    const fetchSpy = vi.spyOn(globalThis, 'fetch').mockResolvedValue(
      new Response(JSON.stringify(mockData), { status: 200 })
    )

    const result = await inviteUser('user@example.com', 'editor')

    expect(result).toEqual(mockData)
    expect(fetchSpy).toHaveBeenCalledWith(
      '/api/admin/users/invite',
      expect.objectContaining({
        method: 'POST',
        headers: expect.objectContaining({ 'Content-Type': 'application/json' }),
        body: JSON.stringify({ email: 'user@example.com', role: 'editor' }),
      })
    )
    fetchSpy.mockRestore()
  })

  it('throws extracted error detail on error response', async () => {
    vi.spyOn(globalThis, 'fetch').mockResolvedValue(
      new Response(JSON.stringify({ detail: 'User already exists' }), { status: 400 })
    )

    await expect(inviteUser('existing@example.com', 'editor')).rejects.toThrow('User already exists')
    vi.restoreAllMocks()
  })
})

describe('updateUserRole', () => {
  beforeEach(() => {
    localStorage.clear()
    setActivePinia(createPinia())
  })

  it('updates role with PUT on success', async () => {
    const mockData = { message: 'Role updated to admin' }
    const fetchSpy = vi.spyOn(globalThis, 'fetch').mockResolvedValue(
      new Response(JSON.stringify(mockData), { status: 200 })
    )

    const result = await updateUserRole('user-1', 'admin')

    expect(result).toEqual(mockData)
    expect(fetchSpy).toHaveBeenCalledWith(
      '/api/admin/users/user-1/role',
      expect.objectContaining({
        method: 'PUT',
        headers: expect.objectContaining({ 'Content-Type': 'application/json' }),
        body: JSON.stringify({ role: 'admin' }),
      })
    )
    fetchSpy.mockRestore()
  })

  it('throws on error response', async () => {
    vi.spyOn(globalThis, 'fetch').mockResolvedValue(
      new Response(JSON.stringify({ detail: 'User not found' }), { status: 404 })
    )

    await expect(updateUserRole('nonexistent', 'admin')).rejects.toThrow('User not found')
    vi.restoreAllMocks()
  })
})

describe('toggleUserActive', () => {
  beforeEach(() => {
    localStorage.clear()
    setActivePinia(createPinia())
  })

  it('toggles active status with PUT on success', async () => {
    const mockData = { message: 'User deactivated' }
    const fetchSpy = vi.spyOn(globalThis, 'fetch').mockResolvedValue(
      new Response(JSON.stringify(mockData), { status: 200 })
    )

    const result = await toggleUserActive('user-1', false)

    expect(result).toEqual(mockData)
    expect(fetchSpy).toHaveBeenCalledWith(
      '/api/admin/users/user-1/active',
      expect.objectContaining({
        method: 'PUT',
        headers: expect.objectContaining({ 'Content-Type': 'application/json' }),
        body: JSON.stringify({ is_active: false }),
      })
    )
    fetchSpy.mockRestore()
  })

  it('throws on error response', async () => {
    vi.spyOn(globalThis, 'fetch').mockResolvedValue(
      new Response(JSON.stringify({ detail: 'User not found' }), { status: 404 })
    )

    await expect(toggleUserActive('nonexistent', true)).rejects.toThrow('User not found')
    vi.restoreAllMocks()
  })
})
