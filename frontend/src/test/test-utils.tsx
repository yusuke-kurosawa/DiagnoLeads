import React from 'react';
import { render, RenderOptions } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { BrowserRouter } from 'react-router-dom';

/**
 * Create a new QueryClient instance for each test to ensure isolation
 */
export function createTestQueryClient() {
  return new QueryClient({
    defaultOptions: {
      queries: {
        retry: false,
        cacheTime: 0,
      },
      mutations: {
        retry: false,
      },
    },
  });
}

interface AllTheProvidersProps {
  children: React.ReactNode;
}

/**
 * Wrapper component that provides all necessary context providers for testing
 */
export function AllTheProviders({ children }: AllTheProvidersProps) {
  const queryClient = createTestQueryClient();

  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>{children}</BrowserRouter>
    </QueryClientProvider>
  );
}

/**
 * Custom render function that wraps components with all necessary providers
 */
export function renderWithProviders(
  ui: React.ReactElement,
  options?: Omit<RenderOptions, 'wrapper'>
) {
  return render(ui, { wrapper: AllTheProviders, ...options });
}

/**
 * Mock API response helper
 */
export function mockApiResponse<T>(data: T, delay = 0): Promise<{ data: T }> {
  return new Promise((resolve) => {
    setTimeout(() => {
      resolve({ data });
    }, delay);
  });
}

/**
 * Mock API error helper
 */
export function mockApiError(
  message: string,
  status = 400,
  delay = 0
): Promise<never> {
  return new Promise((_, reject) => {
    setTimeout(() => {
      reject({
        response: {
          data: { detail: message },
          status,
        },
      });
    }, delay);
  });
}

/**
 * Wait for async operations to complete
 */
export function waitForAsync(ms = 0) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

// Re-export everything from testing library
export * from '@testing-library/react';
export { renderWithProviders as render };
