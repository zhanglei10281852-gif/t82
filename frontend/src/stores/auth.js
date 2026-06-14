import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { login as loginApi, getMe } from '@/api/auth'

export const useAuthStore = defineStore('auth', () => {
  const token = ref(localStorage.getItem('token') || '')
  const user = ref(JSON.parse(localStorage.getItem('user') || 'null'))

  const isAdmin = computed(() => user.value?.role === 'admin')
  const isHost = computed(() => user.value?.role === 'host')

  async function login(username, password) {
    const formData = new FormData()
    formData.append('username', username)
    formData.append('password', password)
    
    const res = await loginApi(formData)
    token.value = res.access_token
    localStorage.setItem('token', res.access_token)
    await fetchUser()
    return res
  }

  async function fetchUser() {
    const res = await getMe()
    user.value = res
    localStorage.setItem('user', JSON.stringify(res))
    return res
  }

  function logout() {
    token.value = ''
    user.value = null
    localStorage.removeItem('token')
    localStorage.removeItem('user')
  }

  return { token, user, isAdmin, isHost, login, fetchUser, logout }
})
