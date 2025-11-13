import axios, { AxiosInstance, AxiosError } from 'axios';
import { ApiErrorHandler, SystemError } from './errorHandler';
import { useAuthStore } from '../store/authStore';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1';

export const createApiClient = (): AxiosInstance => {
  const instance = axios.create({
    baseURL: API_BASE_URL,
    timeout: 30000,
    headers: {
      'Content-Type': 'application/json',
    },
  });

  // Request interceptor - Add auth token
  instance.interceptors.request.use((config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  });

  // Response interceptor - Error handling
  instance.interceptors.response.use(
    (response) => response,
    (error: AxiosError) => {
      const systemError = ApiErrorHandler.handle(error);

      // Log error
      ApiErrorHandler.log(systemError);

      // Handle specific error cases
      if (error.response?.status === 401) {
        // Unauthorized - clear auth and redirect to login
        localStorage.removeItem('access_token');
        localStorage.removeItem('user');
        window.location.href = '/login';
      }

      if (error.response?.status === 403) {
        // Forbidden - redirect to error page
        window.location.href = '/error';
      }

      if (error.response?.status === 500) {
        // Server error - redirect to error page
        window.location.href = '/error';
      }

      // For network/timeout errors, throw with error information
      throw systemError;
    }
  );

  return instance;
};

export const apiClient = createApiClient();

// Utility function to handle API calls with error handling
export async function apiCall<T>(
  fn: (client: AxiosInstance) => Promise<T>
): Promise<{ data?: T; error?: SystemError }> {
  try {
    const data = await fn(apiClient);
    return { data };
  } catch (error) {
    if (error instanceof SystemError || (typeof error === 'object' && error !== null && 'code' in error)) {
      return { error: error as SystemError };
    }

    const systemError = ApiErrorHandler.handle(error);
    return { error: systemError };
  }
}
