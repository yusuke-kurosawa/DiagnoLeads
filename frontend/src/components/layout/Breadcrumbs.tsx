import { Link, useLocation } from 'react-router-dom';
import { ChevronRightIcon } from 'lucide-react';

interface BreadcrumbItem {
  label: string;
  href?: string;
}

interface BreadcrumbsProps {
  items?: BreadcrumbItem[];
}

export function Breadcrumbs({ items: customItems }: BreadcrumbsProps = {}) {
  const location = useLocation();

  const generateBreadcrumbs = (): BreadcrumbItem[] => {
    const pathSegments = location.pathname.split('/').filter(Boolean);
    const breadcrumbs: BreadcrumbItem[] = [
      { label: 'ダッシュボード', href: '/dashboard' },
    ];

    // Extract tenant ID from path
    let tenantId = '';
    if (pathSegments[0] === 'tenants' && pathSegments[1]) {
      tenantId = pathSegments[1];
    }

    // Parse path segments
    let i = 2; // Start after 'tenants/tenantId'
    while (i < pathSegments.length) {
      const segment = pathSegments[i];
      const isLast = i === pathSegments.length - 1;

      if (segment === 'assessments') {
        const href = isLast ? undefined : `/tenants/${tenantId}/assessments`;
        breadcrumbs.push({
          label: '診断管理',
          href,
        });
      } else if (segment === 'leads') {
        const href = isLast ? undefined : `/tenants/${tenantId}/leads`;
        breadcrumbs.push({
          label: 'リード管理',
          href,
        });
      } else if (segment === 'analytics') {
        const href = isLast ? undefined : `/tenants/${tenantId}/analytics`;
        breadcrumbs.push({
          label: '分析',
          href,
        });
      } else if (segment === 'settings') {
        const href = isLast ? undefined : `/tenants/${tenantId}/settings`;
        breadcrumbs.push({
          label: '設定',
          href,
        });
      } else if (segment === 'create') {
        breadcrumbs.push({
          label: '新規作成',
        });
      } else if (segment === 'edit') {
        breadcrumbs.push({
          label: '編集',
        });
      } else if (segment.match(/^[a-f0-9-]{36}$/)) {
        // UUID pattern - detail page
        breadcrumbs.push({
          label: '詳細',
        });
      }

      i++;
    }

    return breadcrumbs;
  };

  const breadcrumbs = customItems || generateBreadcrumbs();

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
          {item.href ? (
            <Link
              to={item.href}
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
