/**
 * Error Report Service
 *
 * Sends error reports to the backend for centralized logging and analysis.
 */

import { apiClient } from './api';

export interface ErrorReport {
  error_type: string;
  error_message: string;
  error_code?: string;
  severity?: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  stack_trace?: string;
  endpoint?: string;
  method?: string;
  status_code?: number;
  context?: Record<string, unknown>;
  correlation_id?: string;
  environment?: string;
}

export interface ErrorLogResponse {
  id: string;
  tenant_id?: string;
  user_id?: string;
  error_type: string;
  error_code?: string;
  severity: string;
  error_message: string;
  stack_trace?: string;
  endpoint?: string;
  method?: string;
  status_code?: number;
  environment: string;
  created_at: string;
}

/**
 * Report an error to the backend
 */
export async function reportError(
  error: unknown,
  context?: {
    component?: string;
    action?: string;
    endpoint?: string;
    method?: string;
    additionalInfo?: Record<string, unknown>;
  }
): Promise<ErrorLogResponse | null> {
  try {
    // Determine error type and extract details
    let errorType = 'FRONTEND_ERROR';
    let errorMessage = 'Unknown error';
    let stackTrace: string | undefined;
    let errorCode: string | undefined;
    let severity: ErrorReport['severity'] = 'MEDIUM';
    let statusCode: number | undefined;

    if (error instanceof Error) {
      errorMessage = error.message;
      stackTrace = error.stack;
      errorType = error.name || 'Error';
    } else if (typeof error === 'object' && error !== null) {
      // Handle API errors
      if ('response' in error) {
        const apiError = error as {
          response?: { data?: { detail?: string }; status?: number };
          message?: string;
        };
        errorType = 'API_ERROR';
        errorMessage = apiError.response?.data?.detail || apiError.message || 'API request failed';
        statusCode = apiError.response?.status;

        // Determine severity based on status code
        if (statusCode && statusCode >= 500) {
          severity = 'HIGH';
        } else if (statusCode === 401 || statusCode === 403) {
          severity = 'MEDIUM';
        } else {
          severity = 'LOW';
        }
      } else {
        errorMessage = JSON.stringify(error);
      }
    } else {
      errorMessage = String(error);
    }

    // Build error report
    const errorReport: ErrorReport = {
      error_type: errorType,
      error_message: errorMessage,
      error_code: errorCode,
      severity,
      stack_trace: stackTrace,
      endpoint: context?.endpoint,
      method: context?.method,
      status_code: statusCode,
      context: {
        component: context?.component,
        action: context?.action,
        ...context?.additionalInfo,
        userAgent: navigator.userAgent,
        url: window.location.href,
        timestamp: new Date().toISOString(),
      },
      environment: import.meta.env.MODE,
    };

    // Send error report to backend
    const response = await apiClient.post<ErrorLogResponse>(
      '/error-logs/report',
      errorReport
    );

    return response.data;
  } catch (reportError) {
    // If error reporting fails, log to console only
    console.error('Failed to report error to backend:', reportError);
    console.error('Original error:', error);
    return null;
  }
}

/**
 * Report error with minimal context (for simple cases)
 */
export async function reportSimpleError(
  message: string,
  severity: ErrorReport['severity'] = 'MEDIUM'
): Promise<ErrorLogResponse | null> {
  return reportError(new Error(message), {
    additionalInfo: { severity },
  });
}

/**
 * Report API error
 */
export async function reportApiError(
  error: unknown,
  endpoint: string,
  method: string
): Promise<ErrorLogResponse | null> {
  return reportError(error, {
    endpoint,
    method,
    action: 'API_REQUEST',
  });
}

/**
 * Report component error
 */
export async function reportComponentError(
  error: unknown,
  componentName: string,
  action?: string
): Promise<ErrorLogResponse | null> {
  return reportError(error, {
    component: componentName,
    action,
  });
}
