# Audit Logging

**Feature ID**: SEC-AUDIT-001
**Status**: Implemented
**Priority**: Critical (Compliance Requirement)
**Last Updated**: 2025-11-23

---

## 📋 Overview

DiagnoLeadsの包括的な監査ログシステム。マスターデータの変更履歴を記録し、GDPR・SOC2コンプライアンス、セキュリティ監視、問題調査を実現します。

### ビジネス価値

- **コンプライアンス対応**: GDPR・SOC2・ISO27001要件を満たす監査証跡
- **セキュリティ監視**: 不正アクセス・データ改ざんの早期検出
- **問題調査**: 「誰が・いつ・何を・どう変更したか」を追跡
- **説明責任**: 顧客への変更履歴開示、内部監査対応

---

## 🎯 主要機能

### 1. マスターデータ変更追跡

4種類の重要エンティティの全変更を記録：

| エンティティ | 説明 | 追跡内容 |
|------------|------|---------|
| **TENANT** | テナント情報 | 企業名、契約プラン、設定変更 |
| **USER** | ユーザー情報 | 権限変更、ロール変更、削除 |
| **TOPIC** | 診断トピック | トピック追加・編集・削除 |
| **INDUSTRY** | 業界分類 | 業界マスター追加・編集・削除 |

### 2. アクション分類

3種類の変更アクションを個別に記録：

| アクション | 説明 | 記録内容 |
|----------|------|---------|
| **CREATE** | 新規作成 | `new_values`のみ記録 |
| **UPDATE** | 更新 | `old_values`と`new_values`の差分記録 |
| **DELETE** | 削除 | `old_values`のみ記録（復元用） |

### 3. 変更詳細の記録

各監査ログに以下を記録：

- **変更前の値（old_values）**: 更新・削除時の元データ（JSON）
- **変更後の値（new_values）**: 作成・更新時の新データ（JSON）
- **変更理由（reason）**: オプションでユーザーが入力可能
- **実行者情報（user_id）**: 変更を実行したユーザー
- **メタデータ**: IPアドレス、User Agent、タイムスタンプ

### 4. ユーザーアクティビティ追跡

- ユーザー別の全操作履歴を時系列で取得
- デフォルト30日、最大365日まで遡及可能
- 不審なアクティビティの検出に活用

---

## 📊 データモデル

### AuditLog

**テーブル**: `audit_logs`

| フィールド | 型 | 制約 | 説明 |
|-----------|-----|-----|------|
| id | UUID | PK | 監査ログID |
| tenant_id | UUID | FK(Tenant), NOT NULL, INDEX | テナント所有者 |
| user_id | UUID | FK(User), NOT NULL | 変更実行ユーザー |
| entity_type | String(50) | NOT NULL, INDEX | エンティティ種別 |
| entity_id | UUID | NOT NULL, INDEX | 変更対象のエンティティID |
| action | String(20) | NOT NULL, INDEX | アクション（CREATE/UPDATE/DELETE） |
| entity_name | String(255) | NULLABLE | エンティティ名（表示用） |
| old_values | JSON | NULLABLE | 変更前の値（UPDATE/DELETE） |
| new_values | JSON | NULLABLE | 変更後の値（CREATE/UPDATE） |
| reason | Text | NULLABLE | 変更理由（オプション） |
| ip_address | String(45) | NULLABLE | クライアントIP（IPv4/IPv6） |
| user_agent | String(500) | NULLABLE | ブラウザUser Agent |
| created_at | Timestamp | DEFAULT now(), NOT NULL, INDEX | 変更実行時刻 |

**インデックス**:
- `[tenant_id]` - テナント別監査ログ取得
- `[entity_type]` - エンティティ種別フィルタリング
- `[entity_id]` - 特定エンティティの変更履歴
- `[action]` - アクション別分析
- `[created_at]` - 時系列分析

**リレーションシップ**:
- Tenant ← 1:N → AuditLog
- User ← 1:N → AuditLog

---

## 🔌 API仕様

### 1. 監査ログ一覧取得

```http
GET /api/v1/audit-logs?tenant_id={tenant_id}&entity_type=USER&action=UPDATE&skip=0&limit=100
Authorization: Bearer {token}
```

**クエリパラメータ**:
| パラメータ | 型 | 必須 | 説明 |
|-----------|-----|-----|------|
| tenant_id | UUID | ✅ | テナントID（必須） |
| entity_type | String | ❌ | エンティティフィルター（TENANT/USER/TOPIC/INDUSTRY） |
| entity_id | UUID | ❌ | 特定エンティティID |
| action | String | ❌ | アクションフィルター（CREATE/UPDATE/DELETE） |
| skip | Integer | ❌ | ページネーション開始位置（デフォルト: 0） |
| limit | Integer | ❌ | 取得件数（1-1000、デフォルト: 100） |

