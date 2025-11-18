import { useState, useEffect, useCallback } from 'react';
import { ApiErrorHandler } from '@/lib/errorHandler';

interface UseAdminCRUDOptions<T, FormData> {
  fetchItems: () => Promise<T[]>;
  createItem: (data: FormData) => Promise<T>;
  updateItem: (id: string, data: FormData) => Promise<T>;
  deleteItem: (id: string) => Promise<void>;
  initialFormData: FormData;
  validateForm?: (data: FormData) => string | null;
  successMessages?: {
    create?: string;
    update?: string;
    delete?: string;
  };
}

export function useAdminCRUD<T extends { id: string }, FormData>(
  options: UseAdminCRUDOptions<T, FormData>
) {
  const {
    fetchItems,
    createItem,
    updateItem,
    deleteItem,
    initialFormData,
    validateForm,
    successMessages = {
      create: '作成しました',
      update: '更新しました',
      delete: '削除しました',
    },
  } = options;

  // State management
  const [items, setItems] = useState<T[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string>('');
  const [successMessage, setSuccessMessage] = useState<string>('');
  const [showForm, setShowForm] = useState(false);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [formData, setFormData] = useState<FormData>(initialFormData);

  // Load items
  const loadItems = useCallback(async () => {
    try {
      setLoading(true);
      setError('');
      const data = await fetchItems();
      setItems(data || []);
    } catch (err: unknown) {
      const errorMsg = ApiErrorHandler.getErrorMessage(err, 'データの読み込みに失敗しました');
      setError(errorMsg);
      console.error('Error loading items:', err);
    } finally {
      setLoading(false);
    }
  }, [fetchItems]);

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

  // Reset form
  const resetForm = useCallback(() => {
    setFormData(initialFormData);
    setEditingId(null);
    setShowForm(false);
    setError('');
  }, [initialFormData]);

  // Handle submit
  const handleSubmit = useCallback(
    async (e: React.FormEvent) => {
      e.preventDefault();

      // Validate form
      if (validateForm) {
        const validationError = validateForm(formData);
        if (validationError) {
          setError(validationError);
          return;
        }
      }

      try {
        setIsSubmitting(true);
        setError('');

        if (editingId) {
          await updateItem(editingId, formData);
          setSuccessMessage(successMessages.update || '更新しました');
        } else {
          await createItem(formData);
          setSuccessMessage(successMessages.create || '作成しました');
        }

        resetForm();
        await loadItems();
      } catch (err: unknown) {
        const errorMsg = ApiErrorHandler.getErrorMessage(
          err,
          editingId ? '更新に失敗しました' : '作成に失敗しました'
        );
        setError(errorMsg);
        console.error('Error submitting form:', err);
      } finally {
        setIsSubmitting(false);
      }
    },
    [
      formData,
      editingId,
      validateForm,
      createItem,
      updateItem,
      resetForm,
      loadItems,
      successMessages,
    ]
  );

  // Handle edit
  const handleEdit = useCallback(
    (item: T) => {
      setFormData(item as unknown as FormData);
      setEditingId(item.id);
      setShowForm(true);
      setError('');
    },
    []
  );

  // Handle delete
  const handleDelete = useCallback(
    async (id: string, name: string) => {
      if (!window.confirm(`「${name}」を削除してもよろしいですか？この操作は取り消せません。`)) {
        return;
      }

      try {
        setError('');
        await deleteItem(id);
        setSuccessMessage(successMessages.delete || '削除しました');
        await loadItems();
      } catch (err: unknown) {
        const errorMsg = ApiErrorHandler.getErrorMessage(err, '削除に失敗しました');
        setError(errorMsg);
        console.error('Error deleting item:', err);
      }
    },
    [deleteItem, loadItems, successMessages]
  );

  return {
    // State
    items,
    setItems,
    loading,
    error,
    setError,
    successMessage,
    setSuccessMessage,
    showForm,
    setShowForm,
    editingId,
    setEditingId,
    isSubmitting,
    formData,
    setFormData,

    // Actions
    loadItems,
    resetForm,
    handleSubmit,
    handleEdit,
    handleDelete,
  };
}
