# OpenSpec - Human-Readable Specifications

このディレクトリは**OpenSpec**（by Fission-AI）による仕様駆動開発を管理します。

## 📋 OpenSpecとは

OpenSpecは、人間とAI coding assistantsが理解しやすいMarkdown形式の仕様管理フレームワークです。

**OpenSpec vs OpenAPI:**
- **OpenSpec**: 人間のための仕様（機能、ビジネスロジック、UI/UX）
- **OpenAPI**: 機械のための仕様（APIエンドポイント、自動型生成）

DiagnoLeadsでは両方を併用し、完全なSpec駆動開発を実現しています。

詳細: [SPEC_STRATEGY.md](../SPEC_STRATEGY.md)

## 📂 ディレクトリ構造

```
openspec/
├── README.md                # このファイル
├── specs/                   # 承認済み仕様（Source of Truth）
│   ├── OVERVIEW.md          # プロジェクト全体概要 ⭐
│   ├── features/            # 機能仕様
│   ├── api/                 # API設計
│   ├── architecture/        # アーキテクチャ設計
│   │   └── technology-stack.md  # 技術スタック仕様 ⭐
│   ├── ui-ux/              # UI/UX設計
│   │   └── guidelines.md    # UI/UXガイドライン仕様 ⭐
│   ├── database/           # データベース設計
│   │   ├── er-diagram-system.md # ER図生成システム ⭐
│   │   ├── diagnoleads-data-model.md
│   │   └── er-diagram-format.md
│   └── integrations/       # 外部連携仕様
├── changes/                # レビュー中の変更提案
└── archive/                # 完了した変更
    └── 2025-11-12-session-reports/  # セッション記録
```

**⭐ = 案2統合により新規に追加された統合仕様**

### specs/ - 承認済み仕様

**これが実装の基準となる唯一の真実（Single Source of Truth）**

実装前に必ずここの仕様を確認してください。

```bash
# 例: Assessment機能の仕様を確認
cat specs/features/assessment-crud.md
```

### changes/ - 変更提案

新機能や変更の提案をここに作成します。
チームでレビュー・議論後、承認されたら`specs/`に移動します。

```bash
# 新しい提案を作成
vim changes/new-feature-proposal.md
```

### archive/ - 完了した変更

実装が完了した変更をアーカイブします。
履歴として保存し、将来の参考にします。

```bash
# 実装完了後にアーカイブ
mv specs/features/feature.md archive/$(date +%Y-%m-%d)-feature.md
```

## 🔄 ワークフロー

### 1. Proposal（提案）

新機能や変更を`changes/`に提案します。

```markdown
# changes/lead-management.md

# Feature Proposal: Lead Management

## Overview
リード管理機能を追加する。

## User Stories
- 営業担当者として、リードを登録したい
- マーケティング担当者として、リードをスコアリングしたい

## Requirements
- リードCRUD機能
- ステータス管理
- スコアリング機能

## API Design (概要)
- POST /api/v1/tenants/{id}/leads
- GET /api/v1/tenants/{id}/leads
...
```

### 2. Review（レビュー）

チームで提案をレビュー・議論します。

```bash
# Pull Requestを作成
git checkout -b feature/lead-management
git add openspec/changes/lead-management.md
git commit -m "proposal: Add lead management feature"
git push
gh pr create
```

### 3. Approve（承認）

レビュー完了後、`specs/`に移動します。

```bash
# 承認後
mv openspec/changes/lead-management.md \
   openspec/specs/features/lead-management.md

git add openspec/
git commit -m "spec: Approve lead management feature"
```

### 4. Implement（実装）

承認された仕様に基づいて実装します。

```bash
# 仕様を確認しながら実装
cat openspec/specs/features/lead-management.md

# バックエンド実装
# → FastAPIエンドポイント、モデル、スキーマ

# OpenAPI自動生成
cd backend && python scripts/generate_openapi.py

# フロントエンド型生成
cd frontend && npm run generate:types

# フロントエンド実装
# → Reactコンポーネント（型安全）
```

### 5. Archive（アーカイブ）

実装完了後、アーカイブします。

