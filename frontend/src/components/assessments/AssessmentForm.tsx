import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { assessmentService, type CreateAssessmentData } from '../../services/assessmentService';
import { useNavigate } from 'react-router-dom';

const assessmentSchema = z.object({
  title: z.string().min(1, '診断名は必須です').max(255, '診断名は255文字以下である必要があります'),
  description: z.string().optional(),
  status: z.enum(['draft', 'published', 'archived']),
  topic: z.string().max(255).optional(),
  industry: z.string().max(100).optional(),
  ai_generated: z.enum(['manual', 'ai', 'hybrid']),
});

type AssessmentFormData = z.infer<typeof assessmentSchema>;

interface AssessmentFormProps {
  tenantId: string;
  initialData?: Partial<AssessmentFormData>;
  assessmentId?: string;
  mode: 'create' | 'edit';
}

export default function AssessmentForm({ 
  tenantId, 
  initialData, 
  assessmentId,
  mode 
}: AssessmentFormProps) {
  const navigate = useNavigate();
  const queryClient = useQueryClient();

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<AssessmentFormData>({
    resolver: zodResolver(assessmentSchema),
    defaultValues: initialData || {
      status: 'draft',
      ai_generated: 'manual',
    },
  });

  const createMutation = useMutation({
    mutationFn: (data: CreateAssessmentData) => 
      assessmentService.create(tenantId, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['assessments', tenantId] });
      navigate(`/tenants/${tenantId}/assessments`);
    },
  });

  const updateMutation = useMutation({
    mutationFn: (data: CreateAssessmentData) => 
      assessmentService.update(tenantId, assessmentId!, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['assessments', tenantId] });
      queryClient.invalidateQueries({ queryKey: ['assessment', tenantId, assessmentId] });
      navigate(`/tenants/${tenantId}/assessments/${assessmentId}`);
    },
  });

  const onSubmit = (data: AssessmentFormData) => {
    if (mode === 'create') {
      createMutation.mutate(data);
    } else {
      updateMutation.mutate(data);
    }
  };

  const mutation = mode === 'create' ? createMutation : updateMutation;

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
      {mutation.error && (
        <div className="bg-red-50 border border-red-200 text-red-800 px-4 py-3 rounded">
          <p className="font-bold">エラー</p>
          <p className="text-sm">{(mutation.error as Error).message}</p>
        </div>
      )}

      <div>
        <label htmlFor="title" className="block text-sm font-medium text-gray-700 mb-1">
          診断名 <span className="text-red-500">*</span>
        </label>
        <input
          {...register('title')}
          type="text"
          id="title"
          className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          placeholder="例：マーケティング効果測定診断"
        />
        {errors.title && (
          <p className="mt-1 text-sm text-red-600">{errors.title.message}</p>
        )}
      </div>

      <div>
        <label htmlFor="description" className="block text-sm font-medium text-gray-700 mb-1">
          説明
        </label>
        <textarea
          {...register('description')}
          id="description"
          rows={4}
          className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          placeholder="この診断の説明を入力してください"
        />
        {errors.description && (
          <p className="mt-1 text-sm text-red-600">{errors.description.message}</p>
        )}
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div>
          <label htmlFor="topic" className="block text-sm font-medium text-gray-700 mb-1">
            トピック
          </label>
          <input
            {...register('topic')}
            type="text"
            id="topic"
            className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            placeholder="例：マーケティング戦略"
          />
          {errors.topic && (
            <p className="mt-1 text-sm text-red-600">{errors.topic.message}</p>
          )}
        </div>

        <div>
          <label htmlFor="industry" className="block text-sm font-medium text-gray-700 mb-1">
            業界
          </label>
          <input
            {...register('industry')}
            type="text"
            id="industry"
            className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            placeholder="例：テクノロジー"
          />
          {errors.industry && (
            <p className="mt-1 text-sm text-red-600">{errors.industry.message}</p>
          )}
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div>
          <label htmlFor="status" className="block text-sm font-medium text-gray-700 mb-1">
            ステータス
          </label>
          <select
            {...register('status')}
            id="status"
            className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          >
            <option value="draft">下書き</option>
            <option value="published">公開中</option>
            <option value="archived">アーカイブ</option>
          </select>
          {errors.status && (
            <p className="mt-1 text-sm text-red-600">{errors.status.message}</p>
          )}
        </div>

        <div>
          <label htmlFor="ai_generated" className="block text-sm font-medium text-gray-700 mb-1">
            作成方式
          </label>
          <select
            {...register('ai_generated')}
            id="ai_generated"
            className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          >
            <option value="manual">手動作成</option>
            <option value="ai">AI生成</option>
            <option value="hybrid">ハイブリッド</option>
          </select>
          {errors.ai_generated && (
            <p className="mt-1 text-sm text-red-600">{errors.ai_generated.message}</p>
          )}
        </div>
      </div>

      <div className="flex justify-end space-x-4 pt-4">
        <button
          type="button"
          onClick={() => navigate(`/tenants/${tenantId}/assessments`)}
          className="px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
        >
          キャンセル
        </button>
        <button
          type="submit"
          disabled={isSubmitting || mutation.isPending}
          className="px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {mutation.isPending ? '保存中...' : mode === 'create' ? '作成' : '更新'}
        </button>
      </div>
    </form>
  );
}
