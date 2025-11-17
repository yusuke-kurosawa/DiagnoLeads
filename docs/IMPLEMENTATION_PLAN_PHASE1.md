# DiagnoLeads - Phase 1 実装計画

**期間**: Week 1-12 (3ヶ月)
**目標**: Microsoft Teams統合、マルチチャネル配信、AI A/Bテストエンジンの基礎実装
**優先度**: 高

---

## 📋 Phase 1 概要

Phase 1では、DiagnoLeadsを他のB2B診断プラットフォームと差別化する3つの主要機能群を実装します：

1. **Microsoft Teams統合** - 業界初のTeams Bot対話型診断
2. **マルチチャネル配信** - LINE、SMS、QRコード対応
3. **AI A/Bテスト自動化** - トンプソンサンプリングによる自動最適化

---

## 🎯 Milestone 1: Teams統合基盤（Week 1-3）

### 目標
Microsoft Teams Appとしての基礎機能を実装し、Adaptive Cards形式でのリード通知を実現

### タスク

#### Week 1: Azure AD & Teams App登録
- [ ] Azure ADにアプリケーション登録
- [ ] Teams Bot作成（Bot Framework SDK）
- [ ] OAuth 2.0認証フロー実装
- [ ] テナント管理画面にTeams連携設定追加

**成果物**:
- Azure Bot Service登録完了
- OAuth認証フロー動作確認
- 管理画面で Teams連携ON/OFF可能

**関連ドキュメント**: [SETUP_GUIDE_TEAMS.md](./SETUP_GUIDE_TEAMS.md)

#### Week 2: Adaptive Cards実装
- [ ] リード情報をAdaptive Cards形式で整形
- [ ] Teams Webhook統合
- [ ] 通知送信API実装 (`POST /api/v1/integrations/teams/notify-lead`)
- [ ] エラーハンドリング（レート制限、リトライロジック）

**成果物**:
- ホットリード獲得時に Teams チャネルへ自動通知
- Adaptive Cards に診断結果サマリー表示
- 営業担当者への自動メンション

#### Week 3: Teams App Manifest & テスト
- [ ] Teams App Manifestファイル作成
- [ ] サイドローディングでテスト
- [ ] チャネル一覧取得API (`GET /api/v1/integrations/teams/channels`)
- [ ] 統合テスト、ドキュメント作成

**成果物**:
- Teams App としてインストール可能
- 実際のTeamsワークスペースでの動作確認完了
- セットアップガイド完成

---

## 🎯 Milestone 2: Teams Bot対話機能（Week 4-6）

### 目標
Teams Botとの会話形式で診断を実施可能にする

### タスク

#### Week 4: Bot Framework統合
- [ ] Bot Framework SDK（Python/Node.js）セットアップ
- [ ] 会話フロー設計（ダイアログマネージャー）
- [ ] Bot Message Handler実装
- [ ] ステート管理（会話履歴、進行状況）

#### Week 5: 診断配信機能
- [ ] 診断リストをBot経由で表示
- [ ] 診断開始コマンド実装 (例: `@DiagnoBot start assessment-123`)
- [ ] 質問の逐次送信（1問ずつ表示）
- [ ] ユーザー回答の記録

**成果物**:
- Teams Botで診断開始可能
- チャット内で質問に回答可能
- 回答データの保存

#### Week 6: 診断結果表示 & 改善
- [ ] 診断完了時の結果表示（Adaptive Cards）
- [ ] スコアリング結果の可視化
- [ ] 会議内での診断共有機能（プロトタイプ）
- [ ] パフォーマンス最適化

**成果物**:
- Teams内で診断完了まで可能
- 美しい結果表示カード
- 会議内診断のデモ動作

---

## 🎯 Milestone 3: LINE統合（Week 7-9）

### 目標
LINE Official Accountとの統合により、日本市場での診断配信を実現

### タスク

#### Week 7: LINE Messaging API統合
- [ ] LINE Developers アカウント作成
- [ ] Webhook設定
- [ ] メッセージ送受信API実装
- [ ] LINE Bot基本機能（挨拶、ヘルプ）

#### Week 8: LINE診断配信
- [ ] Flex Message形式での質問表示
- [ ] Quick Reply による回答選択
- [ ] 診断進行状況の管理
- [ ] リッチメニュー設定（診断一覧表示）

**成果物**:
- LINE Botで診断開始・回答可能
- Flex Message による美しい質問表示
- リッチメニューからの診断起動

#### Week 9: LINE友達管理 & セグメント配信
- [ ] LINE友達の自動登録
- [ ] 診断結果に基づくセグメント作成
- [ ] セグメント配信機能（Messaging APIプッシュ通知）
- [ ] テスト & ドキュメント

**API Endpoints**:
```
POST /api/v1/channels/line/webhook
POST /api/v1/channels/line/send
POST /api/v1/channels/line/segments
GET  /api/v1/channels/line/friends
```

