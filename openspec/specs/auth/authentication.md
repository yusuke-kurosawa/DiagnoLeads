# Authentication Specification

## Feature: User Authentication

### Requirement: User login with email and password

ユーザーはメールアドレスとパスワードでログインできる。

#### Scenario: Successful login

**GIVEN** ユーザーが登録済みである
**AND** 認証情報が正しい
**WHEN** ユーザーがログインフォームに以下を入力する:
  - Email: "user@example.com"
  - Password: "ValidPassword123!"
**AND** "ログイン"ボタンをクリックする
**THEN** システムは認証情報を検証する
**AND** JWTトークンを生成して返す
**AND** ユーザーをダッシュボードにリダイレクトする
**AND** トークンをローカルストレージに保存する

**Technical Requirements:**
- JWT有効期限は24時間 SHALL
- パスワードはbcryptでハッシュ化 SHALL
- HTTPS経由でのみ通信 SHALL
- ログイン試行は5回まで、その後15分間ロックアウト SHALL

#### Scenario: Invalid credentials

**GIVEN** ユーザーが登録済みである
**WHEN** ユーザーが誤ったパスワードを入力する
**THEN** エラーメッセージ "メールアドレスまたはパスワードが正しくありません" を表示する
**AND** ログインを拒否する
**AND** 失敗回数をカウントする

#### Scenario: Account locked after failed attempts

**GIVEN** ユーザーが5回連続でログインに失敗した
**WHEN** ユーザーが再度ログインを試みる
**THEN** エラーメッセージ "アカウントが一時的にロックされています。15分後に再試行してください" を表示する
**AND** ログインを拒否する

### Requirement: User registration

新規ユーザーがアカウントを作成できる。

#### Scenario: Successful registration

**GIVEN** ユーザーが登録されていない
**WHEN** ユーザーが登録フォームに以下を入力する:
  - Name: "山田太郎"
  - Email: "yamada@example.com"
  - Password: "SecurePass123!"
  - Tenant Name: "株式会社サンプル"
**AND** "登録"ボタンをクリックする
**THEN** システムは以下を実行する:
  - メールアドレスの重複チェック
  - パスワード強度の検証
  - 新しいテナントを作成
  - 新しいユーザーを作成（テナント管理者ロール）
  - 確認メールを送信
**AND** ログイン画面にリダイレクトする

**Technical Requirements:**
- パスワードは8文字以上、英大文字・小文字・数字を含む SHALL
- メールアドレスは一意 SHALL
- テナントIDはUUID形式 SHALL
- 初回ユーザーは自動的にテナント管理者となる SHALL

#### Scenario: Email already exists

**GIVEN** メールアドレス "existing@example.com" が既に登録されている
**WHEN** ユーザーが同じメールアドレスで登録を試みる
**THEN** エラーメッセージ "このメールアドレスは既に使用されています" を表示する
**AND** 登録を拒否する

### Requirement: Password reset

ユーザーはパスワードをリセットできる。

#### Scenario: Request password reset

**GIVEN** ユーザーが登録済みである
**WHEN** ユーザーがパスワードリセット画面でメールアドレスを入力する
**AND** "リセットメールを送信"ボタンをクリックする
**THEN** システムはリセットトークン付きメールを送信する
**AND** トークンの有効期限は1時間とする
**AND** 確認メッセージ "パスワードリセットメールを送信しました" を表示する

#### Scenario: Reset password with valid token

**GIVEN** ユーザーがリセットメールのリンクをクリックした
**AND** トークンが有効である
**WHEN** ユーザーが新しいパスワードを入力する
**THEN** システムはパスワードを更新する
**AND** 成功メッセージを表示する
**AND** ログイン画面にリダイレクトする

### Requirement: Token refresh

アクセストークンの有効期限が切れる前に更新できる。

#### Scenario: Refresh access token

**GIVEN** ユーザーがログイン済みである
**AND** アクセストークンの有効期限が1時間以内である
**WHEN** システムが自動的にトークン更新をリクエストする
**THEN** 新しいアクセストークンを発行する
**AND** ローカルストレージを更新する

**Technical Requirements:**
- リフレッシュトークンの有効期限は7日間 SHALL
- アクセストークン有効期限の80%経過時点で自動更新 SHALL

### Requirement: Logout

ユーザーはログアウトできる。

#### Scenario: User logs out

**GIVEN** ユーザーがログイン済みである
**WHEN** ユーザーが"ログアウト"ボタンをクリックする
**THEN** ローカルストレージからトークンを削除する
**AND** ログイン画面にリダイレクトする

---

## API Specification

### POST /api/v1/auth/login

**Request:**
```json
{
  "email": "user@example.com",
  "password": "password123"
}
```

**Response (200 OK):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "Bearer",
  "expires_in": 86400,
  "user": {
    "id": "uuid",
    "email": "user@example.com",
    "name": "山田太郎",
    "tenant_id": "tenant-uuid",
    "role": "tenant_admin"
  }
}
```

**Error Response (401 Unauthorized):**
```json
{
  "error": "INVALID_CREDENTIALS",
  "message": "メールアドレスまたはパスワードが正しくありません"
}
```

### POST /api/v1/auth/register

**Request:**
```json
{
  "name": "山田太郎",
  "email": "yamada@example.com",
  "password": "SecurePass123!",
  "tenant_name": "株式会社サンプル"
}
```

**Response (201 Created):**
```json
{
  "user_id": "uuid",
  "tenant_id": "tenant-uuid",
  "message": "登録が完了しました。ログインしてください。"
}
```

### POST /api/v1/auth/refresh

**Request:**
```json
{
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Response (200 OK):**
```json
{
  "access_token": "new-token",
  "expires_in": 86400
}
```

### POST /api/v1/auth/logout

**Request:**
Headers: `Authorization: Bearer {token}`

**Response (200 OK):**
```json
{
  "message": "ログアウトしました"
}
```

---

## Security Requirements

### Password Policy
- Minimum 8 characters
- At least one uppercase letter
- At least one lowercase letter
- At least one number
- Special characters recommended

### Token Security
- JWTs signed with HS256 algorithm
- Secret key stored in environment variable
- Tokens include tenant_id claim for multi-tenant isolation

### Rate Limiting
- Login endpoint: 5 attempts per 15 minutes per IP
- Registration endpoint: 3 attempts per hour per IP
- Password reset: 3 attempts per hour per email

### HTTPS Only
- All authentication endpoints SHALL require HTTPS in production
- HTTP Strict Transport Security (HSTS) enabled
