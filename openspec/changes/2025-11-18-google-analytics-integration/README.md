# Google Analytics 4 Integration Proposal

## 📊 概要

DiagnoLeadsプラットフォームにGoogle Analytics 4（GA4）統合を追加し、診断ファネルの完全な可視化、ユーザー行動分析、マーケティングROI測定を実現します。

## 🎯 主要機能

### 1. マルチテナント対応GA4統合
- 各テナントが独自のGA4プロパティIDを設定可能
- テナント管理画面でGA4設定を管理
- 接続テスト機能で即座に確認

### 2. フロントエンド（React）トラッキング
- 管理画面でのページビュー自動追跡
- カスタムイベント送信（診断作成、リードステータス変更など）
- react-ga4ライブラリを使用した実装

### 3. 埋め込みウィジェットトラッキング
- 外部サイトに埋め込まれた診断ウィジェットのユーザー行動追跡
- 診断フローの各ステップをイベント化
  - `assessment_view`: 診断ページ表示
  - `assessment_started`: 診断開始
  - `question_answered`: 質問回答
  - `assessment_completed`: 診断完了
  - `lead_generated`: リード獲得
  - `hot_lead_generated`: ホットリード獲得
- クロスドメイントラッキング対応

### 4. サーバーサイドトラッキング（Measurement Protocol）
- バックエンドから重要ビジネスイベントを送信
- クライアントサイドブロッカー対策
- より正確なコンバージョン計測

### 5. プライバシー準拠
- GDPR/CCPA準拠のCookie同意バナー
- PII（個人識別情報）の送信禁止
- オプトアウト機能

## 📁 ドキュメント構成

```
openspec/changes/2025-11-18-google-analytics-integration/
├── README.md                           # このファイル
├── google-analytics-integration.md     # 詳細仕様（OpenSpec）
└── IMPLEMENTATION_GUIDE.md             # 実装ガイド
```

## 🚀 ビジネス価値

### 診断ファネルの可視化
```
診断表示 → 診断開始 → 質問回答 → 完了 → リード化
  100%      80%       60%      40%     20%
```
各ステップの離脱率を把握し、診断を改善

### ROI測定
- マーケティングチャネル別の診断完了率
- リード獲得コスト（CPA）の正確な計測
- ホットリード獲得を即座にコンバージョン計測

### 顧客行動理解
- 質問ごとの平均回答時間
- 離脱ポイントの特定
- 再訪問率、リピート診断率の分析

### A/Bテストの基盤
- GA4イベントデータを活用した診断最適化
- 質問の順番、文言、選択肢の改善

## 🎨 アーキテクチャ

```
┌─────────────────────────────────────────────────────────┐
│                 DiagnoLeads Platform                    │
│                                                         │
│  ┌──────────┐   ┌──────────┐   ┌──────────┐          │
│  │  React   │   │  Embed   │   │ Backend  │          │
│  │  Admin   │   │  Widget  │   │ (FastAPI)│          │
│  │ (gtag)   │   │ (gtag)   │   │  (MP)    │          │
│  └────┬─────┘   └────┬─────┘   └────┬─────┘          │
│       │              │              │                  │
└───────┼──────────────┼──────────────┼─────────────────┘
        │              │              │
        └──────────────┴──────────────┘
                       │
                       ▼
            ┌──────────────────────┐
            │  Google Analytics 4  │
            │  (Per Tenant)        │
            │  - Events            │
            │  - Funnels           │
            │  - Conversions       │
            └──────────────────────┘
```

## 📊 主要イベント一覧

### 診断関連イベント
| Event Name | 説明 | パラメータ |
|-----------|------|----------|
| `assessment_view` | 診断ページ表示 | assessment_id, title, page_location |
| `assessment_started` | 診断開始 | assessment_id, total_questions |
| `question_answered` | 質問回答 | assessment_id, question_number, time_spent |
| `assessment_completed` | 診断完了 | assessment_id, total_time, questions_answered |
| `assessment_abandoned` | 診断途中離脱 | assessment_id, last_question, completion_% |

### リード関連イベント
| Event Name | 説明 | パラメータ |
|-----------|------|----------|
| `lead_generated` | リード獲得 | assessment_id, lead_score, lead_tier |
| `hot_lead_generated` | ホットリード獲得 | assessment_id, lead_score, value (¥1000) |
| `lead_status_changed` | ステータス変更 | lead_id, old_status, new_status |

