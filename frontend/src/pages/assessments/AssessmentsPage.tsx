import { useParams, useNavigate } from 'react-router-dom';
import { useEffect } from 'react';
import { useAuthStore } from '../../store/authStore';
import AssessmentList from '../../components/assessments/AssessmentList';

export function AssessmentsPage() {
  const { tenantId } = useParams<{ tenantId: string }>();
  const navigate = useNavigate();
  const { user } = useAuthStore();

  // Redirect to correct tenant ID if URL has invalid demo-tenant
  useEffect(() => {
    if (tenantId === 'demo-tenant' && user?.tenant_id) {
      navigate(`/tenants/${user.tenant_id}/assessments`, { replace: true });
    }
  }, [tenantId, user?.tenant_id, navigate]);

  if (!tenantId || tenantId === 'demo-tenant') {
    return <div className="p-6">Loading...</div>;
  }

  return (
    <div className="container mx-auto">
      <AssessmentList tenantId={tenantId} />
    </div>
  );
}

export default AssessmentsPage;
