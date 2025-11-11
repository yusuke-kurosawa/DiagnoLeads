# Phase 1 Implementation Plan (MVP+)

**Duration**: 3 months  
**Goal**: 革新的機能の中核を実装し、エンタープライズ市場での競争優位性を確立  
**Target**: 2025年Q2でのβ版リリース

---

## Overview

Phase 1では以下の3つの革新的機能を実装します：

1. **Microsoft Teams Native Integration** (最優先)
2. **Multi-Channel Distribution** (LINE, QRコード中心)
3. **AI-Powered A/B Testing** (基礎実装)

これらの機能により、従来のWeb埋め込みに加えて、エンタープライズで最も使われるTeamsでの診断配信、日本市場で強力なLINE対応、そして継続的なCV率改善を実現します。

---

## Phase 1 Milestones

### Milestone 1: Microsoft Teams統合基盤 (Week 1-3)

**目標**: Teams Bot、Adaptive Cards、基本通知機能

#### Week 1: Azure AD & Bot Framework Setup
- [ ] Azure AD App登録
  - Client ID/Secret取得
  - 必要な権限設定 (`Channel.ReadBasic.All`, `ChannelMessage.Send`, `Team.ReadBasic.All`)
  - Redirect URI設定
- [ ] Bot Framework App登録
  - Bot App ID/Password取得
  - Messaging endpoint設定
- [ ] 環境変数設定
  ```bash
  MICROSOFT_CLIENT_ID=
  MICROSOFT_CLIENT_SECRET=
  MICROSOFT_TENANT_ID=
  BOT_APP_ID=
  BOT_APP_PASSWORD=
  ```

#### Week 2: Microsoft Graph API統合
- [ ] バックエンド実装
  - `backend/app/integrations/microsoft/teams_client.py` 作成
  - `TeamsClient` クラス実装
  - Microsoft Graph SDK統合
  - 認証フロー実装
- [ ] データベーススキーマ
  - `teams_integrations` テーブル作成
  - マイグレーション実行
- [ ] API エンドポイント
  - `POST /api/v1/integrations/teams/install`
  - `GET /api/v1/integrations/teams`
  - `DELETE /api/v1/integrations/teams/{id}`
- [ ] ユニットテスト (カバレッジ 80%+)

#### Week 3: Adaptive Cards & 通知機能
- [ ] Adaptive Cardテンプレート実装
  - ホットリード通知カード
  - 診断共有カード
  - カスタマイズ可能なテンプレートシステム
- [ ] 通知ロジック実装
  - ホットリード検出時の自動通知
  - `POST /api/v1/integrations/teams/notify-lead`
  - メンション機能 (@営業担当)
- [ ] フロントエンド: Teams連携設定画面
  - `frontend/src/features/integrations/TeamsIntegration.tsx`
  - チャネル選択UI
  - テスト通知送信ボタン

**Success Criteria**:
- Azure ADアプリが正常に動作
- Teamsチャネルに通知が送信できる
- ホットリード取得後5秒以内に通知

---

### Milestone 2: Teams Bot対話機能 (Week 4-6)

**目標**: Teams Bot経由での診断実施

#### Week 4: Bot Framework統合
- [ ] Bot実装
  - `backend/app/integrations/microsoft/teams_bot.py`
  - `DiagnoLeadsTeamsBot` クラス
  - メッセージハンドラー
  - Webhook エンドポイント (`POST /api/v1/integrations/teams/bot/webhook`)
- [ ] セッション管理
  - `teams_bot_sessions` テーブル
  - セッション作成・更新ロジック
- [ ] 基本対話フロー
  - 「診断を開始」→ 診断リスト表示
  - 診断選択 → 質問送信

#### Week 5: 質問・回答フロー
- [ ] 質問送信ロジック
  - Quick Reply ボタン生成
  - 進捗状況表示 (3/8問完了)
- [ ] 回答処理
  - ユーザー回答の保存
  - 次の質問への遷移
  - 分岐ロジック対応
- [ ] 完了処理
  - スコア計算
  - 結果カード表示
  - リード情報収集

