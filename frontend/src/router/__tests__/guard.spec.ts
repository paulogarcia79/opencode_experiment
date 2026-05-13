import { describe, it, expect, beforeEach } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { useAdminStore } from '@/stores/admin'
import router from '@/router'

describe('Router guard: auth and verification redirects', () => {
  beforeEach(async () => {
    localStorage.clear()
    setActivePinia(createPinia())
    // Reset router to initial state
    if (router.currentRoute.value.path !== '/') {
      await router.push('/')
    }
  })

  it('redirects unauthenticated user from dashboard to /auth', async () => {
    await router.push('/admin')
    expect(router.currentRoute.value.path).toBe('/auth')
  })

  it('allows public routes without auth', async () => {
    await router.push('/search?q=test')
    expect(router.currentRoute.value.path).toBe('/search')
  })

  it('redirects logged-in unverified user from /auth to /', async () => {
    const store = useAdminStore()
    store.setToken('fake-token')
    // Mock fetchMe to set unverified user
    store.setUser({
      id: '1',
      email: 'unver@test.com',
      role: 'contributor',
      is_active: true,
      is_verified: false,
      created_at: '',
    })

    await router.push('/auth')
    expect(router.currentRoute.value.path).toBe('/')
  })

  it('redirects logged-in verified user from /auth to dashboard', async () => {
    const store = useAdminStore()
    store.setToken('fake-token')
    store.setUser({
      id: '2',
      email: 'editor@test.com',
      role: 'editor',
      is_active: true,
      is_verified: true,
      created_at: '',
    })

    await router.push('/auth')
    expect(router.currentRoute.value.path).toBe('/editor')
  })

  it('allows unverified user to navigate to dashboard routes', async () => {
    const store = useAdminStore()
    store.setToken('fake-token')
    store.setUser({
      id: '3',
      email: 'unver@test.com',
      role: 'contributor',
      is_active: true,
      is_verified: false,
      created_at: '',
    })

    await router.push('/contributor')
    expect(router.currentRoute.value.path).toBe('/contributor')
  })

  it('old /admin/login is not a named route', () => {
    const resolved = router.resolve('/admin/login')
    expect(resolved.name).toBeUndefined()
  })
})
