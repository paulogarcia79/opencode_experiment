import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { User } from '@/types'

const API_BASE = import.meta.env.VITE_API_BASE_URL || ''

export const useAdminStore = defineStore('admin', () => {
  const token = ref(localStorage.getItem('admin_token') || '')
  const user = ref<User | null>(null)

  function setToken(newToken: string) {
    token.value = newToken
    localStorage.setItem('admin_token', newToken)
  }

  function clearToken() {
    token.value = ''
    user.value = null
    localStorage.removeItem('admin_token')
  }

  function setUser(newUser: User) {
    user.value = newUser
  }

  function clearUser() {
    user.value = null
  }

  async function fetchMe() {
    if (!token.value) return
    const res = await fetch(`${API_BASE}/api/auth/me`, {
      headers: { Authorization: `Bearer ${token.value}` },
    })
    if (!res.ok) {
      clearToken()
      return
    }
    const data = await res.json() as User
    setUser(data)
  }

  return { token, user, setToken, clearToken, setUser, clearUser, fetchMe }
})
