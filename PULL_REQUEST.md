# Pull Request: AI Agents リファクタリング + トークン使用量追跡機能

## 概要

AI Agentsの大規模リファクタリングとトークン使用量のデータベース保存機能を追加しました。

**ブランチ**: `claude/refactor-agents-01EYJkyqFy4WT26Ke8NLwPPx` → `main`

## 主な変更内容

### Phase 1: エラーハンドリングとセキュリティ強化

#### 構造化例外システム (`backend/app/services/ai/exceptions.py`)
- `AIServiceError`: ベース例外クラス
- `AIAPIError`: API呼び出し失敗
- `AIRateLimitError`: レート制限エラー
- `AIValidationError`: レスポンス検証失敗
- `AIJSONParseError`: JSON解析失敗
- `AIPromptInjectionError`: プロンプトインジェクション検出

#### 堅牢なJSON抽出 (`backend/app/services/ai/json_extractor.py`)
- 4つの抽出戦略を順番に試行
- Markdown形式、埋め込みJSON、直接JSON解析に対応
- Unicode、エスケープ文字に対応

#### プロンプトインジェクション対策 (`backend/app/services/ai/prompt_sanitizer.py`)
- 疑わしいパターンの検出（"ignore instructions"等）
- 入力長チェックとサニタイズ
- ネスト構造の再帰的検証

#### リトライロジック (`backend/app/services/ai/retry_helper.py`)
- エクスポネンシャルバックオフ（最大3回）
- レート制限、接続エラーに自動対応
- 再試行不可能なエラーの即座の失敗

### Phase 2: アーキテクチャ改善

#### 完全非同期処理 (`backend/app/services/ai_service.py`)
- `AsyncAnthropic` クライアントを使用
- 真の非同期処理で並列実行が可能
- 実行時間の計測機能追加

#### Dependency Injection対応
- `get_ai_service()` 関数を追加 (`backend/app/core/deps.py`)
- テストとモックが容易に
- APIエンドポイントで依存性注入を使用

#### マルチテナント対応
- すべてのAIメソッドに `tenant_id` パラメータを追加
- トークン使用量をテナント別に追跡
- ログにテナントコンテキストを含める

#### プロンプトテンプレート標準化 (`backend/app/services/ai/prompt_templates.py`)
- プロンプトをテンプレートクラスに集約
- バージョン管理可能
- 一貫性のある出力形式

#### 構造化ロギング (`backend/app/core/logging_config.py`)
- 統一されたロギング設定
- 操作ごとの詳細ログ
- トークン使用量の自動記録

### Phase 3: トークン使用量追跡

#### AIUsageLogモデル (`backend/app/models/ai_usage.py`)
- テナント別・ユーザー別の使用量記録
- 自動コスト計算（Claude 3.5 Sonnetの料金）
- 操作種別、モデル、成功/失敗、実行時間を記録
- Assessment/Lead IDとの紐付け

#### データベース保存機能
- `_log_token_usage()` メソッドにDB保存機能を追加
- すべてのAIメソッドに `user_id`, `db` パラメータを追加
- エラー時も失敗として記録

#### データベースマイグレーション
- `ai_usage_logs` テーブルを追加
- 4つのインデックスを作成（効率的なクエリ用）
- 外部キー制約を設定
- 詳細は `MIGRATION_GUIDE.md` を参照

## ファイル変更サマリー

### 新規ファイル (19個)

**AI Services**
- `backend/app/services/ai/exceptions.py` - カスタム例外
- `backend/app/services/ai/json_extractor.py` - JSON抽出ロジック
- `backend/app/services/ai/prompt_sanitizer.py` - 入力サニタイズ
- `backend/app/services/ai/prompt_templates.py` - プロンプトテンプレート
- `backend/app/services/ai/retry_helper.py` - リトライロジック

**モデル**
- `backend/app/models/ai_usage.py` - AIUsageLogモデル

**ロギング**
- `backend/app/core/logging_config.py` - ログ設定

**テスト (40テストケース)**
- `backend/tests/test_ai_json_extractor.py` (10テスト)
- `backend/tests/test_ai_prompt_sanitizer.py` (20テスト)
- `backend/tests/test_ai_exceptions.py` (10テスト)

**マイグレーション**
- `backend/alembic/versions/b2c3d4e5f6g7_add_ai_usage_log_table.py`

**ドキュメント**
- `backend/AGENTS_REFACTORING.md` - リファクタリング詳細
- `backend/MIGRATION_GUIDE.md` - マイグレーション実行ガイド

### 変更ファイル (11個)

