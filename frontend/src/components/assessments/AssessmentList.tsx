import { useQuery } from '@tanstack/react-query';
import { assessmentService, type Assessment } from '../../services/assessmentService';
import { Link } from 'react-router-dom';
import { ClipboardList, Plus } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { SkeletonCard } from '@/components/ui/skeleton';
import { EmptyState, ErrorEmptyState } from '@/components/ui/empty-state';

interface AssessmentListProps {
  tenantId: string;
}

export default function AssessmentList({ tenantId }: AssessmentListProps) {
  const { data: assessments, isLoading, error } = useQuery({
    queryKey: ['assessments', tenantId],
    queryFn: () => assessmentService.list(tenantId),
  });



  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">診断管理</h2>
          <p className="text-sm text-gray-600 mt-1">
            診断コンテンツを作成・管理します
          </p>
        </div>
        <Link to={`/tenants/${tenantId}/assessments/create`}>
          <Button variant="primary" leftIcon={<Plus className="w-4 h-4" />}>
            診断を作成
          </Button>
        </Link>
      </div>

      {/* Loading State */}
      {isLoading && (
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {Array.from({ length: 6 }).map((_, idx) => (
            <SkeletonCard key={idx} />
          ))}
        </div>
      )}

      {/* Error State */}
      {error && (
        <div className="bg-white shadow-sm rounded-lg border border-gray-200 p-4">
          <ErrorEmptyState
            onRetry={() => window.location.reload()}
            errorMessage="診断の読み込みに失敗しました。ネットワーク接続を確認してください。"
          />
        </div>
      )}

      {/* Results */}
      {!isLoading && !error && (
        <>
          {assessments && assessments.length > 0 ? (
            <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
              {assessments.map((assessment: Assessment) => (
                <Link
                  key={assessment.id}
                  to={`/tenants/${tenantId}/assessments/${assessment.id}`}
                  className="block p-6 bg-white border border-gray-200 rounded-lg shadow-sm hover:shadow-md hover:-translate-y-1 transition-all duration-200"
                >
                  <div className="flex justify-between items-start mb-3">
                    <h3 className="text-lg font-semibold text-gray-900 line-clamp-1">
                      {assessment.title}
                    </h3>
                    <Badge
                      variant={
                        assessment.status === 'published'
                          ? 'success'
                          : assessment.status === 'draft'
                          ? 'warning'
                          : 'default'
                      }
                      size="sm"
                    >
                      {assessment.status === 'published'
                        ? '公開中'
                        : assessment.status === 'draft'
                        ? '下書き'
                        : assessment.status}
                    </Badge>
                  </div>
                  {assessment.description && (
                    <p className="text-sm text-gray-600 mb-4 line-clamp-2">
                      {assessment.description}
                    </p>
                  )}
                  <div className="flex items-center justify-between text-xs text-gray-500">
                    <span>
                      {assessment.ai_generated === 'ai' ? '🤖 AI生成' : '✍️ 手動作成'}
                    </span>
                    <span>
                      {new Date(assessment.created_at).toLocaleDateString('ja-JP')}
                    </span>
                  </div>
                </Link>
              ))}
            </div>
          ) : (
            /* Empty State */
            <div className="bg-white shadow-sm rounded-lg border border-gray-200 p-4">
              <EmptyState
                icon={<ClipboardList className="w-16 h-16" />}
                title="診断がありません"
                description="まだ診断が作成されていません。最初の診断を作成して、リード獲得を開始しましょう。"
                action={{
                  label: '診断を作成',
                  onClick: () => window.location.href = `/tenants/${tenantId}/assessments/create`,
                  variant: 'primary',
                  icon: <Plus className="w-4 h-4" />,
                }}
              />
            </div>
          )}
        </>
      )}
    </div>
  );
}
