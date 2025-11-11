import { useParams } from 'react-router-dom';
import AssessmentList from '../../components/assessments/AssessmentList';

export function AssessmentsPage() {
  const { tenantId } = useParams<{ tenantId: string }>();

  if (!tenantId) {
    return <div>Invalid tenant ID</div>;
  }

  return (
    <div className="container mx-auto">
      <AssessmentList tenantId={tenantId} />
    </div>
  );
}

export default AssessmentsPage;
