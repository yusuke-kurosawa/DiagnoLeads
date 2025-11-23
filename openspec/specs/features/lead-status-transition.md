# Lead Status Transition Rules

**Feature ID**: LEAD-STATUS-001
**Status**: Implemented
**Priority**: High (Sales Process)
**Last Updated**: 2025-11-23

---

## 📋 Overview

DiagnoLeadsのリードステータス管理システム。営業ファネルの各段階（new → contacted → qualified → converted）を追跡し、適切なフォローアップを実現します。

### ビジネス価値

- **営業プロセスの可視化**: ファネル各段階のリード数を把握
- **優先順位付け**: ステータス別にアクション優先度を管理
- **コンバージョン追跡**: 各段階の転換率を測定
- **営業効率化**: 適切なタイミングでフォローアップ

---

## 🎯 ステータス定義（5種類）

| ステータス | 説明 | 営業アクション | 次の状態 |
|-----------|------|--------------|---------|
| **new** | 新規獲得 | 初回コンタクト準備 | contacted, disqualified |
| **contacted** | 初回接触済み | フォローアップ継続 | qualified, disqualified |
| **qualified** | 商談可能 | 提案・デモ実施 | converted, disqualified |
| **converted** | 成約済み | 顧客対応へ移行 | - （終了状態） |
| **disqualified** | 不適格 | ナーチャリング or 離脱 | - （終了状態） |

---

## 🔄 ステータス遷移フロー

### 標準的な成約パス

```
new → contacted → qualified → converted
 ↓       ↓           ↓
disqualified (各段階から離脱可能)
```

### 遷移ルール

#### 1. new (新規リード)

**初期状態**: 診断完了・リード獲得時に自動設定

**可能な遷移**:
- → `contacted`: 初回メール/電話でコンタクト
- → `disqualified`: 明らかに不適格（競合、対象外業界等）

**トリガー**:
- 自動: 診断フォーム送信時
- 手動: 営業担当が初回接触

**平均滞在期間**: 0-2日

---

#### 2. contacted (接触済み)

**定義**: 初回コンタクトが完了した状態

**可能な遷移**:
- → `qualified`: 商談意欲あり、予算・決裁権を確認
- → `disqualified`: 興味なし、予算なし等

**トリガー**:
- 手動: 営業担当が接触記録を更新
- 自動: メール開封・リンククリック検知（未実装）

**平均滞在期間**: 3-7日

---

#### 3. qualified (商談可能)

**定義**: BANT条件（Budget, Authority, Need, Timeline）を満たす

**可能な遷移**:
- → `converted`: 契約締結
- → `disqualified`: 検討中止

**トリガー**:
- 手動: 営業担当が商談設定・提案実施

**平均滞在期間**: 7-30日

---

#### 4. converted (成約済み)

**定義**: 契約締結完了

**可能な遷移**: なし（終了状態）

**トリガー**:
- 手動: 契約書締結後に営業が更新
- 自動: 決済完了webhook（未実装）

**備考**: 顧客管理システム（CRM）へ移行

---

#### 5. disqualified (不適格)

**定義**: 商談化できない、またはニーズ不一致

**可能な遷移**: なし（終了状態）

**理由の分類**:
- 予算不足
- 決裁権限なし
- タイミング不適
- 競合選定
- ニーズ不一致

**備考**: 将来的にナーチャリング対象として再活性化可能

---

## 📊 ステータス分布（想定）

| ステータス | 割合 | 件数（月間500リード想定） |
|-----------|------|------------------------|
| new | 45% | 225件 |
| contacted | 30% | 150件 |
| qualified | 15% | 75件 |
| converted | 5% | 25件 |
| disqualified | 5% | 25件 |

**コンバージョン率**: 5%（new → converted）

---

## 🔧 データモデル

### Lead.status フィールド

```python
# /backend/app/models/lead.py
class Lead(Base):
    __tablename__ = "leads"

    # ステータスフィールド
    status = Column(
        String(50),
        default="new",
        nullable=False
    )  # new, contacted, qualified, converted, disqualified

    # 関連フィールド
    last_contacted_at = Column(DateTime(timezone=True), nullable=True)
    last_activity_at = Column(DateTime(timezone=True), nullable=True)
```

**インデックス**: `idx_leads_tenant_status` （tenant_id, status）

---

## 🔒 ステータス更新ルール

### 1. 自動更新

```python
# 診断完了時
lead = Lead(
    name=form_data["name"],
    email=form_data["email"],
    status="new",  # 自動的にnew
    score=calculated_score,
)
```

### 2. 手動更新（API）

```python
# PATCH /api/v1/tenants/{tenant_id}/leads/{lead_id}
{
    "status": "contacted",
    "notes": "2025-11-23 初回メール送信。返信待ち。"
}
```

**バリデーション**:
- ステータス値が5種類のいずれかであること
- テナント権限チェック（クロステナント更新を防止）

### 3. 監査ログ記録

ステータス変更時に自動記録（未実装）:

