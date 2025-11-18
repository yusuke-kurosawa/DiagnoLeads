import axios, { AxiosInstance, AxiosError } from 'axios';
import { ApiErrorHandler } from './errorHandler';
import type { SystemError } from './errorHandler';

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
    (response) => {
      console.log(`✅ API Success: ${response.config.method?.toUpperCase()} ${response.config.url} - Status ${response.status}`);
      return response;
    },
    (error: AxiosError) => {
      const systemError = ApiErrorHandler.handle(error);

      // Log error with full details
      console.group('🚨 API Error Handler Activated');
      console.error('Full Axios Error:', error);
      ApiErrorHandler.log(systemError);
      console.groupEnd();

      // Handle specific error cases
      if (error.response?.status === 401) {
        console.warn('🔐 401 Unauthorized - Clearing auth and redirecting to login');
        localStorage.removeItem('access_token');
        localStorage.removeItem('user');
        setTimeout(() => {
          window.location.href = '/login';
        }, 1000);
      } else if (error.response?.status === 403) {
        console.warn('🚫 403 Forbidden - Redirecting to error page');
        setTimeout(() => {
          window.location.href = '/error';
        }, 1000);
      } else if (error.response?.status === 500) {
        console.error('💥 500 Server Error - Redirecting to error page');
        setTimeout(() => {
          window.location.href = '/error';
        }, 1000);
      } else if (!error.response) {
        console.error('🌐 Network Error - No response from server');
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
