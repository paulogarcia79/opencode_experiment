import { describe, it, expect, beforeEach, vi } from 'vitest'
import { createPinia, setActivePinia } from 'pinia'
import { useAdminStore } from '@/stores/admin'

describe('register', () => {
  beforeEach(() => {
    localStorage.clear()
    setActivePinia(createPinia())
  })

  it('sends correct payload to /api/auth/register', async () => {
    const { register } = await import('@/composables/useAdminApi')
    const fetchSpy = vi.spyOn(globalThis, 'fetch').mockResolvedValue(
      new Response(JSON.stringify({ token: 'jwt-token', type: 'bearer' }), { status: 200 })
    )

    await register('test@example.com', 'SecurePass1', 'SecurePass1')

    expect(fetchSpy).toHaveBeenCalledWith(
      '/api/auth/register',
      expect.objectContaining({
        method: 'POST',
        headers: expect.objectContaining({ 'Content-Type': 'application/json' }),
        body: JSON.stringify({ email: 'test@example.com', password: 'SecurePass1', confirm_password: 'SecurePass1' }),
      })
    )
    fetchSpy.mockRestore()
  })

  it('sets token and fetches profile on successful registration', async () => {
    const { register } = await import('@/composables/useAdminApi')
    const store = useAdminStore()

    const responses = [
      new Response(JSON.stringify({ token: 'jwt-token', type: 'bearer' }), {
        status: 200,
        headers: { 'X-Registration-New': 'true' },
      }),
      new Response(JSON.stringify({ id: '1', email: 'test@example.com', role: 'contributor', is_active: true, is_verified: false, created_at: '' }), { status: 200 }),
    ]
    let callCount = 0
    vi.spyOn(globalThis, 'fetch').mockImplementation(() => {
      return Promise.resolve(responses[callCount++])
    })

    const result = await register('test@example.com', 'SecurePass1', 'SecurePass1')

    expect('token' in result).toBe(true)
    if ('token' in result) {
      expect(result.token).toBe('jwt-token')
    }
    expect(store.token).toBe('jwt-token')
    expect(store.user).not.toBeNull()
    expect(store.user?.is_verified).toBe(false)
  })

  it('detects duplicate email when response has no token', async () => {
    const { register } = await import('@/composables/useAdminApi')

    vi.spyOn(globalThis, 'fetch').mockResolvedValue(
      new Response(JSON.stringify({ detail: 'If that email is not already registered, check your inbox.' }), { status: 200 })
    )

    const result = await register('existing@example.com', 'SecurePass1', 'SecurePass1')

    expect('duplicate' in result).toBe(true)
    if ('duplicate' in result) {
      expect(result.duplicate).toBe(true)
    }
    expect('token' in result).toBe(false)
  })
})

describe('resendVerification', () => {
  beforeEach(() => {
    localStorage.clear()
    setActivePinia(createPinia())
  })

  it('uses Bearer token instead of email in body', async () => {
    const { resendVerification } = await import('@/composables/useAdminApi')
    const store = useAdminStore()
    store.setToken('bearer-token-123')

    const fetchSpy = vi.spyOn(globalThis, 'fetch').mockResolvedValue(
      new Response(JSON.stringify({ message: 'sent' }), { status: 200 })
    )

    await resendVerification()

    expect(fetchSpy).toHaveBeenCalledWith(
      '/api/auth/resend-verification',
      expect.objectContaining({
        method: 'POST',
        headers: expect.objectContaining({ Authorization: 'Bearer bearer-token-123' }),
      })
    )
    // Should NOT have a JSON body
    const callBody = (fetchSpy.mock.calls[0][1] as RequestInit).body
    expect(callBody).toBeUndefined()
    fetchSpy.mockRestore()
  })
})

describe('isVerificationBannerDismissed', () => {
  it('defaults to false', () => {
    setActivePinia(createPinia())
    const store = useAdminStore()
    expect(store.isVerificationBannerDismissed).toBe(false)
  })

  it('is session-only, not persisted in localStorage', () => {
    setActivePinia(createPinia())
    const store = useAdminStore()
    store.isVerificationBannerDismissed = true
    expect(store.isVerificationBannerDismissed).toBe(true)

    // New store (simulating page refresh) should have false
    setActivePinia(createPinia())
    const freshStore = useAdminStore()
    expect(freshStore.isVerificationBannerDismissed).toBe(false)
  })
})
