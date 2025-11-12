import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Bell, Settings, User, LogOut, Building2 } from 'lucide-react';
import { useAuthStore } from '../../store/authStore';

const Header: React.FC = () => {
  const navigate = useNavigate();
  const { user, logout } = useAuthStore();
  
  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const getPlanBadgeColor = (plan?: string) => {
    switch (plan) {
      case 'enterprise':
        return 'bg-purple-100 text-purple-800';
      case 'pro':
        return 'bg-blue-100 text-blue-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const getPlanLabel = (plan?: string) => {
    switch (plan) {
      case 'enterprise':
        return 'エンタープライズ';
      case 'pro':
        return 'プロ';
      default:
        return 'フリー';
    }
  };
  
  return (
    <header className="bg-white border-b border-gray-200 px-6 py-4">
      <div className="flex items-center justify-between">
        {/* Left side - Tenant Information */}
        <div className="flex items-center space-x-4">
          {user && (
            <div className="flex items-center gap-3">
              <Building2 size={18} className="text-gray-600" />
              <div>
                <p className="text-sm font-semibold text-gray-900">{user.tenant_name}</p>
                <p className="text-xs text-gray-500">{user.tenant_slug}</p>
              </div>
              {user.tenant_plan && (
                <span className={`ml-2 px-2 py-1 rounded text-xs font-medium ${getPlanBadgeColor(user.tenant_plan)}`}>
                  {getPlanLabel(user.tenant_plan)}
                </span>
              )}
            </div>
          )}
        </div>
        
        {/* Right side - user actions */}
        <div className="flex items-center space-x-4">
          {/* Notifications */}
          <button
            className="p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-lg transition-colors"
            title="通知"
          >
            <Bell className="w-5 h-5" />
          </button>
          
          {/* Settings */}
          <button
            className="p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-lg transition-colors"
            title="設定"
          >
            <Settings className="w-5 h-5" />
          </button>
          
          {/* User Profile */}
          <div
            className="flex items-center space-x-2 p-2 text-gray-700 rounded-lg"
            title="プロフィール"
          >
            <div className="w-8 h-8 bg-blue-500 rounded-full flex items-center justify-center">
              <User className="w-5 h-5 text-white" />
            </div>
            <div className="text-left">
              <p className="text-sm font-medium">{user?.name || 'ユーザー'}</p>
              <p className="text-xs text-gray-500">{user?.role === 'system_admin' ? 'システム管理者' : user?.role === 'tenant_admin' ? 'テナント管理者' : '一般ユーザー'}</p>
            </div>
          </div>
          
          {/* Logout */}
          <button
            onClick={handleLogout}
            className="flex items-center space-x-2 p-2 text-gray-700 hover:bg-gray-100 rounded-lg transition-colors border-l border-gray-200"
            title="ログアウト"
          >
            <LogOut className="w-5 h-5" />
            <span className="text-sm font-medium">ログアウト</span>
          </button>
        </div>
      </div>
    </header>
  );
};

export { Header };
