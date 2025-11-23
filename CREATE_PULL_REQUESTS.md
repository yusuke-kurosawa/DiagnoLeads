# Pull Request作成手順

## 概要
Phase 1とPhase 2のPRを作成するための詳細な手順です。

---

## 🚀 Phase 1: Database Integrity Management PR

### PR作成URL
```
https://github.com/yusuke-kurosawa/DiagnoLeads/compare/main...feature/database-integrity-management?expand=1
```

### PR情報

**Title:**
```
feat: add database integrity validation system with CI/CD integration (Phase 1)
```

**Description:**
```markdown
## 📋 概要
データベース整合性を自動検証するシステムをCI/CDパイプラインに統合します。PR作成時に自動的にデータベース制約、外部キー、孤立レコード、インデックスなどを検証します。

## ✨ 変更内容

### 1. データベース整合性検証スクリプト
- ✅ 外部キー制約の検証
- ✅ 孤立レコード（Orphan Records）の検出
- ✅ 一意制約の検証
- ✅ チェック制約の検証
- ✅ インデックスの検証
- ✅ リレーションシップの双方向性検証

**ファイル**: `backend/scripts/validate_database_integrity.py` (400+行)

### 2. CI/CDワークフロー
- ✅ PRごとに自動実行
- ✅ PostgreSQLサービスコンテナで検証
- ✅ マイグレーションの適用とロールバックテスト
- ✅ 競合検出
- ✅ PR自動コメント

**ファイル**: `.github/workflows/database-integrity.yml`

### 3. PR テンプレート
- ✅ データベース変更チェックリスト
- ✅ OpenAPI変更チェックリスト
- ✅ フロントエンド変更チェックリスト
- ✅ セキュリティチェックリスト
- ✅ テストチェックリスト

**ファイル**: `.github/pull_request_template.md`

### 4. OpenSpec提案
- ✅ Why/What Changes/User Stories
- ✅ Requirements (FR/NFR)
- ✅ Success Metrics
- ✅ Implementation Notes

**ファイル**: `openspec/changes/database-integrity-management/proposal.md`

## 🎯 目的

### 問題点
- データベースの整合性チェックが手動で、見落としがある
- 外部キー制約違反が本番環境で発生するリスク
- 孤立レコードが蓄積し、データ品質が低下
- マイグレーションの競合が検出されない

### 解決策
- CI/CDでの自動検証により、問題を早期発見
- SQLAlchemyのInspector APIを使用した包括的なチェック
- 明確なエラーメッセージで修正を支援
- PR単位での品質保証

## 📊 検証内容の詳細

### 外部キー制約
```python
# 以下をチェック:
- すべての外部キーが適切なターゲットテーブルを参照
- 参照先のカラムが存在
- ON DELETE / ON UPDATE のルールが適切
```

### 孤立レコード
```python
# 以下をチェック:
- 外部キーで参照されているレコードが存在しない
- 親レコードが削除された後の子レコード
- Multi-tenant分離が正しく機能
```

### リレーションシップ双方向性
```python
# 以下をチェック:
- SQLAlchemyモデルのリレーションシップが双方向に定義
- back_populatesが正しく設定
- リレーションシップ名が一貫
```

## 🧪 テスト方法

### ローカル環境でのテスト
```bash
# 1. データベースを起動
docker-compose up -d postgres

# 2. マイグレーションを適用
cd backend
alembic upgrade head

