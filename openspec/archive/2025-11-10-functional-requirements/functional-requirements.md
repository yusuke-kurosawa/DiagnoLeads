# DiagnoLeads 機能要件（OpenSpec 変更提案）

ステータス: Applied
作成日: 2025-11-10
責任者: プロダクトオーナー（DiagnoLeads）

## 1. ビジョンと目的

診断は“質問”ではなく“体験”である。DiagnoLeadsは、B2B 企業が数分で価値ある体験を設計し、回答データをただのリード情報ではなく「意思決定の材料」に昇華させるためのプラットフォームである。私たちの情熱は、マーケ・セールス・CS の断絶を越えて「診断 → 洞察 → アクション」を最短距離で結ぶこと。

本仕様は、MVP〜GAに向けた機能要件を OpenSpec として定義し、設計・実装・検証の単一のソースオブトゥルースとする。

## 2. スコープ

- 診断ビルダー（ノーコード）
- AI支援（診断自動生成、回答の洞察抽出）
- 埋め込みウィジェット（Web サイト設置）
- リード管理（ホットリード検出、スコアリング）
- 分析ダッシュボード（完了率、離脱、CV ファネル）
- 外部連携（Salesforce / HubSpot / Slack）
- テナント/認証（マルチテナント、RLS 前提）

## 3. ペルソナ

- マーケ担当（Tenant Admin/User）：LP に素早く診断を埋め込み、計測と改善を回したい
- インサイドセールス：ホットリードに優先接触したい
- 事業責任者：企画〜実行のサイクルタイムとCVRを見たい
- 実装エンジニア：安全に短時間で設置・運用したい

## 4. 用語

- 診断（Assessment）：質問群、ロジック、結果表示を含む体験定義
- 回答（Response）：エンドユーザーの回答データ行
- リード（Lead）：回答者情報 + スコア + 状態
- テナント（Tenant）：企業単位の分離境界

---

## 5. 機能エピックと要件

### 5.1 診断ビルダー（ノーコード）

目標：非エンジニアが 15 分で初回公開できる。

- FR-BLD-001: 質問タイプ（単一/複数選択、数値、自由記述、行列、セクション）を追加・並び替え・削除できる
- FR-BLD-002: スコアリングルールを UI から定義（選択肢加点、条件式、重み）できる
- FR-BLD-003: 分岐ロジック（質問スキップ/分岐）を設定できる
- FR-BLD-004: プリセットテンプレート（業界別）を選択して即時編集できる
- FR-BLD-005: 下書き/公開の状態管理、公開バージョンのロールバックができる
- FR-BLD-006: プレビュー（デスクトップ/モバイル）を 2 秒以内で反映
- FR-BLD-007: ブランド設定（色/ロゴ/トーン）をテーマとして保存・適用できる

受入基準（例: FR-BLD-005）
```
Given 下書き版が存在する
When 公開ボタンを押す
Then 公開バージョンが作成され、ウィジェットは新バージョンを提供する
And 任意の過去公開版に 1 クリックでロールバックできる
```

API（案）
- POST /api/v1/tenants/{tenant_id}/assessments
- PATCH /api/v1/tenants/{tenant_id}/assessments/{id}
- POST /api/v1/tenants/{tenant_id}/assessments/{id}/publish
- POST /api/v1/tenants/{tenant_id}/assessments/{id}/rollback

イベント
- assessment.published、assessment.rolled_back

---

### 5.2 AI支援

目標：ブランク状態から 5 分で「提案→編集→公開」へ到達。

- FR-AI-001: トピック/業界/目的の入力から質問・選択肢・スコアリング案を自動生成
- FR-AI-002: 回答データから「課題仮説」「推奨アクション」を抽出し、Sales/CS への次アクションを提示
- FR-AI-003: 質問の難易度・離脱率を自動分析し、改善提案を出す
- FR-AI-004: テンプレ文面の自然言語修正（トーン/長さ/専門度）

