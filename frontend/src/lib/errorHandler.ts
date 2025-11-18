import { AxiosError } from 'axios';

export interface SystemError {
  code: string;
  message: string;
  status: number;
  details?: unknown;
  timestamp: string;
}

export class ApiErrorHandler {
  static handle(error: unknown): SystemError {
    const timestamp = new Date().toISOString();

    // Axios Error
    if (error instanceof AxiosError) {
      const status = error.response?.status || 500;
      const errorData = error.response?.data;
      const detail =
        errorData &&
        typeof errorData === 'object' &&
        'detail' in errorData &&
        typeof errorData.detail === 'string'
          ? errorData.detail
          : undefined;

      return {
        code: `API_ERROR_${status}`,
        message: detail || error.message || 'API request failed',
        status,
        details: errorData,
        timestamp,
      };
    }

    // Network Error
    if (error instanceof Error && error.message.includes('Network')) {
      return {
        code: 'NETWORK_ERROR',
        message: 'Network connection failed. Please check your internet connection.',
        status: 0,
        details: { originalError: error.message },
        timestamp,
      };
    }

    // Timeout Error
    if (error instanceof Error && error.message.includes('timeout')) {
      return {
        code: 'TIMEOUT_ERROR',
        message: 'Request timeout. Please try again.',
        status: 408,
        details: { originalError: error.message },
        timestamp,
      };
    }

    // Generic Error
    if (error instanceof Error) {
      return {
        code: 'APPLICATION_ERROR',
        message: error.message || 'An unexpected error occurred',
        status: 500,
        details: { stack: error.stack },
        timestamp,
      };
    }

    // Unknown Error
    return {
      code: 'UNKNOWN_ERROR',
      message: 'An unexpected error occurred',
      status: 500,
      details: { error },
      timestamp,
    };
  }

  static getUserFacingMessage(error: SystemError): string {
    const errorMessages: { [key: string]: string} = {
      NETWORK_ERROR: 'ネットワーク接続エラーが発生しました。インターネット接続を確認してください。',
      TIMEOUT_ERROR: 'リクエストがタイムアウトしました。もう一度お試しください。',
      API_ERROR_400: 'リクエストが無効です。入力内容を確認してください。',
      API_ERROR_401: 'ログインが必要です。',
      API_ERROR_403: 'このアクションの実行権限がありません。',
      API_ERROR_404: 'リクエストされたリソースが見つかりません。',
      API_ERROR_409: 'リソースが既に存在するか、競合しています。',
      API_ERROR_429: 'リクエストが多すぎます。しばらく待ってからお試しください。',
      API_ERROR_500: 'サーバーエラーが発生しました。しばらく経ってからお試しください。',
      API_ERROR_502: 'サービスが一時的に利用できません。',
      API_ERROR_503: 'サービスが一時的に利用できません。',
      API_ERROR_504: 'サーバーが応答していません。',
      APPLICATION_ERROR: 'アプリケーションエラーが発生しました。',
      UNKNOWN_ERROR: '予期しないエラーが発生しました。',
    };

    return (
      errorMessages[error.code] ||
      errorMessages[`API_ERROR_${error.status}`] ||
      error.message ||
      'An unexpected error occurred'
    );
  }

  static log(error: SystemError): void {
    // Always log errors in all environments for debugging
    console.group(`🔴 System Error: ${error.code}`);
    console.error('Status Code:', error.status);
    console.error('Error Message:', error.message);
    console.error('Error Code:', error.code);
    console.error('Timestamp:', error.timestamp);

    if (error.details) {
      console.group('📋 Detailed Information');
      console.error('Details:', error.details);

      // If it's an API error, show more details
      const details = error.details as Record<string, unknown>;
      if (details && typeof details === 'object' && 'response' in details) {
        console.group('🌐 API Response Details');
        const response = details.response as Record<string, unknown>;
        console.error('Response Status:', response.status);
        console.error('Response Data:', response.data);
        console.error('Response Headers:', response.headers);
        console.groupEnd();
      }

      if (details && typeof details === 'object' && 'config' in details) {
        console.group('⚙️ Request Configuration');
        const config = details.config as Record<string, unknown>;
        console.error('Method:', config.method);
        console.error('URL:', config.url);
        console.error('Data:', config.data);
        console.groupEnd();
      }

      console.groupEnd();
    }

    console.groupEnd();

    // Send to monitoring service (Sentry, etc.)
    // This can be implemented later
  }

  /**
   * Extract error message from unknown error type
   * Useful for catch blocks to avoid using 'any' type
   */
  static getErrorMessage(error: unknown, fallback = '不明なエラーが発生しました'): string {
    // Check for Axios-like error structure (works for both real AxiosError and mocks)
    if (typeof error === 'object' && error !== null && 'response' in error) {
      const errorWithResponse = error as { response?: { data?: unknown } };
      const errorData = errorWithResponse.response?.data;
      if (errorData && typeof errorData === 'object' && 'detail' in errorData) {
        const detail = (errorData as { detail: unknown }).detail;
        if (typeof detail === 'string') return detail;
      }
    }

    if (error instanceof AxiosError) {
      return error.message || fallback;
    }

    if (error instanceof Error) {
      return error.message || fallback;
    }

    if (typeof error === 'string') {
      return error;
    }

    return fallback;
  }
}

export class UserFacingError extends Error {
  code: string;
  userMessage: string;
  technicalDetails?: unknown;

  constructor(code: string, userMessage: string, technicalDetails?: unknown) {
    super(userMessage);
    this.name = 'UserFacingError';
    this.code = code;
    this.userMessage = userMessage;
    this.technicalDetails = technicalDetails;
  }
}