# 3. 検証スクリプトを実行
python scripts/validate_database_integrity.py
```

### CI/CD での自動テスト
```bash
# PRを作成すると自動的に実行されます
# - PostgreSQLコンテナが起動
# - マイグレーションが適用
# - 整合性チェックが実行
# - 結果がPRコメントに投稿
```

## 📈 成功メトリクス

- 🎯 外部キー制約違反: **0件**
- 🎯 孤立レコード: **0件**
- 🎯 一意制約違反: **0件**
- 🎯 マイグレーション競合: **0件**
- 🎯 CI/CD実行時間: **5分以内**

## ⚠️ Breaking Changes
なし。既存機能に影響を与えない追加機能です。

## 📝 チェックリスト

### Database Changes
- [x] 新規検証スクリプトを作成
- [x] CI/CDワークフローを追加
- [x] OpenSpec提案を作成
- [x] 既存データベースで検証済み

### Documentation
- [x] OpenSpec proposal作成
- [x] Implementation notes追加
- [x] PR template更新
- [x] Branch protection guide作成

### Testing
- [x] スクリプトの動作確認
- [x] エラーハンドリングのテスト
- [x] CI/CDワークフローのテスト

## 🔗 関連リンク

- [OpenSpec Proposal](openspec/changes/database-integrity-management/proposal.md)
- [Implementation Tasks](openspec/changes/database-integrity-management/tasks.md)
- [Branch Protection Guide](BRANCH_PROTECTION_GUIDE.md)

## 🚀 次のステップ

1. **このPRマージ後**:
   - Phase 2: OpenAPI Validation Enhancement の実装
   - ブランチ保護ルールの設定

2. **Phase 2での実装予定**:
   - Spectralによる厳格なOpenAPI検証
   - oasdiffによるBreaking Change検出
   - データベーススキーマ制約の明文化

## 👥 レビュアーへの注意事項

### 重点的に確認してほしい箇所
1. **検証ロジック** (`validate_database_integrity.py`):
   - 外部キー検証の網羅性
   - 孤立レコード検出の精度
   - エラーメッセージの明瞭性

2. **CI/CDワークフロー** (`.github/workflows/database-integrity.yml`):
   - PostgreSQL設定の妥当性
   - 環境変数の安全性
   - タイムアウト設定

3. **PRテンプレート** (`.github/pull_request_template.md`):
   - チェックリスト項目の適切性
   - 開発者への分かりやすさ

### 質問事項
- データベース検証の頻度は適切か？（PR作成時のみ）
- エラー時のマージブロックで問題ないか？
- 追加で検証すべき項目はあるか？

---

**作成者**: GitHub Copilot  
**Phase**: 1/3 (Database Integrity Management)  
**関連Issue**: TBD
```

---

## 🚀 Phase 2: OpenAPI Validation Enhancement PR

### PR作成URL
```
https://github.com/yusuke-kurosawa/DiagnoLeads/compare/main...feature/openapi-validation-enhancement?expand=1
```

### PR情報

**Title:**
```
feat: add OpenAPI validation enhancement with Spectral and oasdiff (Phase 2)
```

**Description:**
```markdown
## 📋 概要
OpenAPI仕様の品質を保証するため、SpectralとoasdiffによるCI/CD検証システムを導入します。Multi-tenant対応の自動チェック、Breaking Change検出、命名規則の統一を実現します。

## ✨ 変更内容

### 1. Spectral厳格検証設定
- ✅ Multi-tenant対応の自動検証（すべてのパスに`/tenants/{tenant_id}/`必須）
- ✅ operationId命名規則（camelCase）の強制
- ✅ レスポンススキーマの必須化
- ✅ セキュリティ要件の検証
- ✅ 15+の検証ルール（エラー・警告・ヒントレベル）

**ファイル**: `.spectral.yml` (150+行)

### 2. データベーススキーマ制約の明文化
- ✅ 外部キー制約ルールと理由（CASCADE/SET NULL/RESTRICT）
- ✅ 一意制約の定義
- ✅ チェック制約の定義
- ✅ インデックス戦略
- ✅ Multi-tenant分離戦略
- ✅ 監査要件

**ファイル**: `openspec/specs/database/schema-constraints.yml` (300+行)

### 3. CI/CDワークフロー
- ✅ Spectral自動検証
- ✅ oasdiffによるBreaking Change検出
- ✅ Multi-tenant準拠チェック
- ✅ スキーマ制約の整合性検証
- ✅ PR自動コメント

**ファイル**: `.github/workflows/spec-validation.yml`

### 4. package.jsonスクリプト更新
- ✅ `validate:openapi:strict`: Spectral厳格検証
- ✅ `openapi:diff`: Breaking Change検出
- ✅ `validate`: 包括的検証（型チェック + OpenAPI）

**ファイル**: `frontend/package.json`

### 5. OpenSpec提案
- ✅ Why/What Changes/User Stories
- ✅ Requirements (FR/NFR)
- ✅ Success Metrics
- ✅ Implementation Notes

**ファイル**: `openspec/changes/openapi-validation-enhancement/proposal.md`

## 🎯 目的

### 問題点
- Multi-tenant対応の検証が手動で、漏れが発生
- Breaking Changeが検出されず、クライアントが壊れるリスク
- operationId命名が不統一で、フロントエンド開発が煩雑
- レスポンススキーマの欠落で型安全性が低い
- データベース設計の意図が不明確

### 解決策
- Spectralによる自動検証で、仕様品質を保証
- oasdiffで後方互換性を自動チェック
- 命名規則を強制し、コードベースを統一
- スキーマ制約を明文化し、チーム全体で共有

## 📊 検証内容の詳細

### Spectral検証ルール

#### エラーレベル（マージブロック）
```yaml
- multi-tenant-path: すべてのパスに/tenants/{tenant_id}/を含む
- operation-id-naming: operationIdはcamelCase
- operation-id-required: すべての操作にoperationId必須
- response-schema-required: 成功レスポンスにスキーマ必須
- security-required: すべての操作にセキュリティ要件必須
- tag-required: すべての操作にタグ必須
```

#### 警告レベル（修正推奨）
```yaml
- error-response-format: ErrorResponseスキーマの使用
- path-parameter-description: パラメータ説明の記載
- uuid-format: ID系パラメータはUUIDフォーマット
- list-response-structure: リストレスポンスにitemsとtotal
```

### Breaking Change検出
```bash
# 以下を自動検出:
- エンドポイントの削除
- パスの変更
- HTTPメソッドの変更
- 必須パラメータの追加
- レスポンス型の変更
- Enumの値削除
```

### スキーマ制約の明文化例
```yaml
foreign_key_rules:
  tenants_cascade:
    parent: tenants
    reason: "テナント削除時は全データを削除（GDPR準拠）"
    strategy: CASCADE

  users_set_null:
    parent: users
    reason: "ユーザー削除後もデータを保持（監査目的）"
    strategy: SET NULL
