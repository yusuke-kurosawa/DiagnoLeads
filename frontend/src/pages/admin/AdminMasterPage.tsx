import { useState } from 'react';
import { useAuthStore } from '../../store/authStore';
import { Building2, Users, Layers, Settings, FileText } from 'lucide-react';
import TenantManagement from '../../components/admin/TenantManagement';
import UserManagement from '../../components/admin/UserManagement';
import TaxonomyManagement from '../../components/admin/TaxonomyManagement';

type AdminTab = 'tenants' | 'users' | 'topics' | 'industries' | 'audit-logs';

export default function AdminMasterPage() {
  const { user } = useAuthStore();
  const [activeTab, setActiveTab] = useState<AdminTab>('topics');

  // ロール別のアクセス制御
  const isSystemAdmin = user?.role === 'system_admin';
  const isTenantAdmin = user?.role === 'tenant_admin';
  const canAccessMasters = isSystemAdmin || isTenantAdmin;

  if (!canAccessMasters) {
    return (
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="bg-red-50 border border-red-200 text-red-800 px-6 py-4 rounded-lg">
          <p className="font-bold">アクセス拒否</p>
          <p className="text-sm">マスターメンテナンス機能にアクセスするには、管理者ロールが必要です。</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 text-center mb-2">マスターメンテナンス</h1>
          <p className="text-center text-gray-600">システム設定とデータ管理</p>
        </div>

        {/* Tab Navigation */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 mb-8">
          <div className="flex border-b border-gray-200 overflow-x-auto">
            {/* Tenant Tab - System Admin Only */}
            {isSystemAdmin && (
              <button
                onClick={() => setActiveTab('tenants')}
                className={`flex-shrink-0 px-6 py-3 font-medium text-center transition-colors flex items-center justify-center gap-2 border-b-2 ${
                  activeTab === 'tenants'
                    ? 'text-blue-600 border-blue-600'
                    : 'text-gray-600 hover:text-gray-900 border-transparent'
                }`}
              >
                <Building2 size={18} />
                テナント
              </button>
            )}

            {/* User Tab */}
            <button
              onClick={() => setActiveTab('users')}
              className={`flex-shrink-0 px-6 py-3 font-medium text-center transition-colors flex items-center justify-center gap-2 border-b-2 ${
                activeTab === 'users'
                  ? 'text-blue-600 border-blue-600'
                  : 'text-gray-600 hover:text-gray-900 border-transparent'
              }`}
            >
              <Users size={18} />
              ユーザー
            </button>

            {/* Topic Tab */}
            <button
              onClick={() => setActiveTab('topics')}
              className={`flex-shrink-0 px-6 py-3 font-medium text-center transition-colors flex items-center justify-center gap-2 border-b-2 ${
                activeTab === 'topics'
                  ? 'text-blue-600 border-blue-600'
                  : 'text-gray-600 hover:text-gray-900 border-transparent'
              }`}
            >
              <Layers size={18} />
              トピック
            </button>

            {/* Industry Tab */}
            <button
              onClick={() => setActiveTab('industries')}
              className={`flex-shrink-0 px-6 py-3 font-medium text-center transition-colors flex items-center justify-center gap-2 border-b-2 ${
                activeTab === 'industries'
                  ? 'text-blue-600 border-blue-600'
                  : 'text-gray-600 hover:text-gray-900 border-transparent'
              }`}
            >
              <Settings size={18} />
              業界
            </button>

            {/* Audit Logs Tab */}
            <button
              onClick={() => setActiveTab('audit-logs')}
              className={`flex-shrink-0 px-6 py-3 font-medium text-center transition-colors flex items-center justify-center gap-2 border-b-2 ${
                activeTab === 'audit-logs'
                  ? 'text-blue-600 border-blue-600'
                  : 'text-gray-600 hover:text-gray-900 border-transparent'
              }`}
            >
              <FileText size={18} />
              監査ログ
            </button>
          </div>

          {/* Tab Content */}
          <div className="p-6">
            {/* Tenant Tab Content */}
            {activeTab === 'tenants' && isSystemAdmin && (
              <div className="text-center text-gray-600 py-8">
                <p>テナント管理機能は準備中です</p>
              </div>
            )}

            {/* User Tab Content */}
            {activeTab === 'users' && (
              <UserManagement />
            )}

            {/* Topic Tab Content */}
            {activeTab === 'topics' && (
              <TaxonomyManagement type="topics" />
            )}

            {/* Industry Tab Content */}
            {activeTab === 'industries' && (
              <TaxonomyManagement type="industries" />
            )}

            {/* Audit Logs Tab Content */}
            {activeTab === 'audit-logs' && (
              <div className="text-center text-gray-600 py-8">
                <p>
                  <a
                    href={`/tenants/${user?.tenant_id}/admin/audit-logs`}
                    className="text-blue-600 hover:text-blue-800 font-medium"
                  >
                    監査ログページへ移動 →
                  </a>
                </p>
              </div>
            )}
          </div>
        </div>
      </main>
    </div>
  );
}
