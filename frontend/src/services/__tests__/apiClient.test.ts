/**
 * API Client Tests
 *
 * APIクライアントのテストテンプレート
 * TODO: 実装を追加してください
 */

import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import axios from 'axios';
import MockAdapter from 'axios-mock-adapter';

// TODO: APIクライアントをインポート
// import { apiClient, createApiClient } from '../apiClient';

describe('APIClient', () => {
  let mock: MockAdapter;

  beforeEach(() => {
    // Axiosのモックを初期化
    mock = new MockAdapter(axios);
  });

  afterEach(() => {
    // モックをリセット
    mock.restore();
  });

  it.skip('正常なレスポンスを処理できる', async () => {
    // TODO: 実装後、skipを削除
    // const responseData = { id: 1, name: 'Test' };
    // mock.onGet('/api/v1/test').reply(200, responseData);

    // const response = await apiClient.get('/test');

    // expect(response.data).toEqual(responseData);
  });

  it.skip('401エラー時にlocalStorageをクリアする', async () => {
    // TODO: 実装後、skipを削除
    // NOTE: セキュリティ改善後、HttpOnly Cookie使用に変更される予定
    // const clearSpy = vi.spyOn(Storage.prototype, 'removeItem');

    // mock.onGet('/api/v1/protected').reply(401);

    // try {
    //   await apiClient.get('/protected');
    // } catch (error) {
    //   // エラーが発生することを期待
    // }

    // expect(clearSpy).toHaveBeenCalledWith('access_token');
    // expect(clearSpy).toHaveBeenCalledWith('user');
  });

  it.skip('リクエストヘッダーに認証トークンが含まれる', async () => {
    // TODO: 実装後、skipを削除
    // NOTE: セキュリティ改善後、HttpOnly Cookie使用に変更される予定
    // const token = 'test-token';
    // localStorage.setItem('access_token', token);

    // mock.onGet('/api/v1/test').reply((config) => {
    //   expect(config.headers?.Authorization).toBe(`Bearer ${token}`);
    //   return [200, {}];
    // });

    // await apiClient.get('/test');
  });

  it.skip('ネットワークエラーを適切に処理する', async () => {
    // TODO: 実装後、skipを削除
    // mock.onGet('/api/v1/test').networkError();

    // await expect(apiClient.get('/test')).rejects.toThrow();
  });

  it.skip('タイムアウトエラーを適切に処理する', async () => {
    // TODO: 実装後、skipを削除
    // mock.onGet('/api/v1/test').timeout();

    // await expect(apiClient.get('/test')).rejects.toThrow();
  });
});
