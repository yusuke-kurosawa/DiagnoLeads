import { useParams } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { AssessmentBuilder } from '../../components/assessments/AssessmentBuilder';
import { assessmentService } from '../../services/assessmentService';

export function EditAssessmentPage() {
  const { tenantId, assessmentId } = useParams<{ tenantId: string; assessmentId: string }>();
  const queryClient = useQueryClient();

  const { data: assessment, isLoading, error } = useQuery({
    queryKey: ['assessment', tenantId, assessmentId],
    queryFn: () => assessmentService.get(tenantId!, assessmentId!),
    enabled: !!tenantId && !!assessmentId,
  });

  const updateMutation = useMutation({
    mutationFn: async (data: {
      title?: string;
      description?: string;
      status?: string;
    }) => {
      return assessmentService.update(tenantId!, assessmentId!, data);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['assessment', tenantId, assessmentId] });
    },
  });

  const publishMutation = useMutation({
    mutationFn: async () => {
      return assessmentService.publish(tenantId!, assessmentId!);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['assessment', tenantId, assessmentId] });
      queryClient.invalidateQueries({ queryKey: ['assessments', tenantId] });
    },
  });

  const unpublishMutation = useMutation({
    mutationFn: async () => {
      return assessmentService.unpublish(tenantId!, assessmentId!);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['assessment', tenantId, assessmentId] });
      queryClient.invalidateQueries({ queryKey: ['assessments', tenantId] });
    },
  });

  if (!tenantId || !assessmentId) {
    return <div>Invalid tenant or assessment ID</div>;
  }

  if (isLoading) {
    return (
      <div className="flex justify-center items-center h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">診断を読み込み中...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex justify-center items-center h-screen">
        <div className="bg-red-50 border border-red-200 text-red-800 px-6 py-4 rounded-lg max-w-md">
          <p className="font-bold mb-2">エラーが発生しました</p>
          <p className="text-sm">{(error as Error).message}</p>
        </div>
      </div>
    );
  }

  if (!assessment) {
    return (
      <div className="flex justify-center items-center h-screen">
        <p className="text-gray-600">診断が見つかりません</p>
      </div>
    );
  }

  const handleUpdate = (updatedAssessment: typeof assessment) => {
    // Optimistic update (optional)
    queryClient.setQueryData(['assessment', tenantId, assessmentId], updatedAssessment);
  };

  const handleSave = async (updatedAssessment: typeof assessment) => {
    await updateMutation.mutateAsync({
      title: updatedAssessment.title,
      description: updatedAssessment.description,
      status: updatedAssessment.status,
      // Note: Backend needs to support questions field
      // For now, we'll just save basic fields
    });
  };

  const handlePublish = async () => {
    await publishMutation.mutateAsync();
  };

  const handleUnpublish = async () => {
    await unpublishMutation.mutateAsync();
  };

  return (
    <AssessmentBuilder
      assessment={assessment}
      onUpdate={handleUpdate}
      onSave={handleSave}
      onPublish={handlePublish}
      onUnpublish={handleUnpublish}
    />
  );
}

export default EditAssessmentPage;
