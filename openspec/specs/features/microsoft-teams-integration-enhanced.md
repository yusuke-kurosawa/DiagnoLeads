# Feature: Microsoft Teams Integration (Enhanced)

**Status**: Approved  
**Priority**: High  
**Category**: Integration  
**Created**: 2025-11-11  
**Based on**: innovative-features.md - Microsoft 365 Deep Integration

## 概要

Microsoft Teamsとのネイティブ統合を強化し、エンタープライズ市場での競合優位性を確立する。現在の基本的なWebhook統合から、Teams Bot、Adaptive Cards、会議統合、SharePoint連携まで拡張。

## User Stories

- 営業担当者として、Teamsチャット内で直接診断を配信したい
- マーケティング担当者として、ホットリード獲得時にTeams会議を自動予約したい
- マネージャーとして、診断結果レポートがSharePointに自動保存されてほしい
- チームメンバーとして、リード情報がAdaptive Cardsで見やすく表示されてほしい

## Requirements

### Functional Requirements

#### Phase 1: 基本統合（現在実装中）✅
- ✅ Incoming Webhook経由でのリード通知
- ✅ Adaptive Cardsでのリッチな通知UI
- ✅ リトライロジック（3回まで）
- ✅ テスト送信機能

#### Phase 2: Teams Bot統合（次期）
- Teams Bot経由での診断配信
- チャット内での診断回答（ボット対話）
- メンション通知（@営業担当者）
- Bot Commands（/lead-list, /lead-detail）

#### Phase 3: 高度な統合
- Teams会議内での診断実施（画面共有不要）
- SharePoint統合（診断結果レポート自動保存）
- Teams Appストアでの配信
- Microsoft Graph API統合

### Non-Functional Requirements

- **パフォーマンス**: 通知送信は5秒以内
- **可用性**: 99.9% uptime
- **セキュリティ**: Webhook URLは暗号化保存
- **スケーラビリティ**: 1000+ テナントに対応
- **監視**: 送信成功率のモニタリング

## API Design

### Phase 1 (Current)

```
POST   /api/v1/tenants/{tenant_id}/integrations/teams/webhook
  - Webhook URLの設定

POST   /api/v1/tenants/{tenant_id}/integrations/teams/test
  - テスト通知送信

POST   /api/v1/tenants/{tenant_id}/integrations/teams/send
  - リード通知送信（内部API）
```

### Phase 2 (Bot Integration)

```
POST   /api/v1/integrations/teams/bot/install
  - Teams Botのインストール

POST   /api/v1/integrations/teams/bot/send-assessment
  - Bot経由での診断配信

GET    /api/v1/integrations/teams/channels
  - テナントのTeamsチャネル一覧取得
```

### Phase 3 (Advanced)

```
POST   /api/v1/integrations/teams/meeting/create
  - ホットリード用の自動ミーティング作成

POST   /api/v1/integrations/teams/sharepoint/upload
  - 診断結果をSharePointにアップロード

GET    /api/v1/integrations/teams/app-manifest
  - Teams App マニフェスト取得
```

## Data Model

### TeamsIntegration (Enhanced)

```python
class TeamsIntegration(Base):
    __tablename__ = "teams_integrations"
    
    id: UUID
    tenant_id: UUID  # FK to Tenant
    
    # Phase 1: Webhook
    webhook_url: str  # Encrypted
    enabled: bool
    
    # Phase 2: Bot
    bot_enabled: bool
    bot_app_id: str | None
    bot_app_secret: str | None  # Encrypted
    default_channel_id: str | None
    
    # Phase 3: Advanced
    sharepoint_enabled: bool
    sharepoint_site_url: str | None
    auto_meeting_enabled: bool
    
    # Settings
    notification_settings: dict  # JSONB
    # {
    #   "notify_on_hot_lead": true,
    #   "notify_on_response": false,
    #   "mention_user_id": "user@example.com"
    # }
    
    # Metrics
    total_notifications_sent: int
    last_notification_at: datetime | None
    
    created_at: datetime
    updated_at: datetime
```

## UI/UX Design

### Phase 1: Webhook設定画面（実装済み）

- Webhook URL入力フィールド
- 「接続をテスト」ボタン
- 通知設定（ホットリードのみ、全リード）
- 送信履歴

### Phase 2: Bot設定画面

- 「Teams Botをインストール」ボタン
- チャネル選択ドロップダウン
- メンション先ユーザー設定
- Bot コマンドのヘルプ

### Phase 3: 高度な設定

