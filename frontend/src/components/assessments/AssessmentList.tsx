import { useQuery } from '@tanstack/react-query';
import { assessmentService, type Assessment } from '../../services/assessmentService';
import { Link } from 'react-router-dom';

interface AssessmentListProps {
  tenantId: string;
}

export default function AssessmentList({ tenantId }: AssessmentListProps) {
  const { data: assessments, isLoading, error } = useQuery({
    queryKey: ['assessments', tenantId],
    queryFn: () => assessmentService.list(tenantId),
  });

  if (isLoading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 text-red-800 px-4 py-3 rounded">
        <p className="font-bold">Error loading assessments</p>
        <p className="text-sm">{(error as Error).message}</p>
      </div>
    );
  }

  if (!assessments || assessments.length === 0) {
    return (
      <div className="text-center py-12">
        <svg
          className="mx-auto h-12 w-12 text-gray-400"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
          />
        </svg>
        <h3 className="mt-2 text-sm font-medium text-gray-900">No assessments</h3>
        <p className="mt-1 text-sm text-gray-500">Get started by creating a new assessment.</p>
        <div className="mt-6">
          <Link
            to={`/tenants/${tenantId}/assessments/new`}
            className="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700"
          >
            Create Assessment
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold text-gray-900">Assessments</h2>
        <Link
          to={`/tenants/${tenantId}/assessments/new`}
          className="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700"
        >
          Create Assessment
        </Link>
      </div>

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {assessments.map((assessment: Assessment) => (
          <Link
            key={assessment.id}
            to={`/tenants/${tenantId}/assessments/${assessment.id}`}
            className="block p-6 bg-white border border-gray-200 rounded-lg shadow hover:bg-gray-50 transition"
          >
            <div className="flex justify-between items-start mb-2">
              <h3 className="text-xl font-semibold text-gray-900">{assessment.title}</h3>
              <span
                className={`px-2 py-1 text-xs font-medium rounded-full ${
                  assessment.status === 'published'
                    ? 'bg-green-100 text-green-800'
                    : assessment.status === 'draft'
                    ? 'bg-yellow-100 text-yellow-800'
                    : 'bg-gray-100 text-gray-800'
                }`}
              >
                {assessment.status}
              </span>
            </div>
            {assessment.description && (
              <p className="text-sm text-gray-600 mb-4 line-clamp-2">
                {assessment.description}
              </p>
            )}
            <div className="flex items-center text-xs text-gray-500">
              <span className="mr-4">
                {assessment.ai_generated === 'ai' ? '🤖 AI Generated' : '✍️ Manual'}
              </span>
              <span>
                {new Date(assessment.created_at).toLocaleDateString()}
              </span>
            </div>
          </Link>
        ))}
      </div>
    </div>
  );
}
