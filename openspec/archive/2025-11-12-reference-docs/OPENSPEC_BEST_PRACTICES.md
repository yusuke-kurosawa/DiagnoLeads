# OpenSpec活用のベストプラクティス - DiagnoLeads

このドキュメントは、DiagnoLeadsプロジェクトにおけるOpenSpecの効果的な活用方法をまとめています。

## 🎯 OpenSpec活用の全体像

DiagnoLeadsでは**2つの仕様システム**を併用しています：

### 1. **OpenSpec** (Human-Readable)
- **対象**: 機能仕様、ビジネスロジック、UI/UX設計
- **形式**: Markdown
- **読者**: 開発者、プロダクトマネージャー、ステークホルダー
- **場所**: `openspec/specs/`, `openspec/changes/`, `openspec/archive/`

### 2. **OpenAPI** (Machine-Readable)
- **対象**: APIエンドポイント、リクエスト/レスポンス型
- **形式**: JSON
- **読者**: 型生成ツール、APIクライアント、自動テスト
- **場所**: `openapi.json`

**連携フロー**:
```
OpenSpec (機能仕様)
    ↓
  実装設計
    ↓
コード実装 → OpenAPI生成 → 型生成
    ↓             ↓
  テスト      フロントエンド実装
```

## 📋 OpenSpecワークフローの完全ガイド

### Phase 1: Proposal（提案）

**When**: 新機能、機能変更、アーキテクチャ変更を検討する時

**How**:
```bash
# 1. 変更提案ファイルを作成
mkdir -p openspec/changes/$(date +%Y-%m-%d)-feature-name
vim openspec/changes/$(date +%Y-%m-%d)-feature-name/feature-name.md

# 2. 仕様テンプレートに従って記述
# - Overview: 機能の概要
# - User Stories: ユーザーストーリー
# - Requirements: 機能要件・非機能要件
# - API Design: API設計の概要
# - Data Model: データモデルの概要
# - UI/UX: UI/UX設計
# - Business Logic: ビジネスロジック
# - Testing Strategy: テスト戦略

# 3. Pull Requestを作成
git checkout -b feature/feature-name
git add openspec/changes/
git commit -m "proposal: Add [feature name] specification"
git push origin feature/feature-name
gh pr create --title "Proposal: [Feature Name]" --label "spec-proposal"
```

**Template Example**:
```markdown
# Feature: AI Lead Scoring

## Overview
リードの診断回答から自動的にスコアリングし、ホットリード度を算出する機能。

## User Stories
- 営業担当者として、リードの優先順位を自動判定してほしい
- マーケティング担当者として、どの診断項目がスコアに影響したか知りたい

## Requirements

### Functional Requirements
- 診断回答データからスコアを算出（0-100点）
- スコアリング基準は診断ごとにカスタマイズ可能
- スコアの内訳（どの質問が何点）を表示

### Non-Functional Requirements
- スコア算出は2秒以内に完了
- 診断完了と同時にリアルタイムでスコアリング
- スコアリングロジックはテナント管理者が編集可能

## API Design (概要)

### POST /api/v1/tenants/{tenant_id}/leads/{lead_id}/score
診断回答からスコアを算出

**Request**:
```json
{
  "response_id": "uuid",
  "scoring_rules": {
    "question_weights": {...}
  }
}
```

**Response**:
```json
{
  "lead_id": "uuid",
  "score": 85,
  "breakdown": [
    {"question_id": "uuid", "points": 20, "max": 25},
    ...
  ]
}
```

## Data Model (概要)

### LeadScore
- lead_id: UUID (FK to Lead)
- score: Integer (0-100)
- breakdown: JSONB
- scored_at: DateTime

## UI/UX Design
- リード詳細ページにスコア表示（円グラフ）
- スコア内訳をツールチップで表示
- スコアリング基準編集画面（管理画面）

## Business Logic
1. 診断回答を取得
2. 各質問の回答に重み付けスコアを適用
3. 合計点を算出（0-100に正規化）
4. スコアをLeadScoreテーブルに保存
5. スコアに基づいてリードステータスを更新

## Testing Strategy
- Unit Tests: スコアリングロジックの単体テスト
- Integration Tests: API エンドポイントのテスト
- E2E Tests: 診断完了→スコアリング→表示の流れ

## Related Specs
- [Lead Management](./lead-management.md)
- [Assessment CRUD](./assessment-crud.md)
```

### Phase 2: Review（レビュー）

**When**: Pull Request作成後

