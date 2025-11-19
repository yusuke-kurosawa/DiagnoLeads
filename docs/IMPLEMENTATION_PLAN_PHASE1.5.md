# DiagnoLeads Phase 1.5 Implementation Plan

**フェーズ**: 1.5 (Revenue Foundation & Enterprise Differentiation)
**期間**: 14週間（約3.5ヶ月）
**開始予定**: 2025年12月
**目標**: 収益化基盤の確立とエンタープライズ市場攻略

---

## 📋 Executive Summary

Phase 1.5では、DiagnoLeadsの収益化を加速し、エンタープライズ顧客を獲得するための2つの主要機能を実装します：

1. **サブスクリプション・請求管理システム** (8-10週間)
   - Stripe統合による自動課金
   - 利用量ベース従量課金
   - プラン管理・請求書発行

2. **ホワイトラベル・カスタムブランディング** (6-8週間)
   - カスタムドメイン対応
   - ブランディングカスタマイズ
   - メールテンプレート編集

**ビジネスインパクト**:
- 収益自動化（運用コスト95%削減）
- エンタープライズ獲得率 +60%
- 平均顧客単価 +120%
- 解約率 -40%

---

## 🎯 Phase 1.5 の目標

### ビジネス目標
- **ARR目標**: ¥50,000,000（Phase 1.5完了時点）
- **有料テナント数**: 30社（Starter 20社、Professional 8社、Business 2社）
- **チャーン率**: 月次3%以下
- **LTV/CAC比**: 3.0以上

### 技術目標
- **Stripe統合**: 決済成功率 98%以上
- **カスタムドメイン**: SSL証明書発行成功率 99%
- **システム稼働率**: 99.9%
- **APIレスポンス**: 決済API <500ms, ブランディングAPI <200ms

---

## 📅 全体スケジュール（14週間）

### Week 1-10: サブスクリプション・請求管理
### Week 7-14: ホワイトラベル・ブランディング
※ 並行開発期間: Week 7-10（両チームで協力）

```
Week  1  2  3  4  5  6  7  8  9 10 11 12 13 14
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Subscription   ████████████████████████
Branding                 ████████████████
Testing                          ██████
Launch Prep                           ███
```

---

## 🚀 Milestone 1: サブスクリプション管理基盤（Week 1-4）

### 目標
Stripe統合の基盤を構築し、基本的なサブスクリプション作成・管理機能を実装

### タスク

#### Week 1: Stripe統合セットアップ
- [ ] **Stripe Accountセットアップ**
  - 本番環境・テスト環境の作成
  - APIキー取得・管理
  - Webhook URLの設定
- [ ] **Stripeライブラリ統合**
  - Backend: `stripe-python` インストール
  - Frontend: `@stripe/stripe-js`, `@stripe/react-stripe-js`
- [ ] **環境変数設定**
  ```bash
  STRIPE_SECRET_KEY=sk_test_xxx
  STRIPE_PUBLISHABLE_KEY=pk_test_xxx
  STRIPE_WEBHOOK_SECRET=whsec_xxx
  ```
- [ ] **データベーススキーマ作成**
  - `subscriptions` テーブル
  - `invoices` テーブル
  - `usage_records` テーブル
  - マイグレーション実行

**成果物**:
- Stripe統合基盤コード
- DBマイグレーションファイル
- 環境変数ドキュメント

#### Week 2: Stripe Customer & Subscription API
- [ ] **StripeServiceクラス実装**
  - `create_customer()` - Stripeカスタマー作成
  - `create_subscription()` - サブスクリプション作成
  - `get_subscription()` - サブスクリプション取得
- [ ] **APIエンドポイント作成**
  - `POST /api/v1/billing/subscriptions` - サブスクリプション作成
  - `GET /api/v1/billing/subscriptions/current` - 現在のプラン取得
- [ ] **テナントモデル拡張**
  - `stripe_customer_id` カラム追加
  - `current_plan` カラム追加
- [ ] **単体テスト作成**
  - StripeService のモックテスト
  - API エンドポイントテスト

**成果物**:
- `backend/app/services/billing/stripe_service.py`
- `backend/app/api/v1/billing.py`
- テストコード 15件

#### Week 3: プラン定義 & Pricing Page
- [ ] **Stripe Productsセットアップ**
  - Free, Starter, Professional, Business, Enterprise プラン作成
  - Price ID取得・管理
- [ ] **プラン設定ファイル作成**
  ```python
  PLANS = {
      "free": {"assessments": 1, "leads": 50},
      "starter": {"assessments": 5, "leads": 500},
      # ...
  }
  ```
