# Feature Proposal: Analytics Dashboard

**Status**: 🔄 Proposal  
**Created**: 2025-11-10  
**Priority**: High

## Overview

リードと診断アセスメントの分析データを可視化するダッシュボード機能を追加する。テナント管理者とマーケティング担当者が、リードのパフォーマンス、診断の効果、コンバージョンファネルを把握できるようにする。

## User Stories

### Story 1: リード分析
**As a** マーケティング担当者  
**I want to** リードのステータス分布を可視化したい  
**So that** マーケティング施策の効果を測定できる

### Story 2: スコア分析
**As a** 営業マネージャー  
**I want to** リードスコアの分布を確認したい  
**So that** 営業リソースの配分を最適化できる

### Story 3: 診断パフォーマンス
**As a** テナント管理者  
**I want to** 診断アセスメントの利用状況を把握したい  
**So that** コンテンツの改善ポイントを見つけられる

### Story 4: トレンド分析
**As a** マーケティング担当者  
**I want to** 時系列でリード数の推移を見たい  
**So that** 成長トレンドを把握できる

## Requirements

### Functional Requirements

#### 1. リード分析
- リード総数の表示
- ステータス別の分布（円グラフ）
- スコア別の分布（Hot/Warm/Cold）
- 新規リード数（日次/週次/月次）
- コンバージョン率（新規 → 成約）

#### 2. 診断分析
- 診断総数の表示
- ステータス別の分布（公開/下書き/アーカイブ）
- AI生成 vs 手動作成の比率
- 最も人気の診断（上位5件）

#### 3. 時系列分析
- リード登録数の推移（過去30日間）
- 診断作成数の推移
- スコア平均の推移

#### 4. 比較分析
- 前月比・前年比の表示
- 増減率の可視化
- トレンド矢印表示

#### 5. エクスポート機能
- CSVエクスポート
- PDFレポート生成（将来）

#### 6. マルチテナント対応
- テナントごとに完全分離
- テナント間のデータアクセス禁止

### Non-Functional Requirements

- **パフォーマンス**: 
  - ダッシュボード読み込み: 500ms以内
  - 集計クエリ: 1秒以内
  - キャッシング利用（Redis）

- **セキュリティ**:
  - すべてのクエリでtenant_idフィルタリング必須
  - 認証必須

- **可用性**: 99.9%以上

## Data Model

### AnalyticsSnapshot Entity (将来的なキャッシング用)

```python
class AnalyticsSnapshot(Base):
    """
    Pre-computed analytics data for performance optimization
    """
    
    __tablename__ = "analytics_snapshots"
    
    # Primary Key
    id: UUID
    tenant_id: UUID              # CASCADE DELETE
    
    # Snapshot Type
    snapshot_type: str           # daily, weekly, monthly
    snapshot_date: Date          # The date this snapshot represents
    
    # Lead Metrics
    total_leads: int
    new_leads: int
    contacted_leads: int
    qualified_leads: int
    converted_leads: int
    disqualified_leads: int
    hot_leads: int               # score >= 61
    warm_leads: int              # score 31-60
    cold_leads: int              # score 0-30
    average_score: float
    
    # Assessment Metrics
    total_assessments: int
    published_assessments: int
    draft_assessments: int
    archived_assessments: int
    ai_generated_count: int
    manual_created_count: int
    
    # Conversion Metrics
    conversion_rate: float       # (converted / total) * 100
    
    # Metadata
    created_at: DateTime
    updated_at: DateTime
    
    # Indexes
    Index('idx_analytics_tenant_type_date', tenant_id, snapshot_type, snapshot_date)
```

**Note**: 初期実装ではリアルタイム集計を使用。パフォーマンスが問題になったら、このテーブルでキャッシングを実装。

## API Design (概要)

### Endpoints

```
GET /api/v1/tenants/{tenant_id}/analytics/overview
GET /api/v1/tenants/{tenant_id}/analytics/leads
GET /api/v1/tenants/{tenant_id}/analytics/assessments
GET /api/v1/tenants/{tenant_id}/analytics/trends?period=30d
GET /api/v1/tenants/{tenant_id}/analytics/export?format=csv
```

### Request/Response Examples

#### Get Overview Analytics

**Request:**
```
GET /api/v1/tenants/{tenant_id}/analytics/overview
Authorization: Bearer {token}
```

**Response (200):**
```json
{
  "tenant_id": "uuid",
  "period": "all_time",
  "leads": {
    "total": 150,
    "new": 30,
    "contacted": 50,
    "qualified": 40,
    "converted": 20,
    "disqualified": 10,
    "hot_leads": 25,
    "warm_leads": 60,
    "cold_leads": 65,
    "average_score": 45.5,
    "conversion_rate": 13.3
  },
  "assessments": {
    "total": 15,
    "published": 10,
    "draft": 3,
    "archived": 2,
    "ai_generated": 8,
    "manual_created": 7
  },
  "generated_at": "2025-01-10T10:00:00Z"
}
```

#### Get Lead Trends

**Request:**
```
GET /api/v1/tenants/{tenant_id}/analytics/trends?period=30d&metric=leads
```

