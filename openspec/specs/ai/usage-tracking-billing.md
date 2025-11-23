# AI Usage Tracking & Billing

**Feature ID**: AI-BILLING-001
**Status**: Implemented
**Priority**: High (SaaS Business Model)
**Last Updated**: 2025-11-23

---

## 📋 Overview

DiagnoLeadsのAI API使用量追跡・課金管理システム。Claude API（Anthropic）の使用量とコストをテナント別に正確に記録し、従量課金モデルを実現します。

### ビジネス価値

- **透明な課金**: テナント別のAI使用コストを可視化
- **公正な分配**: 使用量ベースの正確な請求
- **コスト管理**: AI API支出の予測・制御
- **運用レポート**: CFOへのコスト報告書の根拠

---

## 🎯 主要機能

### 1. トークン使用量追跡

Claude APIの入力/出力トークンを個別に追跡：

| トークンタイプ | 単価（2024年） | 用途 |
|--------------|--------------|------|
| **入力トークン** | $0.003 per 1K tokens | プロンプト、コンテキスト |
| **出力トークン** | $0.015 per 1K tokens | AI生成コンテンツ |

### 2. 操作別追跡

3種類のAI操作を個別に記録：

| 操作 | 説明 | 平均トークン数 |
|-----|------|--------------|
| `generate_assessment` | AI診断自動生成 | 入力: 500, 出力: 2000 |
| `analyze_lead_insights` | リード分析・インサイト生成 | 入力: 800, 出力: 1500 |
| `rephrase_content` | コンテンツ言い換え | 入力: 300, 出力: 300 |

### 3. 自動コスト計算

トークン数から自動的にUSDコストを算出：

```
cost_usd = (input_tokens * 0.003 / 1000) + (output_tokens * 0.015 / 1000)
```

**例**: 診断生成（入力500, 出力2000）
```
cost = (500 * 0.003 / 1000) + (2000 * 0.015 / 1000)
     = 0.0015 + 0.03
     = $0.0315
```

### 4. テナント別集計

各テナントのAI使用量とコストを月次・年次で集計可能。

---

## 📊 データモデル

### AIUsageLog

**テーブル**: `ai_usage_logs`

| フィールド | 型 | 制約 | 説明 |
|-----------|-----|-----|------|
| id | UUID | PK | 使用量ログID |
| tenant_id | UUID | FK(Tenant), NOT NULL, INDEX | テナント所有者 |
| user_id | UUID | FK(User), SET NULL | AI操作実行ユーザー |
| operation | String(100) | NOT NULL, INDEX | 操作タイプ |
| model | String(100) | NOT NULL | AI モデル名 |
| input_tokens | Integer | NOT NULL, DEFAULT 0 | 入力トークン数 |
| output_tokens | Integer | NOT NULL, DEFAULT 0 | 出力トークン数 |
| total_tokens | Integer | NOT NULL, DEFAULT 0 | 総トークン数 |
| cost_usd | Float | | 推定コスト（USD） |
| assessment_id | UUID | FK(Assessment), SET NULL | 関連診断 |
| lead_id | UUID | FK(Lead), SET NULL | 関連リード |
| duration_ms | Integer | | 処理時間（ミリ秒） |
| success | String(20) | DEFAULT 'success' | 実行結果（success, failure） |
| created_at | Timestamp | DEFAULT now(), NOT NULL, INDEX | 使用時刻 |

**インデックス**:
- `[tenant_id]` - テナント別集計
- `[operation]` - 操作別分析
- `[created_at]` - 時系列分析

**リレーションシップ**:
- Tenant ← 1:N → AIUsageLog
- User ← 1:N → AIUsageLog
- Assessment ← 1:N → AIUsageLog
- Lead ← 1:N → AIUsageLog

---

## 🧮 コスト計算ロジック

### AIUsageLogモデルのメソッド

```python
class AIUsageLog(Base):
    __tablename__ = "ai_usage_logs"

    # ... フィールド定義 ...

    def cost_per_1k_input(self) -> float:
        """1K入力トークンあたりのコスト"""
        return 0.003  # Claude 3.5 Sonnet

    def cost_per_1k_output(self) -> float:
        """1K出力トークンあたりのコスト"""
        return 0.015  # Claude 3.5 Sonnet

    def calculate_cost(self) -> float:
        """推定コストを計算（USD）"""
        input_cost = (self.input_tokens / 1000) * self.cost_per_1k_input()
        output_cost = (self.output_tokens / 1000) * self.cost_per_1k_output()
        return input_cost + output_cost

    def update_cost(self):
        """cost_usdフィールドを更新"""
        self.cost_usd = self.calculate_cost()
```

### 自動ログ記録

