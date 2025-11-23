# Feature: CRM Integration (Salesforce/HubSpot)

**Feature ID**: INT-CRM-001
**Status**: In Progress
**Priority**: Critical (Sales Enablement)
**Last Updated**: 2025-11-23
**Effort**: Large (3-4 weeks)

---

## 📋 Overview

DiagnoLeadsと主要CRM（Salesforce/HubSpot）との双方向統合システム。リード情報、商談データ、アクティビティを自動同期し、営業チームの既存ワークフローを維持しながらシームレスなデータ連携を実現します。

### ビジネス価値

- **営業効率化**: 手動データ入力を削減、リード対応の高速化
- **データ一元化**: CRM側に診断データ・スコア・インサイトを自動反映
- **既存ワークフロー維持**: 現行のCRM運用を崩さない統合
- **リアルタイム同期**: ホットリード発生から30秒以内にCRM反映

---

## 🎯 主要機能

### 1. 対応CRM

| CRM | OAuth | API | 同期対象 |
|-----|-------|-----|---------|
| **Salesforce** | ✅ OAuth 2.0 | REST API v57.0 | Lead, Contact, Account, Task |
| **HubSpot** | ✅ OAuth 2.0 | v3 API | Contact, Company, Deal, Note |

### 2. 同期方向

| 方向 | タイミング | 同期対象 |
|-----|----------|---------|
| **DiagnoLeads → CRM** | リアルタイム（30秒以内） | リード作成/更新、診断完了 |
| **CRM → DiagnoLeads** | Webhook（即時） or ポーリング（5分間隔） | ステータス更新、担当者変更 |

### 3. 同期データ

#### Salesforce同期マッピング

| DiagnoLeads | Salesforce Object | フィールド |
|------------|------------------|----------|
| Lead | Lead | FirstName, LastName, Email, Company, Phone |
| Lead.score | Lead.LeadScore__c | カスタムフィールド（スコア） |
| Lead.priority_level | Lead.Priority__c | Hot/Warm/Cold |
| Lead.detected_challenges | Lead.DetectedChallenges__c | AI分析結果（JSON） |
| Assessment Response | Task | 診断完了アクティビティ |

#### HubSpot同期マッピング

| DiagnoLeads | HubSpot Object | プロパティ |
|------------|---------------|-----------|
| Lead | Contact | firstname, lastname, email, company, phone |
| Lead.score | Contact.hs_lead_score | リードスコア |
| Lead.priority_level | Contact.lead_priority | Hot/Warm/Cold |
| Lead.detected_challenges | Contact.detected_challenges | AI分析結果（JSON文字列） |
| Assessment Response | Note | 診断完了メモ |

---

## 🔌 API設計

### 1. CRM接続設定API

```http
POST /api/v1/tenants/{tenant_id}/integrations/salesforce/connect
Authorization: Bearer {token}
```

**リクエスト**:
```json
{
  "redirect_uri": "https://app.diagnoleads.com/integrations/salesforce/callback"
}
```

**レスポンス**:
```json
{
  "auth_url": "https://login.salesforce.com/services/oauth2/authorize?client_id=...",
  "state": "secure_random_state_token"
}
```

**フロー**:
1. フロントエンドがauth_urlにリダイレクト
2. ユーザーがSalesforceで認証
3. Salesforceがcallback URLにリダイレクト（code付き）
4. バックエンドがcodeをaccess_tokenに交換

---

### 2. OAuth Callback処理

```http
GET /api/v1/integrations/salesforce/callback?code={code}&state={state}
```

**処理**:
1. stateトークン検証（CSRF防止）
2. codeをaccess_token/refresh_tokenに交換
3. テナントのintegration設定にトークン保存（暗号化）
4. フロントエンドの成功ページにリダイレクト

---

### 3. リード同期API

```http
POST /api/v1/tenants/{tenant_id}/integrations/salesforce/sync-lead
Authorization: Bearer {token}
Content-Type: application/json
```

