import { create } from 'zustand'
import { persist } from 'zustand/middleware'

interface User {
  id: number
  email: string
  full_name: string
  role: string
  occupation?: string
  city?: string
}

interface AuthState {
  user: User | null
  token: string | null
  isAuthenticated: boolean
  setAuth: (user: User, token: string) => void
  clearAuth: () => void
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      user: null,
      token: null,
      isAuthenticated: false,
      setAuth: (user, token) => {
        localStorage.setItem('levelly_token', token)
        set({ user, token, isAuthenticated: true })
      },
      clearAuth: () => {
        localStorage.removeItem('levelly_token')
        localStorage.removeItem('levelly_user')
        set({ user: null, token: null, isAuthenticated: false })
      },
    }),
    {
      name: 'levelly_auth',
      partialize: (state) => ({ user: state.user, token: state.token, isAuthenticated: state.isAuthenticated }),
    }
  )
)
