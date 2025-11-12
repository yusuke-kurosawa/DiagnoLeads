import { useParams } from 'react-router-dom';
import AssessmentForm from '../../components/assessments/AssessmentForm';

export function CreateAssessmentPage() {
  const { tenantId } = useParams<{ tenantId: string }>();

  if (!tenantId) {
    return <div>Invalid tenant ID</div>;
  }

  return (
    <div className="container mx-auto max-w-4xl">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Create Assessment</h1>
        <p className="mt-2 text-sm text-gray-600">
          Create a new diagnostic assessment for your leads.
        </p>
      </div>

      <div className="bg-white shadow rounded-lg p-6">
        <AssessmentForm tenantId={tenantId} mode="create" />
      </div>
    </div>
  );
}

export default CreateAssessmentPage;