- [ ] **Pricing Page実装**
  - プラン比較表UI
  - 「14日間無料トライアル」訴求
  - Stripe Checkout統合
- [ ] **チェックアウトフロー**
  - Stripe Checkout Session作成
  - リダイレクト処理
  - Success/Cancel ページ

**成果物**:
- `frontend/src/features/billing/PricingPage.tsx`
- `frontend/src/features/billing/CheckoutSuccess.tsx`
- Stripeダッシュボード設定ドキュメント

#### Week 4: プラン変更・キャンセル
- [ ] **プラン変更API実装**
  - `PUT /api/v1/billing/subscriptions/plan`
  - 日割り計算（プロレーション）
  - アップグレード・ダウングレード処理
- [ ] **キャンセルAPI実装**
  - `DELETE /api/v1/billing/subscriptions`
  - 即時キャンセル vs 期間終了時キャンセル
- [ ] **プラン管理UI**
  - 現在のプラン表示
  - アップグレード・ダウングレードボタン
  - キャンセルダイアログ
- [ ] **統合テスト**
  - プラン変更フロー
  - キャンセルフロー

**成果物**:
- プラン変更・キャンセル機能
- `frontend/src/features/billing/PlanManagement.tsx`
- 統合テスト 8件

**Milestone 1 完了条件**:
- ✅ ユーザーがプランを選択・支払い可能
- ✅ プラン変更・キャンセルが正常動作
- ✅ Stripe Webhookが受信可能（基本）

---

## 💰 Milestone 2: 利用量管理・従量課金（Week 5-7）

### 目標
リソース使用量をトラッキングし、クォータ管理・従量課金を実装

### タスク

#### Week 5: 使用量トラッキング基盤
- [ ] **UsageTrackerサービス実装**
  - `check_quota()` - クォータチェック
  - `increment_usage()` - 使用量インクリメント
  - `get_current_usage()` - 現在の使用量取得
- [ ] **リソースフック実装**
  - 診断作成時に `increment_usage("assessments")`
  - リード獲得時に `increment_usage("leads")`
  - AI生成時に `increment_usage("ai_generations")`
- [ ] **使用量記録テーブル**
  - `usage_records` への記録
  - 日次集計クエリ最適化
- [ ] **APIエンドポイント**
  - `GET /api/v1/billing/usage` - 現在の利用状況

**成果物**:
- `backend/app/services/billing/usage_tracker.py`
- 使用量トラッキングフック
- 使用量API

#### Week 6: クォータ管理・アラート
- [ ] **クォータ超過ハンドリング**
  - 超過時の制限モード実装
  - または従量課金への自動移行
- [ ] **アラート通知**
  - 80%到達時にメール通知
  - 100%到達時に緊急通知
  - ダッシュボードバナー表示
- [ ] **Usage Dashboardアップデート**
  - 利用状況の可視化（プログレスバー）
  - 「残りXX日で上限到達」予測表示
  - アップグレード誘導
- [ ] **メール通知テンプレート**
  - クォータ警告メール
  - 超過通知メール

**成果物**:
- クォータ管理ロジック
- `frontend/src/features/billing/UsageDashboard.tsx`
- メール通知テンプレート 3件

#### Week 7: 従量課金実装
- [ ] **Stripe Usage-Based Billing設定**
  - Metered Price作成（従量課金用）
  - 使用量レポートAPI統合
- [ ] **オーバーエイジ課金**
  - 超過分の自動記録
  - Stripeへの使用量報告
- [ ] **従量課金レポート**
  - 月次使用量サマリー
  - 請求額プレビュー
- [ ] **テスト**
  - クォータ超過シナリオ
  - 従量課金計算の正確性

**成果物**:
- 従量課金システム
- 使用量レポート機能
- E2Eテスト 5件

**Milestone 2 完了条件**:
- ✅ リソース使用量が正確にトラッキングされる
- ✅ クォータ超過時に適切に処理される
- ✅ 従量課金が正確に計算・請求される

---

## 📄 Milestone 3: 請求書・決済管理（Week 8-10）

### 目標
請求書の自動生成、決済失敗ハンドリング、支払い方法管理を実装

### タスク

#### Week 8: 請求書生成・管理
- [ ] **Webhook Handler実装**
  - `invoice.created` - 請求書作成時
  - `invoice.payment_succeeded` - 決済成功時
  - `invoice.payment_failed` - 決済失敗時
  - `customer.subscription.updated` - サブスクリプション更新時
- [ ] **請求書データ同期**
  - Stripeから請求書データ取得
  - DBに保存（`invoices` テーブル）