```

## 🧪 テスト方法

### ローカル環境でのテスト
```bash
# 1. Spectral/oasdiffをインストール
npm install -g @stoplight/spectral-cli oasdiff

# 2. Spectral検証を実行
cd frontend
npm run validate:openapi:strict

# 3. Breaking Change検出
npm run openapi:diff

# 4. 包括的検証
npm run validate
```

### CI/CD での自動テスト
```bash
# PRを作成すると自動的に実行されます
# - Spectral検証
# - Breaking Change検出
# - Multi-tenant準拠チェック
# - 結果がPRコメントに投稿
```

## 📈 成功メトリクス

- 🎯 OpenAPI仕様の品質スコア: **90%以上**（Spectral）
- 🎯 Multi-tenant対応漏れ: **0件**
- 🎯 Breaking Change検出率: **100%**
- 🎯 命名規則違反: **0件**
- 🎯 レスポンススキーマ欠落: **0件**

## ⚠️ Breaking Changes
なし。既存OpenAPI仕様に多数の警告が出る可能性がありますが、段階的に修正します。

## 📝 チェックリスト

### OpenAPI Validation
- [x] Spectral設定ファイル作成
- [x] カスタムルール定義（Multi-tenant、命名規則）
- [x] CI/CDワークフロー作成
- [x] package.jsonスクリプト追加

### Schema Constraints Documentation
- [x] 外部キー制約ルールと理由を明文化
- [x] 一意制約を定義
- [x] チェック制約を定義
- [x] インデックス戦略を文書化
- [x] Multi-tenant分離戦略を文書化

### Documentation
- [x] OpenSpec proposal作成
- [x] Implementation tasks作成
- [x] Next steps guide作成

### Testing
- [ ] Spectral検証の動作確認（既存仕様でテスト予定）
- [ ] oasdiff検証の動作確認（次のPRでテスト予定）
- [ ] CI/CDワークフローの動作確認（PRマージ後）

## 🔗 関連リンク

- [OpenSpec Proposal](openspec/changes/openapi-validation-enhancement/proposal.md)
- [Implementation Tasks](openspec/changes/openapi-validation-enhancement/tasks.md)
- [Schema Constraints](openspec/specs/database/schema-constraints.yml)
- [Phase 1 PR](https://github.com/yusuke-kurosawa/DiagnoLeads/pull/XXX)
- [Phase 2 Next Steps](PHASE2_NEXT_STEPS.md)

## 🚀 次のステップ

### このPRマージ後
1. **既存OpenAPI仕様のクリーンアップ**（別PR推奨）
   ```bash
   # Spectral検証を実行して問題を洗い出し
   npm run validate:openapi:strict > spectral-report.txt
   
   # エラーと警告を段階的に修正
   # - Multi-tenant対応: /api/v1/tenants/{tenant_id}/ を含める
   # - operationIdをcamelCaseに修正
   # - レスポンススキーマを追加
   ```

2. **ドキュメント更新**（別PR推奨）
   - README.md: 検証コマンドを追加
   - CONTRIBUTING.md: OpenAPIベストプラクティスを追加
   - DEVELOPER_GUIDE.md: Spectral使用方法を追加

3. **ブランチ保護ルールの設定**
   - Required status checks に追加:
     - ✅ Database Integrity Validation (Phase 1)
     - ✅ OpenAPI Specification Validation (Phase 2)

### Phase 3: Living Documentation（計画中）
1. ER図自動生成スクリプト
2. マイグレーション生成補助スクリプト
3. OpenSpec → 実装の追跡システム

## 👥 レビュアーへの注意事項

### 重点的に確認してほしい箇所
1. **Spectral設定** (`.spectral.yml`):
   - ルールの厳しさは適切か？
   - Multi-tenant検証の正確性
   - カスタムルールのロジック

2. **スキーマ制約** (`schema-constraints.yml`):
   - CASCADE/SET NULL/RESTRICTの判断は妥当か？
   - 一意制約の網羅性
   - インデックス戦略の妥当性

3. **CI/CDワークフロー** (`.github/workflows/spec-validation.yml`):
   - Breaking Change検出の精度
   - エラーメッセージの分かりやすさ
   - タイムアウト設定

### 質問事項
- Spectralルールはエラーレベルで良いか？（警告レベルで開始すべきか）
- Breaking Change検出時のポリシーは適切か？
- 既存仕様のクリーンアップはこのPRに含めるべきか？

### Breaking Changeポリシー
Breaking Changeを含むPRは以下を必須とします：
1. APIバージョンのメジャーバンプ
2. 最低3ヶ月の非推奨期間
3. クライアント移行ガイドの作成
4. Tech Leadの承認

---

**作成者**: GitHub Copilot  
**Phase**: 2/3 (OpenAPI Validation Enhancement)  
**依存関係**: Phase 1 (Database Integrity Management)  
**関連Issue**: TBD
```

