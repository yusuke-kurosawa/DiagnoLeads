# Implementation Tasks: Database Integrity Management System

## 1. データベース設計仕様の作成
- [ ] 1.1 `openspec/specs/database/schema-constraints.yml` を作成
  - 外部キー制約ルール（CASCADE/SET NULL/RESTRICT）の定義
  - 各制約の理由を明記
  - 一意制約の定義
  - チェック制約の定義
  - インデックス戦略の定義

## 2. データベース整合性検証スクリプト
- [ ] 2.1 `backend/scripts/validate_database_integrity.py` の作成
  - DatabaseIntegrityValidator クラスの実装
  - validate_foreign_keys() メソッド
  - validate_orphan_records() メソッド
  - validate_unique_constraints() メソッド
  - validate_check_constraints() メソッド
  - validate_indexes() メソッド
  - validate_relationship_bidirectionality() メソッド

- [ ] 2.2 依存パッケージの追加
  - requirements-dev.txt に pyyaml を追加

- [ ] 2.3 スクリプトのテスト
  - ローカル環境で実行確認
  - 各検証項目の動作確認

## 3. CI/CDワークフローの追加
- [ ] 3.1 `.github/workflows/database-integrity.yml` の作成
  - PostgreSQLサービスコンテナの設定
  - マイグレーション実行
  - データベース整合性検証
  - マイグレーション競合チェック
  - ER図同期確認

- [ ] 3.2 `.github/workflows/spec-validation.yml` の作成
  - OpenSpec構造検証
  - Markdown形式検証
  - OpenAPI検証（Spectral）
  - Breaking Change検出（oasdiff）
  - 型整合性チェック
  - Zodスキーマ検証

## 4. OpenAPI厳格検証の追加
- [ ] 4.1 `.spectral.yml` の作成
  - 基本ルールの設定
  - Multi-tenant対応チェックのカスタムルール
  - operationId命名規則の強制
  - レスポンススキーマ必須化
  - エラーレスポンス標準化

- [ ] 4.2 Spectral CLIのインストール
  - frontend/package.json にスクリプト追加
  - CI/CDでの実行設定

- [ ] 4.3 oasdiffの導入
  - Breaking Change検出の設定
  - CI/CDへの統合

## 5. ER図自動生成
- [ ] 5.1 `backend/scripts/generate_er_diagram.py` の作成
  - SQLAlchemy Inspectorを使用した分析
  - Mermaid形式での出力
  - リレーションシップの種類を明示

- [ ] 5.2 CI/CDでの自動実行設定
  - マイグレーション後の自動生成
  - 差分検出とPRステータス更新

## 6. Zodスキーマの統合テスト
- [ ] 6.1 Zodスキーマの作成（フロントエンド）
  - `frontend/src/schemas/lead.schema.ts`
  - `frontend/src/schemas/assessment.schema.ts`
  - その他主要エンティティのスキーマ

- [ ] 6.2 Zodスキーマテストの作成
  - `frontend/src/schemas/*.test.ts`
  - OpenAPI型との整合性テスト
  - ランタイムバリデーションテスト

- [ ] 6.3 package.jsonにテストスクリプト追加
  - `npm run test:schemas` の追加

## 7. PRテンプレートの作成
- [ ] 7.1 `.github/pull_request_template.md` の作成
  - 変更内容のチェックリスト
  - データベース変更に関する確認項目
  - OpenAPI変更に関する確認項目
  - テスト実行の確認

- [ ] 7.2 ブランチ保護ルールの設定（手動）
  - main ブランチへの直接pushを禁止
  - 必須レビュー設定
  - ステータスチェック必須化

## 8. マイグレーション生成補助スクリプト
- [ ] 8.1 `backend/scripts/create_migration.py` の作成
  - alembic revision の自動実行
  - 整合性チェックの自動実行
  - ER図の自動更新

## 9. ドキュメント更新
- [ ] 9.1 README の更新
  - データベース整合性管理システムの説明追加
  - 開発ワークフローの更新

- [ ] 9.2 CONTRIBUTING.md の更新
  - PRの作成方法
  - マイグレーション作成のベストプラクティス
  - CI/CDチェック項目の説明

- [ ] 9.3 openspec/README.md の更新
  - データベース仕様管理の追加

## 10. テストとデプロイ
- [ ] 10.1 ローカル環境での動作確認
  - すべてのスクリプトの実行テスト
  - 各種検証の動作確認

- [ ] 10.2 テストブランチでのCI/CD確認
  - GitHub Actionsの実行確認
  - エラーメッセージの妥当性確認

- [ ] 10.3 チーム向けドキュメントの準備
  - オンボーディングガイド
  - トラブルシューティングガイド

## 実装順序

### Phase 1: 基盤（即座）
1. Task 1.1 - スキーマ制約定義
2. Task 2.1, 2.2 - 検証スクリプト
3. Task 3.1 - データベース整合性CI/CD
4. Task 7.1 - PRテンプレート

### Phase 2: OpenAPI統合（1週間後）
1. Task 4.1, 4.2, 4.3 - Spectral & oasdiff
2. Task 3.2 - Spec検証CI/CD
3. Task 6.1, 6.2, 6.3 - Zodスキーマ

### Phase 3: 自動化強化（2週間後）
1. Task 5.1, 5.2 - ER図自動生成
2. Task 8.1 - マイグレーション補助
3. Task 9.1, 9.2, 9.3 - ドキュメント更新

## 完了条件
- ✅ すべてのCI/CDチェックがPR上で実行される
- ✅ データベース整合性違反が自動検出される
- ✅ 孤児レコードが即座に検出される
- ✅ OpenAPI Breaking Changeが自動検出される
- ✅ ER図が常に最新状態に保たれる
- ✅ mainブランチへの直接pushが防止される
- ✅ チームメンバーが新しいワークフローを理解している
