# Real-time Collaborative Assessment Builder

**Status**: Approved  
**Priority**: High  
**Phase**: 2 (Growth)  
**Estimated Effort**: 6 weeks  
**Dependencies**: Supabase Realtime, WebSocket, CRDT

## Overview

Google Docs風のリアルタイムコラボレーションを診断ビルダーに実装。複数のチームメンバーが同時に診断を編集でき、変更が即座に同期されます。

## Business Value

- **チーム生産性**: +200%（並行作業可能）
- **編集サイクル短縮**: 3日 → 6時間
- **コミュニケーションコスト削減**: ミーティング時間 -50%
- **競合優位**: 診断作成ツールで業界初

## User Stories

### 1. 同時編集

**As a** チームメンバー  
**I want to** 他のメンバーと同時に診断を編集  
**So that** 効率的にコンテンツを作成できる

**Acceptance Criteria**:

**Given**: ユーザーAとBが同じ診断を開いている  
**When**: ユーザーAが質問テキストを変更  
**Then**:
- ユーザーBの画面に即座に変更が反映される（500ms以内）
- 編集中の箇所がハイライト表示
- カーソル位置が表示される（色分け）
- 誰が何を編集しているか表示

### 2. Presence（在室表示）

**As a** 編集者  
**I want to** 誰が今診断を見ているか知りたい  
**So that** 重複作業を避けられる

**Acceptance Criteria**:

**Given**: 診断編集画面を開く  
**When**: 他のユーザーも同じ診断を開いている  
**Then**:
- 画面上部にアバター表示（最大8人）
- ホバーで名前、役職、アクションを表示
- オンライン状態（緑）、編集中（黄）、閲覧のみ（グレー）
- リアルタイムで参加/退出を通知

### 3. コメント機能

**As a** レビュアー  
**I want to** 質問に直接コメントを残す  
**So that** フィードバックを効率的に伝えられる

**Acceptance Criteria**:

**Given**: 質問を選択  
**When**: コメントアイコンをクリック  
**Then**:
- コメント入力欄が表示
- @メンションで特定メンバーに通知
- コメントがリアルタイムで他のユーザーに表示
- 未解決/解決済みステータス管理
- スレッド形式で返信可能

### 4. 変更履歴とUndo/Redo

**As a** コンテンツマネージャー  
**I want to** 過去の変更履歴を確認・復元  
**So that** 誤編集をロールバックできる

**Acceptance Criteria**:

**Given**: 診断が編集されている  
**When**: 「変更履歴」を開く  
**Then**:
- タイムライン形式で変更一覧を表示
- 各変更の差分をハイライト表示
- 「誰が、いつ、何を」変更したか明記
- 任意の時点に復元可能
- Cmd+Z / Cmd+Shift+Z でUndo/Redo

### 5. ロック機能

**As a** 編集者  
**I want to** 編集中の質問を一時的にロック  
**So that** 他の人が同時編集して競合しないようにする

**Acceptance Criteria**:

**Given**: 質問を編集中  
**When**: ロックアイコンをクリック  
**Then**:
- その質問が他のユーザーから編集不可に
- ロック中の表示（🔒マーク + ロックしたユーザー名）
- 3分間編集がなければ自動解除
- 手動で解除可能

## Technical Architecture

### Supabase Realtime統合

