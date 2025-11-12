# OpenSpec × Droid クイックリファレンス

すぐに使えるコマンドとワークフローのチートシート。

## 🚀 1分でわかるOpenSpec

```
OpenSpec (機能仕様) + OpenAPI (API仕様) + Factory Droid (自動化)
= 完全な仕様駆動開発
```

## 📋 必須Droidコマンド

### 毎日使うコマンド

```bash
# 仕様の状態確認
/openspec-status

# 仕様と実装の同期確認
/spec-check

# 品質チェック（テスト・リント・ビルド）
/dev-check

# OpenAPI仕様生成
/openapi生成
```

### 新機能開発時

```bash
# 影響範囲分析
/openspec-impact

# 実装骨組み生成
/openspec-implement

# 実装カバレッジ確認
/openspec-verify

# 完全レポート生成
/openspec-report
```

## 🔄 標準ワークフロー

### 新機能追加（5ステップ）

```bash
# 1. 仕様作成
vim openspec/changes/$(date +%Y-%m-%d)-feature-name/feature.md

# 2. 影響分析
/openspec-impact

# 3. レビュー・承認
gh pr create
# レビュー後
mv openspec/changes/.../feature.md openspec/specs/features/

# 4. 実装
/openspec-implement
# ... コーディング ...
/openapi生成
cd frontend && npm run generate:types

# 5. 検証・完了
/openspec-verify
/dev-check
git commit && git push
```

### API変更（3ステップ）

```bash
# 1. バックエンド実装変更
vim backend/app/api/v1/[endpoint].py

# 2. OpenAPI再生成
cd backend && python scripts/generate_openapi.py
git diff openapi.json  # 差分確認

# 3. フロントエンド型更新
cd frontend && npm run generate:types
git diff src/types/api.generated.ts  # 差分確認
```

### Pull Request前の確認

```bash
# 完全チェック（この3つでOK）
/openspec-verify  # 仕様カバレッジ
/dev-check        # 品質チェック
/openapi生成      # API仕様更新

# PRに含める情報
git diff openapi.json
git diff frontend/src/types/api.generated.ts
```

## 📂 ファイル配置ルール

### 仕様ファイル

```bash
# 変更提案（レビュー前）
openspec/changes/YYYY-MM-DD-feature-name/
  └── feature-name.md

# 承認済み仕様（実装の基準）
openspec/specs/
  ├── features/           # 機能仕様
  │   ├── assessment-crud.md
  │   ├── lead-management.md
  │   └── microsoft-teams-integration.md
  ├── api/                # API設計
  │   └── endpoints-overview.md
  └── auth/               # 認証・認可
      ├── authentication.md
      └── multi-tenant.md

# 完了したもの（アーカイブ）
openspec/archive/
  └── YYYY-MM-DD-feature-name.md
```

### 実装ファイル

```bash
# バックエンド
backend/
  ├── app/
  │   ├── api/v1/         # APIエンドポイント
  │   ├── models/         # データモデル
  │   ├── schemas/        # Pydanticスキーマ
  │   └── services/       # ビジネスロジック
  └── tests/

# フロントエンド
frontend/
  └── src/
      ├── types/
      │   └── api.generated.ts  # 自動生成（編集禁止）
      ├── features/
      └── components/

# API仕様（自動生成）
openapi.json              # 編集禁止
```

## 🎯 仕様テンプレート

### 最小限の仕様

```markdown
# Feature: [Feature Name]

## Overview
機能の概要を1-2文で

## User Stories
- [Role]として、[Action]したい

## Requirements
- 要件1
- 要件2

## Testing Strategy
- どうテストするか
```

### 完全な仕様

```markdown
# Feature: [Feature Name]

## Overview
詳細な概要

## User Stories
- [Role]として、[Action]したい、so that [Benefit]

## Requirements
### Functional Requirements
- 機能要件

### Non-Functional Requirements
- パフォーマンス
- セキュリティ
- マルチテナント考慮

## API Design (概要)
- Endpoint: [Method] [Path]
- Purpose: [説明]

## Data Model (概要)
- Entity: fields

## UI/UX Design
- Component: 説明
- User Flow: 流れ

## Business Logic
具体的なロジック

## Testing Strategy
- Unit Tests: 何をテストするか
- Integration Tests: 何をテストするか
- E2E Tests: どのフローをテストするか

## Related Specs
- [関連仕様へのリンク]

## Implementation Notes
実装時の注意点
```

## ⚡ よく使うGitコマンド

```bash
# 仕様の変更を確認
git diff openspec/

# 仕様の履歴を確認
git log --oneline -- openspec/specs/features/feature.md

# 仕様と実装を同時にコミット
git add openspec/ backend/ frontend/
git commit -m "feat: Implement [feature] based on spec"

# 仕様だけ先にコミット
git add openspec/specs/
git commit -m "spec: Approve [feature] specification"
```

## 🔍 よく使う検索コマンド

