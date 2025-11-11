/**
 * Lead Detail Page
 * 
 * Displays detailed information about a lead with actions.
 */

import React, { useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { FlameIcon, MailIcon, PhoneIcon } from 'lucide-react';
import { useAuthStore } from '../../store/authStore';
import { leadService } from '../../services/leadService';

import { ScoreBreakdown } from '../../components/leads/ScoreBreakdown';
import { ActivityTimeline, generateTimelineFromLead } from '../../components/leads/ActivityTimeline';
import { NotesSection, type Note } from '../../components/leads/NotesSection';
import { StatusDropdown, type LeadStatus } from '../../components/leads/StatusDropdown';
import { StatusHistory, type StatusChange } from '../../components/leads/StatusHistory';

export const LeadDetailPage: React.FC = () => {
  const { leadId } = useParams<{ leadId: string }>();
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const { user } = useAuthStore();
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);

  const { data: lead, isLoading, error } = useQuery({
    queryKey: ['leads', user?.tenant_id, leadId],
    queryFn: () => {
      if (!user?.tenant_id || !leadId) throw new Error('Missing required parameters');
      return leadService.getById(user.tenant_id, leadId);
    },
    enabled: !!user?.tenant_id && !!leadId,
  });

  const deleteMutation = useMutation({
    mutationFn: () => {
      if (!user?.tenant_id || !leadId) throw new Error('Missing required parameters');
      return leadService.delete(user.tenant_id, leadId);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['leads'] });
      navigate(`/tenants/${user?.tenant_id}/leads`);
    },
  });

  const handleDelete = () => {
    deleteMutation.mutate();
  };

  // Note handlers (simulated - would connect to API)
  const [notes, setNotes] = useState<Note[]>([]);

  // Status management
  const [statusHistory, setStatusHistory] = useState<StatusChange[]>([]);

  const handleStatusChange = async (newStatus: LeadStatus, note?: string) => {
    if (!lead) return;
    
    // Simulate API call
    await new Promise(resolve => setTimeout(resolve, 500));
    
    // Add to history
    const change: StatusChange = {
      id: `change-${Date.now()}`,
      from_status: lead.status,
      to_status: newStatus,
      changed_at: new Date().toISOString(),
      changed_by: user?.email,
      note,
    };
    setStatusHistory([change, ...statusHistory]);
    
    // Update lead status (in real app, this would be from API response)
    queryClient.setQueryData(['leads', user?.tenant_id, leadId], {
      ...lead,
      status: newStatus,
      updated_at: new Date().toISOString(),
    });
    
    // Invalidate to refetch from server
    queryClient.invalidateQueries({ queryKey: ['leads', user?.tenant_id, leadId] });
  };

  const handleAddNote = async (content: string) => {
    // Simulate API call
    await new Promise(resolve => setTimeout(resolve, 500));
    const newNote: Note = {
      id: `note-${Date.now()}`,
      content,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
      created_by: user?.email,
    };
    setNotes([newNote, ...notes]);
  };

  const handleEditNote = async (noteId: string, content: string) => {
    // Simulate API call
    await new Promise(resolve => setTimeout(resolve, 500));
    setNotes(notes.map(note =>
      note.id === noteId
        ? { ...note, content, updated_at: new Date().toISOString() }
        : note
    ));
  };

  const handleDeleteNote = async (noteId: string) => {
    // Simulate API call
    await new Promise(resolve => setTimeout(resolve, 500));
    setNotes(notes.filter(note => note.id !== noteId));
  };

  const getScoreColor = (score: number): string => {
    if (score >= 61) return 'text-green-600';
    if (score >= 31) return 'text-yellow-600';
    return 'text-gray-600';
  };



  if (!user || !user.tenant_id) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="text-gray-500">Please log in to view lead details</div>
      </div>
    );
  }

  if (isLoading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="text-gray-500">Loading lead...</div>
      </div>
    );
  }

  if (error || !lead) {
    return (
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
          Error: {error ? (error as Error).message : 'Lead not found'}
        </div>
      </div>
    );
  }

  const isHot = lead.score >= 80;
  const timelineEvents = generateTimelineFromLead(lead);

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Header */}
      <div className="mb-6">
        <button
          onClick={() => navigate(`/tenants/${user.tenant_id}/leads`)}
          className="text-blue-600 hover:text-blue-700 mb-4 flex items-center gap-1"
        >
          ← リード一覧に戻る
        </button>
        
        <div className="bg-white shadow-sm rounded-lg border border-gray-200 p-6">
          <div className="flex justify-between items-start">
            <div className="flex-1">
              <div className="flex items-center gap-3 mb-2">
                {isHot && (
                  <div className="flex items-center gap-2 px-3 py-1 bg-orange-100 text-orange-700 rounded-full border border-orange-300">
                    <FlameIcon className="w-5 h-5 animate-pulse" />
                    <span className="text-sm font-semibold">ホットリード</span>
                  </div>
                )}
                <h1 className="text-3xl font-bold text-gray-900">{lead.name}</h1>
              </div>
              
              <div className="flex items-center gap-3 mb-4">
                <StatusDropdown
                  currentStatus={lead.status as LeadStatus}
                  onChange={handleStatusChange}
                />
                <span className={`text-sm font-semibold ${getScoreColor(lead.score)}`}>
                  スコア: {lead.score} / 100
                </span>
              </div>

              {/* Quick Contact Actions */}
              <div className="flex gap-3 mt-4">
                <a
                  href={`mailto:${lead.email}`}
                  className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
                >
                  <MailIcon className="w-4 h-4" />
                  メール送信
                </a>
                {lead.phone && (
                  <a
                    href={`tel:${lead.phone}`}
                    className="flex items-center gap-2 px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700"
                  >
                    <PhoneIcon className="w-4 h-4" />
                    電話する
                  </a>
                )}
              </div>
            </div>

            <div className="flex gap-3">
              <button
                onClick={() => navigate(`/tenants/${user.tenant_id}/leads/${leadId}/edit`)}
                className="px-4 py-2 bg-gray-100 text-gray-700 rounded-md hover:bg-gray-200 border border-gray-300"
              >
                編集
              </button>
              <button
                onClick={() => setShowDeleteConfirm(true)}
                className="px-4 py-2 bg-red-100 text-red-700 rounded-md hover:bg-red-200 border border-red-300"
              >
                削除
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Delete Confirmation */}
      {showDeleteConfirm && (
        <div className="mb-6 bg-red-50 border border-red-200 p-4 rounded-md">
          <p className="text-red-800 font-medium mb-3">
            Are you sure you want to delete this lead? This action cannot be undone.
          </p>
          <div className="flex gap-3">
            <button
              onClick={handleDelete}
              disabled={deleteMutation.isPending}
              className="px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700 disabled:opacity-50"
            >
              {deleteMutation.isPending ? 'Deleting...' : 'Yes, Delete'}
            </button>
            <button
              onClick={() => setShowDeleteConfirm(false)}
              className="px-4 py-2 bg-white border border-gray-300 text-gray-700 rounded-md hover:bg-gray-50"
            >
              Cancel
            </button>
          </div>
        </div>
      )}

      {/* Content */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Main Content */}
        <div className="lg:col-span-2 space-y-6">
          {/* Score Breakdown */}
          <ScoreBreakdown totalScore={lead.score} />

          {/* Activity Timeline */}
          <ActivityTimeline events={timelineEvents} />

          {/* Status History */}
          <StatusHistory history={statusHistory} />

          {/* Notes Section */}
          <NotesSection
            notes={notes}
            onAdd={handleAddNote}
            onEdit={handleEditNote}
            onDelete={handleDeleteNote}
          />

          {/* Contact Information */}
          <div className="bg-white shadow-sm rounded-lg border border-gray-200 p-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">連絡先情報</h2>
            <dl className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <dt className="text-sm font-medium text-gray-500">Email</dt>
                <dd className="mt-1 text-sm text-gray-900">
                  <a href={`mailto:${lead.email}`} className="text-blue-600 hover:text-blue-700">
                    {lead.email}
                  </a>
                </dd>
              </div>
              
              {lead.phone && (
                <div>
                  <dt className="text-sm font-medium text-gray-500">Phone</dt>
                  <dd className="mt-1 text-sm text-gray-900">
                    <a href={`tel:${lead.phone}`} className="text-blue-600 hover:text-blue-700">
                      {lead.phone}
                    </a>
                  </dd>
                </div>
              )}

              {lead.company && (
                <div>
                  <dt className="text-sm font-medium text-gray-500">Company</dt>
                  <dd className="mt-1 text-sm text-gray-900">{lead.company}</dd>
                </div>
              )}

              {lead.job_title && (
                <div>
                  <dt className="text-sm font-medium text-gray-500">Job Title</dt>
                  <dd className="mt-1 text-sm text-gray-900">{lead.job_title}</dd>
                </div>
              )}
            </dl>
          </div>

          {/* Tags */}
          {lead.tags && lead.tags.length > 0 && (
            <div className="bg-white shadow-sm rounded-lg border border-gray-200 p-6">
              <h2 className="text-xl font-semibold text-gray-900 mb-4">タグ</h2>
              <div className="flex flex-wrap gap-2">
                {lead.tags.map((tag, index) => (
                  <span
                    key={index}
                    className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-blue-100 text-blue-800"
                  >
                    {tag}
                  </span>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Sidebar */}
        <div className="space-y-6">
          {/* Quick Stats */}
          <div className="bg-white shadow-sm rounded-lg border border-gray-200 p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">概要</h3>
            <dl className="space-y-3">
              <div>
                <dt className="text-sm font-medium text-gray-500">作成日</dt>
                <dd className="mt-1 text-sm text-gray-900">
                  {new Date(lead.created_at).toLocaleDateString('ja-JP')}
                </dd>
              </div>
              
              <div>
                <dt className="text-sm font-medium text-gray-500">最終更新</dt>
                <dd className="mt-1 text-sm text-gray-900">
                  {new Date(lead.updated_at).toLocaleDateString('ja-JP')}
                </dd>
              </div>

              {lead.last_contacted_at && (
                <div>
                  <dt className="text-sm font-medium text-gray-500">最終コンタクト</dt>
                  <dd className="mt-1 text-sm text-gray-900">
                    {new Date(lead.last_contacted_at).toLocaleDateString('ja-JP')}
                  </dd>
                </div>
              )}

              {lead.last_activity_at && (
                <div>
                  <dt className="text-sm font-medium text-gray-500">最終アクティビティ</dt>
                  <dd className="mt-1 text-sm text-gray-900">
                    {new Date(lead.last_activity_at).toLocaleDateString('ja-JP')}
                  </dd>
                </div>
              )}
            </dl>
          </div>
        </div>
      </div>
    </div>
  );
};