```bash
# 実装完了
mv openspec/specs/features/lead-management.md \
   openspec/archive/2025-01-10-lead-management.md

git add openspec/
git commit -m "archive: Lead management implementation complete"
```

## 📝 仕様テンプレート

### Feature Specification Template

```markdown
# Feature: [Feature Name]

## Overview
機能の概要を1-2文で説明

## User Stories
- [Role]として、[Action]したい、so that [Benefit]

## Requirements
### Functional Requirements
- 要件1
- 要件2

### Non-Functional Requirements
- パフォーマンス要件
- セキュリティ要件

## API Design (概要)
- Endpoint: [Method] [Path]
- Purpose: [説明]

## Data Model (概要)
- Entity名
  - field1: type
  - field2: type

## UI/UX Design
- Component名: 説明
- User Flow: 説明

## Business Logic
具体的なビジネスルールやロジック

## Testing Strategy
- Unit Tests: [何をテストするか]
- Integration Tests: [何をテストするか]

## Implementation Notes
実装時の注意点や考慮事項

## Related Specs
- [関連する他の仕様へのリンク]
```

### API Specification Template

```markdown
# API: [API Name]

## Endpoints

### [Method] [Path]
**Purpose**: [エンドポイントの目的]

**Parameters:**
- path: [parameter] - [description]
- query: [parameter] - [description]

**Request Body:**
```json
{
  "field": "value"
}
```

**Response (200):**
```json
{
  "id": "uuid",
  "field": "value"
}
```

**Errors:**
- 400: Invalid request
- 403: Forbidden
- 404: Not found

**Business Logic:**
- [処理の流れ]

**Security:**
- [認証・認可の要件]

**Multi-Tenant:**
- [テナント分離の考慮事項]
```

## 🎯 ベストプラクティス

### DO ✅

1. **実装前に仕様を書く**: Spec Firstの原則
2. **具体的に書く**: 曖昧さを避ける
3. **ビジネス価値を明記**: なぜこの機能が必要か
4. **関連仕様にリンク**: 他の仕様との関係を明示
5. **定期的にレビュー**: 仕様が実装と一致しているか確認

### DON'T ❌

1. **仕様なしで実装しない**: 必ず仕様から始める
2. **実装と乖離させない**: 変更時は仕様も更新
3. **OpenAPIと混同しない**: OpenSpecは機能仕様、OpenAPIはAPI仕様
4. **承認前に実装しない**: レビュープロセスを尊重
5. **古い仕様を放置しない**: 定期的にアーカイブ

## 🔧 便利なコマンド

```bash
# 承認済み仕様の一覧
ls openspec/specs/features/

# 変更提案の確認
ls openspec/changes/

# 特定の仕様を検索
grep -r "Assessment" openspec/specs/

# 最近の変更を確認
ls -lt openspec/archive/ | head -10

# 仕様の統計
echo "Specs: $(find openspec/specs -name '*.md' | wc -l)"
echo "Changes: $(find openspec/changes -name '*.md' | wc -l)"
echo "Archive: $(find openspec/archive -name '*.md' | wc -l)"
```

## 🤖 Factory Droid統合

`spec-sync` Droidが自動的に：
- OpenSpec構造の検証
- 仕様と実装の同期確認
- 古い変更提案の検出
- レポート生成

```bash
# Droidによる自動チェック
/spec-check

# ワークフローヘルプ
/spec-help
```

## 📚 参考資料

- [OpenSpec GitHub](https://github.com/Fission-AI/OpenSpec)
- [OpenSpec Official](https://openspec.dev/)
- [SPEC_STRATEGY.md](../SPEC_STRATEGY.md) - OpenSpec + OpenAPI統合戦略
- [README.openspec.md](../README.openspec.md) - OpenAPI仕様駆動開発

## 🎓 学習リソース

- [Specification-Driven Development入門](https://github.com/Fission-AI/OpenSpec#readme)
- [OpenSpec vs Spec Kit](https://hashrocket.com/blog/posts/openspec-vs-spec-kit)
- [How OpenSpec Works](https://jimmysong.io/en/ai/openspec/)

---

**Remember**: OpenSpecは人間のための仕様。機能の「なぜ」と「どのように」を記述する。🎯
