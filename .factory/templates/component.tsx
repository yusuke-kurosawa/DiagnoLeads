/**
 * React Component Template
 * Reactコンポーネントのテンプレート
 * 
 * 使い方:
 * 1. このファイルをコピーして新しいコンポーネントファイルを作成
 * 2. ResourceNameを実際のコンポーネント名に置換
 * 3. 必要な機能を実装
 */

import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';

// Types
interface ResourceName {  // 置換: ResourceName
  id: string;
  tenantId: string;
  name: string;
  description?: string;
  status: 'active' | 'inactive' | 'archived';
  isActive: boolean;
  createdBy: string;
  createdAt: string;
  updatedAt: string;
}

interface ResourceNameFormData {  // 置換: ResourceName
  name: string;
  description?: string;
  status?: string;
  isActive?: boolean;
}

// Props
interface ResourceNameListProps {  // 置換: ResourceName
  tenantId: string;
  onSelect?: (resource: ResourceName) => void;
}

/**
 * リソース名一覧コンポーネント  // 置換: リソース名
 * 
 * テナント固有のリソース一覧を表示
 */
export function ResourceNameList({ tenantId, onSelect }: ResourceNameListProps) {  // 置換: ResourceName
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  
  // データ取得
  const { data: resources, isLoading, error } = useQuery({
    queryKey: ['resources', tenantId],  // 置換: resources
    queryFn: async () => {
      const response = await fetch(`/api/v1/tenants/${tenantId}/resources`);  // 置換: resources
      if (!response.ok) {
        throw new Error('Failed to fetch resources');
      }
      return response.json() as Promise<ResourceName[]>;
    },
    staleTime: 5 * 60 * 1000, // 5分間キャッシュ
  });
  
  // 削除ミューテーション
  const deleteMutation = useMutation({
    mutationFn: async (resourceId: string) => {
      const response = await fetch(
        `/api/v1/tenants/${tenantId}/resources/${resourceId}`,  // 置換: resources
        { method: 'DELETE' }
      );
      if (!response.ok) {
        throw new Error('Failed to delete resource');
      }
    },
    onSuccess: () => {
      // キャッシュを無効化して再取得
      queryClient.invalidateQueries({ queryKey: ['resources', tenantId] });
    },
  });
  
  const handleDelete = (resourceId: string) => {
    if (confirm('このリソースを削除しますか？')) {
      deleteMutation.mutate(resourceId);
    }
  };
  
  if (isLoading) {
    return (
      <div className="flex items-center justify-center p-8">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-gray-900" />
      </div>
    );
  }
  
  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-md p-4">
        <p className="text-red-800">エラーが発生しました: {error.message}</p>
      </div>
    );
  }
  
  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold">リソース一覧</h2>  {/* 置換: リソース */}
        <button
          onClick={() => navigate(`/tenants/${tenantId}/resources/new`)}  // 置換: resources
          className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
        >
          新規作成
        </button>
      </div>
      
      <div className="grid gap-4">
        {resources?.map((resource) => (
          <div
            key={resource.id}
            className="border rounded-lg p-4 hover:shadow-md transition-shadow cursor-pointer"
            onClick={() => onSelect?.(resource)}
          >
            <div className="flex justify-between items-start">
              <div className="flex-1">
                <h3 className="text-lg font-semibold">{resource.name}</h3>
                {resource.description && (
                  <p className="text-gray-600 mt-1">{resource.description}</p>
                )}
                <div className="flex gap-2 mt-2">
                  <span
                    className={`px-2 py-1 rounded text-sm ${
                      resource.status === 'active'
                        ? 'bg-green-100 text-green-800'
                        : 'bg-gray-100 text-gray-800'
                    }`}
                  >
                    {resource.status}
                  </span>
                  <span className="text-sm text-gray-500">
                    作成: {new Date(resource.createdAt).toLocaleDateString()}
                  </span>
                </div>
              </div>
              
              <div className="flex gap-2">
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    navigate(`/tenants/${tenantId}/resources/${resource.id}/edit`);  // 置換: resources
                  }}
                  className="px-3 py-1 text-blue-600 hover:bg-blue-50 rounded"
                >
                  編集
                </button>
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    handleDelete(resource.id);
                  }}
                  className="px-3 py-1 text-red-600 hover:bg-red-50 rounded"
                  disabled={deleteMutation.isPending}
                >
                  削除
                </button>
              </div>
            </div>
          </div>
        ))}
      </div>
      
      {resources?.length === 0 && (
        <div className="text-center py-12 text-gray-500">
          リソースがありません
        </div>
      )}
    </div>
  );
}

