import { useState, useEffect, useCallback } from 'react';
import { Plus, Edit2, Trash2, Loader } from 'lucide-react';
import { useAuthStore } from '../../store/authStore';
import { getUsers, createUser, updateUser, deleteUser } from '../../services/userService';
import { ApiErrorHandler } from '@/lib/errorHandler';
import { AlertError } from '../common/AlertError';
import { AlertSuccess } from '../common/AlertSuccess';
import type { UserAdmin } from '../../types/user';

interface UserFormData {
  email: string;
  name: string;
  role: 'user' | 'tenant_admin' | 'system_admin';
  password?: string;
}

export default function UserManagement() {
  const { user: currentUser } = useAuthStore();
  const [users, setUsers] = useState<UserAdmin[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string>('');
  const [successMessage, setSuccessMessage] = useState<string>('');
  const [showForm, setShowForm] = useState(false);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [formData, setFormData] = useState<UserFormData>({
    email: '',
    name: '',
    role: 'user',
  });

  const loadUsers = useCallback(async () => {
    try {
      setLoading(true);
      setError('');
      // System admin can see all users, tenant admin sees only their tenant's users
      const tenantIdParam = currentUser?.role === 'system_admin' ? undefined : currentUser?.tenant_id;
      const data = await getUsers(tenantIdParam);
      setUsers(data);
    } catch (err: unknown) {
      const errorMsg = ApiErrorHandler.getErrorMessage(err, 'ユーザー情報の読み込みに失敗しました');
      setError(errorMsg);
      console.error('Error loading users:', err);
    } finally {
      setLoading(false);
    }
  }, [currentUser?.role, currentUser?.tenant_id]);

  useEffect(() => {
    loadUsers();
  }, [loadUsers]);

  // Auto-hide success message after 3 seconds
  useEffect(() => {
    if (successMessage) {
      const timer = setTimeout(() => setSuccessMessage(''), 3000);
      return () => clearTimeout(timer);
    }
  }, [successMessage]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    // Validate form data
    if (!formData.name.trim() || !formData.email.trim()) {
      setError('ユーザー名とメールアドレスは必須です');
      return;
    }

    if (!editingId && !formData.password) {
      setError('新規作成時はパスワードが必須です');
      return;
    }

    if (formData.password && formData.password.length < 8) {
      setError('パスワードは最低8文字必要です');
      return;
    }

    try {
      setIsSubmitting(true);
      setError('');

      if (editingId) {
        await updateUser(editingId, {
          email: formData.email,
          name: formData.name,
          role: formData.role,
        });
        setSuccessMessage('ユーザーを更新しました');
      } else {
        await createUser({
          tenant_id: currentUser!.tenant_id,
          email: formData.email,
          password: formData.password!,
          name: formData.name,
          role: formData.role,
        });
        setSuccessMessage('ユーザーを作成しました');
      }

      await loadUsers();
      resetForm();
      setShowForm(false);
    } catch (err: unknown) {
      const errorMsg = ApiErrorHandler.getErrorMessage(err,
        editingId ? 'ユーザーの更新に失敗しました' : 'ユーザーの作成に失敗しました');
      setError(errorMsg);
      console.error('Error submitting form:', err);
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleEdit = (user: UserAdmin) => {
    setFormData({
      email: user.email,
      name: user.name,
      role: user.role as 'user' | 'tenant_admin' | 'system_admin',
    });
    setEditingId(user.id);
    setShowForm(true);
    setError('');
  };

  const handleDelete = async (id: string, name: string) => {
    if (!confirm(`「${name}」を削除してもよろしいですか？この操作は取り消せません。`)) return;

    try {
      setError('');
      await deleteUser(id);
      setSuccessMessage('ユーザーを削除しました');
      await loadUsers();
    } catch (err: unknown) {
      const errorMsg = ApiErrorHandler.getErrorMessage(err, 'ユーザーの削除に失敗しました');
      setError(errorMsg);
      console.error('Error deleting user:', err);
    }
  };

  const resetForm = () => {
    setFormData({
      email: '',
      name: '',
      role: 'user',
      password: undefined,
    });
    setEditingId(null);
  };

  const getRoleBadgeColor = (role: string) => {
    switch (role) {
      case 'system_admin':
        return 'bg-red-100 text-red-800';
      case 'tenant_admin':
        return 'bg-purple-100 text-purple-800';
      default:
        return 'bg-blue-100 text-blue-800';
    }
  };

  const getRoleLabel = (role: string) => {
    switch (role) {
      case 'system_admin':
        return 'システム管理者';
      case 'tenant_admin':
        return 'テナント管理者';
      default:
        return '一般ユーザー';
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
        <h3 className="text-lg font-semibold">ユーザー一覧</h3>
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
              メールアドレス
            </label>
            <input
              type="email"
              value={formData.email}
              onChange={(e) => setFormData({ ...formData, email: e.target.value })}
              required
              disabled={!!editingId}
              maxLength={255}
              className="w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:bg-gray-100"
            />
            {editingId && <p className="text-xs text-gray-500 mt-1">メールアドレスは変更できません</p>}
          </div>

          <div>
            <label className="block text-left text-sm font-medium text-gray-700 mb-1">
              ユーザー名
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

          {!editingId && (
            <div>
              <label className="block text-left text-sm font-medium text-gray-700 mb-1">
                パスワード
              </label>
              <input
                type="password"
                value={formData.password || ''}
                onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                required={!editingId}
                minLength={8}
                maxLength={255}
                className="w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
              <p className="text-xs text-gray-500 mt-1">最低8文字</p>
            </div>
          )}

          <div>
            <label className="block text-left text-sm font-medium text-gray-700 mb-1">
              ロール
            </label>
            <select
              value={formData.role}
              onChange={(e) => setFormData({ ...formData, role: e.target.value as 'user' | 'tenant_admin' | 'system_admin' })}
              className="w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="user">一般ユーザー</option>
              <option value="tenant_admin">テナント管理者</option>
              {currentUser?.role === 'system_admin' && (
                <option value="system_admin">システム管理者</option>
              )}
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
              <th className="px-6 py-3 text-left font-semibold text-gray-700">名前</th>
              <th className="px-6 py-3 text-left font-semibold text-gray-700">メール</th>
              {currentUser?.role === 'system_admin' && (
                <th className="px-6 py-3 text-left font-semibold text-gray-700">テナント</th>
              )}
              <th className="px-6 py-3 text-left font-semibold text-gray-700">ロール</th>
              <th className="px-6 py-3 text-left font-semibold text-gray-700">作成日</th>
              <th className="px-6 py-3 text-left font-semibold text-gray-700">操作</th>
            </tr>
          </thead>
          <tbody>
            {users.map((user) => (
              <tr key={user.id} className="border-b border-gray-200 hover:bg-gray-50">
                <td className="px-6 py-3">{user.name}</td>
                <td className="px-6 py-3 text-sm text-gray-600">{user.email}</td>
                {currentUser?.role === 'system_admin' && (
                  <td className="px-6 py-3 text-sm text-gray-600">
                    {'tenant_name' in user && typeof user.tenant_name === 'string' ? user.tenant_name : 'N/A'}
                  </td>
                )}
                <td className="px-6 py-3">
                  <span className={`px-3 py-1 rounded text-sm font-medium ${getRoleBadgeColor(user.role)}`}>
                    {getRoleLabel(user.role)}
                  </span>
                </td>
                <td className="px-6 py-3 text-sm text-gray-600">
                  {new Date(user.created_at).toLocaleDateString('ja-JP')}
                </td>
                <td className="px-6 py-3 flex gap-2">
                  <button
                    onClick={() => handleEdit(user)}
                    className="p-2 text-blue-600 hover:bg-blue-50 rounded transition-colors"
                    title="編集"
                  >
                    <Edit2 size={18} />
                  </button>
                  <button
                    onClick={() => handleDelete(user.id, user.name)}
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

        {users.length === 0 && (
          <div className="text-center py-8 text-gray-500">
            ユーザーがまだ登録されていません
          </div>
        )}
      </div>
    </div>
  );
}
