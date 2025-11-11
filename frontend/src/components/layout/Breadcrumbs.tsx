import { Link, useLocation } from 'react-router-dom';
import { ChevronRightIcon } from 'lucide-react';

interface BreadcrumbItem {
  label: string;
  path: string | null;
}

export function Breadcrumbs() {
  const location = useLocation();

  const generateBreadcrumbs = (): BreadcrumbItem[] => {
    const pathSegments = location.pathname.split('/').filter(Boolean);
    const breadcrumbs: BreadcrumbItem[] = [
      { label: 'ダッシュボード', path: '/dashboard' },
    ];

    // Parse path segments
    for (let i = 0; i < pathSegments.length; i++) {
      const segment = pathSegments[i];

      if (segment === 'tenants') {
        // Skip tenant ID segment
        i++; // Skip the tenant ID
        continue;
      }

      if (segment === 'assessments') {
        breadcrumbs.push({
          label: '診断管理',
          path: i === pathSegments.length - 1 ? null : location.pathname.split('/').slice(0, i + 3).join('/'),
        });
      } else if (segment === 'leads') {
        breadcrumbs.push({
          label: 'リード管理',
          path: i === pathSegments.length - 1 ? null : location.pathname.split('/').slice(0, i + 3).join('/'),
        });
      } else if (segment === 'analytics') {
        breadcrumbs.push({
          label: '分析',
          path: null,
        });
      } else if (segment === 'settings') {
        breadcrumbs.push({
          label: '設定',
          path: null,
        });
      } else if (segment === 'create') {
        breadcrumbs.push({
          label: '新規作成',
          path: null,
        });
      } else if (segment === 'edit') {
        breadcrumbs.push({
          label: '編集',
          path: null,
        });
      } else if (segment.match(/^[a-f0-9-]{36}$/)) {
        // UUID pattern - skip for now
        // In a real app, you'd fetch the name
        continue;
      }
    }

    return breadcrumbs;
  };

  const breadcrumbs = generateBreadcrumbs();

  // Don't show breadcrumbs on dashboard
  if (location.pathname === '/dashboard') {
    return null;
  }

  return (
    <nav className="flex items-center space-x-2 text-sm px-6 py-3 bg-gray-50 border-b border-gray-200">
      {breadcrumbs.map((item, index) => (
        <div key={index} className="flex items-center">
          {index > 0 && (
            <ChevronRightIcon className="w-4 h-4 text-gray-400 mx-2" />
          )}
          {item.path ? (
            <Link
              to={item.path}
              className="text-blue-600 hover:text-blue-800 hover:underline"
            >
              {item.label}
            </Link>
          ) : (
            <span className="text-gray-700 font-medium">{item.label}</span>
          )}
        </div>
      ))}
    </nav>
  );
}