### 管理画面イベント
| Event Name | 説明 | パラメータ |
|-----------|------|----------|
| `assessment_created` | 診断作成 | assessment_id, creation_method (ai/manual) |
| `assessment_published` | 診断公開 | assessment_id |
| `dashboard_viewed` | ダッシュボード表示 | view_type |

## 🛠️ 実装計画（6週間）

### Phase 1: バックエンド基盤（Week 1-2）
- [ ] データベーススキーマ作成
- [ ] CRUD API実装
- [ ] Measurement Protocolクライアント実装
- [ ] 接続テストAPI

### Phase 2: フロントエンド（Week 2-3）
- [ ] GA4設定画面実装
- [ ] react-ga4統合
- [ ] カスタムイベント送信
- [ ] Cookie同意バナー

### Phase 3: 埋め込みウィジェット（Week 3-4）
- [ ] GA4設定取得API統合
- [ ] gtag.js動的ロード
- [ ] 診断フローイベント送信
- [ ] クロスドメイントラッキング

### Phase 4: サーバーサイドイベント（Week 4-5）
- [ ] リード生成イベント送信
- [ ] ホットリード検出イベント
- [ ] 非同期ジョブ統合（Trigger.dev）

### Phase 5: テスト＆ドキュメント（Week 5-6）
- [ ] E2Eテスト
- [ ] ユーザーガイド作成
- [ ] セキュリティ監査

## 🔐 セキュリティ＆プライバシー

### マルチテナント分離
- すべてのGA4設定は `tenant_id` でフィルタリング
- Row-Level Security（RLS）でデータ漏洩防止
- API Secretは暗号化保存

### プライバシー準拠
- **PII送信禁止**: メール、電話、氏名を絶対に送信しない
- **Cookie同意**: GDPR/CCPA準拠のバナー実装
- **オプトアウト**: ユーザーがトラッキングを拒否可能
- **IP匿名化**: GA4デフォルトで有効

## 📈 成功指標

### 実装成功の指標
- 95%以上のGA4イベント送信成功率
- イベントがGA4リアルタイムレポートに表示
- 診断完了→リード獲得のファネルレポート作成可能
- 埋め込みウィジェットのバンドルサイズ増加 < 5KB

### ビジネスインパクト
- テナントの80%がGA4統合を有効化（6ヶ月以内）
- 診断ファネルの離脱率が可視化され、改善施策実行
- マーケティングROI（CPA、CVR）の正確な計測

## 💰 コスト

- **Google Analytics 4**: 無料
- **Measurement Protocol API**: 無料
- **開発コスト**: 6週間（1エンジニア）
- **運用コスト**: 無料（既存インフラで動作）

## 🔄 他の統合との比較

| 機能 | GA4統合 | Microsoft Teams | Salesforce/HubSpot |
|-----|---------|----------------|-------------------|
| トラッキング | ✅ ユーザー行動 | ❌ | ❌ |
| ファネル分析 | ✅ | ❌ | ⚠️ 限定的 |
| ROI測定 | ✅ | ❌ | ⚠️ CRMベース |
| リアルタイム通知 | ⚠️ 遅延あり | ✅ | ✅ |
| データエクスポート | ✅ BigQuery可 | ❌ | ✅ |
| コスト | 無料 | 無料 | 有料プラン必要 |

## 🚦 Next Steps

1. **レビュー**: このOpenSpec提案をチームでレビュー
2. **承認**: セキュリティ監査とビジネス承認
3. **実装**: Phase 1からスタート
4. **テスト**: 段階的にロールアウト
5. **ドキュメント**: ユーザーガイド作成

## 📚 参考資料

- [詳細仕様（OpenSpec）](./google-analytics-integration.md)
- [実装ガイド](./IMPLEMENTATION_GUIDE.md)
- [GA4 Measurement Protocol API](https://developers.google.com/analytics/devguides/collection/protocol/ga4)
- [react-ga4 Documentation](https://github.com/codler/react-ga4)

## ✅ Checklist for Approval

- [ ] ビジネス価値が明確か？
- [ ] セキュリティリスクは適切に対処されているか？
- [ ] プライバシー規制（GDPR/CCPA）に準拠しているか？
- [ ] 実装計画は現実的か？
- [ ] コストは許容範囲内か？
- [ ] 既存システムとの統合は問題ないか？

---

**Status**: 📝 Proposed (Ready for Review)
**Created**: 2025-11-18
**Author**: Claude Code
**Priority**: High
**Estimated Effort**: 6 weeks
