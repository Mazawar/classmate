import { defineStore } from 'pinia'
import http from '../api/http'

const TOKEN_KEY = 'token'
const USER_KEY = 'user'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    token: localStorage.getItem(TOKEN_KEY) || '',
    user: JSON.parse(localStorage.getItem(USER_KEY) || 'null'),
  }),
  getters: {
    isLoggedIn: (s) => !!s.token,
  },
  actions: {
    async login(username, password) {
      const form = new URLSearchParams()
      form.append('username', username)
      form.append('password', password)
      const data = await http.post('/auth/login', form, {
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      })
      // 先落 token，后续 /me 请求的拦截器才能带上 Authorization
      this.token = data.access_token
      localStorage.setItem(TOKEN_KEY, this.token)
      this.user = await http.get('/auth/me')
      localStorage.setItem(USER_KEY, JSON.stringify(this.user))
    },
    async register(payload) {
      const data = await http.post('/auth/register', payload)
      this.token = data.access_token
      localStorage.setItem(TOKEN_KEY, this.token)
      this.user = await http.get('/auth/me')
      localStorage.setItem(USER_KEY, JSON.stringify(this.user))
    },
    logout() {
      this.token = ''
      this.user = null
      localStorage.removeItem(TOKEN_KEY)
      localStorage.removeItem(USER_KEY)
    },
  },
})