**リクエスト**:
```json
{
  "lead_id": "lead-uuid",
  "sync_type": "create",  // create, update, delete
  "force": false  // true: 既存データを上書き
}
```

**レスポンス**:
```json
{
  "success": true,
  "salesforce_id": "00Q1234567890ABC",
  "synced_at": "2025-11-23T10:30:00Z",
  "fields_synced": ["FirstName", "LastName", "Email", "LeadScore__c"]
}
```

---

### 4. フィールドマッピング設定API

```http
PUT /api/v1/tenants/{tenant_id}/integrations/salesforce/field-mapping
Authorization: Bearer {token}
Content-Type: application/json
```

**リクエスト**:
```json
{
  "mappings": [
    {
      "diagno_field": "lead.name",
      "salesforce_field": "FirstName",
      "transform": "split_first_name"
    },
    {
      "diagno_field": "lead.company",
      "salesforce_field": "Company",
      "transform": null
    },
    {
      "diagno_field": "lead.score",
      "salesforce_field": "LeadScore__c",
      "transform": null
    }
  ]
}
```

---

### 5. 同期ステータス確認API

```http
GET /api/v1/tenants/{tenant_id}/integrations/salesforce/sync-status
Authorization: Bearer {token}
```

**レスポンス**:
```json
{
  "enabled": true,
  "last_sync": "2025-11-23T10:30:00Z",
  "total_synced": 245,
  "failed_syncs": 3,
  "next_poll_at": "2025-11-23T10:35:00Z",
  "health_status": "healthy"
}
```

---

### 6. Webhook受信エンドポイント

```http
POST /api/v1/webhooks/salesforce
Content-Type: application/json
X-Salesforce-Signature: {signature}
```

**リクエスト（Salesforce Outbound Message）**:
```xml
<soapenv:Envelope>
  <soapenv:Body>
    <notifications>
      <Notification>
        <sObject xsi:type="Lead">
          <Id>00Q1234567890ABC</Id>
          <Status>Contacted</Status>
          <OwnerId>00512345678901234</OwnerId>
        </sObject>
      </Notification>
    </notifications>
  </soapenv:Body>
</soapenv:Envelope>
```

**処理**:
1. シグネチャ検証
2. DiagnoLeadsのリードを検索（external_idでマッチング）
3. ステータス・担当者を更新
4. 監査ログ記録

---

## 📊 データモデル

### CRMIntegration

**テーブル**: `crm_integrations`

| フィールド | 型 | 制約 | 説明 |
|-----------|-----|-----|------|
| id | UUID | PK | 統合ID |
| tenant_id | UUID | FK(Tenant), NOT NULL, UNIQUE | テナント（1テナント=1CRM統合） |
| crm_type | String(50) | NOT NULL | salesforce, hubspot |
| enabled | Boolean | DEFAULT True | 統合有効/無効 |
| access_token_encrypted | Text | | 暗号化されたアクセストークン |
| refresh_token_encrypted | Text | | 暗号化されたリフレッシュトークン |
| instance_url | String(255) | | Salesforce instance URL |
| expires_at | Timestamp | | トークン有効期限 |
| field_mappings | JSON | | フィールドマッピング設定 |
| sync_config | JSON | | 同期設定（方向、頻度等） |
| last_sync_at | Timestamp | | 最終同期時刻 |
| created_at | Timestamp | DEFAULT now() | 作成日時 |
| updated_at | Timestamp | DEFAULT now() | 更新日時 |

**インデックス**:
- `[tenant_id]` - テナント検索
- `[crm_type]` - CRMタイプフィルター

---

### CRMSyncLog

**テーブル**: `crm_sync_logs`

