# Feature Proposal: OpenAPI Validation Enhancement (Phase 2)

## Why
現在のOpenAPI検証は基本的なバリデーションのみで、以下の問題があります：

- **Multi-tenant対応の検証不足**: すべてのAPIパスに`tenant_id`が含まれているか自動チェックされない
- **Breaking Changeの検出なし**: APIの後方互換性が保証されない
- **命名規則の不統一**: operationIdの命名が統一されていない
- **レスポンススキーマの不足**: 一部のエンドポイントでスキーマ定義が欠落
- **ランタイムバリデーション不足**: TypeScript型チェックのみで実行時エラーを検出できない

Phase 1で構築したデータベース整合性管理システムに加えて、API仕様の品質保証を強化する必要があります。

## What Changes

### 1. Spectralによる厳格なOpenAPI検証
`.spectral.yml` を作成し、以下をチェック：

#### 必須ルール（エラーレベル）
- ✅ すべてのエンドポイントに `operationId` 必須
- ✅ すべてのパスに `/api/v1/tenants/{tenant_id}/` を含む（Multi-tenant対応）
- ✅ operationId は camelCase 命名規則
- ✅ 成功レスポンス（2xx）にスキーマ必須
- ✅ すべての操作にセキュリティ要件必須
- ✅ すべての操作にタグ必須

#### 推奨ルール（警告レベル）
- ⚠️ エラーレスポンスは `ErrorResponse` スキーマを使用
- ⚠️ パスパラメータに説明を記載
- ⚠️ ID系パラメータは UUID フォーマット
- ⚠️ リストレスポンスは `items` と `total` を含む

### 2. Breaking Change自動検出
`oasdiff` を使用して：
- PRごとにOpenAPI仕様の差分を分析
- 破壊的変更を自動検出
  - エンドポイントの削除
  - 必須パラメータの追加
  - レスポンススキーマの変更
  - 型の変更
- Breaking Changeがある場合はPRに警告コメント

### 3. データベーススキーマ制約の明文化
`openspec/specs/database/schema-constraints.yml` を作成：
- 外部キー制約ルール（CASCADE/SET NULL/RESTRICT）と理由
- 一意制約の定義
- チェック制約の定義
- インデックス戦略
- Multi-tenant分離戦略
- 監査要件

### 4. CI/CD統合
`.github/workflows/spec-validation.yml` を作成：
- OpenSpec構造の検証
- Spectralによる厳格なOpenAPI検証
- oasdiffによるBreaking Change検出
- 型整合性チェック
- データベーススキーマ制約の検証

### 5. package.json スクリプト更新
フロントエンドに以下を追加：
```json
{
  "scripts": {
    "validate:openapi:strict": "spectral lint ../openapi.json",
    "openapi:diff": "oasdiff breaking origin/main:openapi.json openapi.json"
  }
}
```

## User Stories

### 開発者として
- 新しいAPIエンドポイントを追加する際、Multi-tenant対応が自動検証されたい
- PRを作成すると、Breaking Changeが自動検出され、警告されたい
- operationIdの命名規則が自動チェックされ、一貫性が保たれたい

### テックリードとして
- データベース設計の意図（なぜCASCADEなのか）が明文化され、チームで共有されたい
- API仕様の品質基準が明確で、自動的に強制されたい
- 後方互換性が保証され、クライアントアプリが壊れないようにしたい

### QAエンジニアとして
- API仕様の不備が開発段階で検出され、テスト工数が削減されたい
- 仕様とAPIの実装が一致していることが保証されたい

## Requirements

### Functional Requirements

#### FR-1: Spectral厳格検証
- Spectralルールセットを定義できること
- Multi-tenant対応の自動検証
- operationId命名規則の強制
- レスポンススキーマの必須化
- CI/CDで自動実行

#### FR-2: Breaking Change検出
- oasdiffを使用してAPI仕様の差分を分析
- 以下の破壊的変更を検出：
  - エンドポイントの削除
  - パスの変更
  - 必須パラメータの追加
  - レスポンススキーマの変更
  - HTTPメソッドの変更
- PRコメントで結果を通知

#### FR-3: スキーマ制約の明文化
- YAML形式で管理可能
- 外部キー制約の理由を記載
- チーム全体で共有可能
- Phase 1の検証スクリプトと連携

#### FR-4: CI/CD統合
- PRごとに自動実行
- 検証失敗時はマージをブロック
- 結果をPRコメントで可視化

### Non-Functional Requirements

#### NFR-1: パフォーマンス
- Spectral検証は30秒以内に完了
- oasdiff分析は1分以内に完了

#### NFR-2: 保守性
- ルールはYAMLで管理
- カスタムルールを容易に追加可能

#### NFR-3: 可視性
- CI/CD結果をPRコメントで明確に表示
- エラー時は修正方法を提示

## API Design