```typescript
// frontend/src/features/assessments/useRealtimeCollab.ts
import { RealtimeChannel, REALTIME_PRESENCE_LISTEN_EVENTS } from '@supabase/supabase-js'
import { useEffect, useState } from 'react'
import { supabase } from '@/lib/supabase'

export function useRealtimeCollab(assessmentId: string) {
  const [channel, setChannel] = useState<RealtimeChannel | null>(null)
  const [presences, setPresences] = useState<any[]>([])
  const [cursors, setCursors] = useState<Map<string, CursorPosition>>(new Map())

  useEffect(() => {
    const channelName = `assessment:${assessmentId}`
    
    const realtimeChannel = supabase
      .channel(channelName, {
        config: {
          presence: {
            key: user.id,
          },
        },
      })
      // Presence tracking
      .on('presence', { event: 'sync' }, () => {
        const state = realtimeChannel.presenceState()
        setPresences(Object.values(state).flat())
      })
      .on('presence', { event: 'join' }, ({ key, newPresences }) => {
        console.log('User joined:', key)
      })
      .on('presence', { event: 'leave' }, ({ key, leftPresences }) => {
        console.log('User left:', key)
      })
      // Broadcast: カーソル位置
      .on('broadcast', { event: 'cursor-move' }, ({ payload }) => {
        setCursors(prev => {
          const next = new Map(prev)
          next.set(payload.userId, {
            x: payload.x,
            y: payload.y,
            questionId: payload.questionId,
          })
          return next
        })
      })
      // Broadcast: コンテンツ変更
      .on('broadcast', { event: 'content-change' }, ({ payload }) => {
        handleRemoteChange(payload)
      })
      // Database changes
      .on(
        'postgres_changes',
        {
          event: '*',
          schema: 'public',
          table: 'questions',
          filter: `assessment_id=eq.${assessmentId}`,
        },
        (payload) => {
          handleDatabaseChange(payload)
        }
      )
      .subscribe(async (status) => {
        if (status === 'SUBSCRIBED') {
          await realtimeChannel.track({
            userId: user.id,
            userName: user.name,
            userAvatar: user.avatar,
            online_at: new Date().toISOString(),
          })
        }
      })

    setChannel(realtimeChannel)

    return () => {
      realtimeChannel.unsubscribe()
    }
  }, [assessmentId])

  const broadcastCursorMove = (x: number, y: number, questionId: string) => {
    channel?.send({
      type: 'broadcast',
      event: 'cursor-move',
      payload: { userId: user.id, x, y, questionId },
    })
  }

  const broadcastContentChange = (change: ContentChange) => {
    channel?.send({
      type: 'broadcast',
      event: 'content-change',
      payload: change,
    })
  }

  return {
    presences,
    cursors,
    broadcastCursorMove,
    broadcastContentChange,
  }
}
```

### Operational Transformation (OT)

```typescript
// frontend/src/lib/ot/text-operation.ts
export class TextOperation {
  ops: Operation[] = []

  retain(n: number) {
    if (n === 0) return this
    this.ops.push({ type: 'retain', n })
    return this
  }

  insert(str: string) {
    if (str === '') return this
    this.ops.push({ type: 'insert', str })
    return this
  }

  delete(n: number) {
    if (n === 0) return this
    this.ops.push({ type: 'delete', n })
    return this
  }

  compose(other: TextOperation): TextOperation {
    // OTの合成ロジック
    const composed = new TextOperation()
    // ... 実装
    return composed
  }

  transform(other: TextOperation): [TextOperation, TextOperation] {
    // OTの変換ロジック（競合解決）
    // ... 実装
    return [transformedA, transformedB]
  }

  apply(text: string): string {
    let result = ''
    let index = 0
    
    for (const op of this.ops) {
      if (op.type === 'retain') {
        result += text.slice(index, index + op.n)
        index += op.n
      } else if (op.type === 'insert') {
        result += op.str
      } else if (op.type === 'delete') {
        index += op.n
      }
    }
    
    return result + text.slice(index)
  }
}
```

### バックエンド同期処理

```python
# backend/app/services/collaboration_service.py
from typing import Dict, List
import asyncio
from collections import defaultdict

class CollaborationService:
    def __init__(self):
        self.active_sessions: Dict[str, List[str]] = defaultdict(list)
        self.locks: Dict[str, Dict[str, Lock]] = defaultdict(dict)
    
    async def join_session(
        self, 
        assessment_id: str, 
        user_id: str
    ):
        """コラボレーションセッションに参加"""
        self.active_sessions[assessment_id].append(user_id)
        
        # 現在のPresenceをブロードキャスト
        await self._broadcast_presence_update(assessment_id)
    
    async def leave_session(
        self, 
        assessment_id: str, 
        user_id: str
    ):
        """セッションから退出"""
        if user_id in self.active_sessions[assessment_id]:
            self.active_sessions[assessment_id].remove(user_id)
        
        # 保持していたロックを解放
        await self._release_all_locks(assessment_id, user_id)
        
        await self._broadcast_presence_update(assessment_id)
    
    async def acquire_lock(
        self,
        assessment_id: str,
        question_id: str,
        user_id: str,
        timeout: int = 180  # 3分
    ) -> bool:
        """質問のロックを取得"""
        lock_key = f"{assessment_id}:{question_id}"
        
        if lock_key in self.locks[assessment_id]:
            current_lock = self.locks[assessment_id][lock_key]
            if current_lock.user_id != user_id:
                return False  # 既に他のユーザーがロック中
        
        lock = Lock(
            user_id=user_id,
            acquired_at=datetime.now(),
            expires_at=datetime.now() + timedelta(seconds=timeout)
        )
        
        self.locks[assessment_id][lock_key] = lock
        
        # ロック状態をブロードキャスト
        await self._broadcast_lock_update(assessment_id, question_id, lock)
        
        # 自動解放タイマー
        asyncio.create_task(self._auto_release_lock(
            assessment_id, question_id, timeout
        ))
        
        return True
    
    async def apply_change(
        self,
        assessment_id: str,
        change: Dict,
        user_id: str
    ):
        """変更を適用して同期"""
        # 変更履歴に記録
        await self._save_change_history(assessment_id, change, user_id)
        
        # データベースに反映
        await self._apply_to_database(change)
        
        # 他のユーザーにブロードキャスト（送信者以外）
        await self._broadcast_change(
            assessment_id, 
            change, 
            exclude_user=user_id
        )
```