---

## 🎯 Milestone 4: QRコード & SMS配信（Week 10-11）

### 目標
オフラインイベント向けQRコード、SMS経由の診断配信を実装

### タスク

#### Week 10: QRコード生成 & トラッキング
- [ ] QRコード生成ライブラリ統合（qrcode.js / Python qrcode）
- [ ] 診断ごとの専用QRコード生成API
- [ ] QRコードスキャン数トラッキング
- [ ] UTMパラメータ自動付与
- [ ] ダウンロード機能（PNG、SVG、PDF）

**API Endpoints**:
```
GET  /api/v1/channels/qr-code/{assessment_id}
GET  /api/v1/channels/qr-code/{assessment_id}/analytics
POST /api/v1/channels/qr-code/{assessment_id}/download
```

#### Week 11: Twilio SMS統合
- [ ] Twilio アカウント設定
- [ ] SMS送信API実装
- [ ] 短縮URL生成（bit.ly APIまたは自社実装）
- [ ] SMS送信履歴、開封率トラッキング
- [ ] テスト & ドキュメント

**API Endpoints**:
```
POST /api/v1/channels/sms/send
GET  /api/v1/channels/sms/history
GET  /api/v1/channels/sms/analytics
```

**成果物**:
- イベント用QRコードポスター印刷可能
- SMS経由で診断リンク配信可能
- トラッキングダッシュボード

---

## 🎯 Milestone 5: AI A/Bテストエンジン（Week 12）

### 目標
トンプソンサンプリングを使った自動A/Bテスト機能のプロトタイプ

### タスク

#### Week 12: A/Bテスト基盤
- [ ] バリエーション管理データモデル設計
- [ ] トンプソンサンプリングアルゴリズム実装
- [ ] バリエーション配信ロジック（確率的振り分け）
- [ ] コンバージョン率計測
- [ ] 自動最適化ロジック（完了率が高い方に自動シフト）

**データモデル**:
```python
class ABTest(Base):
    id: UUID
    assessment_id: UUID
    variants: List[ABTestVariant]
    status: Enum['running', 'paused', 'completed']
    algorithm: str = 'thompson_sampling'

class ABTestVariant(Base):
    id: UUID
    ab_test_id: UUID
    variant_name: str  # 'A', 'B', 'C'
    impressions: int
    completions: int
    conversion_rate: float
    traffic_allocation: float  # 0.0 - 1.0
```

**成果物**:
- A/Bテスト作成・管理画面
- 自動トラフィック振り分け
- リアルタイム結果ダッシュボード

**API Endpoints**:
```
POST /api/v1/optimization/ab-test/create
GET  /api/v1/optimization/ab-test/{test_id}/results
POST /api/v1/optimization/ab-test/{test_id}/pause
POST /api/v1/optimization/ab-test/{test_id}/resume
```

---

## 📊 Phase 1 完了基準

以下のすべてが満たされた場合、Phase 1完了とみなします：

### 機能要件
- ✅ Teams Botで診断を配信・実施・結果表示可能
- ✅ ホットリード獲得時にTeamsチャネルへ自動通知
- ✅ LINE Botで診断配信・回答可能
- ✅ QRコード生成・ダウンロード・トラッキング可能
- ✅ SMS経由で診断リンク配信可能
- ✅ A/Bテスト作成・自動最適化が動作

### 品質要件
- ✅ 各機能の単体テストカバレッジ70%以上
- ✅ 統合テスト実施済み
- ✅ セットアップガイド、API仕様書完成
- ✅ パフォーマンステスト実施（1000ユーザー同時アクセス）

### ドキュメント
- ✅ [SETUP_GUIDE_TEAMS.md](./SETUP_GUIDE_TEAMS.md)
- ✅ [SETUP_GUIDE_LINE.md](./SETUP_GUIDE_LINE.md)
- ✅ API仕様（OpenAPI）更新
- ✅ ユーザーマニュアル

---

## 🚀 Phase 2 へのバトンタッチ

Phase 1完了後、以下の機能を Phase 2 で実装予定：

- **リアルタイムコラボレーション**: Google Docs風の共同編集
- **診断マーケットプレイス**: テンプレート売買
- **Microsoft Dynamics 365連携**: 双方向同期
- **WhatsApp Business統合**: グローバル展開
- **AIコピーライティング**: 自動文言改善

詳細: [革新的機能提案](../openspec/changes/2025-11-10-innovative-features/innovative-features.md)

---

## 📞 サポート

Phase 1実装中の質問・課題は以下で管理：
- **GitHub Issues**: [Phase 1 Label](https://github.com/yusuke-kurosawa/DiagnoLeads/issues?q=is%3Aissue+label%3Aphase-1)
- **GitHub Milestones**: [Milestones一覧](https://github.com/yusuke-kurosawa/DiagnoLeads/milestones)

---

**Built with ❤️ using OpenSpec Spec-Driven Development**
