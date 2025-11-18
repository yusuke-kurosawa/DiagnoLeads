import { useRouteError, useNavigate } from 'react-router-dom';
import { AlertTriangle, Home, RefreshCw, ChevronRight } from 'lucide-react';

interface RouteError {
  status?: number;
  statusText?: string;
  message?: string;
  data?: unknown;
}

export default function ErrorPage() {
  const error = useRouteError() as RouteError;
  const navigate = useNavigate();

  const status = error?.status || 500;
  const statusText = error?.statusText || 'Internal Server Error';
  const message = error?.message || 'An unexpected error occurred';

  const errorMessages: { [key: number]: { title: string; description: string } } = {
    404: {
      title: 'ページが見つかりません',
      description: 'お探しのページは存在しないか、削除されている可能性があります。',
    },
    403: {
      title: 'アクセスが拒否されました',
      description: 'このページへのアクセス権限がありません。',
    },
    401: {
      title: 'ログインが必要です',
      description: 'このページを表示するにはログインが必要です。',
    },
    500: {
      title: 'サーバーエラーが発生しました',
      description: 'システムで予期しないエラーが発生しました。しばらく経ってからお試しください。',
    },
  };

  const errorInfo = errorMessages[status] || {
    title: 'エラーが発生しました',
    description: `エラーコード: ${status} - ${statusText}`,
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-red-50 to-orange-50 flex items-center justify-center px-4">
      <div className="max-w-md w-full">
        <div className="bg-white rounded-lg shadow-lg p-8 text-center">
          {/* Error Icon */}
          <div className="inline-flex items-center justify-center w-16 h-16 bg-red-100 rounded-full mb-6">
            <AlertTriangle className="w-8 h-8 text-red-600" />
          </div>

          {/* Error Code */}
          <div className="mb-4">
            <span className="inline-block px-3 py-1 bg-red-100 text-red-700 text-sm font-semibold rounded-full">
              エラー {status}
            </span>
          </div>

          {/* Error Title */}
          <h1 className="text-2xl font-bold text-gray-900 mb-3">
            {errorInfo.title}
          </h1>

          {/* Error Description */}
          <p className="text-gray-600 mb-6">
            {errorInfo.description}
          </p>

          {/* Additional Error Details */}
          {message && message !== statusText && (
            <div className="bg-gray-50 border border-gray-200 rounded-lg p-4 mb-6 text-left">
              <p className="text-sm font-semibold text-gray-700 mb-2">
                詳細情報:
              </p>
              <p className="text-sm text-gray-700 font-mono break-words">
                {message}
              </p>
              <p className="text-xs text-gray-500 mt-2">
                💡 ヒント: ブラウザのコンソール (F12キーで開く) を確認すると、詳細なエラー情報が表示されます。
              </p>
            </div>
          )}

          {/* Action Buttons */}
          <div className="flex flex-col gap-3">
            <button
              onClick={() => navigate('/dashboard')}
              className="w-full px-4 py-2 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700 transition-colors flex items-center justify-center gap-2"
            >
              <Home size={18} />
              ダッシュボードに戻る
            </button>

            <button
              onClick={() => window.location.reload()}
              className="w-full px-4 py-2 bg-gray-200 text-gray-800 font-medium rounded-lg hover:bg-gray-300 transition-colors flex items-center justify-center gap-2"
            >
              <RefreshCw size={18} />
              ページを再読み込み
            </button>
          </div>

          {/* Contact Support */}
          <div className="mt-6 pt-6 border-t border-gray-200">
            <p className="text-sm text-gray-600 mb-3">
              問題が解決しない場合は、以下のエラーコードをお手元に控えて、サポートチームにお問い合わせください。
            </p>
            <code className="block text-xs bg-gray-100 text-gray-800 p-3 rounded font-mono break-all">
              {`Error-${status}-${Date.now()}`}
            </code>
          </div>

          {/* Back Link */}
          <button
            onClick={() => navigate(-1)}
            className="mt-6 text-blue-600 hover:text-blue-700 text-sm font-medium flex items-center justify-center gap-1 mx-auto"
          >
            <span>戻る</span>
            <ChevronRight size={14} />
          </button>
        </div>
      </div>
    </div>
  );
}