受入基準（例: FR-AI-001）
```
Given トピック『B2B SaaS のオンボーディング改善』
When 自動生成を実行
Then 10〜15 問の質問案、選択肢、スコアリング案、結果セクション案が返る
And 生成は 20 秒以内、やり直し/追生成が可能
```

API（案）
- POST /api/v1/tenants/{tenant_id}/ai/assessments: body {topic, industry, goal}
- POST /api/v1/tenants/{tenant_id}/ai/insights: body {assessment_id, filters}

イベント
- ai.assessment_proposed、ai.insight_generated

---

### 5.3 埋め込みウィジェット

目標：実装エンジニアが 10 分で設置、マーケがノーコードで更新。

- FR-EMB-001: 1 行スニペットで設置、テナントと診断を自動解決
- FR-EMB-002: モーダル/インライン/フローティングの表示モードに対応
- FR-EMB-003: i18n（日本語/英語）切替、右→左言語は非対象
- FR-EMB-004: パフォーマンス制約（初期 < 35KB gzip、p95 First Interaction < 1.0s）
- FR-EMB-005: イベントフック（onStart, onComplete, onLeadCaptured）
- FR-EMB-006: 同意管理（Cookie 同意、プライバシーリンク挿入）

受入基準（例: FR-EMB-005）
```
Given onComplete フックにコールバックを渡す
When 回答が完了する
Then 結果オブジェクトと lead_id を引数にコールバックが 1 回だけ呼ばれる
```

API（案）
- GET /embed/assessments/{public_id}.js
- POST /api/v1/public/assessments/{public_id}/responses

イベント
- widget.loaded、response.completed、lead.captured

---

### 5.4 リード管理

目標：IS が「今日電話すべき 20 件」を自動で受け取る。

- FR-LEAD-001: 回答完了時にリード作成（氏名/会社/メール/スコア/タグ）
- FR-LEAD-002: ホットリード判定（しきい値、AI 補正、最新回答重み）
- FR-LEAD-003: ステータス管理（New/Qualified/Working/Won/Lost）
- FR-LEAD-004: セグメント（条件保存、動的更新）
- FR-LEAD-005: 重複解決（メールキー、マージポリシー）

受入基準（例: FR-LEAD-002）
```
Given スコア >= 80 かつ 意思表示『導入時期=今期』
When リード作成
Then hot=true としてフラグが付与され、Slack 通知が送信される
```

API（案）
- GET /api/v1/tenants/{tenant_id}/leads?segment=hot&page=1
- PATCH /api/v1/tenants/{tenant_id}/leads/{id}

イベント
- lead.created、lead.updated、lead.merged、lead.hot_marked

---

### 5.5 分析ダッシュボード

目標：改善サイクル（仮説→実験→学習）を 1 週間で回す。

- FR-ANL-001: 完了率、離脱ポイント、平均回答時間を可視化
- FR-ANL-002: ファネル（閲覧→開始→中間→完了→CV）の時系列
- FR-ANL-003: 設問別貢献度と改善提案（AI）
- FR-ANL-004: セグメント比較（流入チャネル、業界、企業規模）
- FR-ANL-005: エクスポート（CSV/Slack サマリー）

受入基準（例: FR-ANL-001）
```
Given 直近 30 日の回答データ
When ダッシュボード表示
Then p95 200ms 以内で指標が表示され、ドリルダウンで個別回答に到達できる
```

API（案）
- GET /api/v1/tenants/{tenant_id}/analytics/overview?range=30d
- GET /api/v1/tenants/{tenant_id}/analytics/funnel?range=30d

イベント
- analytics.snapshot_generated

---

### 5.6 外部連携

目標：既存 CRM/MA の運用を崩さず確実に同期。

- FR-INT-001: Salesforce/HubSpot への双方向同期（Lead/Company/Activity）
- FR-INT-002: Slack 通知（ホットリード、しきい値アラート、毎朝レポート）
- FR-INT-003: レート制限/失敗時の再試行（指数バックオフ、最大3回）
- FR-INT-004: マッピング UI（フィールド対応表、変換ルール）