**How**:
```bash
# 1. チームメンバーがレビュー
# - 機能要件は十分か
# - ビジネスロジックは明確か
# - 実装可能性はあるか
# - 他の仕様との整合性は保たれているか

# 2. フィードバックを反映
git add openspec/changes/
git commit -m "refine: Update specification based on feedback"
git push

# 3. レビュー承認
# GitHubのApproveを使用
```

**Factory Droidの活用**:
```bash
# 変更影響範囲を確認
/openspec-impact

# 仕様の妥当性をチェック
/spec-check
```

### Phase 3: Approve（承認）

**When**: レビュー完了、実装開始前

**How**:
```bash
# 1. 承認済み仕様ディレクトリに移動
git checkout main
git pull
git checkout feature/feature-name

# 機能仕様の場合
mv openspec/changes/2025-11-10-ai-lead-scoring/ai-lead-scoring.md \
   openspec/specs/features/ai-lead-scoring.md

# API仕様の場合
mv openspec/changes/2025-11-10-lead-scoring-api/lead-scoring-api.md \
   openspec/specs/api/lead-scoring.md

# 2. コミット
git add openspec/
git commit -m "spec: Approve AI lead scoring feature specification"
git push

# 3. PRをマージ
gh pr merge --squash
```

### Phase 4: Implement（実装）

**When**: 仕様承認後

**How**:

#### Step 1: 仕様を確認しながら実装計画を立てる
```bash
# 承認済み仕様を確認
cat openspec/specs/features/ai-lead-scoring.md

# 影響範囲を確認
/openspec-impact

# 実装骨組みのヒントを取得
/openspec-implement
```

#### Step 2: バックエンド実装
```bash
# 1. データモデル作成
vim backend/app/models/lead_score.py

# 2. スキーマ定義
vim backend/app/schemas/lead_score.py

# 3. ビジネスロジック実装
vim backend/app/services/lead_scoring_service.py

# 4. APIエンドポイント実装
vim backend/app/api/v1/lead_score.py

# 5. テスト作成
vim backend/tests/test_lead_scoring.py
```

#### Step 3: OpenAPI仕様を自動生成
```bash
cd backend
source venv/bin/activate
python scripts/generate_openapi.py

# 差分を確認
git diff ../openapi.json
```

#### Step 4: フロントエンド型生成と実装
```bash
cd frontend

# TypeScript型を生成
npm run generate:types

# 差分を確認
git diff src/types/api.generated.ts

# 実装
vim src/features/leads/components/LeadScoreCard.tsx
vim src/features/leads/services/leadScoringService.ts
```

#### Step 5: テスト実行
```bash
# バックエンドテスト
cd backend
pytest tests/test_lead_scoring.py -v

# フロントエンドテスト
cd frontend
npm test -- LeadScoreCard.test.tsx

# 統合テスト
npm run test:e2e
```

#### Step 6: 品質チェック
```bash
# Factory Droidで自動チェック
/dev-check

# 仕様との整合性確認
/openspec-verify
```

### Phase 5: Archive（アーカイブ）

**When**: 実装完了、テスト通過、本番デプロイ後

**How**:
```bash
# 1. 実装完了を確認
git log --oneline | grep "lead-scoring"

# 2. 仕様をアーカイブに移動
mv openspec/specs/features/ai-lead-scoring.md \
   openspec/archive/$(date +%Y-%m-%d)-ai-lead-scoring.md

# 3. アーカイブメタデータを追加
cat << EOF >> openspec/archive/$(date +%Y-%m-%d)-ai-lead-scoring.md

---

## Implementation History

- **Proposed**: 2025-11-10
- **Approved**: 2025-11-15
- **Implemented**: 2025-11-20
- **Deployed**: 2025-11-22
- **Related PRs**: #123, #124, #125
- **Related Commits**: abc123, def456

EOF

# 4. コミット
git add openspec/
git commit -m "archive: AI lead scoring specification (implementation complete)"
git push
```

## 🎯 Droid活用の実践例

### 1. 日常的な仕様チェック

```bash
# 朝の確認ルーチン
/openspec-status     # 仕様の状態を確認
/spec-check          # 仕様と実装の同期確認
```

### 2. 新機能開発時

```bash
# 1. 変更提案を作成
vim openspec/changes/2025-11-11-new-feature/new-feature.md

# 2. 影響範囲を分析
/openspec-impact

# 3. レビュー後、承認
mv openspec/changes/2025-11-11-new-feature/new-feature.md \
   openspec/specs/features/new-feature.md

# 4. 実装開始
/openspec-implement

# 5. 実装中の定期チェック
/openspec-verify

# 6. 実装完了後
/dev-check
/openspec-report
```

