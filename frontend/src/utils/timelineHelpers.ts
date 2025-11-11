/**
 * Timeline Helper Functions
 * 
 * Utility functions for generating timeline events from lead data
 */

export interface TimelineEvent {
  id: string;
  type: 'created' | 'assessment' | 'status_change' | 'note' | 'contact';
  title: string;
  description?: string;
  timestamp: string;
  user?: string;
  metadata?: Record<string, unknown>;
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
  last_contacted_at?: string | null;
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
  return events.sort((a, b) => 
    new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime()
  );
}
