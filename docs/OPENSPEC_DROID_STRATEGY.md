# OpenSpec × Droid 最大活用戦略

DiagnoLeadsでOpenSpecとFactory Droidを組み合わせて、仕様駆動開発を最大限に効率化する方法を解説します。

## 🎯 戦略の全体像

```
┌─────────────────────────────────────────────────────────┐
│                  OpenSpec Ecosystem                     │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────┐│
│  │  OpenSpec    │───▶│   Factory    │───▶│  実装    ││
│  │  (機能仕様)   │    │    Droid     │    │          ││
│  └──────────────┘    └──────────────┘    └──────────┘│
│         │                    │                  │      │
│         ▼                    ▼                  ▼      │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────┐│
│  │  OpenAPI     │    │   自動検証    │    │  テスト  ││
│  │  (API仕様)    │    │   レポート   │    │          ││
│  └──────────────┘    └──────────────┘    └──────────┘│
│                                                         │
└─────────────────────────────────────────────────────────┘
```

## 📊 活用レベル別の戦略

### Level 1: 基本活用（今すぐ始められる）

**目的**: 仕様管理の基盤を整える

**アクション**:
1. **定期的な仕様確認**
   ```bash
   # 毎朝のルーチン
   /openspec-status
   ```
   - 承認待ちの仕様を確認
   - 実装状況を把握

2. **変更提案の習慣化**
   ```bash
   # 新機能を考えたら、まず仕様を書く
   vim openspec/changes/$(date +%Y-%m-%d)-feature/feature.md
   ```

3. **実装前の影響分析**
   ```bash
   /openspec-impact
   ```
   - どこに影響するか事前に把握
   - リスクを最小化

**期待効果**:
- 仕様の可視化
- チーム内での認識共有
- 実装の手戻り減少

### Level 2: 中級活用（チーム全体で統一）

**目的**: 仕様駆動開発の自動化

**アクション**:
1. **Pull Request時の自動チェック**
   ```yaml
   # .github/workflows/pr-check.yml
   - name: Spec Validation
     run: |
       /spec-check
       /openspec-verify
       /dev-check
   ```

2. **実装カバレッジの可視化**
   ```bash
   # 週次レポート
   /openspec-report > reports/openspec-$(date +%Y-%m-%d).md
   git add reports/
   git commit -m "docs: Weekly OpenSpec report"
   ```

3. **型生成の自動化**
   ```bash
   # コミット前フック
   # .git/hooks/pre-commit
   cd backend && python scripts/generate_openapi.py
   cd frontend && npm run generate:types
   ```

**期待効果**:
- 仕様と実装の自動同期
- レビュー効率の向上
- バグの早期発見

### Level 3: 上級活用（完全自動化）

**目的**: AIを活用した仕様駆動開発

**アクション**:
1. **仕様から実装の自動生成**
   ```bash
   # 承認された仕様から骨組みを生成
   /openspec-implement
   
   # Droidが以下を自動生成:
   # - データモデル (backend/app/models/)
   # - APIエンドポイント (backend/app/api/)
   # - Pydanticスキーマ (backend/app/schemas/)
   # - Reactコンポーネント (frontend/src/components/)
   ```

2. **仕様の自動補完**
   ```bash
   # 不完全な仕様をAIが補完
   /openspec-enhance openspec/changes/draft-feature.md
   
   # Droidが追加:
   # - 詳細なUser Stories
   # - エッジケースの考慮
   # - テスト戦略の提案
   # - 関連仕様へのリンク
   ```

3. **実装からの仕様逆生成**
   ```bash
   # 既存コードから仕様を生成
   /openspec-extract backend/app/api/v1/leads.py
   
   # 生成される仕様:
   # - APIエンドポイントの説明
   # - ビジネスロジックの文書化
   # - データモデルの説明
   ```

**期待効果**:
- 仕様作成時間の50%削減
- 実装の一貫性向上
- ドキュメントの自動更新

