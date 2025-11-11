/**
 * Timeline Helpers Unit Tests
 * 
 * Tests for generateTimelineFromLead function
 */

import { describe, it, expect } from 'vitest';
import { generateTimelineFromLead } from '../timelineHelpers';

describe('timelineHelpers', () => {
  describe('generateTimelineFromLead', () => {
    it('should generate created event for a basic lead', () => {
      const lead = {
        id: 'lead-123',
        name: '山田太郎',
        created_at: '2025-01-01T00:00:00Z',
        updated_at: '2025-01-01T00:00:00Z',
        score: 75,
        status: 'new',
      };

      const events = generateTimelineFromLead(lead);

      expect(events).toHaveLength(1);
      expect(events[0]).toMatchObject({
        type: 'created',
        title: 'リード作成',
        description: '山田太郎 が新規リードとして追加されました',
      });
    });

    it('should generate assessment completion events', () => {
      const lead = {
        id: 'lead-123',
        name: '山田太郎',
        created_at: '2025-01-01T00:00:00Z',
        updated_at: '2025-01-02T00:00:00Z',
        score: 85,
        status: 'qualified',
        assessment_responses: [
          {
            id: 'response-1',
            assessment_title: 'ビジネス課題診断',
            completed_at: '2025-01-01T10:00:00Z',
            created_at: '2025-01-01T10:00:00Z',
          },
          {
            id: 'response-2',
            assessment_title: 'ニーズ診断',
            completed_at: '2025-01-02T10:00:00Z',
            created_at: '2025-01-02T10:00:00Z',
          },
        ],
      };

      const events = generateTimelineFromLead(lead);

      const assessmentEvents = events.filter(e => e.type === 'assessment');
      expect(assessmentEvents).toHaveLength(2);
      
      // イベントは新しい順にソートされているので、最新の診断が最初に来る
      expect(assessmentEvents[0]).toMatchObject({
        type: 'assessment',
        title: '診断完了',
        description: 'ニーズ診断',
        metadata: {
          スコア: '85点',
        },
      });
      
      expect(assessmentEvents[1]).toMatchObject({
        type: 'assessment',
        title: '診断完了',
        description: 'ビジネス課題診断',
        metadata: {
          スコア: '85点',
        },
      });
    });

    it('should generate status change event for non-new status', () => {
      const lead = {
        id: 'lead-123',
        name: '山田太郎',
        created_at: '2025-01-01T00:00:00Z',
        updated_at: '2025-01-02T00:00:00Z',
        score: 75,
        status: 'contacted',
      };

      const events = generateTimelineFromLead(lead);

      const statusEvents = events.filter(e => e.type === 'status_change');
      expect(statusEvents).toHaveLength(1);
      expect(statusEvents[0]).toMatchObject({
        type: 'status_change',
        title: 'ステータス変更',
        description: 'ステータスが「contacted」に変更されました',
      });
    });

    it('should not generate status change event for new status', () => {
      const lead = {
        id: 'lead-123',
        name: '山田太郎',
        created_at: '2025-01-01T00:00:00Z',
        updated_at: '2025-01-01T00:00:00Z',
        score: 75,
        status: 'new',
      };

      const events = generateTimelineFromLead(lead);

      const statusEvents = events.filter(e => e.type === 'status_change');
      expect(statusEvents).toHaveLength(0);
    });

    it('should generate contact event when last_contacted_at is provided', () => {
      const lead = {
        id: 'lead-123',
        name: '山田太郎',
        created_at: '2025-01-01T00:00:00Z',
        updated_at: '2025-01-02T00:00:00Z',
        score: 75,
        status: 'contacted',
        last_contacted_at: '2025-01-02T14:00:00Z',
      };

      const events = generateTimelineFromLead(lead);

      const contactEvents = events.filter(e => e.type === 'contact');
      expect(contactEvents).toHaveLength(1);
      expect(contactEvents[0]).toMatchObject({
        type: 'contact',
        title: 'コンタクト実施',
        description: '担当者がリードにコンタクトしました',
        timestamp: '2025-01-02T14:00:00Z',
      });
    });

    it('should handle null last_contacted_at', () => {
      const lead = {
        id: 'lead-123',
        name: '山田太郎',
        created_at: '2025-01-01T00:00:00Z',
        updated_at: '2025-01-01T00:00:00Z',
        score: 75,
        status: 'new',
        last_contacted_at: null,
      };

      const events = generateTimelineFromLead(lead);

      const contactEvents = events.filter(e => e.type === 'contact');
      expect(contactEvents).toHaveLength(0);
    });

    it('should sort events by timestamp (newest first)', () => {
      const lead = {
        id: 'lead-123',
        name: '山田太郎',
        created_at: '2025-01-01T00:00:00Z',
        updated_at: '2025-01-03T00:00:00Z',
        score: 85,
        status: 'contacted',
        assessment_responses: [
          {
            id: 'response-1',
            assessment_title: '診断1',
            completed_at: '2025-01-02T00:00:00Z',
            created_at: '2025-01-02T00:00:00Z',
          },
        ],
        last_contacted_at: '2025-01-04T00:00:00Z',
      };

      const events = generateTimelineFromLead(lead);

      // タイムスタンプを確認（新しい順）
      const timestamps = events.map(e => new Date(e.timestamp).getTime());
      for (let i = 0; i < timestamps.length - 1; i++) {
        expect(timestamps[i]).toBeGreaterThanOrEqual(timestamps[i + 1]);
      }
    });

    it('should handle assessment without assessment_title', () => {
      const lead = {
        id: 'lead-123',
        name: '山田太郎',
        created_at: '2025-01-01T00:00:00Z',
        updated_at: '2025-01-02T00:00:00Z',
        score: 85,
        status: 'new',
        assessment_responses: [
          {
            id: 'response-1',
            created_at: '2025-01-01T10:00:00Z',
          },
        ],
      };

      const events = generateTimelineFromLead(lead);

      const assessmentEvents = events.filter(e => e.type === 'assessment');
      expect(assessmentEvents[0].description).toBe('診断に回答しました');
    });

    it('should generate all event types for a complete lead', () => {
      const lead = {
        id: 'lead-123',
        name: '山田太郎',
        created_at: '2025-01-01T00:00:00Z',
        updated_at: '2025-01-03T00:00:00Z',
        score: 85,
        status: 'qualified',
        assessment_responses: [
          {
            id: 'response-1',
            assessment_title: 'ビジネス課題診断',
            completed_at: '2025-01-02T00:00:00Z',
            created_at: '2025-01-02T00:00:00Z',
          },
        ],
        last_contacted_at: '2025-01-04T00:00:00Z',
      };

      const events = generateTimelineFromLead(lead);

      const eventTypes = events.map(e => e.type);
      expect(eventTypes).toContain('created');
      expect(eventTypes).toContain('assessment');
      expect(eventTypes).toContain('status_change');
      expect(eventTypes).toContain('contact');
    });

    it('should generate unique IDs for all events', () => {
      const lead = {
        id: 'lead-123',
        name: '山田太郎',
        created_at: '2025-01-01T00:00:00Z',
        updated_at: '2025-01-03T00:00:00Z',
        score: 85,
        status: 'qualified',
        assessment_responses: [
          {
            id: 'response-1',
            assessment_title: '診断1',
            completed_at: '2025-01-02T00:00:00Z',
            created_at: '2025-01-02T00:00:00Z',
          },
          {
            id: 'response-2',
            assessment_title: '診断2',
            completed_at: '2025-01-02T10:00:00Z',
            created_at: '2025-01-02T10:00:00Z',
          },
        ],
        last_contacted_at: '2025-01-04T00:00:00Z',
      };

      const events = generateTimelineFromLead(lead);

      const ids = events.map(e => e.id);
      const uniqueIds = new Set(ids);
      expect(uniqueIds.size).toBe(ids.length);
    });
  });
});