**レスポンス**:
```json
{
  "total": 456,
  "skip": 0,
  "limit": 100,
  "items": [
    {
      "id": "audit-uuid-123",
      "tenant_id": "tenant-uuid",
      "user_id": "user-uuid",
      "entity_type": "USER",
      "entity_id": "changed-user-uuid",
      "action": "UPDATE",
      "entity_name": "山田太郎",
      "old_values": {
        "role": "user",
        "email": "yamada@example.com"
      },
      "new_values": {
        "role": "admin",
        "email": "yamada@example.com"
      },
      "reason": "管理者権限付与のため",
      "ip_address": "203.0.113.45",
      "user_agent": "Mozilla/5.0...",
      "created_at": "2025-11-23T10:15:30Z"
    }
  ]
}
```

**認証**: JWT必須
**認可**: System Admin（全テナント）、Tenant Admin/User（自テナントのみ）

---

### 2. エンティティ変更履歴取得

```http
GET /api/v1/audit-logs/entity/{entity_type}/{entity_id}?tenant_id={tenant_id}
Authorization: Bearer {token}
```

**パス パラメータ**:
- `entity_type`: エンティティ種別（TENANT/USER/TOPIC/INDUSTRY）
- `entity_id`: エンティティID

**用途**: 特定エンティティの完全な変更履歴を時系列で取得

**レスポンス**:
```json
[
  {
    "id": "audit-uuid-001",
    "action": "CREATE",
    "new_values": {"name": "佐藤花子", "role": "user"},
    "created_at": "2025-11-01T09:00:00Z"
  },
  {
    "id": "audit-uuid-002",
    "action": "UPDATE",
    "old_values": {"role": "user"},
    "new_values": {"role": "admin"},
    "reason": "昇格のため",
    "created_at": "2025-11-15T14:30:00Z"
  },
  {
    "id": "audit-uuid-003",
    "action": "UPDATE",
    "old_values": {"email": "sato@example.com"},
    "new_values": {"email": "hanako.sato@example.com"},
    "created_at": "2025-11-20T11:45:00Z"
  }
]
```

**認証**: JWT必須
**認可**: テナント内アクセスのみ

---

### 3. ユーザーアクティビティ取得

```http
GET /api/v1/audit-logs/user/{user_id}?tenant_id={tenant_id}&days=30
Authorization: Bearer {token}
```

**パス パラメータ**:
- `user_id`: ユーザーID

**クエリパラメータ**:
- `tenant_id`: テナントID（必須）
- `days`: 遡及日数（1-365、デフォルト: 30）

**用途**: 特定ユーザーの全操作履歴を取得（セキュリティ監視、内部監査）

**レスポンス**:
```json
[
  {
    "id": "audit-uuid-789",
    "entity_type": "TOPIC",
    "entity_id": "topic-uuid",
    "action": "CREATE",
    "entity_name": "マーケティング診断",
    "new_values": {"name": "マーケティング診断", "description": "..."},
    "created_at": "2025-11-23T08:30:00Z"
  },
  {
    "id": "audit-uuid-790",
    "entity_type": "USER",
    "entity_id": "other-user-uuid",
    "action": "UPDATE",
    "entity_name": "鈴木一郎",
    "old_values": {"role": "user"},
    "new_values": {"role": "admin"},
    "reason": "権限変更",
    "created_at": "2025-11-22T16:00:00Z"
  }
]
```

**認証**: JWT必須
**認可**: テナント内アクセスのみ

---

## 🔒 セキュリティ機能

### 1. テナント分離

- すべての監査ログに`tenant_id`が必須
- Row-Level Security (RLS) でテナント間のデータ漏洩を防止
- System Adminのみ全テナントの監査ログ閲覧可

### 2. 権限チェック

```python
def check_audit_access(current_user: User, requested_tenant_id: UUID):
    """監査ログアクセス権限検証"""
    # System Admin: 全テナントOK
    if current_user.role == "system_admin":
        return True

    # Tenant Admin/User: 自テナントのみOK
    if current_user.tenant_id == requested_tenant_id:
        return True

    raise HTTPException(status_code=403, detail="Access forbidden")
```

### 3. 機密情報の保護

**記録対象外のフィールド**:
- パスワード（ハッシュも含む）
- APIキー、トークン
- クレジットカード情報
- その他のPII（個人情報）

