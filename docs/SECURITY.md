# セキュリティガイドライン

## 概要

DiagnoLeadsプロジェクトのセキュリティガイドラインです。開発時には必ずこのドキュメントを参照してください。

## 重要なセキュリティ要件

### 1. マルチテナント分離（最優先）

**要件**: テナント間のデータ漏洩を完全に防止すること

**実装規則**:
- すべてのデータベースクエリに`tenant_id`フィルタを適用
- APIエンドポイントで必ずテナント検証を実施
- ミドルウェアまたはデコレーターで自動的にテナントスコープを適用

**悪い例**:
```python
# テナントフィルタなし - セキュリティリスク
assessments = db.query(Assessment).all()
```

**良い例**:
```python
# 必ずテナントでフィルタリング
assessments = db.query(Assessment).filter(
    Assessment.tenant_id == current_tenant.id
).all()
```

**テスト要件**:
- `/backend/tests/integration/test_multi_tenant_isolation.py` で包括的なテストを実施
- すべての新機能に対してマルチテナント分離テストを追加

---

### 2. 認証トークンの安全な管理

**現在の問題（優先度: 高）**:
- フロントエンドで`localStorage`にJWTトークンを保存 → XSS脆弱性のリスク

**推奨される改善（Phase 2で実装予定）**:

#### バックエンド側
```python
# backend/app/api/v1/auth.py
from fastapi import Response

@router.post("/login")
async def login(response: Response, credentials: LoginRequest):
    # ... 認証処理 ...

    # HttpOnly Cookie にトークンを設定
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,      # XSS対策: JavaScriptからアクセス不可
        secure=True,        # HTTPS のみ (本番環境)
        samesite="strict",  # CSRF対策
        max_age=86400,      # 24時間
        domain=".diagnoleads.com",  # サブドメイン共有
    )

    return {"message": "ログイン成功"}
```

#### フロントエンド側
```typescript
// frontend/src/lib/apiClient.ts
// localStorage を削除し、Cookie ベースの認証に変更

const instance = axios.create({
  baseURL: API_BASE_URL,
  withCredentials: true,  // Cookie を自動送信
});

// リクエストインターセプターから localStorage の参照を削除
instance.interceptors.request.use((config) => {
  // Cookie が自動的に送信されるため、手動設定不要
  return config;
});
```

**移行計画**:
1. バックエンドでHttpOnly Cookie対応を追加
2. フロントエンドをCookieベースに変更
3. 既存のlocalStorageトークンをマイグレーション
4. 古い実装を削除

---

### 3. パスワード管理

**要件**:
- パスワードは必ずbcryptでハッシュ化
- ソルトラウンド: 12以上
- パスワード最小長: 8文字
- 複雑性要件: 英大文字・小文字・数字を含む

**実装**:
```python
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# ハッシュ化
hashed = pwd_context.hash(plain_password)

# 検証
is_valid = pwd_context.verify(plain_password, hashed)
```

---

### 4. SQLインジェクション対策

**要件**: すべてのデータベースクエリでORMのパラメータ化を使用

**悪い例**:
```python
# 生SQLでユーザー入力を直接埋め込み - 危険！
query = f"SELECT * FROM users WHERE email = '{email}'"
db.execute(query)
```

**良い例**:
```python
# ORMのパラメータ化クエリ - 安全
user = db.query(User).filter(User.email == email).first()
```

---

### 5. XSS (Cross-Site Scripting) 対策

**フロントエンド**:
- ユーザー入力は必ずエスケープ
- `dangerouslySetInnerHTML` は使用禁止
- DOMPurify などのライブラリを使用

**バックエンド**:
- APIレスポンスのContent-Typeを適切に設定
- CSP (Content Security Policy) ヘッダーを設定

```python
# FastAPI middleware でCSPヘッダーを追加
@app.middleware("http")
async def add_security_headers(request, call_next):
    response = await call_next(request)
    response.headers["Content-Security-Policy"] = "default-src 'self'"
    return response
```

---

### 6. CSRF (Cross-Site Request Forgery) 対策

**要件**:
- HttpOnly Cookie使用時は必ずCSRFトークンを実装
- SameSite=Strict または Lax を設定