| フィールド | 型 | 制約 | 説明 |
|-----------|-----|-----|------|
| id | UUID | PK | ログID |
| integration_id | UUID | FK(CRMIntegration), NOT NULL | CRM統合 |
| lead_id | UUID | FK(Lead), SET NULL | 対象リード |
| sync_type | String(20) | NOT NULL | create, update, delete |
| direction | String(20) | NOT NULL | to_crm, from_crm |
| status | String(20) | NOT NULL | success, failed, pending |
| crm_record_id | String(255) | | CRM側のレコードID |
| fields_synced | JSON | | 同期されたフィールド |
| error_message | Text | | エラーメッセージ |
| retry_count | Integer | DEFAULT 0 | リトライ回数 |
| synced_at | Timestamp | | 同期実行時刻 |
| created_at | Timestamp | DEFAULT now() | 作成日時 |

**インデックス**:
- `[integration_id, created_at]` - 統合別ログ検索
- `[lead_id]` - リード別同期履歴
- `[status]` - 失敗ログ検索

---

## 🔧 技術実装

### 1. CRMベースクラス

```python
# backend/app/integrations/crm/base.py
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from uuid import UUID

class CRMClient(ABC):
    """CRM統合の基底クラス"""

    def __init__(self, integration_id: UUID, config: Dict[str, Any]):
        self.integration_id = integration_id
        self.config = config

    @abstractmethod
    async def authenticate(self, code: str) -> Dict[str, str]:
        """OAuth認証コードをトークンに交換"""
        pass

    @abstractmethod
    async def refresh_token(self) -> Dict[str, str]:
        """アクセストークンをリフレッシュ"""
        pass

    @abstractmethod
    async def create_lead(self, lead_data: Dict[str, Any]) -> str:
        """リードを作成してCRM側のIDを返す"""
        pass

    @abstractmethod
    async def update_lead(self, crm_id: str, lead_data: Dict[str, Any]) -> bool:
        """リードを更新"""
        pass

    @abstractmethod
    async def get_lead(self, crm_id: str) -> Dict[str, Any]:
        """リードを取得"""
        pass

    @abstractmethod
    async def delete_lead(self, crm_id: str) -> bool:
        """リードを削除"""
        pass
```

---

### 2. Salesforce実装

```python
# backend/app/integrations/crm/salesforce_client.py
import httpx
from app.integrations.crm.base import CRMClient
from app.integrations.microsoft.retry_policy import with_retry

class SalesforceClient(CRMClient):
    """Salesforce統合クライアント"""

    API_VERSION = "v57.0"

    @with_retry(max_retries=3)
    async def create_lead(self, lead_data: Dict[str, Any]) -> str:
        """Salesforceにリードを作成"""
        url = f"{self.config['instance_url']}/services/data/{self.API_VERSION}/sobjects/Lead"

        # フィールドマッピング適用
        mapped_data = self._apply_field_mapping(lead_data)

        async with httpx.AsyncClient() as client:
            response = await client.post(
                url,
                json=mapped_data,
                headers={
                    "Authorization": f"Bearer {self.config['access_token']}",
                    "Content-Type": "application/json"
                }
            )
            response.raise_for_status()

            result = response.json()
            return result["id"]  # Salesforce Lead ID

    def _apply_field_mapping(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """DiagnoLeadsフィールドをSalesforceフィールドにマッピング"""
        mappings = self.config.get("field_mappings", {})

        # デフォルトマッピング
        default_mapping = {
            "name": ("FirstName", "LastName"),
            "email": "Email",
            "company": "Company",
            "phone": "Phone",
            "score": "LeadScore__c",
            "priority_level": "Priority__c",
        }

        mapped = {}

        for diagno_field, salesforce_field in default_mapping.items():
            if diagno_field in data:
                if diagno_field == "name":
                    # 名前を分割
                    parts = data["name"].split(" ", 1)
                    mapped["FirstName"] = parts[0]
                    mapped["LastName"] = parts[1] if len(parts) > 1 else parts[0]
                else:
                    mapped[salesforce_field] = data[diagno_field]

        return mapped
```

---

### 3. HubSpot実装

