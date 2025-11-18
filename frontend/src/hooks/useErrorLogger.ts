import { useCallback } from 'react';
import type { SystemError } from '../lib/errorHandler';

export const useErrorLogger = () => {
  const logError = useCallback((error: unknown, context?: string) => {
    console.group(`❌ エラーが発生しました${context ? ` - ${context}` : ''}`);
    
    // Error のタイプに応じた処理
    if (error instanceof Error) {
      console.error('エラー名:', error.name);
      console.error('エラーメッセージ:', error.message);
      console.error('スタックトレース:', error.stack);
    } else if (typeof error === 'object' && error !== null) {
      console.error('エラーオブジェクト:', error);
      
      // SystemError の場合
      if ('code' in error && 'status' in error) {
        const systemError = error as SystemError;
        console.group('📋 システムエラー詳細');
        console.error('コード:', systemError.code);
        console.error('ステータス:', systemError.status);
        console.error('メッセージ:', systemError.message);
        console.error('詳細:', systemError.details);
        console.error('タイムスタンプ:', systemError.timestamp);
        console.groupEnd();
      }
      
      // AxiosError の場合
      if ('response' in error || 'config' in error) {
        console.group('🌐 APIエラー詳細');
        console.error('全体:', error);
        if ('response' in error) {
          console.error('レスポンス:', (error as any).response?.data);
          console.error('ステータスコード:', (error as any).response?.status);
          console.error('ヘッダー:', (error as any).response?.headers);
        }
        if ('config' in error) {
          console.error('リクエスト設定:', (error as any).config);
        }
        console.groupEnd();
      }
    } else {
      console.error('エラー:', error);
    }
    
    console.groupEnd();
  }, []);

  const logApiCall = useCallback((method: string, url: string, data?: any) => {
    console.group(`🌐 API呼び出し: ${method} ${url}`);
    if (data) {
      console.log('リクエストボディ:', data);
    }
    console.groupEnd();
  }, []);

  const logApiResponse = useCallback((method: string, url: string, status: number, data?: any) => {
    const statusColor = status >= 200 && status < 300 ? '✅' : '⚠️';
    console.group(`${statusColor} API レスポンス: ${method} ${url} (${status})`);
    if (data) {
      console.log('レスポンスボディ:', data);
    }
    console.groupEnd();
  }, []);

  return {
    logError,
    logApiCall,
    logApiResponse,
  };
};
