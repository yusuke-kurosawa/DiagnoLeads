import { Link, useLocation, useParams } from 'react-router-dom';
import { 
  HomeIcon, 
  FileTextIcon, 
  UsersIcon, 
  BarChart3Icon, 
  SettingsIcon 
} from 'lucide-react';

interface NavigationItem {
  icon: React.ComponentType<{ className?: string }>;
  label: string;
  path: string;
  badge?: number;
}

export function Sidebar() {
  const location = useLocation();
  const { tenantId } = useParams();
  
  // Default tenant ID for demo (should come from auth store)
  const currentTenantId = tenantId || 'demo-tenant';
  
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
    <aside className="w-64 bg-gray-900 text-white min-h-screen flex flex-col">
      {/* Logo */}
      <div className="p-6 border-b border-gray-800">
        <h1 className="text-2xl font-bold text-blue-400">DiagnoLeads</h1>
        <p className="text-xs text-gray-400 mt-1">診断サービスプラットフォーム</p>
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
                >
                  <Icon className="w-5 h-5" />
                  <span className="font-medium">{item.label}</span>
                  {item.badge && (
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
      <div className="p-4 border-t border-gray-800">
        <div className="text-xs text-gray-400">
          <p>© 2025 DiagnoLeads</p>
          <p className="mt-1">Version 0.1.0</p>
        </div>
      </div>
    </aside>
  );
}
