/* eslint-disable react-refresh/only-export-components */
import React, { ReactNode } from 'react';
import { useNavigate } from 'react-router-dom';
import { AlertTriangle } from 'lucide-react';

interface Props {
  children: ReactNode;
}

interface State {
  hasError: boolean;
  error: Error | null;
  errorInfo: React.ErrorInfo | null;
}

export class ErrorBoundary extends React.Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = {
      hasError: false,
      error: null,
      errorInfo: null,
    };
  }

  static getDerivedStateFromError(): Partial<State> {
    return { hasError: true };
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    console.error('Error caught by boundary:', error, errorInfo);
    this.setState({
      error,
      errorInfo,
    });
  }

  render() {
    if (this.state.hasError) {
      return <ErrorFallback error={this.state.error} errorInfo={this.state.errorInfo} />;
    }

    return this.props.children;
  }
}

interface ErrorFallbackProps {
  error: Error | null;
  errorInfo: React.ErrorInfo | null;
}

function ErrorFallback({ error, errorInfo }: ErrorFallbackProps) {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen bg-gradient-to-br from-red-50 to-orange-50 flex items-center justify-center px-4">
      <div className="max-w-md w-full">
        <div className="bg-white rounded-lg shadow-lg p-8 text-center">
          {/* Error Icon */}
          <div className="inline-flex items-center justify-center w-16 h-16 bg-red-100 rounded-full mb-6">
            <AlertTriangle className="w-8 h-8 text-red-600" />
          </div>

          {/* Error Title */}
          <h1 className="text-2xl font-bold text-gray-900 mb-3">
            申し訳ございません
          </h1>

          {/* Error Description */}
          <p className="text-gray-600 mb-6">
            予期しないエラーが発生しました。ページを再度読み込むか、ダッシュボードに戻ってください。
          </p>

          {/* Error Details */}
          {error && (
            <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6 text-left max-h-48 overflow-y-auto">
              <p className="text-xs font-semibold text-red-700 mb-2">エラー詳細:</p>
              <p className="text-xs text-red-600 font-mono break-words mb-3">
                {error.message}
              </p>
              {errorInfo && (
                <details className="text-xs text-red-600">
                  <summary className="cursor-pointer font-semibold mb-2">
                    スタックトレース
                  </summary>
                  <pre className="font-mono text-xs overflow-x-auto whitespace-pre-wrap break-words">
                    {errorInfo.componentStack}
                  </pre>
                </details>
              )}
            </div>
          )}

          {/* Action Buttons */}
          <div className="flex flex-col gap-3">
            <button
              onClick={() => window.location.reload()}
              className="w-full px-4 py-2 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700 transition-colors"
            >
              ページを再読み込み
            </button>

            <button
              onClick={() => navigate('/dashboard')}
              className="w-full px-4 py-2 bg-gray-200 text-gray-800 font-medium rounded-lg hover:bg-gray-300 transition-colors"
            >
              ダッシュボードに戻る
            </button>
          </div>

          {/* Support Info */}
          <div className="mt-6 pt-6 border-t border-gray-200">
            <p className="text-xs text-gray-600">
              問題が続く場合は、ブラウザのコンソールで詳細を確認するか、サポートチームにお問い合わせください。
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