**Response (200):**
```json
{
  "period": "30d",
  "metric": "leads",
  "data_points": [
    {"date": "2025-01-01", "value": 5},
    {"date": "2025-01-02", "value": 7},
    {"date": "2025-01-03", "value": 3},
    ...
  ],
  "summary": {
    "total": 150,
    "average_per_day": 5.0,
    "trend": "increasing",
    "growth_rate": 15.5
  }
}
```

### Security

すべてのエンドポイントで：
- ✅ JWT認証必須
- ✅ テナント権限確認
- ✅ 不一致の場合は403 Forbidden

## UI/UX Design

### Components

#### 1. AnalyticsDashboard (メインページ)
- **レイアウト**: グリッドレイアウト（2-3列）
- **セクション**:
  - Overview Cards（総数、成約率）
  - Lead Status Chart（円グラフ）
  - Lead Score Distribution（棒グラフ）
  - Trend Chart（線グラフ）
  - Top Assessments（リスト）

#### 2. MetricCard
- 数値表示（大きく）
- ラベル（小さく）
- 前期比（増減矢印）
- 色分け（良い=緑、悪い=赤、中立=青）

#### 3. StatusPieChart
- ステータス別の円グラフ
- 凡例表示
- パーセンテージ表示
- ホバーで詳細

#### 4. TrendLineChart
- 時系列データの線グラフ
- 期間選択（7日、30日、90日）
- ツールチップ
- グリッド表示

#### 5. TopAssessmentsList
- 人気順にアセスメントを表示
- クリック数、完了率を表示
- 各アセスメントへのリンク

### User Flow

```
[Dashboard] → "Analytics" リンク
    ↓
[AnalyticsDashboard]
    ├─ Overview Cards（一目で状況把握）
    ├─ Lead Status Chart（ステータス分布）
    ├─ Score Distribution（Hot/Warm/Cold）
    ├─ Trend Chart（時系列推移）
    └─ Top Assessments（人気診断）
    
    ↓ "Export CSV" ボタン
[CSV Download]
```

### Responsive Design

- **Desktop**: 3列グリッド、グラフ横並び
- **Tablet**: 2列グリッド
- **Mobile**: 1列スタック、スクロール

## Business Logic

### 1. リード分析集計

```python
def get_lead_analytics(tenant_id: UUID):
    # 1. テナント権限確認
    # 2. 全リードを取得（tenant_idフィルタ）
    leads = db.query(Lead).filter(Lead.tenant_id == tenant_id).all()
    
    # 3. ステータス別集計
    status_counts = {
        "new": count_by_status(leads, "new"),
        "contacted": count_by_status(leads, "contacted"),
        "qualified": count_by_status(leads, "qualified"),
        "converted": count_by_status(leads, "converted"),
        "disqualified": count_by_status(leads, "disqualified"),
    }
    
    # 4. スコア別集計
    score_distribution = {
        "hot": count_by_score_range(leads, 61, 100),
        "warm": count_by_score_range(leads, 31, 60),
        "cold": count_by_score_range(leads, 0, 30),
    }
    
    # 5. 平均スコア計算
    average_score = sum(lead.score for lead in leads) / len(leads)
    
    # 6. コンバージョン率
    conversion_rate = (status_counts["converted"] / len(leads)) * 100
    
    return {
        "total": len(leads),
        "status_counts": status_counts,
        "score_distribution": score_distribution,
        "average_score": average_score,
        "conversion_rate": conversion_rate,
    }
```

### 2. トレンド分析

```python
def get_trend_data(tenant_id: UUID, period: str):
    # 1. 期間を計算（30d, 90d）
    end_date = datetime.now()
    start_date = end_date - timedelta(days=parse_period(period))
    
    # 2. 期間内のリードを取得
    leads = db.query(Lead).filter(
        and_(
            Lead.tenant_id == tenant_id,
            Lead.created_at >= start_date,
            Lead.created_at <= end_date,
        )
    ).all()
    
    # 3. 日付別に集計
    daily_counts = group_by_date(leads)
    
    # 4. トレンド計算（増加/減少/安定）
    trend = calculate_trend(daily_counts)
    
    return {
        "data_points": daily_counts,
        "trend": trend,
        "growth_rate": calculate_growth_rate(daily_counts),
    }
```

### 3. マルチテナント分離

**すべての集計クエリで必須:**

```python
# 必ずtenant_idでフィルタ
query = query.filter(Model.tenant_id == tenant_id)

# クロステナントアクセスチェック
if current_user.tenant_id != tenant_id:
    raise HTTPException(403, "Access forbidden")
```

## Testing Strategy

### Unit Tests (Backend)
- `test_get_overview_analytics` - 全体統計取得
- `test_get_lead_analytics` - リード分析
- `test_get_assessment_analytics` - 診断分析
- `test_get_trends_30d` - 30日間トレンド
- `test_get_trends_7d` - 7日間トレンド
- `test_empty_analytics` - データなしの場合
- `test_cross_tenant_analytics_denied` - **クロステナントアクセス拒否**
- `test_analytics_performance` - パフォーマンステスト（1秒以内）