## 🤖 Droid活用パターン

### パターン1: 日常開発フロー

```bash
# 朝（開発開始時）
/openspec-status        # 今日のタスク確認
/spec-check            # 仕様と実装の同期確認

# 新機能開発時
# 1. 仕様作成
vim openspec/changes/new-feature.md

# 2. 影響分析
/openspec-impact

# 3. チームレビュー（GitHub PR）

# 4. 承認後、実装開始
/openspec-implement    # 骨組み生成
# ... 実装 ...

# 5. 実装中の確認
/openspec-verify       # カバレッジ確認

# 6. 実装完了
/dev-check            # 品質チェック
/openapi生成          # API仕様更新

# 夕方（1日の終わり）
git commit -m "feat: Implement [feature]"
git push
```

### パターン2: Pull Requestフロー

```bash
# PR作成前
/openspec-verify       # 実装カバレッジ確認
/dev-check            # テスト・リント・ビルド
/openapi生成          # OpenAPI仕様更新

# PR作成
gh pr create --title "feat: [Feature]" \
             --body "$(cat << EOF
## Changes
- Implemented [feature] based on openspec/specs/features/[feature].md

## Verification
- [x] Spec coverage: /openspec-verify
- [x] Quality check: /dev-check
- [x] OpenAPI updated: /openapi生成

## Related
- Spec: openspec/specs/features/[feature].md
- API changes: see openapi.json diff
EOF
)"

# PR上でDroidが自動実行:
# - /spec-check
# - /openspec-verify
# - /dev-check
```

### パターン3: リファクタリング時

```bash
# 1. 影響範囲の確認
/openspec-impact

# 2. 関連する仕様を特定
grep -r "[keyword]" openspec/specs/

# 3. リファクタリング実行
# ... コード変更 ...

# 4. 仕様の更新が必要か確認
/openspec-verify

# 5. 必要なら仕様も更新
vim openspec/specs/features/affected-feature.md

# 6. 検証
/dev-check
/openspec-verify
```

## 🎯 具体的なユースケース

### ユースケース1: Microsoft Teams統合の追加

**背景**: Microsoft Teams通知機能を追加したい

**OpenSpec × Droid活用**:

```bash
# Step 1: 仕様作成
cat > openspec/changes/2025-11-11-teams-integration/teams-integration.md << 'EOF'
# Feature: Microsoft Teams Integration

## Overview
診断完了時にMicrosoft Teamsに通知を送信する機能。

## User Stories
- 営業担当者として、ホットリードが発生したらTeamsで即座に通知を受けたい
- マーケティング担当者として、診断完了数をTeamsで日次レポートしたい

## Requirements
### Functional Requirements
- Teams Incoming Webhook連携
- リード獲得時のリアルタイム通知
- Adaptive Cardsによるリッチな通知UI
- 通知のオン/オフ設定

### API Design
POST /api/v1/tenants/{tenant_id}/integrations/teams/test
POST /api/v1/tenants/{tenant_id}/integrations/teams/send

### Data Model
TeamsIntegration:
  - tenant_id: UUID
  - webhook_url: String (encrypted)
  - enabled: Boolean
  - notification_settings: JSONB

## Testing Strategy
- Webhook送信のUnit Test
- リトライロジックのTest
- E2E: リード獲得→Teams通知

EOF

# Step 2: 影響分析
/openspec-impact
# Output:
# - Affected: backend/app/integrations/
# - New files: backend/app/integrations/teams_integration.py
# - Related specs: integrations.md

# Step 3: 仕様レビュー・承認
gh pr create --title "Proposal: Teams Integration"
# ... レビュー ...
mv openspec/changes/2025-11-11-teams-integration/teams-integration.md \
   openspec/specs/features/microsoft-teams-integration.md

# Step 4: 実装の骨組み生成
/openspec-implement
# Droidが提案:
# - backend/app/models/teams_integration.py
# - backend/app/services/teams_service.py
# - backend/app/api/v1/integrations/teams.py
# - frontend/src/features/integrations/components/TeamsIntegrationForm.tsx

# Step 5: 実装
# ... コーディング ...

# Step 6: OpenAPI更新
cd backend
python scripts/generate_openapi.py

# Step 7: フロントエンド型生成
cd frontend
npm run generate:types

# Step 8: 検証
/openspec-verify
# Output:
# ✅ Feature specification: microsoft-teams-integration.md
# ✅ Backend implementation: teams_service.py, teams.py
# ✅ Frontend implementation: TeamsIntegrationForm.tsx
# ✅ OpenAPI updated: teams endpoints added
# ✅ Tests exist: test_teams_integration.py

/dev-check
# ✅ All tests passed
# ✅ Coverage: 85%

# Step 9: 完了、アーカイブ
mv openspec/specs/features/microsoft-teams-integration.md \
   openspec/archive/2025-11-20-microsoft-teams-integration.md
```