#### Week 6: テスト & 改善
- [ ] E2Eテスト
  - Bot対話フロー全体
  - エラーハンドリング
  - タイムアウト処理
- [ ] パフォーマンス最適化
  - Bot応答速度 < 3秒
- [ ] ドキュメント作成
  - Teams App設定マニュアル
  - 管理者向けガイド

**Success Criteria**:
- Teams Bot経由で診断完了可能
- Bot完了率 70%+
- 応答速度 < 3秒

---

### Milestone 3: LINE Official Account統合 (Week 7-9)

**目標**: LINE経由での診断配信とBot対話

#### Week 7: LINE Messaging API統合
- [ ] LINE Developers登録
  - Channel ID/Secret/Access Token取得
  - Webhook URL設定
- [ ] バックエンド実装
  - `backend/app/integrations/line/line_client.py`
  - `LineClient` クラス
  - LINE Messaging API SDK統合
- [ ] データベース
  - `channel_campaigns` テーブル (汎用)
  - `line_bot_sessions` テーブル
- [ ] API エンドポイント
  - `POST /api/v1/channels/line/install`
  - `POST /api/v1/channels/line/send`
  - `POST /api/v1/channels/line/webhook`

#### Week 8: Flex Message & Bot対話
- [ ] Flex Messageテンプレート
  - 診断カード (Hero Image, CTA)
  - 結果カード
- [ ] Bot対話ロジック
  - 質問送信 (Quick Reply)
  - 回答処理
  - 進捗表示
- [ ] リッチメニュー対応
  - リッチメニュー設定API
  - 診断リンク配置

#### Week 9: ブロードキャスト & 分析
- [ ] ブロードキャスト機能
  - 友達全員に配信
  - セグメント配信 (将来拡張)
- [ ] 分析ダッシュボード
  - LINE経由のコンバージョン率
  - 友達数推移
- [ ] フロントエンド
  - LINE連携設定画面
  - ブロードキャスト作成画面

**Success Criteria**:
- LINE Bot経由で診断完了可能
- Flex Messageが美しく表示される
- LINE経由CVR 35%+

---

### Milestone 4: QRコード & SMS配信 (Week 10-11)

**目標**: オフラインイベント対応

#### Week 10: QRコード生成
- [ ] QRコード生成サービス
  - `backend/app/services/qr_service.py`
  - `qrcode` ライブラリ統合
  - UTMパラメータ自動付与
- [ ] ポスター生成
  - PDFテンプレート (A4, A3)
  - カスタマイズ可能 (ロゴ、色)
- [ ] トラッキング
  - `qr_code_scans` テーブル
  - スキャン数リアルタイム表示
- [ ] API
  - `GET /api/v1/channels/qr-code/{assessment_id}`
  - `GET /api/v1/channels/qr-code/{assessment_id}/poster`

#### Week 11: SMS配信 (Twilio)
- [ ] Twilio統合
  - Account SID/Auth Token設定
  - `backend/app/integrations/sms/twilio_client.py`
- [ ] SMS送信機能
  - 単発送信
  - 一括送信 (CSV対応)
  - 短縮URL生成
- [ ] 配信ステータス追跡
  - Webhook受信
  - 配信成功/失敗の記録
- [ ] フロントエンド
  - SMSキャンペーン作成画面
  - 電話番号リストアップロード

**Success Criteria**:
- QRコード高解像度生成可能
- SMS配信率 98%+
- スキャン数トラッキング動作

---

### Milestone 5: AI A/Bテストエンジン (Week 12)

**目標**: 自動最適化の基盤

#### Week 12: A/Bテスト基本機能
- [ ] A/Bテストエンジン
  - `backend/app/services/optimization/ab_test_engine.py`
  - バリエーション割り当てロジック
  - 統計的有意差計算 (Z検定)
- [ ] データベース
  - `ab_tests` テーブル
  - `ab_test_variants` テーブル
- [ ] API
  - `POST /api/v1/optimization/ab-tests`
  - `GET /api/v1/optimization/ab-tests/{test_id}`
- [ ] フロントエンド
  - A/Bテスト作成画面 (シンプル)
  - 結果ダッシュボード (基本統計)
