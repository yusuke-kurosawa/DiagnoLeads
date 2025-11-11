/**
 * Notes Section Component
 * 
 * Manage lead notes with:
 * - Add new notes
 * - Edit existing notes
 * - Delete notes
 * - Display notes chronologically
 */

import React, { useState } from 'react';
import { PlusIcon, EditIcon, TrashIcon, SaveIcon, XIcon, StickyNoteIcon } from 'lucide-react';

export interface Note {
  id: string;
  content: string;
  created_at: string;
  updated_at: string;
  created_by?: string;
}

interface NotesSectionProps {
  notes: Note[];
  onAdd: (content: string) => Promise<void>;
  onEdit: (noteId: string, content: string) => Promise<void>;
  onDelete: (noteId: string) => Promise<void>;
}

export function NotesSection({ notes, onAdd, onEdit, onDelete }: NotesSectionProps) {
  const [isAdding, setIsAdding] = useState(false);
  const [newNoteContent, setNewNoteContent] = useState('');
  const [editingId, setEditingId] = useState<string | null>(null);
  const [editContent, setEditContent] = useState('');
  const [isSaving, setIsSaving] = useState(false);

  const handleAdd = async () => {
    if (!newNoteContent.trim()) return;

    setIsSaving(true);
    try {
      await onAdd(newNoteContent.trim());
      setNewNoteContent('');
      setIsAdding(false);
    } catch (error) {
      console.error('Failed to add note:', error);
      alert('メモの追加に失敗しました');
    } finally {
      setIsSaving(false);
    }
  };

  const handleEdit = async (noteId: string) => {
    if (!editContent.trim()) return;

    setIsSaving(true);
    try {
      await onEdit(noteId, editContent.trim());
      setEditingId(null);
      setEditContent('');
    } catch (error) {
      console.error('Failed to edit note:', error);
      alert('メモの編集に失敗しました');
    } finally {
      setIsSaving(false);
    }
  };

  const handleDelete = async (noteId: string) => {
    if (!confirm('このメモを削除してもよろしいですか？')) return;

    setIsSaving(true);
    try {
      await onDelete(noteId);
    } catch (error) {
      console.error('Failed to delete note:', error);
      alert('メモの削除に失敗しました');
    } finally {
      setIsSaving(false);
    }
  };

  const startEdit = (note: Note) => {
    setEditingId(note.id);
    setEditContent(note.content);
  };

  const cancelEdit = () => {
    setEditingId(null);
    setEditContent('');
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('ja-JP', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  return (
    <div className="bg-white shadow-sm rounded-lg border border-gray-200 p-6">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-gray-900">メモ</h3>
        {!isAdding && (
          <button
            onClick={() => setIsAdding(true)}
            className="flex items-center gap-2 px-3 py-1.5 text-sm bg-blue-600 text-white rounded-md hover:bg-blue-700"
          >
            <PlusIcon className="w-4 h-4" />
            メモを追加
          </button>
        )}
      </div>

      {/* Add Note Form */}
      {isAdding && (
        <div className="mb-4 p-4 border-2 border-blue-200 rounded-lg bg-blue-50">
          <textarea
            value={newNoteContent}
            onChange={(e) => setNewNoteContent(e.target.value)}
            placeholder="メモを入力..."
            rows={4}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500 resize-none"
            autoFocus
          />
          <div className="flex gap-2 mt-3">
            <button
              onClick={handleAdd}
              disabled={isSaving || !newNoteContent.trim()}
              className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50"
            >
              <SaveIcon className="w-4 h-4" />
              {isSaving ? '保存中...' : '保存'}
            </button>
            <button
              onClick={() => {
                setIsAdding(false);
                setNewNoteContent('');
              }}
              disabled={isSaving}
              className="flex items-center gap-2 px-4 py-2 bg-white border border-gray-300 text-gray-700 rounded-md hover:bg-gray-50"
            >
              <XIcon className="w-4 h-4" />
              キャンセル
            </button>
          </div>
        </div>
      )}

      {/* Notes List */}
      <div className="space-y-3">
        {notes.length === 0 ? (
          <div className="text-center py-8 text-gray-500">
            <StickyNoteIcon className="w-12 h-12 mx-auto mb-3 text-gray-300" />
            <p>まだメモがありません</p>
            <p className="text-sm mt-1">「メモを追加」ボタンから最初のメモを作成しましょう</p>
          </div>
        ) : (
          notes.map((note) => (
            <div key={note.id} className="border border-gray-200 rounded-lg p-4 hover:bg-gray-50">
              {editingId === note.id ? (
                // Edit Mode
                <div>
                  <textarea
                    value={editContent}
                    onChange={(e) => setEditContent(e.target.value)}
                    rows={4}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500 resize-none"
                    autoFocus
                  />
                  <div className="flex gap-2 mt-3">
                    <button
                      onClick={() => handleEdit(note.id)}
                      disabled={isSaving || !editContent.trim()}
                      className="flex items-center gap-2 px-3 py-1.5 text-sm bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50"
                    >
                      <SaveIcon className="w-4 h-4" />
                      {isSaving ? '保存中...' : '保存'}
                    </button>
                    <button
                      onClick={cancelEdit}
                      disabled={isSaving}
                      className="flex items-center gap-2 px-3 py-1.5 text-sm bg-white border border-gray-300 text-gray-700 rounded-md hover:bg-gray-50"
                    >
                      <XIcon className="w-4 h-4" />
                      キャンセル
                    </button>
                  </div>
                </div>
              ) : (
                // View Mode
                <div>
                  <div className="flex items-start justify-between gap-3 mb-2">
                    <p className="text-sm text-gray-900 whitespace-pre-wrap flex-1">
                      {note.content}
                    </p>
                    <div className="flex gap-1 flex-shrink-0">
                      <button
                        onClick={() => startEdit(note)}
                        className="p-1.5 text-gray-600 hover:text-blue-600 hover:bg-blue-50 rounded"
                        title="編集"
                      >
                        <EditIcon className="w-4 h-4" />
                      </button>
                      <button
                        onClick={() => handleDelete(note.id)}
                        className="p-1.5 text-gray-600 hover:text-red-600 hover:bg-red-50 rounded"
                        title="削除"
                      >
                        <TrashIcon className="w-4 h-4" />
                      </button>
                    </div>
                  </div>
                  <div className="flex items-center gap-3 text-xs text-gray-500">
                    <span>{formatDate(note.created_at)}</span>
                    {note.created_by && (
                      <>
                        <span>•</span>
                        <span>{note.created_by}</span>
                      </>
                    )}
                    {note.updated_at !== note.created_at && (
                      <>
                        <span>•</span>
                        <span>編集済み</span>
                      </>
                    )}
                  </div>
                </div>
              )}
            </div>
          ))
        )}
      </div>
    </div>
  );
}