### ユースケース2: API仕様変更への対応

**背景**: リードAPIにフィルタリング機能を追加

```bash
# Step 1: 既存の仕様を確認
cat openspec/specs/api/endpoints-overview.md

# Step 2: 仕様を更新
vim openspec/specs/api/endpoints-overview.md
# 追加:
# GET /api/v1/tenants/{id}/leads?status=hot&score_min=80

# Step 3: 影響分析
/openspec-impact
# Output:
# - OpenAPI spec will need update
# - Affected endpoint: backend/app/api/v1/leads.py
# - Frontend types will change

# Step 4: バックエンド実装
vim backend/app/api/v1/leads.py
# クエリパラメータを追加

# Step 5: OpenAPI再生成
cd backend
python scripts/generate_openapi.py

# Diff確認
git diff openapi.json
# 差分:
# + "parameters": [
# +   {"name": "status", "in": "query", ...},
# +   {"name": "score_min", "in": "query", ...}
# + ]

# Step 6: フロントエンド型再生成
cd frontend
npm run generate:types

# Diff確認
git diff src/types/api.generated.ts
# 新しい型定義が追加されている

# Step 7: フロントエンド実装
vim frontend/src/features/leads/services/leadService.ts
# 型安全なAPIコールを実装

# Step 8: 検証
/dev-check
/openspec-verify
```

### ユースケース3: レガシーコードのドキュメント化

**背景**: ドキュメントのない既存機能を仕様化

```bash
# Step 1: 既存コードから仕様を抽出
/openspec-extract backend/app/api/v1/assessments.py

# Droidが生成:
# openspec/specs/features/assessment-crud.md
# - API endpoints discovered
# - Data models identified
# - Business logic extracted

# Step 2: 生成された仕様をレビュー
vim openspec/specs/features/assessment-crud.md

# Step 3: 不足情報を追加
# - User Stories
# - Non-Functional Requirements
# - Testing Strategy

# Step 4: 検証
/openspec-verify
# ✅ Specification exists
# ✅ Implementation matches spec
```

## 📈 効果測定

### KPI設定

| KPI | 目標値 | 測定方法 |
|-----|--------|----------|
| 仕様カバレッジ | 80%+ | `/openspec-verify` |
| 仕様鮮度（乖離日数） | 7日以内 | Git履歴比較 |
| 変更提案スループット | 3日以内 | PR作成→マージ |
| 実装バグ率 | 前月比20%減 | Issue追跡 |
| 開発速度 | 前月比30%向上 | Velocity測定 |

### 効果の可視化

