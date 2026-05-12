import { describe, it, expect, beforeEach, vi } from 'vitest'
import { createPinia, setActivePinia } from 'pinia'
import { useAdminStore } from '@/stores/admin'

const mockUser = {
  id: 'test-user-id',
  email: 'test@example.com',
  role: 'editor',
  is_active: true,
  is_verified: true,
  created_at: '2026-01-01T00:00:00Z',
}

describe('admin store', () => {
  beforeEach(() => {
    localStorage.clear()
    setActivePinia(createPinia())
  })

  it('initializes with empty token and null user', () => {
    const store = useAdminStore()
    expect(store.token).toBe('')
    expect(store.user).toBeNull()
  })

  it('restores token from localStorage on init', () => {
    localStorage.setItem('admin_token', 'existing-token')
    setActivePinia(createPinia())
    const store = useAdminStore()
    expect(store.token).toBe('existing-token')
  })

  it('sets and persists token', () => {
    const store = useAdminStore()
    store.setToken('new-token')
    expect(store.token).toBe('new-token')
    expect(localStorage.getItem('admin_token')).toBe('new-token')
  })

  it('clears token and user', () => {
    const store = useAdminStore()
    store.setToken('some-token')
    store.setUser(mockUser)
    store.clearToken()
    expect(store.token).toBe('')
    expect(store.user).toBeNull()
    expect(localStorage.getItem('admin_token')).toBeNull()
  })

  it('sets user profile', () => {
    const store = useAdminStore()
    store.setUser(mockUser)
    expect(store.user).toEqual(mockUser)
  })

  it('clears user profile', () => {
    const store = useAdminStore()
    store.setUser(mockUser)
    store.clearUser()
    expect(store.user).toBeNull()
  })

  it('fetches user profile and stores it', async () => {
    global.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: () => Promise.resolve(mockUser),
    })

    const store = useAdminStore()
    store.setToken('valid-token')
    await store.fetchMe()

    expect(store.user).toEqual(mockUser)
    expect(global.fetch).toHaveBeenCalledWith(
      '/api/auth/me',
      { headers: { Authorization: 'Bearer valid-token' } }
    )
  })

  it('clears token on fetchMe failure', async () => {
    global.fetch = vi.fn().mockResolvedValue({
      ok: false,
    })

    const store = useAdminStore()
    store.setToken('invalid-token')
    await store.fetchMe()

    expect(store.token).toBe('')
    expect(store.user).toBeNull()
  })

  it('does nothing on fetchMe if no token', async () => {
    global.fetch = vi.fn()

    const store = useAdminStore()
    await store.fetchMe()

    expect(global.fetch).not.toHaveBeenCalled()
  })
})
