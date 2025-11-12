import { useState } from 'react';
import { Link, useLocation, useParams } from 'react-router-dom';
import { useAuthStore } from '../../store/authStore';
import { 
  HomeIcon, 
  FileTextIcon, 
  UsersIcon, 
  BarChart3Icon, 
  SettingsIcon,
  ChevronLeft,
  ChevronRight
} from 'lucide-react';

interface NavigationItem {
  icon: React.ComponentType<{ className?: string }>;
  label: string;
  path: string;
  badge?: number;
}

export function Sidebar() {
  const [isOpen, setIsOpen] = useState(true);
  const location = useLocation();
  const { tenantId } = useParams();
  const { user } = useAuthStore();
  
  // Use tenant ID from URL params or fallback to authenticated user's tenant ID
  const currentTenantId = tenantId || user?.tenant_id || 'demo-tenant';
  
  const navigationItems: NavigationItem[] = [
    {
      icon: HomeIcon,
      label: 'ダッシュボード',
      path: '/dashboard',
    },
    {
      icon: FileTextIcon,
      label: '診断管理',
      path: `/tenants/${currentTenantId}/assessments`,
    },
    {
      icon: UsersIcon,
      label: 'リード管理',
      path: `/tenants/${currentTenantId}/leads`,
    },
    {
      icon: BarChart3Icon,
      label: '分析',
      path: `/tenants/${currentTenantId}/analytics`,
    },
    {
      icon: SettingsIcon,
      label: '設定',
      path: `/tenants/${currentTenantId}/settings`,
    },
  ];

  const isActive = (path: string) => {
    return location.pathname === path || location.pathname.startsWith(path);
  };

  return (
    <aside className={`${isOpen ? 'w-64' : 'w-20'} bg-gray-900 text-white min-h-screen flex flex-col transition-all duration-300`}>
      {/* Logo + Toggle */}
      <div className="p-4 border-b border-gray-800 flex items-center justify-between">
        {isOpen && (
          <div>
            <h1 className="text-2xl font-bold text-blue-400">DiagnoLeads</h1>
            <p className="text-xs text-gray-400 mt-1">診断サービスプラットフォーム</p>
          </div>
        )}
        <button
          onClick={() => setIsOpen(!isOpen)}
          className="p-2 hover:bg-gray-800 rounded-lg transition-colors flex-shrink-0"
          title={isOpen ? '折りたたむ' : '展開'}
        >
          {isOpen ? (
            <ChevronLeft className="w-5 h-5" />
          ) : (
            <ChevronRight className="w-5 h-5" />
          )}
        </button>
      </div>

      {/* Navigation */}
      <nav className="flex-1 p-4">
        <ul className="space-y-2">
          {navigationItems.map((item) => {
            const Icon = item.icon;
            const active = isActive(item.path);
            
            return (
              <li key={item.path}>
                <Link
                  to={item.path}
                  className={`
                    flex items-center gap-3 px-4 py-3 rounded-lg
                    transition-colors duration-200
                    ${
                      active
                        ? 'bg-blue-600 text-white'
                        : 'text-gray-300 hover:bg-gray-800 hover:text-white'
                    }
                  `}
                  title={!isOpen ? item.label : undefined}
                >
                  <Icon className="w-5 h-5 flex-shrink-0" />
                  {isOpen && <span className="font-medium">{item.label}</span>}
                  {isOpen && item.badge && (
                    <span className="ml-auto bg-red-500 text-white text-xs px-2 py-1 rounded-full">
                      {item.badge}
                    </span>
                  )}
                </Link>
              </li>
            );
          })}
        </ul>
      </nav>

      {/* Footer */}
      {isOpen && (
        <div className="p-4 border-t border-gray-800">
          <div className="text-xs text-gray-400">
            <p>© 2025 DiagnoLeads</p>
            <p className="mt-1">Version 0.1.0</p>
          </div>
        </div>
      )}
    </aside>
  );
}
