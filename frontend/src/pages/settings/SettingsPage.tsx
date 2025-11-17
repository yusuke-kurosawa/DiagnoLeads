import { useState } from 'react';
import { useParams } from 'react-router-dom';
import { Settings, Bell, Lock, Palette, Database, Plug } from 'lucide-react';
import TeamsIntegration from '@/components/settings/TeamsIntegration';

type SettingsTab = 'general' | 'notifications' | 'security' | 'appearance' | 'integrations' | 'advanced';

export default function SettingsPage() {
  const { tenantId } = useParams<{ tenantId: string }>();
  const [activeTab, setActiveTab] = useState<SettingsTab>('general');
  const [settings, setSettings] = useState({
    // General settings
    tenantName: 'Sample Tenant',
    email: 'admin@sample.com',
    timezone: 'Asia/Tokyo',
    language: 'ja',

    // Notification settings
    emailNotifications: true,
    assessmentReminders: true,
    leadsNotifications: true,
    weeklyReport: true,

    // Security settings
    twoFactorAuth: false,
    loginAlerts: true,
    sessionTimeout: 30,
    apiKeyRotation: 90,

    // Appearance settings
    theme: 'light',
    sidebarCollapsed: false,

    // Advanced settings
    apiEnabled: true,
    webhooksEnabled: false,
    dataRetention: 365,
  });

  const handleSettingChange = (key: string, value: any) => {
    setSettings(prev => ({
      ...prev,
      [key]: value
    }));
  };

  const handleSave = () => {
    console.log('Saving settings:', settings);
    alert('設定が保存されました');
  };

  const tabs: Array<{ id: SettingsTab; label: string; icon: React.ReactNode }> = [
    { id: 'general', label: '一般設定', icon: <Settings size={18} /> },
    { id: 'notifications', label: '通知', icon: <Bell size={18} /> },
    { id: 'integrations', label: '外部連携', icon: <Plug size={18} /> },
    { id: 'security', label: 'セキュリティ', icon: <Lock size={18} /> },
    { id: 'appearance', label: '表示設定', icon: <Palette size={18} /> },
    { id: 'advanced', label: '詳細設定', icon: <Database size={18} /> },
  ];

  return (
    <div className="min-h-screen bg-gray-50">
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">システム環境設定</h1>
          <p className="text-gray-600">テナントの設定を管理</p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          {/* Sidebar Navigation */}
          <div className="lg:col-span-1">
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
              {tabs.map(tab => (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`w-full px-4 py-3 text-left font-medium flex items-center gap-3 transition-colors border-l-2 ${
                    activeTab === tab.id
                      ? 'bg-blue-50 text-blue-600 border-blue-600'
                      : 'text-gray-700 hover:bg-gray-50 border-transparent'
                  }`}
                >
                  {tab.icon}
                  {tab.label}
                </button>
              ))}
            </div>
          </div>

          {/* Settings Content */}
          <div className="lg:col-span-3">
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
              {/* General Settings */}
              {activeTab === 'general' && (
                <div className="space-y-6">
                  <h2 className="text-xl font-semibold text-gray-900 mb-4">一般設定</h2>
                  
                  <div>
                    <label className="block text-left text-sm font-medium text-gray-700 mb-2">
                      テナント名
                    </label>
                    <input
                      type="text"
                      value={settings.tenantName}
                      onChange={(e) => handleSettingChange('tenantName', e.target.value)}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                    />
                  </div>

                  <div>
                    <label className="block text-left text-sm font-medium text-gray-700 mb-2">
                      メールアドレス
                    </label>
                    <input
                      type="email"
                      value={settings.email}
                      onChange={(e) => handleSettingChange('email', e.target.value)}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                    />
                  </div>

                  <div>
                    <label className="block text-left text-sm font-medium text-gray-700 mb-2">
                      タイムゾーン
                    </label>
                    <select
                      value={settings.timezone}
                      onChange={(e) => handleSettingChange('timezone', e.target.value)}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                    >
                      <option value="Asia/Tokyo">Asia/Tokyo (JST)</option>
                      <option value="Asia/Shanghai">Asia/Shanghai (CST)</option>
                      <option value="UTC">UTC</option>
                      <option value="America/New_York">America/New_York (EST)</option>
                    </select>
                  </div>

                  <div>
                    <label className="block text-left text-sm font-medium text-gray-700 mb-2">
                      言語
                    </label>
                    <select
                      value={settings.language}
                      onChange={(e) => handleSettingChange('language', e.target.value)}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                    >
                      <option value="ja">日本語</option>
                      <option value="en">English</option>
                      <option value="zh">中文</option>
                    </select>
                  </div>
                </div>
              )}

              {/* Notification Settings */}
              {activeTab === 'notifications' && (
                <div className="space-y-6">
                  <h2 className="text-xl font-semibold text-gray-900 mb-4">通知設定</h2>

                  <div className="flex items-start justify-between">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        メール通知を有効化
                      </label>
                      <p className="text-sm text-gray-500">
                        重要なイベントについてメール通知を受け取ります
                      </p>
                    </div>
                    <input
                      type="checkbox"
                      checked={settings.emailNotifications}
                      onChange={(e) => handleSettingChange('emailNotifications', e.target.checked)}
                      className="w-5 h-5 border-gray-300 rounded mt-1"
                    />
                  </div>

                  <div className="flex items-start justify-between">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        診断リマインダー
                      </label>
                      <p className="text-sm text-gray-500">
                        進行中の診断についてのリマインダーを受け取ります
                      </p>
                    </div>
                    <input
                      type="checkbox"
                      checked={settings.assessmentReminders}
                      onChange={(e) => handleSettingChange('assessmentReminders', e.target.checked)}
                      className="w-5 h-5 border-gray-300 rounded mt-1"
                    />
                  </div>

                  <div className="flex items-start justify-between">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        リード通知
                      </label>
                      <p className="text-sm text-gray-500">
                        新規リード獲得時に通知を受け取ります
                      </p>
                    </div>
                    <input
                      type="checkbox"
                      checked={settings.leadsNotifications}
                      onChange={(e) => handleSettingChange('leadsNotifications', e.target.checked)}
                      className="w-5 h-5 border-gray-300 rounded mt-1"
                    />
                  </div>

                  <div className="flex items-start justify-between">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        週間レポート
                      </label>
                      <p className="text-sm text-gray-500">
                        毎週のサマリーレポートを受け取ります
                      </p>
                    </div>
                    <input
                      type="checkbox"
                      checked={settings.weeklyReport}
                      onChange={(e) => handleSettingChange('weeklyReport', e.target.checked)}
                      className="w-5 h-5 border-gray-300 rounded mt-1"
                    />
                  </div>
                </div>
              )}

              {/* Integrations */}
              {activeTab === 'integrations' && (
                <div className="space-y-6">
                  <h2 className="text-xl font-semibold text-gray-900 mb-4">外部連携</h2>
                  <TeamsIntegration />
                </div>
              )}

              {/* Security Settings */}
              {activeTab === 'security' && (
                <div className="space-y-6">
                  <h2 className="text-xl font-semibold text-gray-900 mb-4">セキュリティ設定</h2>

                  <div className="flex items-start justify-between">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        二要素認証（2FA）
                      </label>
                      <p className="text-sm text-gray-500">
                        追加のセキュリティレイヤー
                      </p>
                    </div>
                    <input
                      type="checkbox"
                      checked={settings.twoFactorAuth}
                      onChange={(e) => handleSettingChange('twoFactorAuth', e.target.checked)}
                      className="w-5 h-5 border-gray-300 rounded mt-1"
                    />
                  </div>

                  <div className="flex items-start justify-between">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        ログインアラート
                      </label>
                      <p className="text-sm text-gray-500">
                        新規ログイン時にアラート通知
                      </p>
                    </div>
                    <input
                      type="checkbox"
                      checked={settings.loginAlerts}
                      onChange={(e) => handleSettingChange('loginAlerts', e.target.checked)}
                      className="w-5 h-5 border-gray-300 rounded mt-1"
                    />
                  </div>

                  <div>
                    <label className="block text-left text-sm font-medium text-gray-700 mb-2">
                      セッションタイムアウト（分）
                    </label>
                    <input
                      type="number"
                      value={settings.sessionTimeout}
                      onChange={(e) => handleSettingChange('sessionTimeout', parseInt(e.target.value))}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                    />
                  </div>

                  <div>
                    <label className="block text-left text-sm font-medium text-gray-700 mb-2">
                      APIキーローテーション（日数）
                    </label>
                    <input
                      type="number"
                      value={settings.apiKeyRotation}
                      onChange={(e) => handleSettingChange('apiKeyRotation', parseInt(e.target.value))}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                    />
                  </div>
                </div>
              )}

              {/* Appearance Settings */}
              {activeTab === 'appearance' && (
                <div className="space-y-6">
                  <h2 className="text-xl font-semibold text-gray-900 mb-4">表示設定</h2>

                  <div>
                    <label className="block text-left text-sm font-medium text-gray-700 mb-2">
                      テーマ
                    </label>
                    <select
                      value={settings.theme}
                      onChange={(e) => handleSettingChange('theme', e.target.value)}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                    >
                      <option value="light">ライト</option>
                      <option value="dark">ダーク</option>
                      <option value="auto">自動</option>
                    </select>
                  </div>

                  <div className="flex items-start justify-between">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        サイドバーを折りたたむ
                      </label>
                      <p className="text-sm text-gray-500">
                        デフォルトでサイドバーを折りたたむ
                      </p>
                    </div>
                    <input
                      type="checkbox"
                      checked={settings.sidebarCollapsed}
                      onChange={(e) => handleSettingChange('sidebarCollapsed', e.target.checked)}
                      className="w-5 h-5 border-gray-300 rounded mt-1"
                    />
                  </div>
                </div>
              )}

              {/* Advanced Settings */}
              {activeTab === 'advanced' && (
                <div className="space-y-6">
                  <h2 className="text-xl font-semibold text-gray-900 mb-4">詳細設定</h2>

                  <div className="flex items-start justify-between">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        API を有効化
                      </label>
                      <p className="text-sm text-gray-500">
                        外部からの API アクセスを許可
                      </p>
                    </div>
                    <input
                      type="checkbox"
                      checked={settings.apiEnabled}
                      onChange={(e) => handleSettingChange('apiEnabled', e.target.checked)}
                      className="w-5 h-5 border-gray-300 rounded mt-1"
                    />
                  </div>

                  <div className="flex items-start justify-between">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Webhooks を有効化
                      </label>
                      <p className="text-sm text-gray-500">
                        イベント駆動型の統合を許可
                      </p>
                    </div>
                    <input
                      type="checkbox"
                      checked={settings.webhooksEnabled}
                      onChange={(e) => handleSettingChange('webhooksEnabled', e.target.checked)}
                      className="w-5 h-5 border-gray-300 rounded mt-1"
                    />
                  </div>

                  <div>
                    <label className="block text-left text-sm font-medium text-gray-700 mb-2">
                      データ保持期間（日数）
                    </label>
                    <input
                      type="number"
                      value={settings.dataRetention}
                      onChange={(e) => handleSettingChange('dataRetention', parseInt(e.target.value))}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                    />
                    <p className="mt-1 text-sm text-gray-500">
                      0 = 無制限
                    </p>
                  </div>
                </div>
              )}

              {/* Save Button */}
              <div className="mt-8 pt-6 border-t border-gray-200">
                <button
                  onClick={handleSave}
                  className="px-6 py-2 bg-blue-600 text-white font-medium rounded-md hover:bg-blue-700 transition-colors"
                >
                  設定を保存
                </button>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