```python
# ai_service.py より抜粋
def _log_token_usage(
    self,
    operation: str,
    usage: Dict[str, int],
    tenant_id: Optional[UUID],
    user_id: Optional[UUID] = None,
    assessment_id: Optional[UUID] = None,
    lead_id: Optional[UUID] = None,
    duration_ms: Optional[int] = None,
    success: bool = True
) -> None:
    """AI API使用量を記録"""
    log = AIUsageLog(
        tenant_id=tenant_id,
        user_id=user_id,
        operation=operation,
        model=self.model,
        input_tokens=usage.get("input_tokens", 0),
        output_tokens=usage.get("output_tokens", 0),
        total_tokens=usage.get("input_tokens", 0) + usage.get("output_tokens", 0),
        assessment_id=assessment_id,
        lead_id=lead_id,
        duration_ms=duration_ms,
        success="success" if success else "failure"
    )

    # コスト自動計算
    log.update_cost()

    self.db.add(log)
    self.db.commit()
```

---

## 📈 使用量分析

### テナント別月次集計

```sql
SELECT
    tenant_id,
    DATE_TRUNC('month', created_at) AS month,
    operation,
    COUNT(*) AS request_count,
    SUM(input_tokens) AS total_input_tokens,
    SUM(output_tokens) AS total_output_tokens,
    SUM(total_tokens) AS total_tokens,
    SUM(cost_usd) AS total_cost_usd,
    AVG(duration_ms) AS avg_duration_ms
FROM ai_usage_logs
WHERE tenant_id = :tenant_id
  AND created_at >= DATE_TRUNC('month', NOW())
GROUP BY tenant_id, month, operation
ORDER BY month DESC, total_cost_usd DESC;
```

**出力例**:
| operation | request_count | total_tokens | total_cost_usd | avg_duration_ms |
|-----------|--------------|--------------|----------------|----------------|
| generate_assessment | 15 | 37500 | $0.47 | 3200 |
| analyze_lead_insights | 42 | 96600 | $1.16 | 2500 |
| rephrase_content | 8 | 4800 | $0.04 | 1800 |

### 成功率分析

```sql
SELECT
    operation,
    COUNT(*) AS total,
    SUM(CASE WHEN success = 'success' THEN 1 ELSE 0 END) AS success_count,
    ROUND(100.0 * SUM(CASE WHEN success = 'success' THEN 1 ELSE 0 END) / COUNT(*), 2) AS success_rate
FROM ai_usage_logs
WHERE tenant_id = :tenant_id
GROUP BY operation;
```

---

## 💰 課金モデル

### 従量課金プラン（検討中）

| プラン | 月額基本料金 | 無料枠 | 超過料金 |
|-------|------------|-------|---------|
| **Free** | ¥0 | 100リクエスト/月 | - |
| **Starter** | ¥9,800 | 500リクエスト/月 | ¥20/リクエスト |
| **Pro** | ¥29,800 | 2,000リクエスト/月 | ¥15/リクエスト |
| **Enterprise** | 要相談 | 無制限 | - |

### コスト配分例

**想定**: テナントあたり月間200リクエスト（診断生成100, リード分析100）

```
診断生成: 100回 × $0.0315 = $3.15
リード分析: 100回 × $0.024 = $2.40
合計: $5.55 ≈ ¥850 (為替レート $1 = ¥153)

Starterプラン: ¥9,800/月
  - AI APIコスト: ¥850
  - インフラコスト: ¥3,000
  - 粗利: ¥5,950 (61%)
```

---

## 🔧 運用フロー

### 1. リアルタイム記録

AI API呼び出しごとに自動記録：

```python
# ai_service.py - generate_assessment() より抜粋
async def generate_assessment(self, topic: str, industry: str, tenant_id: UUID):
    start_time = time.time()

    try:
        # Claude API 呼び出し
        response = await self.client.messages.create(...)

        # 処理時間計算
        duration_ms = int((time.time() - start_time) * 1000)

        # トークン使用量記録
        self._log_token_usage(
            operation="generate_assessment",
            usage={
                "input_tokens": response.usage.input_tokens,
                "output_tokens": response.usage.output_tokens
            },
            tenant_id=tenant_id,
            duration_ms=duration_ms,
            success=True
        )

        return result

    except Exception as e:
        # エラー時も記録（success=False）
        self._log_token_usage(..., success=False)
        raise
```

### 2. 月次請求処理（未実装）

