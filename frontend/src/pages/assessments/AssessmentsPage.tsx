import { useParams } from 'react-router-dom';
import AssessmentList from '../../components/assessments/AssessmentList';
import { Layout } from '../../components/layout/Layout';

export function AssessmentsPage() {
  const { tenantId } = useParams<{ tenantId: string }>();

  if (!tenantId) {
    return <div>Invalid tenant ID</div>;
  }

  return (
    <Layout>
      <div className="container mx-auto">
        <AssessmentList tenantId={tenantId} />
      </div>
    </Layout>
  );
}

export default AssessmentsPage;