---

## 📋 PR作成後の次のステップ

### 1. PRレビュー・マージ
- [ ] Phase 1 PRのレビュー依頼
- [ ] Phase 2 PRのレビュー依頼
- [ ] CI/CD結果の確認
- [ ] フィードバック対応
- [ ] Phase 1マージ
- [ ] Phase 2マージ

### 2. ブランチ保護ルール設定
`BRANCH_PROTECTION_GUIDE.md` に従って設定：
```
Settings → Branches → Branch protection rules → Add rule

Branch name pattern: main

Required status checks:
✅ Database Integrity Validation
✅ OpenAPI Specification Validation

Require pull request reviews: 1 approval
Require branches to be up to date: Yes
```

### 3. 既存OpenAPI仕様のクリーンアップ（別PR）
```bash
git checkout main
git pull origin main
git checkout -b fix/openapi-spec-cleanup

cd frontend
npm run validate:openapi:strict > ../spectral-report.txt 2>&1

# エラーと警告を修正
# - Multi-tenant対応
# - operationId修正
# - レスポンススキーマ追加

npm run validate:openapi:strict
git add ../openapi.json
git commit -m "fix: clean up OpenAPI spec for Spectral compliance"
git push -u origin fix/openapi-spec-cleanup
```

### 4. ドキュメント更新（別PR）
```bash
git checkout -b docs/openapi-validation-guide

# 更新するファイル:
# - README.md
# - CONTRIBUTING.md
# - docs/DEVELOPER_GUIDE.md

git push -u origin docs/openapi-validation-guide
```

---

## 🎉 完了！

Phase 1とPhase 2のPR作成の準備が整いました。上記のURLからPRを作成してください。

質問や問題があれば、いつでもお知らせください！ 🚀