**実装** (Cookie移行後):
```python
from fastapi_csrf_protect import CsrfProtect

@app.post("/api/v1/leads")
async def create_lead(csrf_protect: CsrfProtect = Depends()):
    await csrf_protect.validate_csrf(request)
    # ... 処理 ...
```

---

### 7. レート制限

**要件**:
- すべての公開APIエンドポイントにレート制限を適用
- 認証エンドポイントは特に厳格に

**実装**:
```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@app.post("/login")
@limiter.limit("5/minute")  # 1分間に5回まで
async def login(request: Request):
    # ... 認証処理 ...
```

**設定** (`backend/app/core/config.py`):
```python
RATE_LIMIT_ENABLED: bool = True
RATE_LIMIT_PER_MINUTE: int = 60
RATE_LIMIT_PER_HOUR: int = 1000
```

---

### 8. 機密情報の管理

**要件**:
- API鍵、DB認証情報は`.env`ファイルで管理
- `.env`ファイルは`.gitignore`に追加
- 本番環境では環境変数または暗号化ストレージを使用

**NG**:
```python
# ハードコーディング - 絶対NG
ANTHROPIC_API_KEY = "sk-ant-api03-xxxxx"
```

**OK**:
```python
# 環境変数から読み込み
from app.core.config import settings
ANTHROPIC_API_KEY = settings.ANTHROPIC_API_KEY
```

**本番環境での機密情報暗号化**:
```python
# backend/app/core/security.py
from cryptography.fernet import Fernet

class SecretManager:
    def __init__(self, key: str):
        self.cipher = Fernet(key.encode())

    def encrypt(self, plaintext: str) -> str:
        return self.cipher.encrypt(plaintext.encode()).decode()

    def decrypt(self, ciphertext: str) -> str:
        return self.cipher.decrypt(ciphertext.encode()).decode()
```

---

### 9. HTTPS / TLS

**要件**:
- 本番環境では必ずHTTPS使用
- 証明書は Let's Encrypt などの信頼できるCAから取得
- TLS 1.2以上を使用

**Nginx設定例**:
```nginx
server {
    listen 443 ssl http2;
    server_name api.diagnoleads.com;

    ssl_certificate /etc/letsencrypt/live/api.diagnoleads.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/api.diagnoleads.com/privkey.pem;

    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
}
```

---

### 10. 入力バリデーション

**要件**:
- すべてのユーザー入力をバリデーション
- Pydantic スキーマで型とバリデーションを定義

**実装例**:
```python
from pydantic import BaseModel, EmailStr, validator

class LeadCreate(BaseModel):
    email: EmailStr
    name: str
    company: str

    @validator('name')
    def name_must_not_be_empty(cls, v):
        if not v.strip():
            raise ValueError('名前は必須です')
        return v.strip()

    @validator('company')
    def company_max_length(cls, v):
        if len(v) > 100:
            raise ValueError('会社名は100文字以内です')
        return v
```

---

## セキュリティチェックリスト

新機能を実装する際は、以下をチェックしてください：

- [ ] マルチテナント分離テストを追加したか
- [ ] すべてのDBクエリに`tenant_id`フィルタがあるか
- [ ] ユーザー入力をバリデーションしたか
- [ ] パスワードをハッシュ化したか
- [ ] SQLインジェクション対策をしたか（ORMパラメータ化）
- [ ] XSS対策をしたか（エスケープ処理）
- [ ] APIエンドポイントにレート制限があるか
- [ ] 機密情報をハードコーディングしていないか
- [ ] HTTPSを使用しているか（本番環境）
- [ ] 認証・認可が適切に実装されているか

---

## セキュリティインシデント対応

セキュリティ上の問題を発見した場合:

1. **即座に報告**: プロジェクトオーナーに連絡
2. **公開しない**: GitHubのIssueなど公開の場で報告しない
3. **影響範囲の調査**: どのユーザー・データが影響を受けるか特定
4. **パッチの作成**: 最優先で修正パッチを作成
5. **デプロイ**: 即座に本番環境にデプロイ
6. **通知**: 影響を受けるユーザーに通知（必要に応じて）

---

## 参考資料

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [JWT Best Practices](https://auth0.com/blog/a-look-at-the-latest-draft-for-jwt-bcp/)
- [FastAPI Security](https://fastapi.tiangolo.com/tutorial/security/)
- [OWASP Multi-Tenancy Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Multitenant_Architecture_Cheat_Sheet.html)