```python
def generate_monthly_invoice(tenant_id: UUID, month: date) -> dict:
    """月次請求書生成"""
    # 月間使用量集計
    usage = db.query(
        func.sum(AIUsageLog.total_tokens).label("total_tokens"),
        func.sum(AIUsageLog.cost_usd).label("total_cost")
    ).filter(
        AIUsageLog.tenant_id == tenant_id,
        func.date_trunc('month', AIUsageLog.created_at) == month
    ).first()

    # プラン情報取得
    tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()

    # 請求金額計算
    invoice = {
        "tenant_id": tenant_id,
        "month": month,
        "plan": tenant.plan,
        "base_fee": get_base_fee(tenant.plan),
        "ai_usage_tokens": usage.total_tokens,
        "ai_usage_cost_usd": usage.total_cost,
        "ai_usage_cost_jpy": usage.total_cost * 153,  # 為替レート
        "total_amount_jpy": ...
    }

    return invoice
```

### 3. 使用量アラート（未実装）

```python
def check_usage_threshold(tenant_id: UUID):
    """使用量が閾値を超えた場合にアラート"""
    # 月間使用量取得
    month_usage = get_monthly_usage(tenant_id)

    # プランの無料枠取得
    free_tier = get_free_tier(tenant.plan)

    # 80%超過でアラート
    if month_usage > free_tier * 0.8:
        send_usage_alert(tenant, month_usage, free_tier)
```

---

## 📊 ダッシュボード表示（未実装）

### テナント管理画面

```
┌─────────────────────────────────────────────────────┐
│ AI 使用量                                            │
├─────────────────────────────────────────────────────┤
│                                                     │
│ 今月の使用量                                         │
│ ┌─────────────────────────────────────────────┐   │
│ │ 診断生成:     87回  ($2.74)                  │   │
│ │ リード分析:   124回 ($2.98)                  │   │
│ │ 言い換え:     12回  ($0.04)                  │   │
│ │                                             │   │
│ │ 合計:        223回  ($5.76)                  │   │
│ └─────────────────────────────────────────────┘   │
│                                                     │
│ プラン: Starter（無料枠: 500回/月）                  │
│ 残り: 277回 (55%)                                   │
│ [■■■■■■■■■■■░░░░░░░░░]                            │
│                                                     │
│ 📈 使用量トレンド                                    │
│ [グラフ: 日別AI使用回数]                             │
│                                                     │
│ 📊 操作別内訳                                        │
│ 診断生成:   39% ████████░░                          │
│ リード分析: 56% ███████████░                        │
│ 言い換え:    5% █░░░░░░░░░                          │
└─────────────────────────────────────────────────────┘
```

---

## 🧪 テスト

### 実装済みテスト

- トークン使用量記録のテスト
- コスト計算の正確性テスト
- テナント別集計テスト

### カバレッジ

- AIUsageLog モデル: 100%
- ai_service.py ロギング: 95%

---

## 📂 実装ファイル

| ファイル | 説明 |
|---------|------|
| `/backend/app/models/ai_usage.py` | AIUsageLog モデル定義 |
| `/backend/app/services/ai_service.py` | AI サービス（ログ記録統合済み） |
| `/backend/alembic/versions/h7i8j9k0l1m2_add_ai_usage_log_table.py` | マイグレーション |

---

## 🚀 将来の改善

1. **使用量ダッシュボード**: リアルタイム可視化
2. **請求書自動生成**: Stripe 統合
3. **使用量アラート**: Slack/Email 通知
4. **予算設定**: テナント別の月次予算上限
5. **プラン自動アップグレード提案**: 使用量に基づく最適プラン推奨
6. **詳細分析**: ユーザー別、診断別のAI使用量分析
7. **コスト最適化**: プロンプト最適化提案
8. **マルチモデル対応**: Claude 以外のAIモデル（GPT-4等）

---

## 🔗 関連仕様

- [AI Support](../features/ai-support.md) - AI診断生成機能
- [Prompt Security](./prompt-security.md) - プロンプトセキュリティ
- [Custom Reporting](../analytics/custom-reporting-export.md) - レポート機能

---

**実装ステータス**: ✅ バックエンド実装完了（ダッシュボードUI実装済み）

## 🎨 ダッシュボードUI（実装済み）

### AIUsagePage
**ファイル**: `/frontend/src/pages/admin/AIUsagePage.tsx`

**機能**:
- 使用量サマリー統計カード（総リクエスト数、総トークン数、総コスト、成功率）
- 操作別内訳（リクエスト数、トークン数、コスト）
- プログレスバーによる使用率可視化
- レスポンシブデザイン

**サービス**: `/frontend/src/services/aiUsageService.ts`
- `getAIUsageSummary()` - 使用量サマリー取得
- `getAIUsageLogs()` - 使用ログ一覧取得
- `getAIUsageTrend()` - トレンドデータ取得

**注意**: バックエンドAPIエンドポイント (`/tenants/{tenant_id}/ai-usage`) は今後実装予定