- SharePoint サイトURL設定
- 自動ミーティング作成の有効化
- カレンダー統合設定

## Business Logic

### Phase 1: Webhook通知（実装済み）

1. リードが作成される
2. リードのスコアを確認
3. スコアが閾値以上（ホットリード）の場合:
   - Adaptive Cardを生成
   - Teams Webhook URLに送信
   - リトライロジック（最大3回、指数バックオフ）
4. 送信結果を記録

### Phase 2: Bot統合

1. ユーザーがTeamsで `/diagnoleads` コマンド実行
2. Botが診断リストを表示
3. ユーザーが診断を選択
4. Botがチャット内で質問を順次表示
5. ユーザーがボタンで回答
6. 完了時、結果を表示してリードを作成

### Phase 3: 自動ミーティング

1. ホットリード（スコア80+）が作成される
2. Microsoft Graph APIでカレンダーをチェック
3. 営業担当者の空き時間を検索
4. Teams会議を自動予約
5. リードにメール招待を送信

## Testing Strategy

### Unit Tests

- `TeamsService.send_notification()`: 通知送信ロジック
- `TeamsService.retry_logic()`: リトライロジック
- `AdaptiveCardBuilder.build_lead_card()`: Card生成

### Integration Tests

- Teams Webhook API呼び出し
- Microsoft Graph API認証
- エラーハンドリング（Webhook URL無効、ネットワークエラー）

### E2E Tests

- リード作成 → Teams通知送信 → 成功確認
- Bot経由での診断実施 → リード作成
- 自動ミーティング作成 → カレンダー確認

### Manual Tests

- 実際のTeamsワークスペースでの動作確認
- Adaptive Cardsのレンダリング確認
- Teams Appストアへの提出前テスト

## Implementation Notes

### Phase 1（完了）

- ✅ 基本的なWebhook統合は完了
- ✅ Adaptive Cards対応済み
- ✅ リトライロジック実装済み
- ⚠️ テスト充実化が必要

### Phase 2（次期スプリント）

**技術スタック**:
- Microsoft Bot Framework SDK
- Azure Bot Service（必要に応じて）
- MSAL (Microsoft Authentication Library)

**開発ステップ**:
1. Bot Framework SDKのセットアップ
2. Bot認証フロー実装
3. 対話型診断ロジック
4. Teamsチャネルとの統合

**推定工数**: 3-4週間

### Phase 3（中長期）

**前提条件**:
- Microsoft 365 Enterprise契約
- Graph API権限の取得
- Teams App審査通過

**推定工数**: 8-12週間

### セキュリティ考慮事項

1. **Webhook URL**: 必ず暗号化して保存
2. **Bot Secret**: 環境変数で管理、DB保存時は暗号化
3. **Graph API Token**: 短期トークン、リフレッシュトークンを安全に保存
4. **アクセス制御**: テナント管理者のみが設定変更可能
5. **監査ログ**: すべての通知送信を記録

### パフォーマンス最適化

1. **非同期処理**: Trigger.devで通知送信を非同期化
2. **バッチ処理**: 複数リードの通知を1つのAdaptive Cardにまとめる
3. **キャッシュ**: Teamsチャネル情報をRedisにキャッシュ
4. **レート制限**: Microsoft Graph APIのレート制限を考慮

## Related Specs

- [Integrations Overview](./integrations.md)
- [Lead Management](./lead-management.md)
- [Innovative Features Proposal](../../changes/2025-11-10-innovative-features/innovative-features.md)

## Migration Path

既存のWebhook統合ユーザーは、Phase 2のBot統合への移行をシームレスに実施可能:

1. 既存のWebhook設定は維持
2. Bot統合を追加オプションとして提供
3. 両方を併用可能（Webhook + Bot）
4. ユーザーが好みに応じて選択

## Success Metrics

- **Phase 1**: 通知送信成功率 95%以上
- **Phase 2**: Bot経由の診断完了率 30%以上
- **Phase 3**: エンタープライズ顧客獲得率 +300%

## Documentation

- [Teams Webhook Setup Guide](../../docs/TEAMS_QUICKSTART.md)
- [Teams Integration Technical Guide](../../docs/TEAMS_LEAD_SERVICE_INTEGRATION.md)
- [Microsoft Teams App Development](https://docs.microsoft.com/en-us/microsoftteams/platform/)

---

**Status**: Phase 1完了、Phase 2開発準備中  
**Next Review**: 2週間後（Bot統合の進捗確認）