```bash
# 仕様を検索
grep -r "keyword" openspec/specs/

# 特定機能の仕様を探す
find openspec/specs -name "*assessment*"

# 仕様のカテゴリを確認
ls openspec/specs/

# 最近更新された仕様
ls -lt openspec/specs/**/*.md | head -10

# ペンディング中の変更
ls openspec/changes/

# 古い変更提案（30日以上）
find openspec/changes -name "*.md" -mtime +30
```

## 🎨 Droidカスタマイズ例

### プロジェクト固有のチェック

```yaml
# .factory/droids/my-custom-droid.yml
name: my-custom-check
description: プロジェクト固有の検証

activation:
  commands:
    - "/my-check"

workflows:
  custom_check:
    steps:
      - name: "Custom Validation"
        command: |
          echo "カスタムチェック実行中..."
          # 独自の検証ロジック
```

## 📊 レポート生成

```bash
# 週次レポート
/openspec-report > reports/$(date +%Y-%m-%d)-weekly.md

# カスタムレポート
cat << 'EOF' > reports/custom-report.md
# Custom Report

## Specs
$(find openspec/specs -name "*.md" | wc -l) total

## Implementation
$(find backend/app/api -name "*.py" ! -name "__init__.py" | wc -l) API endpoints
$(find backend/app/models -name "*.py" ! -name "__init__.py" | wc -l) models

## Coverage
$(echo "scale=2; $(find backend/app/api -name "*.py" ! -name "__init__.py" | wc -l) / $(find openspec/specs/api -name "*.md" | wc -l) * 100" | bc)%
EOF
```

## 🚨 トラブルシューティング

### 問題: 仕様と実装が乖離

```bash
# 確認
/openspec-verify

# OpenAPI再生成
cd backend && python scripts/generate_openapi.py

# 型再生成
cd frontend && npm run generate:types

# 再確認
/openspec-verify
```

### 問題: Droidコマンドが動かない

```bash
# Droid設定を確認
ls .factory/droids/

# Droidを再読み込み
# Factory Droidを再起動

# ログを確認
cat .factory/logs/*.log
```

### 問題: 型生成エラー

```bash
# OpenAPI仕様を確認
cat openapi.json | jq

# 仕様を検証
cd frontend && npm run validate:openapi

# キャッシュクリア
rm -rf frontend/node_modules/.cache
cd frontend && npm run generate:types
```

## 🎓 学習パス

### Day 1: 基本理解
- [ ] README.md を読む
- [ ] openspec/README.md を読む
- [ ] 既存の仕様を読む（openspec/specs/）

### Day 2: 実践
- [ ] /openspec-status を実行
- [ ] /spec-check を実行
- [ ] 小さな仕様を1つ書いてみる

### Day 3: ワークフロー
- [ ] 変更提案を作成（openspec/changes/）
- [ ] Pull Requestを作成
- [ ] レビューを受ける

### Week 2: 自動化
- [ ] /openspec-impact を使う
- [ ] /openapi生成 を使う
- [ ] 型生成を理解する

### Week 3: 習慣化
- [ ] 毎朝 /openspec-status
- [ ] PR前に /openspec-verify
- [ ] 完了後にアーカイブ

## 💡 Tips & Tricks

### Tip 1: 仕様はシンプルに
```markdown
# ❌ 悪い例: 技術的すぎる
FastAPIのDependency Injectionを使い、
async defでエンドポイントを実装する

# ✅ 良い例: 機能に焦点
ユーザーがリードを作成できる
```

### Tip 2: User Storiesを活用
```markdown
# ユーザーの視点で書く
- 営業担当者として、ホットリードを優先的に確認したい
- マーケティング担当者として、診断完了率を可視化したい
```

### Tip 3: 関連仕様にリンク
```markdown
## Related Specs
- [Lead Management](./lead-management.md)
- [Authentication](../auth/authentication.md)
```

### Tip 4: テスト戦略を明記
```markdown
## Testing Strategy
- Unit: スコアリングロジックの単体テスト
- Integration: APIエンドポイントのテスト
- E2E: リード作成→スコアリング→表示
```

### Tip 5: 実装ノートを残す
```markdown
## Implementation Notes
- テナントIDによるデータ分離を必ず実施
- スコアは0-100に正規化
- リトライロジックは3回まで
```

## 🎯 成功のポイント

1. **Spec First**: コードより先に仕様
2. **Droid活用**: 手動チェックは最小限に
3. **定期確認**: /openspec-status を習慣化
4. **自動化**: CI/CDに統合
5. **継続改善**: 定期的にワークフロー見直し

---

**困ったら**:
- [OPENSPEC_BEST_PRACTICES.md](./OPENSPEC_BEST_PRACTICES.md) - 詳細ガイド
- [OPENSPEC_DROID_STRATEGY.md](./OPENSPEC_DROID_STRATEGY.md) - 活用戦略
- [openspec/README.md](../openspec/README.md) - 基本概念

**すぐ始める**:
```bash
/openspec-status    # 今の状態を確認
/spec-check         # 同期状態を確認
```

Happy Spec-Driven Development! 🚀
