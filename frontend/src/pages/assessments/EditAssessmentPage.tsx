import { useParams } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import AssessmentForm from '../../components/assessments/AssessmentForm';
import { assessmentService } from '../../services/assessmentService';

export default function EditAssessmentPage() {
  const { tenantId, assessmentId } = useParams<{ tenantId: string; assessmentId: string }>();

  const { data: assessment, isLoading, error } = useQuery({
    queryKey: ['assessment', tenantId, assessmentId],
    queryFn: () => assessmentService.get(tenantId!, assessmentId!),
    enabled: !!tenantId && !!assessmentId,
  });

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

  return (
    <div className="container mx-auto px-4 py-8 max-w-4xl">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Edit Assessment</h1>
        <p className="mt-2 text-sm text-gray-600">
          Update the assessment details.
        </p>
      </div>

      <div className="bg-white shadow rounded-lg p-6">
        <AssessmentForm 
          tenantId={tenantId} 
          assessmentId={assessmentId}
          initialData={assessment}
          mode="edit" 
        />
      </div>
    </div>
  );
}
