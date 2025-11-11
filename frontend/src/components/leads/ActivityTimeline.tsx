/**
 * Activity Timeline Component
 * 
 * Displays chronological activity history:
 * - Assessment completions
 * - Status changes
 * - Notes added
 * - Contact events
 */


import {
  ClipboardCheckIcon,
  RefreshCwIcon,
  MessageSquareIcon,
  MailIcon,
  UserPlusIcon,
  CalendarIcon,
} from 'lucide-react';

export interface TimelineEvent {
  id: string;
  type: 'assessment' | 'status_change' | 'note' | 'contact' | 'created';
  title: string;
  description?: string;
  timestamp: string;
  user?: string;
  metadata?: Record<string, unknown>;
}

interface ActivityTimelineProps {
  events: TimelineEvent[];
}

export function ActivityTimeline({ events }: ActivityTimelineProps) {
  const getEventIcon = (type: string) => {
    switch (type) {
      case 'assessment':
        return <ClipboardCheckIcon className="w-5 h-5" />;
      case 'status_change':
        return <RefreshCwIcon className="w-5 h-5" />;
      case 'note':
        return <MessageSquareIcon className="w-5 h-5" />;
      case 'contact':
        return <MailIcon className="w-5 h-5" />;
      case 'created':
        return <UserPlusIcon className="w-5 h-5" />;
      default:
        return <CalendarIcon className="w-5 h-5" />;
    }
  };

  const getEventColor = (type: string) => {
    switch (type) {
      case 'assessment':
        return 'bg-blue-100 text-blue-600 border-blue-200';
      case 'status_change':
        return 'bg-purple-100 text-purple-600 border-purple-200';
      case 'note':
        return 'bg-green-100 text-green-600 border-green-200';
      case 'contact':
        return 'bg-yellow-100 text-yellow-600 border-yellow-200';
      case 'created':
        return 'bg-gray-100 text-gray-600 border-gray-200';
      default:
        return 'bg-gray-100 text-gray-600 border-gray-200';
    }
  };

  const formatTimestamp = (timestamp: string) => {
    const date = new Date(timestamp);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffMins < 1) return '今';
    if (diffMins < 60) return `${diffMins}分前`;
    if (diffHours < 24) return `${diffHours}時間前`;
    if (diffDays < 7) return `${diffDays}日前`;

    return date.toLocaleDateString('ja-JP', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  if (events.length === 0) {
    return (
      <div className="bg-white shadow-sm rounded-lg border border-gray-200 p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">アクティビティ履歴</h3>
        <div className="text-center py-8 text-gray-500">
          <CalendarIcon className="w-12 h-12 mx-auto mb-3 text-gray-300" />
          <p>まだアクティビティがありません</p>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white shadow-sm rounded-lg border border-gray-200 p-6">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">アクティビティ履歴</h3>
      
      <div className="space-y-4">
        {events.map((event, index) => (
          <div key={event.id} className="relative">
            {/* Timeline line */}
            {index < events.length - 1 && (
              <div className="absolute left-6 top-12 w-0.5 h-full bg-gray-200" />
            )}

            {/* Event */}
            <div className="flex gap-4">
              {/* Icon */}
              <div
                className={`flex-shrink-0 w-12 h-12 rounded-full border-2 flex items-center justify-center ${getEventColor(
                  event.type
                )}`}
              >
                {getEventIcon(event.type)}
              </div>

              {/* Content */}
              <div className="flex-1 min-w-0">
                <div className="flex items-start justify-between gap-2">
                  <div className="flex-1">
                    <h4 className="text-sm font-medium text-gray-900">{event.title}</h4>
                    {event.description && (
                      <p className="text-sm text-gray-600 mt-1">{event.description}</p>
                    )}
                    {event.metadata && (
                      <div className="mt-2 text-xs text-gray-500">
                        {Object.entries(event.metadata).map(([key, value]) => (
                          <div key={key}>
                            <span className="font-medium">{key}:</span> {String(value)}
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                  <time className="text-xs text-gray-500 whitespace-nowrap">
                    {formatTimestamp(event.timestamp)}
                  </time>
                </div>
                {event.user && (
                  <div className="text-xs text-gray-500 mt-1">by {event.user}</div>
                )}
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

// Helper function to generate timeline from lead data
export function generateTimelineFromLead(lead: {
  id: string;
  name: string;
  created_at: string;
  updated_at: string;
  score: number;
  status: string;
  assessment_responses?: Array<{
    id: string;
    assessment_title?: string;
    completed_at?: string;
    created_at: string;
  }>;
  last_contacted_at?: string;
}): TimelineEvent[] {
  const events: TimelineEvent[] = [];

  // Created event
  events.push({
    id: `created-${lead.id}`,
    type: 'created',
    title: 'リード作成',
    description: `${lead.name} が新規リードとして追加されました`,
    timestamp: lead.created_at,
  });

  // Assessment completion (if available)
  if (lead.assessment_responses && lead.assessment_responses.length > 0) {
    lead.assessment_responses.forEach((response) => {
      events.push({
        id: `assessment-${response.id}`,
        type: 'assessment',
        title: '診断完了',
        description: response.assessment_title || '診断に回答しました',
        timestamp: response.completed_at || response.created_at,
        metadata: {
          スコア: `${lead.score}点`,
        },
      });
    });
  }

  // Status changes (simulated - would come from audit log)
  if (lead.status !== 'new') {
    events.push({
      id: `status-${lead.updated_at}`,
      type: 'status_change',
      title: 'ステータス変更',
      description: `ステータスが「${lead.status}」に変更されました`,
      timestamp: lead.updated_at,
    });
  }

  // Last contacted
  if (lead.last_contacted_at) {
    events.push({
      id: `contact-${lead.last_contacted_at}`,
      type: 'contact',
      title: 'コンタクト実施',
      description: '担当者がリードにコンタクトしました',
      timestamp: lead.last_contacted_at,
    });
  }

  // Sort by timestamp (newest first)
  return events.sort(
    (a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime()
  );
}
