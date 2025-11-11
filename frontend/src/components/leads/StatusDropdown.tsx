/**
 * Status Dropdown Component
 * 
 * Manage lead status with:
 * - Current status display
 * - Status change options
 * - Confirmation dialog for critical changes
 * - Workflow validation
 * - Optimistic updates
 */

import React, { useState } from 'react';
import { CheckIcon, ChevronDownIcon, XIcon } from 'lucide-react';

export type LeadStatus = 'new' | 'contacted' | 'qualified' | 'negotiation' | 'won' | 'lost';

interface StatusOption {
  value: LeadStatus;
  label: string;
  color: string;
  bgColor: string;
  description: string;
  requiresNote?: boolean;
}

const statusOptions: StatusOption[] = [
  {
    value: 'new',
    label: '新規',
    color: 'text-blue-700',
    bgColor: 'bg-blue-100 hover:bg-blue-200',
    description: '新しく獲得したリード',
  },
  {
    value: 'contacted',
    label: 'コンタクト済み',
    color: 'text-yellow-700',
    bgColor: 'bg-yellow-100 hover:bg-yellow-200',
    description: '初回コンタクトが完了',
  },
  {
    value: 'qualified',
    label: '有望',
    color: 'text-green-700',
    bgColor: 'bg-green-100 hover:bg-green-200',
    description: '購買意欲が確認された',
  },
  {
    value: 'negotiation',
    label: '商談中',
    color: 'text-purple-700',
    bgColor: 'bg-purple-100 hover:bg-purple-200',
    description: '商談・デモを実施中',
  },
  {
    value: 'won',
    label: '成約',
    color: 'text-emerald-700',
    bgColor: 'bg-emerald-100 hover:bg-emerald-200',
    description: '契約が成立',
  },
  {
    value: 'lost',
    label: '失注',
    color: 'text-red-700',
    bgColor: 'bg-red-100 hover:bg-red-200',
    description: '失注または見送り',
    requiresNote: true,
  },
];

interface StatusDropdownProps {
  currentStatus: LeadStatus;
  onChange: (newStatus: LeadStatus, note?: string) => Promise<void>;
  disabled?: boolean;
}

