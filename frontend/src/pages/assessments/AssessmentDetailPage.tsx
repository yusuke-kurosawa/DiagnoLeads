import { useParams, useNavigate, Link } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useState } from 'react';
import { assessmentService } from '../../services/assessmentService';
import { ABTestManager } from '../../components/assessments/ABTestManager';
import { SMSCampaignManager } from '../../components/assessments/SMSCampaignManager';
import { QRCodeDownload } from '../../components/assessments/QRCodeDownload';

type TabType = 'overview' | 'ab-tests' | 'sms' | 'qr-codes';

export function AssessmentDetailPage() {
  const { tenantId, assessmentId } = useParams<{ tenantId: string; assessmentId: string }>();
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [activeTab, setActiveTab] = useState<TabType>('overview');

  const { data: assessment, isLoading, error } = useQuery({
    queryKey: ['assessment', tenantId, assessmentId],
    queryFn: () => assessmentService.get(tenantId!, assessmentId!),
    enabled: !!tenantId && !!assessmentId,
  });

  const deleteMutation = useMutation({
    mutationFn: () => {
      if (!tenantId || !assessmentId) throw new Error('Missing IDs');
      return assessmentService.delete(tenantId, assessmentId);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['assessments', tenantId] });
      navigate(`/tenants/${tenantId}/assessments`);
    },
  });

  const handleDelete = () => {
    if (window.confirm('Are you sure you want to delete this assessment?')) {
      deleteMutation.mutate();
    }
  };

  if (!tenantId || !assessmentId) {
    return <div>Invalid tenant or assessment ID</div>;
  }

  if (isLoading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="bg-red-50 border border-red-200 text-red-800 px-4 py-3 rounded">
          <p className="font-bold">Error loading assessment</p>
          <p className="text-sm">{(error as Error).message}</p>
        </div>
      </div>
    );
  }

  if (!assessment) {
    return <div>Assessment not found</div>;
  }

  const tabs: { id: TabType; label: string }[] = [
    { id: 'overview', label: '概要' },
    { id: 'ab-tests', label: 'A/Bテスト' },
    { id: 'sms', label: 'SMSキャンペーン' },
    { id: 'qr-codes', label: 'QRコード' },
  ];

  return (
    <div className="container mx-auto max-w-6xl px-4 py-8">
      {deleteMutation.error && (
        <div className="mb-4 bg-red-50 border border-red-200 text-red-800 px-4 py-3 rounded">
          <p className="font-bold">Error deleting assessment</p>
          <p className="text-sm">{(deleteMutation.error as Error).message}</p>
        </div>
      )}

      <div className="bg-white shadow rounded-lg overflow-hidden">
        {/* Header */}
        <div className="px-6 py-4 border-b border-gray-200 bg-gray-50">
          <div className="flex justify-between items-start">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">{assessment.title}</h1>
              <div className="mt-2 flex items-center space-x-4">
                <span
                  className={`px-3 py-1 text-sm font-medium rounded-full ${
                    assessment.status === 'published'
                      ? 'bg-green-100 text-green-800'
                      : assessment.status === 'draft'
                      ? 'bg-yellow-100 text-yellow-800'
                      : 'bg-gray-100 text-gray-800'
                  }`}
                >
                  {assessment.status}
                </span>
                <span className="text-sm text-gray-500">
                  {assessment.ai_generated === 'ai' ? '🤖 AI Generated' : 
                   assessment.ai_generated === 'hybrid' ? '🤝 Hybrid' : '✍️ Manual'}
                </span>
              </div>
            </div>
            <div className="flex space-x-2">
              <Link
                to={`/tenants/${tenantId}/assessments/${assessmentId}/edit`}
                className="px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50"
              >
                Edit
              </Link>
              <button
                onClick={handleDelete}
                disabled={deleteMutation.isPending}
                className="px-4 py-2 border border-red-300 rounded-md shadow-sm text-sm font-medium text-red-700 bg-white hover:bg-red-50 disabled:opacity-50"
              >
                {deleteMutation.isPending ? 'Deleting...' : 'Delete'}
              </button>
            </div>
          </div>
        </div>

        {/* Tabs */}
        <div className="border-b border-gray-200">
          <nav className="flex -mb-px">
            {tabs.map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`px-6 py-3 text-sm font-medium border-b-2 transition-colors ${
                  activeTab === tab.id
                    ? 'border-blue-600 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                {tab.label}
              </button>
            ))}
          </nav>
        </div>

        {/* Tab Content */}
        <div className="px-6 py-6">
          {activeTab === 'overview' && (
            <div className="space-y-6">
          {assessment.description && (
            <div>
              <h2 className="text-sm font-medium text-gray-500 uppercase tracking-wide">
                Description
              </h2>
              <p className="mt-2 text-gray-900">{assessment.description}</p>
            </div>
          )}

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {assessment.topic && (
              <div>
                <h2 className="text-sm font-medium text-gray-500 uppercase tracking-wide">
                  Topic
                </h2>
                <p className="mt-2 text-gray-900">{assessment.topic}</p>
              </div>
            )}

            {assessment.industry && (
              <div>
                <h2 className="text-sm font-medium text-gray-500 uppercase tracking-wide">
                  Industry
                </h2>
                <p className="mt-2 text-gray-900">{assessment.industry}</p>
              </div>
            )}
          </div>

          <div className="border-t border-gray-200 pt-6">
            <h2 className="text-sm font-medium text-gray-500 uppercase tracking-wide mb-4">
              Metadata
            </h2>
            <dl className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <dt className="text-sm text-gray-500">Created</dt>
                <dd className="mt-1 text-sm text-gray-900">
                  {new Date(assessment.created_at).toLocaleString()}
                </dd>
              </div>
              <div>
                <dt className="text-sm text-gray-500">Last Updated</dt>
                <dd className="mt-1 text-sm text-gray-900">
                  {new Date(assessment.updated_at).toLocaleString()}
                </dd>
              </div>
            </dl>
          </div>
            </div>
          )}

          {activeTab === 'ab-tests' && (
            <ABTestManager assessmentId={assessmentId!} tenantId={tenantId!} />
          )}

          {activeTab === 'sms' && (
            <SMSCampaignManager assessmentId={assessmentId!} tenantId={tenantId!} />
          )}

          {activeTab === 'qr-codes' && assessment.qr_code_url && (
            <QRCodeDownload
              qrCodeId={assessment.id}
              tenantId={tenantId!}
              qrCodeUrl={assessment.qr_code_url}
            />
          )}

          {activeTab === 'qr-codes' && !assessment.qr_code_url && (
            <div className="text-center py-12 bg-gray-50 rounded-lg">
              <p className="text-gray-600">この診断にはまだQRコードが作成されていません。</p>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="px-6 py-4 border-t border-gray-200 bg-gray-50">
          <Link
            to={`/tenants/${tenantId}/assessments`}
            className="text-sm text-blue-600 hover:text-blue-800"
          >
            ← Back to assessments
          </Link>
        </div>
      </div>
    </div>
  );
}


export default AssessmentDetailPage;
