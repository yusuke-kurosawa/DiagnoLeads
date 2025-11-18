import { useState, useEffect } from 'react';
import { Plus, Edit2, Trash2, AlertCircle, Loader } from 'lucide-react';
import { getTenants, createTenant, updateTenant, deleteTenant } from '../../services/tenantService';
import type { Tenant } from '../../types/tenant';

interface TenantFormData {
  name: string;
  slug: string;
  plan: 'free' | 'pro' | 'enterprise';
}

export default function TenantManagement() {
  const [tenants, setTenants] = useState<Tenant[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string>('');
  const [successMessage, setSuccessMessage] = useState<string>('');
  const [showForm, setShowForm] = useState(false);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [formData, setFormData] = useState<TenantFormData>({
    name: '',
    slug: '',
    plan: 'free',
  });

  useEffect(() => {
    loadTenants();
  }, []);

  // Auto-hide success message after 3 seconds
  useEffect(() => {
    if (successMessage) {
      const timer = setTimeout(() => setSuccessMessage(''), 3000);
      return () => clearTimeout(timer);
    }
  }, [successMessage]);

  const loadTenants = async () => {
    try {
      setLoading(true);
      setError('');
      const data = await getTenants();
      setTenants(data);
    } catch (err: unknown) {
      const errorMsg = (err as { response?: { data?: { detail?: string } }; message?: string }).response?.data?.detail || err.message || 'テナント情報の読み込みに失敗しました';
      setError(errorMsg);
      console.error('Error loading tenants:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    // Validate form data
    if (!formData.name.trim() || !formData.slug.trim()) {
      setError('テナント名とスラッグは必須です');
      return;
    }

    try {
      setIsSubmitting(true);
      setError('');
      
      if (editingId) {
        await updateTenant(editingId, formData);
        setSuccessMessage('テナントを更新しました');
      } else {
        await createTenant(formData);
        setSuccessMessage('テナントを作成しました');
      }
      
      await loadTenants();
      resetForm();
      setShowForm(false);
    } catch (err: unknown) {
      const errorMsg = (err as { response?: { data?: { detail?: string } }; message?: string }).response?.data?.detail || err.message || 
        (editingId ? 'テナントの更新に失敗しました' : 'テナントの作成に失敗しました');
      setError(errorMsg);
      console.error('Error submitting form:', err);
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleEdit = (tenant: Tenant) => {
    setFormData({
      name: tenant.name,
      slug: tenant.slug,
      plan: tenant.plan as 'free' | 'pro' | 'enterprise',
    });
    setEditingId(tenant.id);
    setShowForm(true);
    setError('');
  };

  const handleDelete = async (id: string, name: string) => {
    if (!confirm(`「${name}」を削除してもよろしいですか？この操作は取り消せません。`)) return;

    try {
      setError('');
      await deleteTenant(id);
      setSuccessMessage('テナントを削除しました');
      await loadTenants();
    } catch (err: unknown) {
      const errorMsg = (err as { response?: { data?: { detail?: string } }; message?: string }).response?.data?.detail || err.message || 'テナントの削除に失敗しました';
      setError(errorMsg);
      console.error('Error deleting tenant:', err);
    }
  };

  const resetForm = () => {
    setFormData({
      name: '',
      slug: '',
      plan: 'free',
    });
    setEditingId(null);
  };

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
      {error && (
        <div className="p-4 bg-red-50 border border-red-200 text-red-800 rounded flex gap-2 items-start">
          <AlertCircle size={20} className="flex-shrink-0 mt-0.5" />
          <div>
            <p className="font-semibold">エラーが発生しました</p>
            <p className="text-sm mt-1">{error}</p>
          </div>
        </div>
      )}

      {successMessage && (
        <div className="p-4 bg-green-50 border border-green-200 text-green-800 rounded flex gap-2">
          <span className="text-lg">✓</span>
          <span>{successMessage}</span>
        </div>
      )}

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
              onChange={(e) => setFormData({ ...formData, plan: e.target.value })}
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
