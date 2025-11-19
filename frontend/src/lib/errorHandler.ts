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
      const errorData = error.response?.data as { detail?: string } | undefined;

      return {
        code: `API_ERROR_${status}`,
        message: errorData?.detail || error.message || 'API request failed',
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

  static getErrorMessage(error: SystemError): string {
    const errorMessages: { [key: string]: string } = {
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
      const details = error.details as { response?: { status?: number; data?: unknown; headers?: unknown }; config?: { method?: string; url?: string; data?: unknown } };
      if (details.response) {
        console.group('🌐 API Response Details');
        console.error('Response Status:', details.response.status);
        console.error('Response Data:', details.response.data);
        console.error('Response Headers:', details.response.headers);
        console.groupEnd();
      }

      if (details.config) {
        console.group('⚙️ Request Configuration');
        console.error('Method:', details.config.method);
        console.error('URL:', details.config.url);
        console.error('Data:', details.config.data);
        console.groupEnd();
      }

      console.groupEnd();
    }
    
    console.groupEnd();

    // Send to monitoring service (Sentry, etc.)
    // This can be implemented later
  }
}

export class UserFacingError extends Error {
  code: string;
  userMessage: string;
  technicalDetails?: unknown;

  constructor(
    code: string,
    userMessage: string,
    technicalDetails?: unknown
  ) {
    super(userMessage);
    this.name = 'UserFacingError';
    this.code = code;
    this.userMessage = userMessage;
    this.technicalDetails = technicalDetails;
  }
}