### Frontend Tests
- AnalyticsDashboard レンダリング
- MetricCard 表示
- チャートコンポーネント
- 期間選択

## Implementation Plan

### Phase 1: Backend (2-3 hours)
1. Service作成 (`analytics_service.py`)
2. API endpoints作成 (`analytics.py`)
3. Tests作成 (`test_analytics.py`)

**Note**: Modelは不要（既存データから集計）

### Phase 2: OpenAPI & Types (30 min)
1. OpenAPI仕様生成
2. TypeScript型生成

### Phase 3: Frontend (3-4 hours)
1. Chart library選定・インストール（Recharts推奨）
2. Components作成:
   - `AnalyticsDashboard.tsx`
   - `MetricCard.tsx`
   - `StatusPieChart.tsx`
   - `TrendLineChart.tsx`
   - `TopAssessmentsList.tsx`
3. Pages作成:
   - `AnalyticsPage.tsx`
4. Service作成:
   - `analyticsService.ts`

### Phase 4: Testing & Verification (1 hour)
1. Backend tests実行・修正
2. Frontend build・lint
3. 手動テスト

## Technical Considerations

### Performance Optimization

**初期実装**: リアルタイム集計
```sql
SELECT status, COUNT(*) FROM leads WHERE tenant_id = ? GROUP BY status
```

**将来的な最適化**:
1. **集計テーブル**（`analytics_snapshots`）
2. **バックグラウンドジョブ**（1日1回更新）
3. **Redisキャッシング**（TTL: 1時間）

### Chart Library Selection

**推奨: Recharts**
- React用のシンプルなチャートライブラリ
- TypeScript対応
- レスポンシブデザイン
- 軽量（依存関係少ない）

**Alternative: Chart.js**
- より高機能
- ファイルサイズ大きい

### Data Aggregation Strategy

```python
# 効率的な集計クエリ
def get_status_counts(tenant_id: UUID):
    result = db.query(
        Lead.status,
        func.count(Lead.id).label('count')
    ).filter(
        Lead.tenant_id == tenant_id
    ).group_by(
        Lead.status
    ).all()
    
    return {status: count for status, count in result}
```

## Related Features

### 依存する機能
- ✅ Lead CRUD（実装済み）
- ✅ Assessment CRUD（実装済み）

### 今後の拡張
- [ ] リアルタイム更新（WebSocket）
- [ ] カスタムレポート作成
- [ ] スケジュール化レポート（メール送信）
- [ ] データエクスポート（PDF、Excel）
- [ ] 比較分析（期間比較、テナント間比較）
- [ ] 予測分析（AI活用）

## Open Questions

1. **集計タイミング**: リアルタイム vs バッチ処理？
   - **提案**: 初期はリアルタイム、パフォーマンス問題があればバッチ化

2. **キャッシング**: 必要か？
   - **提案**: 初期は不要、1,000リード超えたら検討

3. **チャートライブラリ**: Recharts vs Chart.js？
   - **提案**: Recharts（軽量・TypeScript対応）

4. **エクスポート形式**: CSV only? PDF?
   - **提案**: 初期はCSV、Phase 2でPDF追加

## Acceptance Criteria

- [ ] Analyticsダッシュボードが表示される
- [ ] リードのステータス分布が円グラフで表示される
- [ ] スコア分布が表示される
- [ ] トレンドチャートが表示される（30日間）
- [ ] テナント分離が保証される
- [ ] すべてのテストがパスする
- [ ] ページ読み込みが500ms以内
- [ ] レスポンシブデザイン対応

## Risks & Mitigation

### Risk 1: パフォーマンス問題（大量データ）
- **リスク**: 10,000+リードで集計が遅い
- **対策**: インデックス最適化、キャッシング、バッチ処理

### Risk 2: チャートライブラリのサイズ
- **リスク**: バンドルサイズが増加
- **対策**: 軽量ライブラリ選択、code splitting

### Risk 3: リアルタイム性とパフォーマンスのトレードオフ
- **リスク**: リアルタイムだと遅い、キャッシュだと古い
- **対策**: 段階的アプローチ（初期はリアルタイム、後でキャッシング）

## Timeline

- **Phase 1 (Backend)**: 2-3 hours
- **Phase 2 (OpenAPI/Types)**: 30 min
- **Phase 3 (Frontend)**: 3-4 hours
- **Phase 4 (Testing)**: 1 hour

**Total**: 6-8 hours

## Dependencies

### New Dependencies

**Backend:**
- なし（既存ライブラリで実装可能）

**Frontend:**
- `recharts`: React用チャートライブラリ
- `date-fns`: 日付処理

### Installation

```bash
# Frontend
cd frontend
npm install recharts date-fns
```

---

**Next Steps**:
1. チームレビュー
2. 承認後、`openspec/specs/features/analytics-dashboard.md`に移動
3. 実装開始（Backend → OpenAPI Gen → Frontend）

**Reviewers**: @team  
**Estimated Effort**: 6-8 hours  
**Priority**: High  
**Complexity**: Medium
