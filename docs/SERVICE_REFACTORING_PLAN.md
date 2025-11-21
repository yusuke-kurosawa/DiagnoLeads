# サービス層リファクタリング計画

## 概要

現在のサービス層には500行を超える大きなファイルが複数存在し、保守性に課題があります。
このドキュメントでは、段階的なリファクタリング計画を提示します。

---

## 現状分析

### 大きなサービスファイル

| ファイル | 行数 | 主な責務 | 問題点 |
|---------|------|----------|--------|
| **lead_service.py** | 522 | リード管理、GA4通知、Teams通知、検索 | 複数の責務が混在 |
| **ai_service.py** | 475 | AI診断生成、分析、プロンプト構築 | ドメイン別分離が必要 |
| **qr_code_service.py** | 465 | QRコード生成、追跡、GA4連携 | GA4連携を分離すべき |
| **report_service.py** | 446 | レポート生成、データ集計 | 集計ロジックを分離 |

---

## リファクタリング優先順位

### 🔴 優先度: 高（今すぐ実施推奨）

#### 1. lead_service.py の分割 (522行 → 4モジュール)

**分割計画**:

```
backend/app/services/leads/
├── __init__.py                 # パブリックインターフェース
├── lead_crud.py                # CRUD操作 (~150行)
├── lead_scoring.py             # スコアリングロジック (~100行)
├── lead_notifications.py       # GA4・Teams通知 (~150行)
└── lead_search.py              # 検索・フィルタリング (~100行)
```

**現在のメソッド配置**:

| メソッド | 移動先モジュール | 理由 |
|---------|-----------------|------|
| `list_by_tenant` | lead_crud.py | 基本的なCRUD操作 |
| `get_by_id` | lead_crud.py | 基本的なCRUD操作 |
| `get_by_email` | lead_crud.py | 基本的なCRUD操作 |
| `create` | lead_crud.py | 基本的なCRUD操作 |
| `update` | lead_crud.py | 基本的なCRUD操作 |
| `delete` | lead_crud.py | 基本的なCRUD操作 |
| `count_by_tenant` | lead_crud.py | 基本的なCRUD操作 |
| `update_score` | lead_scoring.py | スコアリング専門 |
| `get_hot_leads` | lead_scoring.py | スコア基準の検索 |
| `update_status` | lead_notifications.py | ステータス変更時に通知 |
| `_send_ga4_event` | lead_notifications.py | 通知処理 |
| `_send_teams_notification` | lead_notifications.py | 通知処理 |
| `search` | lead_search.py | 検索機能 |

**実装例**:

```python
# backend/app/services/leads/lead_crud.py
from uuid import UUID
from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.lead import Lead
from app.schemas.lead import LeadCreate, LeadUpdate

class LeadCRUDService:
    """リードのCRUD操作"""

    def __init__(self, db: Session):
        self.db = db

    def list_by_tenant(
        self,
        tenant_id: UUID,
        skip: int = 0,
        limit: int = 100,
        status: Optional[str] = None
    ) -> List[Lead]:
        """テナント別リード一覧取得"""
        query = self.db.query(Lead).filter(Lead.tenant_id == tenant_id)

        if status:
            query = query.filter(Lead.status == status)

        return query.offset(skip).limit(limit).all()

    def get_by_id(self, lead_id: UUID, tenant_id: UUID) -> Optional[Lead]:
        """IDでリード取得（テナント分離）"""
        return self.db.query(Lead).filter(
            Lead.id == lead_id,
            Lead.tenant_id == tenant_id
        ).first()

    # ... 他のCRUDメソッド
```

```python
# backend/app/services/leads/__init__.py
"""
リードサービス統合モジュール

後方互換性のため、既存のLeadServiceインターフェースを提供
"""

from .lead_crud import LeadCRUDService
from .lead_scoring import LeadScoringService
from .lead_notifications import LeadNotificationService
from .lead_search import LeadSearchService

class LeadService:
    """統合リードサービス（後方互換性）"""

    def __init__(self, db):
        self.crud = LeadCRUDService(db)
        self.scoring = LeadScoringService(db)
        self.notifications = LeadNotificationService(db)
        self.search = LeadSearchService(db)

    # 既存のメソッドを委譲
    def list_by_tenant(self, *args, **kwargs):
        return self.crud.list_by_tenant(*args, **kwargs)

    def get_by_id(self, *args, **kwargs):
        return self.crud.get_by_id(*args, **kwargs)

    # ... 他のメソッドを委譲
```

**実装手順**:

1. ✅ リファクタリング計画作成（このドキュメント）
2. ⬜ `backend/app/services/leads/` ディレクトリ作成
3. ⬜ `lead_crud.py` の実装
4. ⬜ `lead_scoring.py` の実装
5. ⬜ `lead_notifications.py` の実装
6. ⬜ `lead_search.py` の実装
7. ⬜ `__init__.py` で統合インターフェース作成
8. ⬜ 既存のテストが通ることを確認
9. ⬜ 新しいモジュール別テストを追加
10. ⬜ 古い `lead_service.py` を非推奨化（deprecation warning）
11. ⬜ 数バージョン後に削除