### 変更履歴管理

```python
# backend/app/services/change_history_service.py
class ChangeHistoryService:
    async def save_change(
        self,
        assessment_id: str,
        change_type: str,
        data: Dict,
        user_id: str
    ) -> ChangeHistory:
        """変更を記録"""
        change = ChangeHistory(
            assessment_id=assessment_id,
            change_type=change_type,
            data=data,
            user_id=user_id,
            timestamp=datetime.now()
        )
        
        await db.add(change)
        await db.commit()
        
        return change
    
    async def get_history(
        self,
        assessment_id: str,
        limit: int = 100
    ) -> List[ChangeHistory]:
        """変更履歴を取得"""
        return await db.query(ChangeHistory)\
            .filter(ChangeHistory.assessment_id == assessment_id)\
            .order_by(ChangeHistory.timestamp.desc())\
            .limit(limit)\
            .all()
    
    async def revert_to(
        self,
        assessment_id: str,
        change_id: str
    ):
        """指定の変更時点に復元"""
        target_change = await db.get(ChangeHistory, change_id)
        
        # その時点までの変更を逆順に適用
        changes_to_revert = await db.query(ChangeHistory)\
            .filter(
                ChangeHistory.assessment_id == assessment_id,
                ChangeHistory.timestamp > target_change.timestamp
            )\
            .order_by(ChangeHistory.timestamp.desc())\
            .all()
        
        for change in changes_to_revert:
            await self._apply_inverse_change(change)
```

## API Endpoints

```
POST   /api/v1/collaboration/sessions/{assessment_id}/join
       - セッション参加

POST   /api/v1/collaboration/sessions/{assessment_id}/leave
       - セッション退出

GET    /api/v1/collaboration/sessions/{assessment_id}/presences
       - 現在のPresence取得

POST   /api/v1/collaboration/locks/{assessment_id}/{question_id}/acquire
       - ロック取得

POST   /api/v1/collaboration/locks/{assessment_id}/{question_id}/release
       - ロック解放

POST   /api/v1/collaboration/changes/{assessment_id}
       - 変更適用

GET    /api/v1/collaboration/history/{assessment_id}
       - 変更履歴取得

POST   /api/v1/collaboration/history/{assessment_id}/revert
       - 変更を復元

POST   /api/v1/collaboration/comments
       - コメント追加

GET    /api/v1/collaboration/comments/{assessment_id}
       - コメント一覧取得
```

## Database Schema

```sql
-- 変更履歴
CREATE TABLE collab_change_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    assessment_id UUID NOT NULL REFERENCES assessments(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id),
    
    change_type VARCHAR(50) NOT NULL,  -- question_add, question_edit, question_delete
    entity_id UUID,  -- question_id or choice_id
    
    before_data JSONB,
    after_data JSONB,
    
    timestamp TIMESTAMP DEFAULT NOW(),
    
    INDEX(assessment_id, timestamp DESC),
    INDEX(entity_id)
);

-- コメント
CREATE TABLE collab_comments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    assessment_id UUID NOT NULL REFERENCES assessments(id) ON DELETE CASCADE,
    question_id UUID REFERENCES questions(id) ON DELETE CASCADE,
    
    user_id UUID NOT NULL REFERENCES users(id),
    content TEXT NOT NULL,
    
    parent_comment_id UUID REFERENCES collab_comments(id),
    
    status VARCHAR(50) DEFAULT 'open',  -- open, resolved
    resolved_by UUID REFERENCES users(id),
    resolved_at TIMESTAMP,
    
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    
    INDEX(assessment_id, status),
    INDEX(question_id)
);
```

## Success Metrics

- **同時編集セッション数**: 月間500+
- **変更競合率**: <1%（OTによる自動解決）
- **コメント利用率**: 80%のチーム
- **編集サイクル時間短縮**: 70%削減

## Related Specifications

- [Microsoft Teams Integration](./microsoft-teams-integration.md)
- [Assessment Builder](./diagnostics-builder.md)