- `backend/app/services/ai_service.py` - 完全リファクタリング
- `backend/app/services/ai/__init__.py` - 新モジュールのエクスポート
- `backend/app/api/v1/ai.py` - DI対応、user_id/db追加
- `backend/app/core/deps.py` - `get_ai_service()` 追加
- `backend/app/core/constants.py` - 優先度定数追加
- `backend/app/models/tenant.py` - ai_usage_logsリレーションシップ
- `backend/app/models/__init__.py` - AIUsageLogエクスポート
- `backend/requirements.txt` - Anthropic SDK更新 (v0.34.0+)

## テストカバレッジ

- JSON抽出: 10テストケース
- プロンプトサニタイザー: 20テストケース
- 例外クラス: 10テストケース
- **合計: 40テストケース**

## データベース変更

### 新規テーブル: `ai_usage_logs`

**カラム:**
- `id` (UUID): 主キー
- `tenant_id` (UUID): テナントID
- `user_id` (UUID): ユーザーID
- `operation` (VARCHAR): 操作種別
- `model` (VARCHAR): AIモデル
- `input_tokens`, `output_tokens`, `total_tokens` (INTEGER): トークン数
- `cost_usd` (FLOAT): 推定コスト
- `assessment_id`, `lead_id` (UUID): 関連レコード
- `duration_ms` (INTEGER): 実行時間
- `success` (VARCHAR): 成功/失敗
- `created_at` (TIMESTAMP): 作成日時

**インデックス:**
- `idx_ai_usage_logs_tenant_id`
- `idx_ai_usage_logs_operation`
- `idx_ai_usage_logs_created_at`
- `idx_ai_usage_logs_tenant_created` (複合)

## マイグレーション実行方法

```bash
cd backend

# マイグレーション実行
python << 'EOF'
from alembic.config import Config
from alembic import command
command.upgrade(Config("alembic.ini"), "head")
EOF
```

詳細は `MIGRATION_GUIDE.md` を参照してください。

## 破壊的変更

**なし** - すべての変更は後方互換性を保持しています。

既存のAPIエンドポイントは変更なく動作し、新しいパラメータはオプションです。

## セキュリティ改善

1. **プロンプトインジェクション対策**: 悪意のある入力を検出・ブロック
2. **入力検証**: 長さ制限と形式チェック
3. **エラーメッセージの適切な処理**: 機密情報の漏洩を防止
4. **テナント分離**: マルチテナント環境でのデータ保護強化

## パフォーマンス影響

**ポジティブ:**
- 非同期処理によるスループット向上
- リトライロジックによる成功率向上

**ネガティブ:**
- 入力サニタイズによる若干のオーバーヘッド（数ms程度）
- トークン使用量のDB保存（非同期処理のため影響最小）

**総合:** 全体的なシステムの信頼性とパフォーマンスは向上

## デプロイ手順

1. **コードマージ**: このPRをmainブランチにマージ
2. **依存関係更新**: `pip install -r backend/requirements.txt`
3. **マイグレーション実行**: 上記のマイグレーションコマンドを実行
4. **アプリケーション再起動**: バックエンドサービスを再起動
5. **動作確認**: AI API呼び出しを実行してログ記録を確認

## 確認事項

- [ ] すべてのテストがパス
- [ ] マイグレーションファイルのレビュー完了
- [ ] ドキュメント（AGENTS_REFACTORING.md, MIGRATION_GUIDE.md）の確認
- [ ] データベースバックアップの取得（本番環境）
- [ ] マイグレーション実行計画の確認

## 関連コミット

- `59b7546` - feat: AIトークン使用量テーブルのマイグレーション追加
- `1aab17c` - feat: トークン使用量のデータベース保存とテスト追加
- `dfb996a` - refactor: AI Agents の大規模リファクタリング

## 参考ドキュメント

- [AGENTS_REFACTORING.md](backend/AGENTS_REFACTORING.md) - リファクタリング詳細ドキュメント
- [MIGRATION_GUIDE.md](backend/MIGRATION_GUIDE.md) - マイグレーション実行ガイド

## 今後の拡張可能性

このリファクタリングにより、以下の機能が実装しやすくなりました：

1. テナント別のAPI使用量制限
2. コスト分析ダッシュボード
3. 異常検知（使用量スパイク検出）
4. プロンプトテンプレートのA/Bテスト
5. モデル切り替え機能

---

**レビュワーへ**: 特に以下の点をご確認ください：
- マイグレーションファイルの妥当性
- エラーハンドリングの適切性
- セキュリティ対策の有効性
- パフォーマンスへの影響