- [ ] **請求書PDF生成**
  - PDFライブラリ（WeasyPrint or ReportLab）
  - 適格請求書番号（インボイス制度対応）
  - 会社情報・明細・税金表示
- [ ] **APIエンドポイント**
  - `GET /api/v1/billing/invoices` - 請求書一覧
  - `GET /api/v1/billing/invoices/{id}/pdf` - PDF取得

**成果物**:
- Webhook Handler完成
- 請求書PDF生成機能
- 請求書管理API

#### Week 9: 決済失敗ハンドリング
- [ ] **ダンニング（督促）システム**
  - 決済失敗時のリトライロジック（3日、7日、14日後）
  - リマインダーメール自動送信
- [ ] **制限モード実装**
  - 14日後も未払いの場合、制限モード移行
  - 新規診断作成・リード獲得を停止
  - 既存データは閲覧可能
- [ ] **カード更新フロー**
  - 支払い方法更新UI
  - 更新後の自動再試行
- [ ] **アカウント停止処理**
  - 30日後も未払いの場合、一時停止
  - 復旧プロセス

**成果物**:
- ダンニングシステム
- 制限モード実装
- 決済失敗通知メール 3件

#### Week 10: 支払い方法管理
- [ ] **支払い方法管理UI**
  - カード一覧表示
  - デフォルトカード設定
  - カード追加・削除
- [ ] **Stripe Setup Intent統合**
  - カード情報の安全な収集
- [ ] **APIエンドポイント**
  - `GET /api/v1/billing/payment-methods`
  - `POST /api/v1/billing/payment-methods`
  - `DELETE /api/v1/billing/payment-methods/{id}`
- [ ] **統合テスト**
  - 請求書生成フロー
  - 決済失敗 → リトライ → 成功
  - カード更新フロー

**成果物**:
- 支払い方法管理機能
- `frontend/src/features/billing/PaymentMethods.tsx`
- 統合テスト 10件

**Milestone 3 完了条件**:
- ✅ 請求書が自動生成・PDF化される
- ✅ 決済失敗時に適切にリトライ・通知される
- ✅ ユーザーが支払い方法を管理できる

---

## 🎨 Milestone 4: ホワイトラベル基盤（Week 7-10）

### 目標
カスタムドメイン、ブランディング設定の基盤を構築

### タスク

#### Week 7: カスタムドメイン基盤
- [ ] **DomainServiceクラス実装**
  - `add_custom_domain()` - ドメイン追加
  - `verify_domain()` - DNS検証
  - `issue_ssl_certificate()` - SSL証明書発行
- [ ] **DNS検証ロジック**
  - CNAMEレコードチェック
  - TXTレコード検証
  - DNS Resolverライブラリ統合
- [ ] **データベーススキーマ**
  - `tenant_domains` テーブル作成
  - `tenant_branding` テーブル作成
- [ ] **APIエンドポイント**
  - `POST /api/v1/branding/domains`
  - `POST /api/v1/branding/domains/{id}/verify`

**成果物**:
- `backend/app/services/branding/domain_service.py`
- ドメイン管理API
- DBマイグレーション

#### Week 8: SSL証明書自動発行
- [ ] **Let's Encrypt統合**
  - Certbot ライブラリ統合
  - 証明書自動発行ワークフロー
  - 証明書更新ジョブ（90日ごと）
- [ ] **CDN/ロードバランサー統合**
  - 証明書のアップロード
  - ドメインルーティング設定
- [ ] **SSL証明書管理**
  - 有効期限監視
  - 更新アラート

**成果物**:
- SSL証明書自動発行システム
- 証明書更新バッチジョブ

#### Week 9: ドメイン設定UI
- [ ] **Domain Settings Page実装**
  - ドメイン追加フォーム
  - DNS設定手順表示
  - 検証ステータス表示
- [ ] **ドメイン一覧・管理**
  - 登録済みドメイン一覧
  - ドメイン削除機能
- [ ] **ユーザーガイド**
  - DNS設定手順書
  - トラブルシューティング

**成果物**:
- `frontend/src/features/branding/DomainSettings.tsx`
- ユーザーガイドドキュメント

#### Week 10: 並行開発（サブスクリプションチームと協力）
- [ ] **統合テスト準備**
- [ ] **ドキュメント作成**
- [ ] **バグ修正**

**Milestone 4 完了条件**:
- ✅ カスタムドメインを追加・検証できる
- ✅ SSL証明書が自動発行される
- ✅ カスタムドメインでアクセス可能

---

## 🖌️ Milestone 5: ブランディングカスタマイズ（Week 11-12）

### 目標
ロゴ、カラースキーム、フォントのカスタマイズ機能を実装

### タスク

