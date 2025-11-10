import { useParams } from 'react-router-dom';
import AssessmentList from '../../components/assessments/AssessmentList';

export default function AssessmentsPage() {
  const { tenantId } = useParams<{ tenantId: string }>();

  if (!tenantId) {
    return <div>Invalid tenant ID</div>;
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <AssessmentList tenantId={tenantId} />
    </div>
  );
}
