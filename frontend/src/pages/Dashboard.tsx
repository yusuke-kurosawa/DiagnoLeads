/**
 * Dashboard Page
 *
 * Main dashboard for authenticated users
 */

import { useAuthStore } from '../store/authStore';
import { useNavigate } from 'react-router-dom';

export default function Dashboard() {
  const { user, logout } = useAuthStore();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <div className="min-h-screen bg-gray-100">
      {/* Header */}
      <header className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 flex justify-between items-center">
          <h1 className="text-2xl font-bold text-gray-900">DiagnoLeads</h1>
          <button
            onClick={handleLogout}
            className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50"
          >
            ログアウト
          </button>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Welcome Section */}
        <div className="bg-white rounded-lg shadow p-6 mb-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-2">
            ようこそ、{user?.name}さん！
          </h2>
          <div className="text-sm text-gray-600 space-y-1">
            <p>メール: {user?.email}</p>
            <p>ロール: {user?.role}</p>
            <p>テナントID: {user?.tenant_id}</p>
          </div>
        </div>

        {/* Feature Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-2">診断作成</h3>
            <p className="text-gray-600 text-sm mb-4">
              ノーコードで簡単に診断を作成できます
            </p>
            <button
              onClick={() => user?.tenant_id && navigate(`/tenants/${user.tenant_id}/assessments`)}
              className="text-blue-600 hover:text-blue-700 font-medium text-sm"
            >
              作成開始 →
            </button>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-2">リード管理</h3>
            <p className="text-gray-600 text-sm mb-4">
              診断結果から収集したリードを管理
            </p>
            <button
              onClick={() => user?.tenant_id && navigate(`/tenants/${user.tenant_id}/leads`)}
              className="text-blue-600 hover:text-blue-700 font-medium text-sm"
            >
              リード一覧 →
            </button>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-2">アナリティクス</h3>
            <p className="text-gray-600 text-sm mb-4">
              リードと診断のパフォーマンスを分析
            </p>
            <button
              onClick={() => user?.tenant_id && navigate(`/tenants/${user.tenant_id}/analytics`)}
              className="text-blue-600 hover:text-blue-700 font-medium text-sm"
            >
              ダッシュボード →
            </button>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-2">AI分析</h3>
            <p className="text-gray-600 text-sm mb-4">
              AIを活用したリード分析とレポート生成
            </p>
            <button className="text-blue-600 hover:text-blue-700 font-medium text-sm">
              分析開始 →
            </button>
          </div>
        </div>

        {/* Info Box */}
        <div className="mt-6 bg-blue-50 border border-blue-200 rounded-lg p-6">
          <h3 className="text-lg font-semibold text-blue-900 mb-2">
            🎉 アカウント登録完了
          </h3>
          <p className="text-blue-800 text-sm">
            DiagnoLeadsへようこそ！まずは診断を作成して、リード収集を開始しましょう。
          </p>
        </div>
      </main>
    </div>
  );
}