本機能は内部ツールのため、外部APIの変更はありません。

## Data Model

新規テーブルの追加はありません。`schema-constraints.yml` で既存スキーマを文書化します。

## UI/UX Design

### PR画面での表示（成功時）

```
✅ OpenAPI Specification Validation - PASSED

- ✓ Spectral validation passed (32 rules checked)
- ✓ No breaking changes detected
- ✓ All endpoints follow multi-tenant pattern
- ✓ operationId naming convention compliant
- ✓ Response schemas defined for all operations
```

### PR画面での表示（警告時）

```
⚠️  OpenAPI Specification Validation - WARNINGS

Spectral Warnings (3):
  - operation-description: Missing description for POST /api/v1/tenants/{tenant_id}/leads
  - path-parameter-description: Parameter 'tenant_id' missing description
  - error-response-format: Error response should use ErrorResponse schema

Breaking Changes Detected (1):
  ⚠️  BREAKING: Removed endpoint DELETE /api/v1/tenants/{tenant_id}/assessments/{id}/archive
  
  Impact: Clients using this endpoint will break
  Suggestion: 
    - Keep the old endpoint and mark as deprecated
    - Add new endpoint with different name
    - Update all clients before removing
```

### PR画面での表示（エラー時）

```
❌ OpenAPI Specification Validation - FAILED

Critical Errors (2):
  ✗ multi-tenant-path: Path '/api/v1/leads' must include /tenants/{tenant_id}/
  ✗ operation-id-naming: operationId 'Create_Lead' must be camelCase

Action Required:
  1. Update path to /api/v1/tenants/{tenant_id}/leads
  2. Change operationId to 'createLead'
  3. Run: npm run validate:openapi:strict
```

## Business Logic

### Spectral検証のルール優先度

1. **Error**: マージをブロック
   - Multi-tenant対応
   - operationId命名規則
   - セキュリティ要件

2. **Warning**: マージは可能だが修正推奨
   - エラーレスポンス形式
   - パラメータ説明

3. **Hint**: 情報提供のみ
   - デフォルトレスポンスの推奨

### Breaking Change判定基準

**Breaking Change（破壊的変更）**:
- エンドポイントの削除
- パスの変更
- HTTPメソッドの変更
- 必須パラメータの追加
- レスポンス型の変更（string→number等）
- Enumの値削除

**Non-Breaking Change（安全な変更）**:
- 新しいエンドポイントの追加
- オプショナルパラメータの追加
- レスポンスフィールドの追加
- Enumの値追加

## Testing Strategy

### Unit Tests
- Spectralカスタムルールのテスト
- 様々なOpenAPI仕様でのテスト

### Integration Tests
- CI/CDパイプラインでの実行テスト
- PR作成→検証→コメント投稿のフロー

### Manual Tests
- 意図的にルール違反を作成してテスト
- Breaking Changeを含むPRでテスト

## Implementation Notes

### Phase 2の実装手順

1. **Spectral設定** (`.spectral.yml`)
2. **スキーマ制約定義** (`schema-constraints.yml`)
3. **CI/CDワークフロー** (`spec-validation.yml`)
4. **package.jsonスクリプト追加**
5. **ドキュメント更新**

### 依存パッケージ

```bash
# Spectral CLI
npm install -g @stoplight/spectral-cli

# oasdiff
npm install -g oasdiff
# または
brew install oasdiff
```

### 制約・注意事項

- Spectralルールはプロジェクトに合わせてカスタマイズ可能
- Breaking Changeは警告のみ。最終判断は人間が行う
- 既存のOpenAPI仕様に多数の警告が出る可能性あり→段階的に修正

## Related Specs

- [Database Integrity Management](./database-integrity-management/proposal.md) - Phase 1
- [Database Schema Constraints](../specs/database/schema-constraints.yml)
- [OpenAPI Integration](../../README.openspec.md)

## Success Metrics

- 🎯 OpenAPI仕様の品質スコア: 90%以上（Spectral）
- 🎯 Breaking Change検出率: 100%
- 🎯 Multi-tenant対応漏れ: 0件
- 🎯 命名規則違反: 0件

## Risks & Mitigations

### リスク1: 既存仕様の大量警告
- **影響**: 初回導入時に多数の警告
- **対策**: 警告レベルから開始、段階的にエラーレベルへ

### リスク2: False Positive（誤検出）
- **影響**: 正当な変更がBreakingと判定
- **対策**: 除外ルールの提供、人間の最終判断

### リスク3: CI/CD実行時間の増加
- **影響**: PR作成から完了までの時間増加
- **対策**: 並列実行、キャッシュ活用

## Next Steps (Phase 3)

Phase 2完了後、以下を実装予定：
1. ER図自動生成スクリプト
2. マイグレーション生成補助スクリプト
3. Living Documentation自動生成
4. Design Tokens統合
