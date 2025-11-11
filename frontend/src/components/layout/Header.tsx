import React from 'react';
import { useParams } from 'react-router-dom';
import { Bell, Settings, User } from 'lucide-react';

const Header: React.FC = () => {
  const { tenantId } = useParams();
  
  return (
    <header className="bg-white border-b border-gray-200 px-6 py-4">
      <div className="flex items-center justify-between">
        {/* Left side - could add breadcrumbs or page title */}
        <div className="flex items-center space-x-4">
          <h1 className="text-xl font-semibold text-gray-900">
            DiagnoLeads
          </h1>
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
          <button
            className="flex items-center space-x-2 p-2 text-gray-700 hover:bg-gray-100 rounded-lg transition-colors"
            title="プロフィール"
          >
            <div className="w-8 h-8 bg-blue-500 rounded-full flex items-center justify-center">
              <User className="w-5 h-5 text-white" />
            </div>
            <span className="text-sm font-medium">ユーザー</span>
          </button>
        </div>
      </div>
    </header>
  );
};

export default Header;
