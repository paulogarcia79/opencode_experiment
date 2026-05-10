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
