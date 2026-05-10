import { describe, it, expect, beforeEach } from 'vitest'
import { createPinia, setActivePinia } from 'pinia'
import { useAdminStore } from '@/stores/admin'

describe('useAdminStore', () => {
  beforeEach(() => {
    localStorage.clear()
    setActivePinia(createPinia())
  })

  it('initializes token from localStorage', () => {
    localStorage.setItem('admin_token', 'existing-token')
    const store = useAdminStore()
    expect(store.token).toBe('existing-token')
  })

  it('initializes with empty token when localStorage has no token', () => {
    const store = useAdminStore()
    expect(store.token).toBe('')
  })

  it('setToken updates value and persists to localStorage', () => {
    const store = useAdminStore()
    store.setToken('new-token')
    expect(store.token).toBe('new-token')
    expect(localStorage.getItem('admin_token')).toBe('new-token')
  })

  it('clearToken resets value and removes from localStorage', () => {
    localStorage.setItem('admin_token', 'some-token')
    const store = useAdminStore()
    store.clearToken()
    expect(store.token).toBe('')
    expect(localStorage.getItem('admin_token')).toBeNull()
  })
})