```python
# backend/app/integrations/crm/hubspot_client.py
import httpx
from app.integrations.crm.base import CRMClient
from app.integrations.microsoft.retry_policy import with_retry

class HubSpotClient(CRMClient):
    """HubSpot統合クライアント"""

    BASE_URL = "https://api.hubapi.com"

    @with_retry(max_retries=3)
    async def create_lead(self, lead_data: Dict[str, Any]) -> str:
        """HubSpotにContactを作成"""
        url = f"{self.BASE_URL}/crm/v3/objects/contacts"

        # フィールドマッピング適用
        properties = self._apply_field_mapping(lead_data)

        async with httpx.AsyncClient() as client:
            response = await client.post(
                url,
                json={"properties": properties},
                headers={
                    "Authorization": f"Bearer {self.config['access_token']}",
                    "Content-Type": "application/json"
                }
            )
            response.raise_for_status()

            result = response.json()
            return result["id"]  # HubSpot Contact ID

    def _apply_field_mapping(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """DiagnoLeadsフィールドをHubSpotプロパティにマッピング"""
        default_mapping = {
            "name": ("firstname", "lastname"),
            "email": "email",
            "company": "company",
            "phone": "phone",
            "score": "hs_lead_score",
            "priority_level": "lead_priority",
        }

        properties = {}

        for diagno_field, hubspot_prop in default_mapping.items():
            if diagno_field in data:
                if diagno_field == "name":
                    parts = data["name"].split(" ", 1)
                    properties["firstname"] = parts[0]
                    properties["lastname"] = parts[1] if len(parts) > 1 else ""
                else:
                    properties[hubspot_prop] = str(data[diagno_field])

        return properties
```

---

### 4. CRM同期サービス

```python
# backend/app/services/crm_sync_service.py
from app.integrations.crm.salesforce_client import SalesforceClient
from app.integrations.crm.hubspot_client import HubSpotClient
from app.models.crm_integration import CRMIntegration, CRMSyncLog

class CRMSyncService:
    """CRM同期を管理するサービス"""

    async def sync_lead_to_crm(
        self,
        db: AsyncSession,
        lead_id: UUID,
        tenant_id: UUID,
        sync_type: str = "create"
    ) -> CRMSyncLog:
        """リードをCRMに同期"""

        # CRM統合設定を取得
        integration = await self._get_active_integration(db, tenant_id)
        if not integration:
            raise ValueError("CRM integration not configured")

        # リード情報を取得
        lead = await db.get(Lead, lead_id)
        if not lead:
            raise ValueError(f"Lead {lead_id} not found")

        # CRMクライアントを初期化
        client = self._get_crm_client(integration)

        # 同期実行
        sync_log = CRMSyncLog(
            integration_id=integration.id,
            lead_id=lead_id,
            sync_type=sync_type,
            direction="to_crm",
            status="pending"
        )

        try:
            # リードデータを準備
            lead_data = {
                "name": lead.name,
                "email": lead.email,
                "company": lead.company,
                "phone": lead.phone,
                "score": lead.score,
                "priority_level": lead.priority_level,
            }

            # CRMに送信
            if sync_type == "create":
                crm_id = await client.create_lead(lead_data)
            elif sync_type == "update":
                crm_id = lead.crm_external_id
                await client.update_lead(crm_id, lead_data)
            else:
                raise ValueError(f"Invalid sync_type: {sync_type}")

            # 成功を記録
            sync_log.status = "success"
            sync_log.crm_record_id = crm_id
            sync_log.synced_at = datetime.now(timezone.utc)

            # リードにCRM IDを保存
            lead.crm_external_id = crm_id

        except Exception as e:
            # 失敗を記録
            sync_log.status = "failed"
            sync_log.error_message = str(e)

            # リトライスケジュール（Trigger.devで実装予定）
            await self._schedule_retry(sync_log)

            raise

        finally:
            db.add(sync_log)
            await db.commit()

        return sync_log

    def _get_crm_client(self, integration: CRMIntegration):
        """CRMタイプに応じたクライアントを返す"""
        config = {
            "access_token": integration.decrypt_access_token(),
            "instance_url": integration.instance_url,
            "field_mappings": integration.field_mappings,
        }

        if integration.crm_type == "salesforce":
            return SalesforceClient(integration.id, config)
        elif integration.crm_type == "hubspot":
            return HubSpotClient(integration.id, config)
        else:
            raise ValueError(f"Unsupported CRM type: {integration.crm_type}")
```