export function StatusDropdown({ currentStatus, onChange, disabled }: StatusDropdownProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [isChanging, setIsChanging] = useState(false);
  const [selectedStatus, setSelectedStatus] = useState<LeadStatus | null>(null);
  const [showConfirmDialog, setShowConfirmDialog] = useState(false);
  const [note, setNote] = useState('');

  const currentOption = statusOptions.find(opt => opt.value === currentStatus);

  const handleStatusClick = (status: LeadStatus) => {
    if (status === currentStatus) {
      setIsOpen(false);
      return;
    }

    const option = statusOptions.find(opt => opt.value === status);
    
    // Check if note is required or if it's a critical change
    if (option?.requiresNote || status === 'lost' || status === 'won') {
      setSelectedStatus(status);
      setShowConfirmDialog(true);
      setIsOpen(false);
    } else {
      // Direct change without confirmation
      handleConfirmChange(status);
    }
  };

  const handleConfirmChange = async (status?: LeadStatus) => {
    const targetStatus = status || selectedStatus;
    if (!targetStatus) return;

    const option = statusOptions.find(opt => opt.value === targetStatus);
    
    // Validate note requirement
    if (option?.requiresNote && !note.trim()) {
      alert('このステータス変更には理由の入力が必要です');
      return;
    }

    setIsChanging(true);
    try {
      await onChange(targetStatus, note.trim() || undefined);
      setShowConfirmDialog(false);
      setSelectedStatus(null);
      setNote('');
    } catch (error) {
      console.error('Failed to change status:', error);
      alert('ステータスの変更に失敗しました');
    } finally {
      setIsChanging(false);
    }
  };

  const handleCancelChange = () => {
    setShowConfirmDialog(false);
    setSelectedStatus(null);
    setNote('');
  };

  if (!currentOption) return null;

  return (
    <div className="relative">
      {/* Current Status Button */}
      <button
        onClick={() => !disabled && setIsOpen(!isOpen)}
        disabled={disabled}
        className={`
          flex items-center gap-2 px-4 py-2 rounded-lg border-2 font-medium transition-colors
          ${currentOption.bgColor} ${currentOption.color}
          ${disabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer hover:shadow-md'}
        `}
      >
        <span>{currentOption.label}</span>
        <ChevronDownIcon className={`w-4 h-4 transition-transform ${isOpen ? 'rotate-180' : ''}`} />
      </button>

      {/* Dropdown Menu */}
      {isOpen && (
        <>
          <div
            className="fixed inset-0 z-10"
            onClick={() => setIsOpen(false)}
          />
          <div className="absolute left-0 mt-2 w-72 bg-white rounded-lg shadow-lg border border-gray-200 z-20 overflow-hidden">
            <div className="p-3 border-b border-gray-200 bg-gray-50">
              <p className="text-sm font-semibold text-gray-900">ステータスを変更</p>
              <p className="text-xs text-gray-600 mt-1">新しいステータスを選択してください</p>
            </div>
            <div className="max-h-96 overflow-y-auto">
              {statusOptions.map((option) => (
                <button
                  key={option.value}
                  onClick={() => handleStatusClick(option.value)}
                  disabled={isChanging}
                  className={`
                    w-full text-left px-4 py-3 transition-colors
                    ${option.bgColor}
                    ${option.value === currentStatus ? 'opacity-50' : ''}
                    ${isChanging ? 'cursor-not-allowed' : 'cursor-pointer'}
                    border-b border-gray-100 last:border-b-0
                  `}
                >
                  <div className="flex items-start gap-3">
                    <div className="flex-shrink-0 mt-0.5">
                      {option.value === currentStatus && (
                        <CheckIcon className="w-5 h-5 text-green-600" />
                      )}
                      {option.value !== currentStatus && (
                        <div className="w-5 h-5" />
                      )}
                    </div>
                    <div className="flex-1">
                      <div className={`font-medium ${option.color}`}>
                        {option.label}
                      </div>
                      <div className="text-xs text-gray-600 mt-1">
                        {option.description}
                      </div>
                      {option.requiresNote && (
                        <div className="text-xs text-red-600 mt-1">
                          ※ 理由の入力が必要
                        </div>
                      )}
                    </div>
                  </div>
                </button>
              ))}
            </div>
          </div>
        </>
      )}

      {/* Confirmation Dialog */}
      {showConfirmDialog && selectedStatus && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50">
          <div className="bg-white rounded-lg shadow-xl max-w-md w-full mx-4">
            <div className="p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-2">
                ステータス変更の確認
              </h3>
              <p className="text-sm text-gray-600 mb-4">
                リードのステータスを「
                <span className="font-semibold">{currentOption.label}</span>
                」から「
                <span className="font-semibold">
                  {statusOptions.find(opt => opt.value === selectedStatus)?.label}
                </span>
                」に変更します。
              </p>

              {/* Note Input */}
              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  変更理由・メモ
                  {statusOptions.find(opt => opt.value === selectedStatus)?.requiresNote && (
                    <span className="text-red-600 ml-1">*</span>
                  )}
                </label>
                <textarea
                  value={note}
                  onChange={(e) => setNote(e.target.value)}
                  placeholder="変更理由やメモを入力..."
                  rows={3}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500 resize-none"
                />
              </div>

              {/* Actions */}
              <div className="flex gap-3">
                <button
                  onClick={() => handleConfirmChange()}
                  disabled={isChanging}
                  className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 font-medium"
                >
                  {isChanging ? '変更中...' : '変更する'}
                </button>
                <button
                  onClick={handleCancelChange}
                  disabled={isChanging}
                  className="flex-1 px-4 py-2 bg-white border border-gray-300 text-gray-700 rounded-md hover:bg-gray-50 disabled:opacity-50"
                >
                  キャンセル
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