```bash
# 週次レポート生成
/openspec-report > reports/weekly-$(date +%Y-%m-%d).md

# 月次ダッシュボード
cat << 'EOF' > reports/monthly-dashboard.md
# OpenSpec Monthly Dashboard

## 仕様統計
- 承認済み仕様: 50 (+5 from last month)
- 実装済み機能: 45 (90% coverage)
- ペンディング変更: 3

## 品質指標
- テストカバレッジ: 85%
- バグ発生率: 0.5% (前月比 -20%)
- 実装スピード: 8 features/month (+30%)

## トップコントリビューター
1. Developer A: 10 specs
2. Developer B: 8 specs
3. Developer C: 6 specs
EOF
```

## 🎓 チーム展開戦略

### Phase 1: パイロット導入（1-2週間）

**対象**: コアチーム（2-3人）

**アクション**:
1. OpenSpec基本構造のセットアップ
2. 1つの機能で完全フローを試す
3. Droidコマンドの習熟
4. 課題の洗い出し

### Phase 2: チーム拡大（2-4週間）

**対象**: 全開発チーム

**アクション**:
1. オンボーディングセッション
2. ペアレビューで仕様作成を学習
3. 週次のSpec Review Meeting
4. ベストプラクティスの共有

### Phase 3: 組織展開（1-2ヶ月）

**対象**: PM、デザイナー含む全体

**アクション**:
1. 非エンジニアも仕様作成に参加
2. 仕様テンプレートのカスタマイズ
3. 自動化の拡張
4. 継続的改善プロセスの確立

## 🔧 カスタマイズ例

### カスタムDroidの作成

```yaml
# .factory/droids/custom-openspec.yml
name: custom-openspec-analyzer
description: プロジェクト固有のOpenSpec分析Droid

workflows:
  analyze_multi_tenant:
    description: マルチテナント対応の仕様チェック
    steps:
      - name: "Check Tenant Isolation"
        command: |
          # 仕様にテナント分離の記述があるか確認
          grep -r "tenant" openspec/specs/ | \
          grep -i "isolation\|security\|separation"
        on_error: warn
```

### プロジェクト固有の検証ルール

```bash
# .factory/workflows/custom-spec-validation.sh
#!/bin/bash

echo "カスタム仕様検証"

# 1. セキュリティ要件の確認
if ! grep -q "Security" openspec/specs/features/*.md; then
  echo "⚠️  WARNING: Some features lack security requirements"
fi

# 2. マルチテナント考慮の確認
for spec in openspec/specs/features/*.md; do
  if ! grep -qi "tenant" "$spec"; then
    echo "⚠️  WARNING: $spec may not consider multi-tenancy"
  fi
done

# 3. テスト戦略の確認
for spec in openspec/specs/features/*.md; do
  if ! grep -q "Testing Strategy" "$spec"; then
    echo "⚠️  WARNING: $spec lacks testing strategy"
  fi
done
```

## 📚 学習リソース

### 社内ドキュメント
- [OPENSPEC_BEST_PRACTICES.md](./OPENSPEC_BEST_PRACTICES.md)
- [openspec/README.md](../openspec/README.md)
- [SPEC_STRATEGY.md](../SPEC_STRATEGY.md)

### 外部リソース
- [OpenSpec公式](https://github.com/Fission-AI/OpenSpec)
- [Specification by Example](https://gojko.net/books/specification-by-example/)
- [Living Documentation](https://leanpub.com/livingdocumentation)

## 🎯 まとめ: 最大活用のポイント

1. **仕様ファースト**: コードより先に仕様を書く習慣
2. **Droid活用**: 手動チェックをDroidに任せる
3. **自動化**: CI/CDに統合して継続的に検証
4. **可視化**: レポートで現状を常に把握
5. **改善**: 定期的にワークフローを見直す

**最も重要なこと**: 
OpenSpecは「ドキュメント」ではなく「開発の中心」として扱う。
実装 → ドキュメント化 ではなく、仕様 → 実装 の順序を徹底する。

---

**次のステップ**:
1. `/openspec-status` で現状確認
2. 小さな機能で完全フローを試す
3. チームでレトロスペクティブ
4. 継続的改善 🚀
