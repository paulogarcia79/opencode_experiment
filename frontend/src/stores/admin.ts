import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { User } from '@/types'

const API_BASE = import.meta.env.VITE_API_BASE_URL || ''

export const useAdminStore = defineStore('admin', () => {
  const token = ref(localStorage.getItem('admin_token') || '')
  const user = ref<User | null>(null)
  const profileLoaded = ref(false)

  function setToken(newToken: string) {
    token.value = newToken
    localStorage.setItem('admin_token', newToken)
  }

  function clearToken() {
    token.value = ''
    user.value = null
    profileLoaded.value = false
    localStorage.removeItem('admin_token')
  }

  function setUser(newUser: User) {
    user.value = newUser
    profileLoaded.value = true
  }

  function clearUser() {
    user.value = null
    profileLoaded.value = false
  }

  async function fetchMe() {
    if (!token.value) return
    try {
      const res = await fetch(`${API_BASE}/api/auth/me`, {
        headers: { Authorization: `Bearer ${token.value}` },
      })
      if (!res.ok) {
        clearToken()
        return
      }
      const data = await res.json() as User
      setUser(data)
    } catch {
      clearToken()
    }
  }

  return { token, user, profileLoaded, setToken, clearToken, setUser, clearUser, fetchMe }
})