- [ ] トンプソンサンプリング (簡易版)
  - Beta分布サンプリング
  - 動的トラフィック配分

**Success Criteria**:
- 2つのバリエーションでA/Bテスト実行可能
- 統計的有意差が正しく計算される
- 結果がダッシュボードに表示される

---

## Technical Dependencies

### Backend
```bash
# 新規依存関係
pip install msal msgraph-sdk  # Microsoft Graph
pip install botbuilder-core botbuilder-schema  # Bot Framework
pip install line-bot-sdk  # LINE Messaging API
pip install twilio  # SMS
pip install qrcode pillow  # QRコード生成
pip install scipy  # 統計計算 (A/Bテスト)
```

### Frontend
```bash
npm install @microsoft/teams-js  # Teams SDK (将来)
npm install recharts  # A/Bテストグラフ
```

### Infrastructure
- **Azure AD**: App登録 (Teams統合)
- **LINE Developers**: Official Account作成
- **Twilio**: アカウント作成、電話番号取得

---

## Testing Strategy

### Unit Tests
- **Target Coverage**: 80%+
- **Priority Areas**:
  - Teams/LINE API統合
  - A/Bテストロジック
  - QRコード生成

### Integration Tests
- Teams: Adaptive Card送信、Bot Webhook
- LINE: Flex Message送信、Quick Reply
- SMS: Twilio配信ステータス確認

### E2E Tests
- Teams Bot対話フロー全体
- LINE Bot対話フロー全体
- A/Bテスト作成→実行→結果確認

---

## Risk Management

| Risk | Impact | Mitigation |
|------|--------|-----------|
| Microsoft Graph APIレート制限 | High | キャッシング、バックオフ戦略 |
| LINE APIの制約 | Medium | ドキュメント熟読、事前検証 |
| Twilioコスト | Medium | 初期は小規模テスト、段階的拡大 |
| A/Bテスト計算の複雑さ | Low | scipyライブラリ使用、専門家レビュー |

---

## Resource Allocation

### Backend開発 (60%)
- Teams統合: 3週間
- LINE統合: 2週間
- QR/SMS: 1週間
- A/Bテスト: 1週間

### Frontend開発 (30%)
- 設定画面: 2週間
- ダッシュボード: 1週間

### テスト & ドキュメント (10%)
- 継続的にテスト作成
- 最終週にドキュメント整備

---

## Success Metrics (Phase 1終了時)

### Technical KPIs
- [ ] Teams通知送信成功率 > 99%
- [ ] Bot応答速度 < 3秒
- [ ] LINE/Teams経由診断完了率 > 70%
- [ ] QRコード生成速度 < 1秒
- [ ] テストカバレッジ > 80%

### Business KPIs
- [ ] 3社以上のβテナントでTeams連携有効化
- [ ] LINE経由CVR 35%達成
- [ ] A/Bテストで平均+15%のCVR改善

---

## Post-Phase 1 Roadmap

### Phase 2 (Q3 2025)
- Microsoft Dynamics 365連携
- WhatsApp Business対応
- リアルタイムコラボレーション
- マーケットプレイス (α版)

### Phase 3 (Q4 2025)
- 音声/ビデオ診断
- ゲーミフィケーション
- 予測分析 (機械学習)
- White-Label対応

---

## Next Immediate Actions

1. **Azure AD App登録** (所要時間: 30分)
2. **LINE Developers登録** (所要時間: 30分)
3. **Twilio試験アカウント作成** (所要時間: 15分)
4. **GitHub Issues作成** (各機能のタスク分解)
5. **技術スパイク**: Teams Bot最小プロトタイプ (2日)

---

## References

- [Microsoft Teams App開発ガイド](https://learn.microsoft.com/microsoftteams/platform/)
- [LINE Messaging API Reference](https://developers.line.biz/ja/reference/messaging-api/)
- [Twilio SMS API Docs](https://www.twilio.com/docs/sms)
- [A/B Testing Best Practices](https://www.optimizely.com/optimization-glossary/ab-testing/)

---

**Document Version**: 1.0  
**Last Updated**: 2025-11-10  
**Status**: Ready for Execution 🚀