### 3. Pull Request時

```bash
# PR作成前に必ず実行
/openspec-verify   # 仕様カバレッジ確認
/dev-check         # 品質チェック
/openapi生成       # OpenAPI仕様の更新

# PRに含める情報
git diff openapi.json  # API変更内容
git diff frontend/src/types/api.generated.ts  # 型変更内容
```

### 4. 定期レポート

```bash
# 週次レポート生成
/openspec-report

# 内容:
# - 承認済み仕様数
# - 実装済み機能数
# - 未実装仕様
# - 実装カバレッジ
```

## 📊 仕様の品質基準

### 良い仕様の特徴

✅ **明確な目的**: なぜこの機能が必要か明記
✅ **具体的なUser Stories**: ユーザーの視点で記述
✅ **詳細な要件**: 機能要件・非機能要件を網羅
✅ **実装可能性**: 技術的に実現可能
✅ **テスト戦略**: どうやって検証するか明記
✅ **関連仕様へのリンク**: 他の仕様との関係を明示

### 避けるべき仕様

❌ **曖昧な表現**: "いい感じに"、"適切に"など
❌ **要件の欠如**: 何をすべきか不明確
❌ **技術的実装の詳細**: コードレベルの記述（それはコメントで）
❌ **古い情報**: 承認後に更新されていない
❌ **孤立した仕様**: 他の仕様との関係が不明

## 🔧 トラブルシューティング

### 問題: 仕様と実装が乖離している

```bash
# 1. 現状を確認
/openspec-verify

# 2. 変更内容を分析
git diff openspec/specs/

# 3. 実装を更新
# または
# 仕様を実装に合わせて更新（後者は慎重に）

# 4. 再検証
/openspec-verify
```

### 問題: 承認されていない変更が多数ある

```bash
# 1. ペンディング中の変更を確認
ls openspec/changes/

# 2. 古い提案を確認
find openspec/changes -name "*.md" -mtime +30

# 3. レビューを促進
# - チームミーティングでレビュー
# - 優先度の高いものから承認

# 4. 不要な提案は削除
rm openspec/changes/old-proposal.md
```

### 問題: OpenSpecとOpenAPIの不整合

```bash
# 1. OpenAPI仕様を再生成
cd backend
python scripts/generate_openapi.py

# 2. 差分を確認
git diff openapi.json

# 3. フロントエンド型を再生成
cd frontend
npm run generate:types

# 4. ビルドして確認
npm run build
```

## 🎓 チーム内でのOpenSpec文化の醸成

### 1. オンボーディングプロセス

新メンバー向けのチェックリスト：
- [ ] OpenSpecとは何か理解する（README.md）
- [ ] ワークフローを理解する（proposal → approve → implement → archive）
- [ ] 既存の仕様を読む（openspec/specs/）
- [ ] 小さな変更提案を作成してみる
- [ ] Factory Droidコマンドを使ってみる（/openspec-status, /spec-check）

### 2. レビュー文化

- **定期的なSpec Review Meeting**: 週次で未承認の変更提案をレビュー
- **Spec Champions**: 各カテゴリ（API、Feature、Auth等）の責任者を決める
- **Feedback Loop**: 実装後に仕様の改善点をフィードバック

### 3. ツールとの統合

```yaml
# .github/workflows/ci.yml に追加
- name: OpenSpec Validation
  run: |
    /spec-check
    /openspec-verify
```

## 📚 参考資料

- [OpenSpec公式ドキュメント](https://github.com/Fission-AI/OpenSpec)
- [OpenAPI Specification](https://spec.openapis.org/oas/v3.1.0)
- [プロジェクト仕様駆動開発ガイド](../SPEC_STRATEGY.md)
- [Factory Droidドキュメント](../.factory/README.md)

## 🎯 成功の指標

OpenSpecが効果的に活用されているかの指標：

1. **仕様カバレッジ**: 全機能の80%以上に仕様が存在
2. **仕様鮮度**: 仕様と実装の乖離が1週間以内に解消
3. **変更提案のスループット**: 提案から承認まで平均3日以内
4. **実装品質**: 仕様ベースの実装でバグ発生率が低下
5. **チーム理解度**: 新メンバーが仕様を見て実装できる

---

**Remember**: 
- OpenSpec（機能仕様）は「何を作るか」を定義
- OpenAPI（API仕様）は「どう動くか」を定義
- 両方を維持して、初めて完全なSpec駆動開発が実現する 🎯
