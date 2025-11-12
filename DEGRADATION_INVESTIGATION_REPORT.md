# 🔴 デグレード調査報告書

**調査開始日時**: 2025-11-12 07:15 JST  
**ステータス**: 🔍 **調査中 - 原因特定**  
**重大度**: ⚠️ **HIGH**

---

## 📊 現在の状況

### Git 状態

```
ブランチ: main
未コミット変更: 4個のファイル
- backend/app/api/v1/auth.py (修正中)
- backend/app/models/user.py (修正中)
- backend/app/schemas/auth.py (修正中)
- frontend/src/types/auth.ts (修正中)
```

### 最新コミット

```
d734231: Production deployment final checklist
5689db4: Restore demo account information (← 問題の可能性)
479f693: Complete OpenSpec documentation
```

---

## 🔍 変更内容の分析

### 1️⃣ auth.py の新規関数

```python
def build_user_response(user) -> UserResponse:
    """Build UserResponse with tenant information"""
    tenant_name = None
    tenant_slug = None
    tenant_plan = None
    
    if hasattr(user, 'tenant') and user.tenant:  # ⚠️ ここが問題の可能性
        tenant_name = user.tenant.name
        tenant_slug = user.tenant.slug
        tenant_plan = user.tenant.plan
    
    return UserResponse(...)
```

**潜在的な問題:**
- ❌ SQLAlchemy セッション close 後の遅延読み込みアクセス
- ❌ user.tenant が None (未ロード) の場合の処理
- ❌ DetachedInstanceError の可能性

### 2️⃣ UserResponse スキーマの変更

```python
class UserResponse(BaseModel):
    id: str
    email: str
    name: str
    role: str
    tenant_name: Optional[str] = None        # ✅ 追加
    tenant_slug: Optional[str] = None        # ✅ 追加
    tenant_plan: Optional[str] = None        # ✅ 追加
    created_at: datetime
```

**問題点:**
- ❌ フロントエンド型定義に対応していない
- ❌ レスポンス形式が変わった

### 3️⃣ auth.py のすべてのレスポンスで置換

```python
# 以下の4箇所で置換:
1. register エンドポイント
2. login エンドポイント  
3. login_json エンドポイント
4. get_current_user エンドポイント
5. refresh_token エンドポイント

# すべて:
user=UserResponse.model_validate(user)  # ← 古い方法
↓
user=build_user_response(user)         # ← 新しい方法
```

---

## ⚠️ デグレード症状（推定）

### 可能性のある問題

**問題1: SQLAlchemy DetachedInstanceError**
```python
# SQLAlchemy セッションが close された後に
# user.tenant にアクセスする
# → DetachedInstanceError が発生
# → API 500 エラー
```

**問題2: 遅延読み込みの失敗**
```python
# user.tenant が query で JOIN されていない場合
# user.tenant = None (未ロード) 
# → tenant_name = None (意図通り)
# ただし、将来的に問題になる可能性
```

**問題3: フロントエンド互換性**
```python
# UserResponse の形式が変わった
# フロントエンドが新しいフィールドを期待していない
# → 型エラーまたはレイアウトずれ
```

---

## 🔧 推奨される修正

### 修正1: SQLAlchemy セッション管理を改善

```python
def build_user_response(user) -> UserResponse:
    """Build UserResponse with tenant information"""
    # Option 1: Eager load の確認
    # Query で joinedload を使用していることを確認
    
    # Option 2: None チェック強化
    try:
        tenant_name = user.tenant.name if user.tenant else None
        tenant_slug = user.tenant.slug if user.tenant else None
        tenant_plan = user.tenant.plan if user.tenant else None
    except Exception:
        tenant_name = None
        tenant_slug = None
        tenant_plan = None
    
    return UserResponse(
        id=user.id,
        tenant_id=user.tenant_id,
        email=user.email,
        name=user.name,
        role=user.role,
        tenant_name=tenant_name,
        tenant_slug=tenant_slug,
        tenant_plan=tenant_plan,
        created_at=user.created_at,
    )
```

### 修正2: User モデルで Tenant をeager load

```python
# models/user.py
from sqlalchemy.orm import joinedload

# Query 時:
user = db.query(User).options(
    joinedload(User.tenant)
).filter(User.id == user_id).first()
```

### 修正3: フロントエンド型定義を更新

```typescript
// frontend/src/types/auth.ts
export interface UserResponse {
    id: string;
    email: string;
    name: string;
    role: string;
    tenant_name?: string;      // ✅ 追加
    tenant_slug?: string;      // ✅ 追加
    tenant_plan?: string;      // ✅ 追加
    created_at: string;
}
```

---

## 📋 診断チェックリスト

### 実行すべき確認

- [ ] Docker ログ確認: `docker logs diagnoleads-backend`
- [ ] API テスト実行: `/api/v1/auth/login` をテスト
- [ ] エラーログ確認: SQLAlchemy エラーメッセージ
- [ ] database セッション確認: close() タイミング
- [ ] User モデル確認: tenant リレーション定義
- [ ] フロントエンド console: ネットワークエラー確認

---

## 🎯 即座に実施すべき対応

### ステップ1: 変更をロールバック（最速復旧）

```bash
# 未コミット変更を破棄
git checkout backend/app/api/v1/auth.py
git checkout backend/app/schemas/auth.py
git checkout backend/app/models/user.py
git checkout frontend/src/types/auth.ts

# サーバー再起動
docker-compose restart
```

### ステップ2: 修正を適用

修正1-3 の方法を使用して、段階的に修正を適用。

### ステップ3: テスト実行

```bash
python test_production_readiness.py
# 9/9 ALL PASSING になることを確認
```

---

## 📝 根本原因の推定

**最も可能性の高い原因:**

```
SQLAlchemy の DetachedInstanceError

原因の流れ:
1. User をクエリ時に tenant を join していない
2. レスポンス生成時に user.tenant にアクセス
3. セッションが既に close されている
4. DetachedInstanceError → 500 エラー
```

**対応:**
- Eager loading を使用（joinedload）
- またはセッション内で tenant を取得
- またはセッション外での None チェック

---

## ✅ 次のアクション

### 直ちに実行

1. **ロールバック** (2分)
   ```bash
   git checkout -- .
   docker-compose restart
   ```

2. **テスト実行** (3分)
   ```bash
   python test_production_readiness.py
   ```

3. **ログ確認** (5分)
   - エラーメッセージ確認
   - SQLAlchemy ログ確認

4. **修正実装** (15分)
   - 上記修正1-3を適用
   - 段階的にテスト

---

## 📊 対応予想時間

```
ロールバック:     2分
テスト:          3分
診断:            10分
修正:            15分
再テスト:        5分
─────────────
合計:            35分
```

---

**🔴 デグレード調査 - 進行中** 🔍

*調査開始日時*: 2025-11-12 07:15 JST
*重大度*: HIGH
*対応: 即座にロールバック推奨*