/**
 * リソース名作成/編集フォームコンポーネント  // 置換: リソース名
 */
interface ResourceNameFormProps {  // 置換: ResourceName
  tenantId: string;
  resourceId?: string;
  onSuccess?: () => void;
}

export function ResourceNameForm({ tenantId, resourceId, onSuccess }: ResourceNameFormProps) {  // 置換: ResourceName
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const isEdit = !!resourceId;
  
  const [formData, setFormData] = useState<ResourceNameFormData>({
    name: '',
    description: '',
    status: 'active',
    isActive: true,
  });
  
  // 編集時: 既存データ取得
  const { data: resource } = useQuery({
    queryKey: ['resource', tenantId, resourceId],  // 置換: resource
    queryFn: async () => {
      const response = await fetch(
        `/api/v1/tenants/${tenantId}/resources/${resourceId}`  // 置換: resources
      );
      if (!response.ok) {
        throw new Error('Failed to fetch resource');
      }
      return response.json() as Promise<ResourceName>;
    },
    enabled: isEdit,
  });
  
  useEffect(() => {
    if (resource) {
      setFormData({
        name: resource.name,
        description: resource.description,
        status: resource.status,
        isActive: resource.isActive,
      });
    }
  }, [resource]);
  
  // 作成/更新ミューテーション
  const saveMutation = useMutation({
    mutationFn: async (data: ResourceNameFormData) => {
      const url = isEdit
        ? `/api/v1/tenants/${tenantId}/resources/${resourceId}`
        : `/api/v1/tenants/${tenantId}/resources`;  // 置換: resources
      
      const response = await fetch(url, {
        method: isEdit ? 'PUT' : 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data),
      });
      
      if (!response.ok) {
        throw new Error(`Failed to ${isEdit ? 'update' : 'create'} resource`);
      }
      
      return response.json();
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['resources', tenantId] });
      onSuccess?.();
      navigate(`/tenants/${tenantId}/resources`);  // 置換: resources
    },
  });
  
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    saveMutation.mutate(formData);
  };
  
  return (
    <form onSubmit={handleSubmit} className="space-y-6 max-w-2xl">
      <h2 className="text-2xl font-bold">
        {isEdit ? 'リソース編集' : 'リソース作成'}  {/* 置換: リソース */}
      </h2>
      
      <div>
        <label htmlFor="name" className="block text-sm font-medium text-gray-700">
          名前 *
        </label>
        <input
          type="text"
          id="name"
          value={formData.name}
          onChange={(e) => setFormData({ ...formData, name: e.target.value })}
          required
          className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
        />
      </div>
      
      <div>
        <label htmlFor="description" className="block text-sm font-medium text-gray-700">
          説明
        </label>
        <textarea
          id="description"
          value={formData.description}
          onChange={(e) => setFormData({ ...formData, description: e.target.value })}
          rows={3}
          className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
        />
      </div>
      
      <div className="flex gap-4">
        <button
          type="submit"
          disabled={saveMutation.isPending}
          className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50"
        >
          {saveMutation.isPending ? '保存中...' : '保存'}
        </button>
        <button
          type="button"
          onClick={() => navigate(-1)}
          className="px-4 py-2 bg-gray-200 text-gray-800 rounded-md hover:bg-gray-300"
        >
          キャンセル
        </button>
      </div>
      
      {saveMutation.error && (
        <div className="bg-red-50 border border-red-200 rounded-md p-4">
          <p className="text-red-800">
            エラー: {saveMutation.error.message}
          </p>
        </div>
      )}
    </form>
  );
}