**実装例**:
```python
# old_valuesとnew_valuesからパスワードを除外
safe_old_values = {k: v for k, v in old_values.items() if k != "password"}
safe_new_values = {k: v for k, v in new_values.items() if k != "password"}
```

---

## 📈 監査ログの活用

### 1. セキュリティ監視

```sql
-- 24時間以内の全DELETE操作を確認
SELECT
    entity_type,
    entity_name,
    user_id,
    created_at
FROM audit_logs
WHERE action = 'DELETE'
  AND created_at >= NOW() - INTERVAL '24 hours'
ORDER BY created_at DESC;
```

### 2. ユーザー権限変更の追跡

```sql
-- ユーザーロール変更履歴
SELECT
    entity_name AS user_name,
    old_values->>'role' AS old_role,
    new_values->>'role' AS new_role,
    reason,
    created_at
FROM audit_logs
WHERE entity_type = 'USER'
  AND action = 'UPDATE'
  AND (old_values ? 'role' OR new_values ? 'role')
ORDER BY created_at DESC;
```

### 3. 月次監査レポート

```sql
-- 月間アクション統計
SELECT
    entity_type,
    action,
    COUNT(*) AS change_count
FROM audit_logs
WHERE created_at >= DATE_TRUNC('month', NOW())
GROUP BY entity_type, action
ORDER BY change_count DESC;
```

**出力例**:
| entity_type | action | change_count |
|------------|--------|--------------|
| USER | UPDATE | 125 |
| TOPIC | CREATE | 87 |
| USER | CREATE | 45 |
| INDUSTRY | UPDATE | 23 |
| TENANT | UPDATE | 12 |

### 4. 不審なアクティビティ検出

```sql
-- 1ユーザーが1時間に10件以上の削除を実行
SELECT
    user_id,
    COUNT(*) AS delete_count,
    MIN(created_at) AS first_delete,
    MAX(created_at) AS last_delete
FROM audit_logs
WHERE action = 'DELETE'
  AND created_at >= NOW() - INTERVAL '1 hour'
GROUP BY user_id
HAVING COUNT(*) >= 10;
```

---

## 🛠️ 実装フロー

### 1. 監査ログの自動記録

**サービス層での実装例**:
```python
from app.services.audit_service import AuditService

class UserService:
    def update_user(self, db: Session, user_id: UUID, data: UserUpdate, current_user: User):
        # ユーザー取得
        user = db.query(User).filter(User.id == user_id).first()
        old_values = {"role": user.role, "email": user.email}

        # ユーザー更新
        user.role = data.role
        user.email = data.email
        db.commit()

        new_values = {"role": user.role, "email": user.email}

        # 監査ログ記録
        AuditService.log_change(
            db=db,
            tenant_id=user.tenant_id,
            user_id=current_user.id,
            entity_type="USER",
            entity_id=user.id,
            action="UPDATE",
            entity_name=user.name,
            old_values=old_values,
            new_values=new_values,
            reason="ユーザー情報更新",
        )

        return user
```

### 2. API層での実装例

```python
@router.put("/users/{user_id}")
async def update_user(
    user_id: UUID,
    data: UserUpdate,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # ユーザー更新（監査ログは自動記録）
    user = UserService.update_user(db, user_id, data, current_user)

    # IPアドレス・User Agentを追加記録（オプション）
    ip_address = request.client.host
    user_agent = request.headers.get("user-agent")

    return user
```

### 3. フロントエンドからの利用

```typescript
// 監査ログ一覧取得
const auditLogs = await api.get('/api/v1/audit-logs', {
  params: {
    tenant_id: currentTenant.id,
    entity_type: 'USER',
    action: 'UPDATE',
    skip: 0,
    limit: 50
  }
});

// 特定エンティティの変更履歴
const history = await api.get(`/api/v1/audit-logs/entity/USER/${userId}`, {
  params: { tenant_id: currentTenant.id }
});

// ユーザーアクティビティ
const activity = await api.get(`/api/v1/audit-logs/user/${userId}`, {
  params: { tenant_id: currentTenant.id, days: 7 }
});
```

---

## 🗑️ データ保持ポリシー

### 自動削除ルール

```python
# audit_service.py
@staticmethod
def cleanup_old_logs(db: Session, days: int = 90) -> int:
    """90日以上前の監査ログを削除"""
    cutoff_date = datetime.utcnow() - timedelta(days=days)
    count = db.query(AuditLog).filter(
        AuditLog.created_at < cutoff_date
    ).delete()
    db.commit()
    return count
```

**保持期間**:
| 環境 | 保持期間 | 理由 |
|-----|---------|------|
| **production** | 90日 | GDPR準拠、ストレージコスト最適化 |
| **staging** | 30日 | 検証期間 |
| **development** | 7日 | 開発用途 |