```python
# AuditLog に記録
AuditLog(
    tenant_id=lead.tenant_id,
    user_id=current_user.id,
    entity_type="LEAD",
    entity_id=lead.id,
    action="UPDATE",
    old_values={"status": "new"},
    new_values={"status": "contacted"},
    reason="初回コンタクト完了",
)
```

---

## 📈 ステータス別アクション

### new → contacted

**営業アクション**:
1. リード情報レビュー（名前、メール、スコア、診断回答）
2. 初回メール作成（テンプレート利用）
3. 送信 + `last_contacted_at` 更新
4. ステータス更新 → `contacted`

**テンプレート例**:
```
件名: {診断名}の診断ありがとうございました

{name}様

DiagnoLeadsの診断をご利用いただきありがとうございます。

診断結果から、{pain_point}の課題をお持ちかと拝察しました。
弊社では{solution}で多くの企業様の課題解決をサポートしております。

もしよろしければ、30分ほどのオンライン相談会を...
```

---

### contacted → qualified

**営業アクション**:
1. 返信確認・商談意欲の確認
2. BANT条件の確認
   - Budget: 予算規模
   - Authority: 決裁権限
   - Need: 課題の深刻度
   - Timeline: 導入時期
3. 条件クリア → ステータス更新 → `qualified`
4. 商談日程調整

---

### qualified → converted

**営業アクション**:
1. デモ・提案実施
2. 見積書提示
3. 契約書締結
4. ステータス更新 → `converted`
5. CRMへデータ移行（Salesforce/HubSpot連携）

---

## 📊 ファネル分析

### SQL クエリ例

```sql
-- ステータス別集計
SELECT
    status,
    COUNT(*) AS count,
    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 2) AS percentage
FROM leads
WHERE tenant_id = '{tenant_id}'
GROUP BY status
ORDER BY
    CASE status
        WHEN 'new' THEN 1
        WHEN 'contacted' THEN 2
        WHEN 'qualified' THEN 3
        WHEN 'converted' THEN 4
        WHEN 'disqualified' THEN 5
    END;
```

**出力例**:
| status | count | percentage |
|--------|-------|-----------|
| new | 225 | 45.00% |
| contacted | 150 | 30.00% |
| qualified | 75 | 15.00% |
| converted | 25 | 5.00% |
| disqualified | 25 | 5.00% |

---

## 🚀 将来の改善

### 1. ステータス遷移の自動化

機械学習でステータス更新を提案：

```python
class StatusPredictionService:
    def predict_next_status(self, lead: Lead) -> str:
        """次のステータスを予測"""
        # メール開封率、返信速度、スコア等から予測
        features = [
            lead.score,
            lead.email_open_rate,
            lead.reply_time_hours,
        ]
        return model.predict(features)  # "qualified" 等
```

### 2. ステータス別SLA（Service Level Agreement）

```python
STATUS_SLA = {
    "new": timedelta(days=1),  # 24時間以内に接触
    "contacted": timedelta(days=3),  # 3日以内にフォローアップ
    "qualified": timedelta(days=7),  # 7日以内に提案
}

# SLA違反アラート
if lead.status == "new" and lead.created_at < now() - STATUS_SLA["new"]:
    send_slack_alert(f"Lead {lead.name} のSLA違反")
```

### 3. カスタムステータス

テナント固有のステータス定義：

```python
class CustomLeadStatus(Base):
    __tablename__ = "custom_lead_statuses"

    tenant_id = Column(UUID, ForeignKey("tenants.id"))
    name = Column(String(50))  # "demo_scheduled", "contract_sent"
    order = Column(Integer)
    color = Column(String(7))  # Hex color
```

### 4. ステータス遷移webhook

```python
# ステータス変更時に外部システムへ通知
@event_listener("lead.status_changed")
def on_status_change(lead, old_status, new_status):
    webhook_service.send({
        "event": "lead.status_changed",
        "lead_id": str(lead.id),
        "old_status": old_status,
        "new_status": new_status,
    })
```

### 5. ステータス遷移の可視化

Sankey diagram等でファネル可視化：

```
new (500) ─────→ contacted (300) ────→ qualified (100) ───→ converted (25)
    │                  │                     │
    └→ disqualified (200)
                  └→ disqualified (200)
                                     └→ disqualified (75)
```

---

## 📂 実装ファイル

| ファイル | 説明 |
|---------|------|
| `/backend/app/models/lead.py` | Lead.status フィールド定義 |
| `/backend/app/api/v1/leads.py` | ステータス更新API |
| `/backend/app/services/analytics_service.py` | ステータス別集計 |

---

## 🔗 関連仕様

- [Lead Management](./lead-management.md) - リード管理機能全般
- [Lead Analysis & Actions](../ai/lead-analysis-actions.md) - AIリード分析
- [Audit Logging](../security/audit-logging.md) - 変更履歴追跡

---

**実装ステータス**: ✅ 基本ステータス管理実装済み
**拡張機能**: ⏳ 自動遷移、SLA、カスタムステータス、webhook は未実装