---

## 🔒 セキュリティ

### 1. トークンの暗号化

```python
from cryptography.fernet import Fernet
from app.core.config import settings

class CRMIntegration(Base):
    access_token_encrypted = Column(Text)
    refresh_token_encrypted = Column(Text)

    def encrypt_access_token(self, token: str):
        """アクセストークンを暗号化して保存"""
        f = Fernet(settings.ENCRYPTION_KEY.encode())
        self.access_token_encrypted = f.encrypt(token.encode()).decode()

    def decrypt_access_token(self) -> str:
        """暗号化されたアクセストークンを復号"""
        f = Fernet(settings.ENCRYPTION_KEY.encode())
        return f.decrypt(self.access_token_encrypted.encode()).decode()
```

### 2. OAuth State検証（CSRF防止）

```python
import secrets

def generate_oauth_state(tenant_id: UUID) -> str:
    """安全なOAuthステートトークンを生成"""
    state = secrets.token_urlsafe(32)
    # Redisに保存（15分で有効期限切れ）
    redis_client.setex(f"oauth_state:{state}", 900, str(tenant_id))
    return state

def verify_oauth_state(state: str) -> UUID:
    """ステートトークンを検証してテナントIDを返す"""
    tenant_id = redis_client.get(f"oauth_state:{state}")
    if not tenant_id:
        raise ValueError("Invalid or expired OAuth state")
    redis_client.delete(f"oauth_state:{state}")
    return UUID(tenant_id.decode())
```

---

## 🧪 テスト戦略

### Unit Tests
- CRMClient基底クラスのテスト
- フィールドマッピングロジックのテスト
- トークン暗号化/復号のテスト

### Integration Tests
- Salesforce/HubSpot APIモックによる統合テスト
- OAuth認証フローのテスト
- リトライロジックのテスト
- Webhook受信処理のテスト

### E2E Tests
- DiagnoLeadsでリード作成 → Salesforceに反映確認
- Salesforceでステータス変更 → DiagnoLeadsに反映確認

---

## 📈 成功指標

- **同期成功率**: 99%以上
- **同期遅延**: リード作成から30秒以内にCRM反映
- **トークン更新成功率**: 100%（リフレッシュトークンによる自動更新）
- **ユーザー設定完了率**: OAuth認証完了率80%以上

---

## 🚀 実装ロードマップ

### Phase 1: 基盤構築（Week 1）
- [x] CRMベースクラス実装
- [ ] Salesforceクライアント実装
- [ ] HubSpotクライアント実装
- [ ] CRM統合データモデル作成

### Phase 2: OAuth認証（Week 2）
- [ ] Salesforce OAuth実装
- [ ] HubSpot OAuth実装
- [ ] トークン暗号化・更新ロジック
- [ ] フロントエンド接続UI

### Phase 3: 双方向同期（Week 3）
- [ ] DiagnoLeads → CRM同期（リアルタイム）
- [ ] CRM → DiagnoLeads同期（Webhook）
- [ ] フィールドマッピングUI
- [ ] 同期ログ・モニタリング

### Phase 4: 本番対応（Week 4）
- [ ] エラーハンドリング強化
- [ ] リトライ・バックオフロジック
- [ ] 監視・アラート設定
- [ ] ドキュメント・テスト完成

---

## 🔗 関連仕様

- [Lead Management](./lead-management.md) - リード管理機能
- [Lead Analysis & Actions](../ai/lead-analysis-actions.md) - AI分析機能
- [Resilience & Retry](../operations/resilience-retry.md) - リトライパターン
- [Multi-tenant Architecture](../auth/multi-tenant.md) - テナント分離

---

**実装ステータス**: 🔨 Phase 1 進行中（基盤構築）
**次のステップ**: Salesforceクライアント実装
