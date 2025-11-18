import { Plus, Edit2, Trash2, Loader } from 'lucide-react';
import { getTenants, createTenant, updateTenant, deleteTenant } from '../../services/tenantService';
import { AlertError } from '../common/AlertError';
import { AlertSuccess } from '../common/AlertSuccess';
import { useAdminCRUD } from '../../hooks/useAdminCRUD';
import type { Tenant } from '../../types/tenant';

interface TenantFormData {
  name: string;
  slug: string;
  plan: 'free' | 'pro' | 'enterprise';
}

export default function TenantManagement() {
  const {
    items: tenants,
    loading,
    error,
    setError,
    successMessage,
    setSuccessMessage,
    showForm,
    setShowForm,
    editingId,
    isSubmitting,
    formData,
    setFormData,
    resetForm,
    handleSubmit,
    handleEdit,
    handleDelete,
  } = useAdminCRUD<Tenant, TenantFormData>({
    fetchItems: getTenants,
    createItem: createTenant,
    updateItem: updateTenant,
    deleteItem: deleteTenant,
    initialFormData: {
      name: '',
      slug: '',
      plan: 'free',
    },
    validateForm: (data) => {
      if (!data.name.trim() || !data.slug.trim()) {
        return 'テナント名とスラッグは必須です';
      }
      return null;
    },
    successMessages: {
      create: 'テナントを作成しました',
      update: 'テナントを更新しました',
      delete: 'テナントを削除しました',
    },
  });

  const getPlanBadgeColor = (plan: string) => {
    switch (plan) {
      case 'enterprise':
        return 'bg-purple-100 text-purple-800';
      case 'pro':
        return 'bg-blue-100 text-blue-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center py-8">
        <Loader className="animate-spin mr-2" size={20} />
        <span>読み込み中...</span>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {error && <AlertError message={error} onClose={() => setError('')} />}
      {successMessage && <AlertSuccess message={successMessage} onClose={() => setSuccessMessage('')} />}

      <div className="flex justify-between items-center">
        <h3 className="text-lg font-semibold">テナント一覧</h3>
        <button
          onClick={() => {
            resetForm();
            setShowForm(!showForm);
            setError('');
          }}
          className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 transition-colors"
        >
          <Plus size={18} />
          {showForm ? 'キャンセル' : '新規作成'}
        </button>
      </div>

      {showForm && (
        <form onSubmit={handleSubmit} className="bg-gray-50 p-6 rounded-lg border border-gray-200 space-y-4">
          <div>
            <label className="block text-left text-sm font-medium text-gray-700 mb-1">
              テナント名
            </label>
            <input
              type="text"
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              required
              maxLength={255}
              className="w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          <div>
            <label className="block text-left text-sm font-medium text-gray-700 mb-1">
              スラッグ (URL用)
            </label>
            <input
              type="text"
              value={formData.slug}
              onChange={(e) => setFormData({ ...formData, slug: e.target.value.toLowerCase().replace(/[^a-z0-9-]/g, '-') })}
              required
              pattern="^[a-z0-9-]+$"
              maxLength={100}
              className="w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
            <p className="text-xs text-gray-500 mt-1">小文字、数字、ハイフンのみ使用可</p>
          </div>

          <div>
            <label className="block text-left text-sm font-medium text-gray-700 mb-1">
              プラン
            </label>
            <select
              value={formData.plan}
              onChange={(e) => setFormData({ ...formData, plan: e.target.value as 'free' | 'pro' | 'enterprise' })}
              className="w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="free">フリー</option>
              <option value="pro">プロ</option>
              <option value="enterprise">エンタープライズ</option>
            </select>
          </div>

          <div className="flex gap-2">
            <button
              type="submit"
              disabled={isSubmitting}
              className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center gap-2"
            >
              {isSubmitting && <Loader size={16} className="animate-spin" />}
              {editingId ? '更新' : '作成'}
            </button>
            <button
              type="button"
              onClick={() => {
                setShowForm(false);
                resetForm();
                setError('');
              }}
              className="px-4 py-2 bg-gray-200 text-gray-800 rounded hover:bg-gray-300 transition-colors"
            >
              キャンセル
            </button>
          </div>
        </form>
      )}

      <div className="overflow-x-auto">
        <table className="w-full border-collapse">
          <thead>
            <tr className="bg-gray-100 border-b border-gray-200">
              <th className="px-6 py-3 text-left font-semibold text-gray-700">テナント名</th>
              <th className="px-6 py-3 text-left font-semibold text-gray-700">スラッグ</th>
              <th className="px-6 py-3 text-left font-semibold text-gray-700">プラン</th>
              <th className="px-6 py-3 text-left font-semibold text-gray-700">作成日</th>
              <th className="px-6 py-3 text-left font-semibold text-gray-700">操作</th>
            </tr>
          </thead>
          <tbody>
            {tenants.map((tenant) => (
              <tr key={tenant.id} className="border-b border-gray-200 hover:bg-gray-50">
                <td className="px-6 py-3">{tenant.name}</td>
                <td className="px-6 py-3 text-sm text-gray-600">{tenant.slug}</td>
                <td className="px-6 py-3">
                  <span className={`px-3 py-1 rounded text-sm font-medium ${getPlanBadgeColor(tenant.plan)}`}>
                    {tenant.plan === 'enterprise' ? 'エンタープライズ' : tenant.plan === 'pro' ? 'プロ' : 'フリー'}
                  </span>
                </td>
                <td className="px-6 py-3 text-sm text-gray-600">
                  {new Date(tenant.created_at).toLocaleDateString('ja-JP')}
                </td>
                <td className="px-6 py-3 flex gap-2">
                  <button
                    onClick={() => handleEdit(tenant)}
                    className="p-2 text-blue-600 hover:bg-blue-50 rounded transition-colors"
                    title="編集"
                  >
                    <Edit2 size={18} />
                  </button>
                  <button
                    onClick={() => handleDelete(tenant.id, tenant.name)}
                    className="p-2 text-red-600 hover:bg-red-50 rounded transition-colors"
                    title="削除"
                  >
                    <Trash2 size={18} />
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>

        {tenants.length === 0 && (
          <div className="text-center py-8 text-gray-500">
            テナントがまだ登録されていません
          </div>
        )}
      </div>
    </div>
  );
}
