/**
 * Authentication Service
 *
 * Handles API calls for authentication
 */

import api from './api';
import type { LoginCredentials, RegisterData, AuthResponse, User } from '../types/auth';

export const authService = {
  /**
   * Login with email and password
   */
  async login(credentials: LoginCredentials): Promise<AuthResponse> {
    const response = await api.post<AuthResponse>('/auth/login/json', credentials);
    return response.data;
  },

  /**
   * Register a new user and tenant
   */
  async register(data: RegisterData): Promise<AuthResponse> {
    const response = await api.post<AuthResponse>('/auth/register', data);
    return response.data;
  },

  /**
   * Get current user info
   */
  async getCurrentUser(): Promise<User> {
    const response = await api.get<User>('/auth/me');
    return response.data;
  },

  /**
   * Logout (clear local storage)
   */
  logout(): void {
    localStorage.removeItem('access_token');
    localStorage.removeItem('user');
  },
};

export default authService;