---

### 🟡 優先度: 中（1-2ヶ月以内）

#### 2. ai_service.py の分割 (475行 → 3モジュール)

**分割計画**:

```
backend/app/services/ai/
├── __init__.py
├── ai_assessment.py      # 診断生成 (~200行)
├── ai_analysis.py        # リード分析 (~150行)
└── ai_prompts.py         # プロンプトテンプレート (~100行)
```

**理由**: AI機能は将来的に拡張される可能性が高いため、早めにドメイン分離

---

#### 3. qr_code_service.py の分割 (465行 → 3モジュール)

**分割計画**:

```
backend/app/services/qr_codes/
├── __init__.py
├── qr_generation.py      # QRコード生成 (~150行)
├── qr_tracking.py        # スキャン追跡 (~200行)
└── qr_analytics.py       # GA4連携・分析 (~100行)
```

---

#### 4. report_service.py の分割 (446行 → 2モジュール)

**分割計画**:

```
backend/app/services/reports/
├── __init__.py
├── report_generation.py  # レポート生成 (~250行)
└── report_aggregation.py # データ集計 (~180行)
```

---

### 🟢 優先度: 低（必要に応じて）

以下のサービスは現在のサイズでも許容範囲内:

- `report_export_service.py` (340行) - 単一責務
- `auth.py` (262行) - 適切なサイズ
- `analytics_service.py` (243行) - 適切なサイズ
- `google_analytics_service.py` (223行) - 適切なサイズ
- `assessment_service.py` (209行) - 適切なサイズ

---

## リファクタリングの原則

### 1. 後方互換性の維持

**重要**: 既存のコードを壊さないこと

```python
# 古いインターフェース（非推奨だが動作する）
from app.services.lead_service import LeadService

lead_service = LeadService(db)
lead = lead_service.get_by_id(lead_id, tenant_id)  # ✅ 動作する

# 新しいインターフェース（推奨）
from app.services.leads import LeadCRUDService

lead_crud = LeadCRUDService(db)
lead = lead_crud.get_by_id(lead_id, tenant_id)  # ✅ 同じ動作
```

### 2. 段階的な移行

**フェーズ1**: 新モジュール作成（既存コード維持）
**フェーズ2**: 新モジュールへの移行を推奨（deprecation warning）
**フェーズ3**: 数バージョン後、古いコードを削除

### 3. テストの完全性

**必須**: すべてのリファクタリングでテストが通ること

```bash
# リファクタリング前後でテストが通ることを確認
pytest tests/test_lead.py -v
pytest tests/test_lead_service.py -v
```

---

## 期待される効果

### コード品質

| メトリクス | 現状 | リファクタリング後 | 改善 |
|-----------|------|------------------|------|
| 平均ファイルサイズ | 290行 | <200行 | 31%削減 |
| 最大ファイルサイズ | 522行 | <250行 | 52%削減 |
| メソッド数/ファイル | 平均8個 | 平均5個 | 37%削減 |
| テストの粒度 | 粗い | 細かい | 向上 |

### 開発体験

- **可読性**: ファイルが小さくなり、目的のコードを見つけやすい
- **テスタビリティ**: 小さなモジュールは単体テストが容易
- **並行開発**: 別々のファイルで競合が減少
- **責務の明確化**: 各モジュールの役割が明確

---

## 実装タイムライン

### Week 1-2: lead_service.py の分割
- [ ] モジュール設計
- [ ] 実装
- [ ] テスト
- [ ] ドキュメント更新

### Week 3-4: ai_service.py の分割
- [ ] モジュール設計
- [ ] 実装
- [ ] テスト
- [ ] ドキュメント更新

### Week 5-6: qr_code_service.py の分割
- [ ] モジュール設計
- [ ] 実装
- [ ] テスト
- [ ] ドキュメント更新

### Week 7-8: report_service.py の分割（オプション）
- [ ] 必要性の再評価
- [ ] 実装（必要な場合）

---

## 参考リソース

### 設計パターン
- [Service Layer Pattern](https://martinfowler.com/eaaCatalog/serviceLayer.html)
- [Clean Architecture](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html)
- [Domain-Driven Design](https://www.domainlanguage.com/ddd/)

### Pythonベストプラクティス
- [PEP 8 - Style Guide](https://peps.python.org/pep-0008/)
- [Python Package Structure](https://packaging.python.org/en/latest/guides/packaging-namespace-packages/)

---

## まとめ

このリファクタリング計画により：

✅ **保守性の大幅向上** - ファイルサイズ50%削減
✅ **テスタビリティ向上** - モジュール単位のテスト
✅ **並行開発の促進** - ファイル競合の減少
✅ **責務の明確化** - SRP (Single Responsibility Principle) 遵守
✅ **後方互換性の維持** - 既存コードを壊さない

優先度の高い**lead_service.pyの分割**から開始することを強く推奨します。
