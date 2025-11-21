/**
 * Lead Service Tests
 *
 * リードサービスのテストテンプレート
 * TODO: 実装を追加してください
 */

import { describe, it, vi, beforeEach } from 'vitest';

// TODO: leadServiceをインポート
// import { leadService } from '../leadService';

// NOTE: テストの実装時に以下のインポートのコメントを解除してください:
// - expect (from 'vitest')

describe('LeadService', () => {
  beforeEach(() => {
    // モックをクリア
    vi.clearAllMocks();
  });

  describe('getLeads', () => {
    it.skip('リードのリストを取得できる', async () => {
      // TODO: 実装後、skipを削除
      // const mockLeads = [
      //   { id: '1', name: '山田太郎', email: 'yamada@example.com', score: 75 },
      //   { id: '2', name: '佐藤花子', email: 'sato@example.com', score: 85 },
      // ];

      // // APIクライアントをモック
      // vi.spyOn(apiClient, 'get').mockResolvedValue({ data: mockLeads });

      // const result = await leadService.getLeads();

      // expect(result).toEqual(mockLeads);
      // expect(apiClient.get).toHaveBeenCalledWith('/leads');
    });

    it.skip('ページネーションパラメータを正しく送信する', async () => {
      // TODO: 実装後、skipを削除
      // vi.spyOn(apiClient, 'get').mockResolvedValue({ data: [] });

      // await leadService.getLeads({ page: 2, limit: 20 });

      // expect(apiClient.get).toHaveBeenCalledWith('/leads', {
      //   params: { page: 2, limit: 20 },
      // });
    });
  });

  describe('getLeadById', () => {
    it.skip('特定のリードを取得できる', async () => {
      // TODO: 実装後、skipを削除
      // const mockLead = {
      //   id: '123',
      //   name: '山田太郎',
      //   email: 'yamada@example.com',
      //   score: 75,
      //   status: 'new',
      // };

      // vi.spyOn(apiClient, 'get').mockResolvedValue({ data: mockLead });

      // const result = await leadService.getLeadById('123');

      // expect(result).toEqual(mockLead);
      // expect(apiClient.get).toHaveBeenCalledWith('/leads/123');
    });

    it.skip('リードが見つからない場合エラーを投げる', async () => {
      // TODO: 実装後、skipを削除
      // vi.spyOn(apiClient, 'get').mockRejectedValue(new Error('Not Found'));

      // await expect(leadService.getLeadById('invalid-id')).rejects.toThrow();
    });
  });

  describe('updateLeadStatus', () => {
    it.skip('リードのステータスを更新できる', async () => {
      // TODO: 実装後、skipを削除
      // const leadId = '123';
      // const newStatus = 'contacted';

      // vi.spyOn(apiClient, 'patch').mockResolvedValue({ data: { id: leadId, status: newStatus } });

      // const result = await leadService.updateLeadStatus(leadId, newStatus);

      // expect(result.status).toBe(newStatus);
      // expect(apiClient.patch).toHaveBeenCalledWith(`/leads/${leadId}`, { status: newStatus });
    });
  });

  describe('exportLeads', () => {
    it.skip('リードをCSVエクスポートできる', async () => {
      // TODO: 実装後、skipを削除
      // const mockBlob = new Blob(['csv,data'], { type: 'text/csv' });

      // vi.spyOn(apiClient, 'get').mockResolvedValue({ data: mockBlob });

      // const result = await leadService.exportLeads('csv');

      // expect(result).toBeInstanceOf(Blob);
      // expect(apiClient.get).toHaveBeenCalledWith('/leads/export', {
      //   params: { format: 'csv' },
      //   responseType: 'blob',
      // });
    });
  });
});
