/**
 * Authentication Store (Zustand)
 *
 * Global state management for authentication
 */

import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import type { User, LoginCredentials, RegisterData, AuthState } from '../types/auth';
import authService from '../services/authService';

interface AuthStore extends AuthState {
  login: (credentials: LoginCredentials) => Promise<void>;
  register: (data: RegisterData) => Promise<void>;
  logout: () => void;
  setUser: (user: User, token: string) => void;
  checkAuth: () => Promise<void>;
}

export const useAuthStore = create<AuthStore>()(
  persist(
    (set) => ({
      user: null,
      token: null,
      isAuthenticated: false,
      isLoading: false,

      /**
       * Login
       */
      login: async (credentials: LoginCredentials) => {
        set({ isLoading: true });
        try {
          const response = await authService.login(credentials);
          localStorage.setItem('access_token', response.access_token);
          set({
            user: response.user,
            token: response.access_token,
            isAuthenticated: true,
            isLoading: false,
          });
        } catch (error) {
          set({ isLoading: false });
          throw error;
        }
      },

      /**
       * Register
       */
      register: async (data: RegisterData) => {
        set({ isLoading: true });
        try {
          const response = await authService.register(data);
          localStorage.setItem('access_token', response.access_token);
          set({
            user: response.user,
            token: response.access_token,
            isAuthenticated: true,
            isLoading: false,
          });
        } catch (error) {
          set({ isLoading: false });
          throw error;
        }
      },

      /**
       * Logout
       */
      logout: () => {
        authService.logout();
        set({
          user: null,
          token: null,
          isAuthenticated: false,
        });
      },

      /**
       * Set user and token (used after successful auth)
       */
      setUser: (user: User, token: string) => {
        set({
          user,
          token,
          isAuthenticated: true,
        });
      },

      /**
       * Check if user is authenticated (verify token)
       */
      checkAuth: async () => {
        const token = localStorage.getItem('access_token');
        if (!token) {
          set({ isAuthenticated: false, user: null, token: null });
          return;
        }

        try {
          const user = await authService.getCurrentUser();
          set({
            user,
            token,
            isAuthenticated: true,
          });
        } catch {
          // Token is invalid
          localStorage.removeItem('access_token');
          set({
            user: null,
            token: null,
            isAuthenticated: false,
          });
        }
      },
    }),
    {
      name: 'auth-storage',
      partialize: (state) => ({
        user: state.user,
        token: state.token,
        isAuthenticated: state.isAuthenticated,
      }),
    }
  )
);

export default useAuthStore;