#### Week 11: ロゴ・カラー設定
- [ ] **BrandingServiceクラス実装**
  - `upload_logo()` - ロゴアップロード
  - `update_color_scheme()` - カラー更新
  - `generate_custom_css()` - CSS生成
- [ ] **画像アップロード処理**
  - ファイルバリデーション（サイズ、形式）
  - CDNアップロード
  - サムネイル生成
- [ ] **カラースキーム管理**
  - プライマリ・セカンダリ・アクセントカラー
  - コントラスト比チェック（WCAG準拠）
  - 補色自動生成
- [ ] **Logo Uploader UI**
  - ドラッグ&ドロップアップロード
  - プレビュー機能
  - 推奨サイズガイド

**成果物**:
- `backend/app/services/branding/branding_service.py`
- `frontend/src/features/branding/LogoUploader.tsx`
- `frontend/src/features/branding/ColorSchemeEditor.tsx`

#### Week 12: カスタムフォント・プレビュー
- [ ] **フォント設定**
  - Google Fonts統合
  - カスタムフォントURL対応
- [ ] **リアルタイムプレビュー**
  - iframeプレビュー
  - ブランディング設定の即時反映
- [ ] **CSS生成・配信**
  - カスタムCSSファイル生成
  - CDNへのアップロード
  - キャッシュ管理
- [ ] **APIエンドポイント**
  - `GET /api/v1/branding` - ブランディング設定取得
  - `PUT /api/v1/branding` - 設定更新
  - `POST /api/v1/branding/logo`

**成果物**:
- フォント設定機能
- リアルタイムプレビュー
- ブランディングAPI完成

**Milestone 5 完了条件**:
- ✅ ロゴをアップロードできる
- ✅ カラースキームをカスタマイズできる
- ✅ 変更がリアルタイムでプレビューされる

---

## 📧 Milestone 6: メールテンプレート・高度な設定（Week 13-14）

### 目標
メール通知のカスタマイズ、ウィジェットブランディング、高度な設定を実装

### タスク

#### Week 13: メールテンプレートエディター
- [ ] **EmailTemplateServiceクラス実装**
  - `customize_template()` - テンプレート編集
  - `render_email()` - メールレンダリング
  - `verify_sender_email()` - 送信元認証
- [ ] **テンプレートエディターUI**
  - WYSIWYGエディター（TinyMCE or Quill）
  - 変数挿入機能
  - プレビュー（デスクトップ・モバイル）
  - テストメール送信
- [ ] **送信元メール認証**
  - 認証メール送信
  - 検証フロー
  - SPF/DKIM設定ガイド
- [ ] **デフォルトテンプレート作成**
  - リード獲得通知
  - ウェルカムメール
  - 請求書送付メール

**成果物**:
- `backend/app/services/branding/email_template_service.py`
- `frontend/src/features/branding/EmailTemplateEditor.tsx`
- デフォルトテンプレート 5件

#### Week 14: ウィジェット・最終調整
- [ ] **ウィジェットブランディング**
  - ブランドカラー自動適用
  - ロゴ表示・非表示設定
  - 「Powered by」ラベル制御（Enterprise）
- [ ] **カスタムCSS/JS（上級者向け）**
  - CSSエディター実装
  - セーフモード機能
  - バージョン履歴
- [ ] **ドキュメント整備**
  - ブランディング設定ガイド
  - カスタムドメイン設定手順
  - トラブルシューティング
- [ ] **最終テスト**
  - E2Eテスト実行
  - パフォーマンステスト
  - セキュリティ監査

**成果物**:
- ウィジェットブランディング機能
- カスタムCSS/JSエディター
- 完全なドキュメント

**Milestone 6 完了条件**:
- ✅ メールテンプレートをカスタマイズできる
- ✅ ウィジェットがブランディングに従う
- ✅ すべての機能が統合され正常動作

---

## 🧪 Testing & QA Plan

### 単体テスト（継続的）
- **カバレッジ目標**: 80%以上
- **テストフレームワーク**: pytest (Backend), Vitest (Frontend)
- **テスト対象**:
  - StripeService: 決済ロジック
  - UsageTracker: クォータ計算
  - DomainService: DNS検証
  - BrandingService: CSS生成

### 統合テスト（Week 10, 14）
- Stripe API統合テスト（テストモード使用）
- Webhook受信・処理テスト
- DNS検証フロー
- メール送信テスト

### E2Eテスト（Week 14）
- **プラン登録フロー**: Free → Starter (トライアル) → Professional (アップグレード)
- **決済失敗フロー**: 決済失敗 → リトライ → カード更新 → 成功
- **クォータ超過フロー**: 使用量増加 → 80%警告 → 100%超過 → 従量課金
- **ブランディングフロー**: ドメイン追加 → DNS検証 → SSL発行 → ロゴアップロード → カラー変更

