import { useState, useEffect, useCallback } from 'react';
import { Plus, Edit2, Trash2, GripVertical, Loader } from 'lucide-react';
import { useParams } from 'react-router-dom';
import { getTopics, createTopic, updateTopic, deleteTopic, getIndustries, createIndustry, updateIndustry, deleteIndustry } from '../../services/taxonomyService';
import { ApiErrorHandler } from '@/lib/errorHandler';
import { AlertError } from '../common/AlertError';
import { AlertSuccess } from '../common/AlertSuccess';
import type { Topic, Industry } from '../../types/taxonomy';

type TaxonomyType = 'topics' | 'industries';

interface FormData {
  name: string;
  description: string;
  color: string;
  icon: string;
}

const DEFAULT_COLORS = ['#3B82F6', '#EF4444', '#10B981', '#F59E0B', '#8B5CF6', '#EC4899'];

export default function TaxonomyManagement({ type }: { type: TaxonomyType }) {
  const { tenantId } = useParams();
  const [items, setItems] = useState<(Topic | Industry)[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string>('');
  const [successMessage, setSuccessMessage] = useState<string>('');
  const [showForm, setShowForm] = useState(false);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [draggedId, setDraggedId] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [formData, setFormData] = useState<FormData>({
    name: '',
    description: '',
    color: DEFAULT_COLORS[0],
    icon: '',
  });

  const loadItems = useCallback(async () => {
    try {
      setLoading(true);
      setError('');
      if (!tenantId) return;

      let data;
      if (type === 'topics') {
        data = await getTopics(tenantId);
      } else {
        data = await getIndustries(tenantId);
      }
      setItems(data || []);
    } catch (err: unknown) {
      const errorMsg = ApiErrorHandler.getErrorMessage(err, 'データの読み込みに失敗しました');
      setError(errorMsg);
      console.error('Error loading items:', err);
    } finally {
      setLoading(false);
    }
  }, [tenantId, type]);

  useEffect(() => {
    loadItems();
  }, [loadItems]);

  // Auto-hide success message
  useEffect(() => {
    if (successMessage) {
      const timer = setTimeout(() => setSuccessMessage(''), 3000);
      return () => clearTimeout(timer);
    }
  }, [successMessage]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!formData.name.trim()) {
      setError('名前は必須です');
      return;
    }

    try {
      setIsSubmitting(true);
      setError('');
      if (!tenantId) return;

      if (editingId) {
        if (type === 'topics') {
          await updateTopic(tenantId, editingId, formData);
        } else {
          await updateIndustry(tenantId, editingId, formData);
        }
        setSuccessMessage('更新しました');
      } else {
        if (type === 'topics') {
          await createTopic(tenantId, formData);
        } else {
          await createIndustry(tenantId, formData);
        }
        setSuccessMessage('作成しました');
      }

      await loadItems();
      resetForm();
      setShowForm(false);
    } catch (err: unknown) {
      const errorMsg = ApiErrorHandler.getErrorMessage(err, '保存に失敗しました');
      setError(errorMsg);
      console.error('Error submitting form:', err);
    } finally{
      setIsSubmitting(false);
    }
  };

  const handleEdit = (item: Topic | Industry) => {
    setFormData({
      name: item.name,
      description: item.description || '',
      color: item.color || '#3B82F6',
      icon: item.icon || '',
    });
    setEditingId(item.id);
    setShowForm(true);
    setError('');
  };

  const handleDelete = async (id: string, name: string) => {
    if (!confirm(`「${name}」を削除してもよろしいですか？`)) return;

    try {
      setError('');
      if (!tenantId) return;

      if (type === 'topics') {
        await deleteTopic(tenantId, id);
      } else {
        await deleteIndustry(tenantId, id);
      }
      setSuccessMessage('削除しました');
      await loadItems();
    } catch (err: unknown) {
      const errorMsg = ApiErrorHandler.getErrorMessage(err, '削除に失敗しました');
      setError(errorMsg);
      console.error('Error deleting item:', err);
    }
  };

  const resetForm = () => {
    setFormData({
      name: '',
      description: '',
      color: DEFAULT_COLORS[0],
      icon: '',
    });
    setEditingId(null);
  };

  const label = type === 'topics' ? 'トピック' : '業界';

  const handleDragEnd = async (draggedItemId: string, targetItemId: string) => {
    if (draggedItemId === targetItemId) {
      setDraggedId(null);
      return;
    }

    try {
      // Find indices
      const draggedIndex = items.findIndex((item) => item.id === draggedItemId);
      const targetIndex = items.findIndex((item) => item.id === targetItemId);

      if (draggedIndex === -1 || targetIndex === -1) return;

      // Create new sorted array
      const newItems = [...items];
      [newItems[draggedIndex], newItems[targetIndex]] = [
        newItems[targetIndex],
        newItems[draggedIndex],
      ];

      // Update sort_order for all items
      const updates = newItems.map((item, index) => ({
        ...item,
        sort_order: index,
      }));

      // Optimistically update UI
      setItems(updates);

      // Send updates to server
      if (!tenantId) return;

      for (const item of updates) {
        if (type === 'topics') {
          await updateTopic(tenantId, item.id, { sort_order: item.sort_order });
        } else {
          await updateIndustry(tenantId, item.id, { sort_order: item.sort_order });
        }
      }

      setSuccessMessage('並び順を更新しました');
    } catch (err: unknown) {
      const errorMsg = ApiErrorHandler.getErrorMessage(err, '並び順の更新に失敗しました');
      setError(errorMsg);
      console.error('Error updating sort order:', err);
      // Reload to revert
      await loadItems();
    } finally {
      setDraggedId(null);
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
        <h3 className="text-lg font-semibold">{label}一覧</h3>
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
              {label}名
            </label>
            <input
              type="text"
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              required
              maxLength={100}
              className="w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          <div>
            <label className="block text-left text-sm font-medium text-gray-700 mb-1">
              説明
            </label>
            <textarea
              value={formData.description}
              onChange={(e) => setFormData({ ...formData, description: e.target.value })}
              maxLength={500}
              className="w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
              rows={3}
            />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-left text-sm font-medium text-gray-700 mb-1">
                色
              </label>
              <div className="flex gap-2 flex-wrap">
                {DEFAULT_COLORS.map((color) => (
                  <button
                    key={color}
                    type="button"
                    onClick={() => setFormData({ ...formData, color })}
                    className={`w-8 h-8 rounded border-2 transition-all ${
                      formData.color === color ? 'border-gray-800 scale-110' : 'border-gray-300'
                    }`}
                    style={{ backgroundColor: color }}
                  />
                ))}
              </div>
            </div>

            <div>
              <label className="block text-left text-sm font-medium text-gray-700 mb-1">
                アイコン
              </label>
              <input
                type="text"
                value={formData.icon}
                onChange={(e) => setFormData({ ...formData, icon: e.target.value })}
                placeholder="lucide icon name"
                maxLength={50}
                className="w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
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

      <div className="space-y-2">
        {items.map((item) => (
          <div
            key={item.id}
            draggable
            onDragStart={() => setDraggedId(item.id)}
            onDragOver={(e) => e.preventDefault()}
            onDrop={() => draggedId && handleDragEnd(draggedId, item.id)}
            className={`flex items-center gap-4 p-4 bg-white border rounded hover:bg-gray-50 cursor-move transition-colors ${
              draggedId === item.id ? 'opacity-50 bg-gray-100' : draggedId ? 'border-blue-300 bg-blue-50' : ''
            }`}
          >
            <GripVertical size={18} className="text-gray-400" />

            <div
              className="w-6 h-6 rounded"
              style={{ backgroundColor: item.color || '#3B82F6' }}
            />

            <div className="flex-1">
              <p className="font-medium">{item.name}</p>
              {item.description && (
                <p className="text-sm text-gray-600">{item.description}</p>
              )}
            </div>

            <div className="flex gap-2">
              <button
                onClick={() => handleEdit(item)}
                className="p-2 text-blue-600 hover:bg-blue-50 rounded transition-colors"
                title="編集"
              >
                <Edit2 size={18} />
              </button>
              <button
                onClick={() => handleDelete(item.id, item.name)}
                className="p-2 text-red-600 hover:bg-red-50 rounded transition-colors"
                title="削除"
              >
                <Trash2 size={18} />
              </button>
            </div>
          </div>
        ))}

        {items.length === 0 && (
          <div className="text-center py-8 text-gray-500">
            {label}がまだ登録されていません
          </div>
        )}
      </div>
    </div>
  );
}