受入基準（例: FR-INT-001）
```
Given HubSpot 接続済
When リードが更新される
Then 30 秒以内に HubSpot Lead が更新され、失敗時は 3 回まで自動再試行される
```

イベント
- integration.synced、integration.failed、integration.retried

---

### 5.7 認証・マルチテナント

目標：強固な分離と、運用のシンプルさを両立。

- FR-AUTH-001: Supabase Auth による JWT 認証（ロール: system_admin/tenant_admin/user）
- FR-AUTH-002: すべてのクエリが tenant_id でフィルタされる（RLS）
- FR-AUTH-003: 監査ログ（誰が/いつ/何を）
- FR-AUTH-004: 招待リンク、SSO（Google, Microsoft）

受入基準（例: FR-AUTH-002）
```
Given 異なるテナント A/B
When A のユーザーが B の ID を指定しても
Then 404 もしくは空集合が返る（リークは発生しない）
```

---

## 6. 非機能境界（機能要件に付随する運用制約）

- p95 API 応答 < 200ms（分析集計系は別途 1s まで許容）
- 可用性 99.5% 以上、RPO=24h/RTO=4h（MVP）
- ウィジェット初期バンドル < 35KB gzip、依存の遅延読み込み
- すべてのイベントを監査テーブルに非同期記録（個人情報はトークン化）

---

## 7. リリーススライス

MVP（β）
- 診断ビルダー（基本型/スコア/公開）
- 埋め込み（インライン/モーダル）
- リード作成 + ホットリード通知（Slack）
- 分析（完了率/離脱）
- 認証/テナント/RLS

GA
- AI 改善提案/洞察
- 外部連携マッピング UI
- セグメント比較、CSV エクスポート
- バージョン管理とロールバック

---

## 8. 受入テスト（ハッピーパス）

1) 15 分チャレンジ
```
Given 空のテナント
When テンプレから作成→AI で微調整→公開→LP に設置
Then 問い合わせ 1 件が作成され、ダッシュボードで完了率が見える
```

2) ホットリード検出
```
Given スコア 85, 時期=今期 の回答
When リード生成
Then hot=true で Slack 通知、IS キューに並ぶ
```

3) 回答から洞察
```
Given 50 件の回答
When AI 洞察を実行
Then 『オンボーディング手順の複雑さ』が主要阻害要因として提示され、改善提案が 3 件表示される
```

---

## 9. トラッキング・イベントスキーマ（要約）

- widget.loaded {tenant_id, assessment_id, version, mode}
- response.started {public_id, session_id}
- response.completed {lead_id, score, duration}
- lead.hot_marked {lead_id, score, reason}
- analytics.snapshot_generated {range, counts}

---

## 10. 依存・前提

- Supabase（PostgreSQL, Auth）/ Upstash Redis / Railway / Vercel
- Anthropic Claude API（生成/洞察）
- Row-Level Security の常時有効化

---

## 11. 開放的な余白（私たちの挑戦）

1) 診断の“正答”ではなく“行動”を導く UX 研究（結果ページでのインタラクティブ・プレイブック）
2) スコアよりも“成熟度プロファイル”提示（レーダーチャート + 推奨ステップ）
3) A/B/C 実験を標準装備（質問文/順序/色/コンポーネント差し替え）

この仕様は、企業が「質問を作る」負担を最小化し、「学びと行動」を最大化するための約束である。私たちは、診断を最も速い顧客理解エンジンにする。

---

## 12. 適用リンク / コミット

Applied Specs（2025-11-10）
- specs/api/endpoints-overview.md
- specs/features/ai-support.md
- specs/features/embed-widget.md
- specs/features/lead-management.md
- specs/features/analytics-dashboard.md
- specs/features/integrations.md
- specs/features/publishing-and-versioning.md

関連コミット
- 57f9a20: spec: Add functional requirements proposal and feature specs（GitHub: https://github.com/yusuke-kurosawa/DiagnoLeads/commit/57f9a20 ）