### パフォーマンステスト（Week 14）
- **負荷テスト**: 100同時ユーザー
- **Webhookレスポンス**: <200ms
- **CSS生成**: <3秒
- **ドメイン検証**: <10秒

---

## 🚀 Launch Checklist

### Pre-Launch（Week 13-14）
- [ ] すべての機能が仕様通り動作
- [ ] E2Eテストがパス
- [ ] セキュリティ監査完了
- [ ] ドキュメント完成
- [ ] エラーハンドリング・ロギング整備
- [ ] 監視・アラート設定（Sentry, Datadog）

### Stripe設定
- [ ] 本番環境のStripe Accountセットアップ
- [ ] Webhook URLを本番に変更
- [ ] プラン価格の最終確認
- [ ] 請求書テンプレートの確認

### インフラ
- [ ] データベースバックアップ体制確認
- [ ] CDN設定（カスタムドメイン・SSL証明書）
- [ ] ロードバランサー設定
- [ ] スケーリング設定

### マーケティング
- [ ] Pricing Pageの公開
- [ ] ブログ記事: Phase 1.5リリース告知
- [ ] 既存ユーザーへのメール通知
- [ ] SNS投稿準備

### Launch Day（Week 15予定）
- [ ] Phase 1.5機能を本番環境にデプロイ
- [ ] 機能フラグをON
- [ ] 監視ダッシュボードを確認
- [ ] カスタマーサポート体制を待機
- [ ] マーケティング施策実行

---

## 📊 Success Metrics & KPIs

### 初月（リリース後1ヶ月）
- **有料プラン登録数**: 10社
- **トライアル → 有料転換率**: 30%
- **決済成功率**: 95%以上
- **カスタムドメイン設定成功率**: 80%

### 3ヶ月後
- **MRR（月次経常収益）**: ¥1,500,000
- **有料テナント数**: 30社
- **チャーン率**: 3%以下
- **アップグレード率**: 15%
- **ブランディング機能利用率**: Business/Enterpriseプランの60%

### 6ヶ月後
- **ARR**: ¥50,000,000
- **有料テナント数**: 100社
- **ARPU**: ¥50,000/月
- **LTV/CAC比**: 3.0以上

---

## 🔧 Technical Debt & Future Improvements

Phase 1.5で対応しない項目（Phase 2以降に持ち越し）:

### サブスクリプション管理
- [ ] 年間プラン対応（現在は月次のみ）
- [ ] クーポン・プロモーションコード管理UI
- [ ] 会計システム連携（freee, マネーフォワード）
- [ ] 複数通貨対応（現在は日本円のみ）

### ホワイトラベル
- [ ] 完全カスタムHTML/JS（現在はCSS のみ）
- [ ] モバイルアプリのブランディング
- [ ] APIのホワイトラベル化
- [ ] 多言語ブランディング

---

## 👥 Team & Responsibilities

### Backend Team（2名）
- **Lead Backend Engineer**: Stripe統合、請求管理、Webhook
- **Backend Engineer**: ドメイン管理、ブランディングサービス

### Frontend Team（2名）
- **Lead Frontend Engineer**: Pricing Page、プラン管理、決済UI
- **Frontend Engineer**: ブランディングダッシュボード、ドメイン設定UI

### DevOps/Infrastructure（1名）
- SSL証明書管理
- CDN設定
- 監視・アラート

### QA/Testing（1名）
- テスト計画策定
- E2Eテスト実行
- バグトラッキング

### Product Manager（1名）
- 仕様確認
- ステークホルダー調整
- ローンチ計画

---

## 📚 References

### 仕様ドキュメント
- [Subscription & Billing Specification](../openspec/specs/features/subscription-billing.md)
- [White Label Branding Specification](../openspec/specs/features/white-label-branding.md)

### 技術ドキュメント
- [Stripe API Documentation](https://stripe.com/docs/api)
- [Stripe Billing Guide](https://stripe.com/docs/billing)
- [Let's Encrypt Documentation](https://letsencrypt.org/docs/)
- [WCAG Accessibility Guidelines](https://www.w3.org/WAI/WCAG21/)

### プロジェクト管理
- [Phase 1 Implementation Plan](./IMPLEMENTATION_PLAN_PHASE1.md)
- [Production Deployment Guide](./PRODUCTION_DEPLOYMENT_GUIDE.md)

---

**次のステップ**: Milestone 1からの実装開始！🚀