**延長オプション**:
- コンプライアンス要件により1年・3年保持も設定可能
- エクスポート機能でアーカイブ保存推奨

---

## 📊 ダッシュボード表示（未実装）

### 管理画面イメージ

```
┌─────────────────────────────────────────────────────┐
│ 監査ログ                                             │
├─────────────────────────────────────────────────────┤
│                                                     │
│ フィルター                                           │
│ ┌────────────┬────────────┬────────────┐          │
│ │ エンティティ │ アクション  │ 期間        │          │
│ │ [USER    ▼] │ [UPDATE  ▼] │ [7日間   ▼] │          │
│ └────────────┴────────────┴────────────┘          │
│                                                     │
│ 📋 変更履歴                                          │
│ ┌───────────────────────────────────────────┐     │
│ │ 2025-11-23 10:15 | 山田太郎            │     │
│ │ USER UPDATE: 佐藤花子                  │     │
│ │ role: user → admin                     │     │
│ │ 理由: 昇格のため                        │     │
│ │                                           │     │
│ │ 2025-11-23 09:30 | 鈴木一郎            │     │
│ │ TOPIC CREATE: マーケティング診断        │     │
│ │                                           │     │
│ │ 2025-11-22 16:00 | 田中次郎            │     │
│ │ USER DELETE: 高橋三郎                   │     │
│ │ 理由: 退職のため                        │     │
│ └───────────────────────────────────────────┘     │
│                                                     │
│ 📊 統計                                              │
│ 今月の変更数: 456件                                  │
│  - CREATE: 187件 (41%)                              │
│  - UPDATE: 234件 (51%)                              │
│  - DELETE: 35件 (8%)                                │
│                                                     │
│ 最も活発なユーザー:                                  │
│ 1. 山田太郎 (87件)                                   │
│ 2. 佐藤花子 (65件)                                   │
│ 3. 鈴木一郎 (54件)                                   │
└─────────────────────────────────────────────────────┘
```

---

## 🧪 テスト

### 実装済みテスト

- 監査ログ記録のテスト（CREATE/UPDATE/DELETE）
- テナント分離検証テスト
- API エンドポイントテスト
- 権限チェックテスト

### テストケース例

```python
def test_audit_log_creation(db_session, test_tenant, test_user):
    """監査ログ作成のテスト"""
    AuditService.log_change(
        db=db_session,
        tenant_id=test_tenant.id,
        user_id=test_user.id,
        entity_type="USER",
        entity_id=test_user.id,
        action="UPDATE",
        old_values={"role": "user"},
        new_values={"role": "admin"},
    )

    logs, total = AuditService.get_audit_logs(
        db=db_session,
        tenant_id=test_tenant.id,
    )

    assert total == 1
    assert logs[0].action == "UPDATE"
```

---

## 📂 実装ファイル

| ファイル | 説明 |
|---------|------|
| `/backend/app/models/audit_log.py` | AuditLogモデル定義 |
| `/backend/app/services/audit_service.py` | 監査ログサービス（4.1KB） |
| `/backend/app/api/v1/audit_logs.py` | APIエンドポイント（3件） |
| `/backend/app/schemas/audit_log.py` | Pydanticスキーマ定義 |
| `/backend/alembic/versions/xxx_add_audit_logs_table.py` | マイグレーション |

---

## 🚀 将来の改善

1. **リアルタイムアラート**: 不審なアクティビティ検出時にSlack/Email通知
2. **差分ビューワー**: old_values と new_values の視覚的な差分表示
3. **監査レポート自動生成**: 月次・四半期・年次レポートのPDF出力
4. **変更承認ワークフロー**: 重要な変更に対する承認プロセス
5. **AI異常検出**: 機械学習による不正操作パターン検出
6. **エクスポート機能**: 監査ログのCSV/Excel/JSON エクスポート
7. **長期アーカイブ**: S3/GCSへの自動アーカイブ保存
8. **詳細フィルタリング**: IPアドレス範囲、User Agentでのフィルター
9. **可視化ダッシュボード**: 時系列グラフ、ヒートマップ表示
10. **SIEM統合**: Splunk、DataDog等のSIEMツールとの連携

---

## 🔗 関連仕様

- [Error Logging & Monitoring](../operations/error-logging-monitoring.md) - エラーログシステム
- [Multi-tenant Architecture](../auth/multi-tenant.md) - テナント分離アーキテクチャ
- [Authentication](../auth/authentication.md) - 認証・認可

---

**実装ステータス**: ✅ 完全実装済み（ダッシュボードUI未実装）
