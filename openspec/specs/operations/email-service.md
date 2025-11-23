# Email Service

**Feature ID**: OPS-EMAIL-001
**Status**: Implemented
**Priority**: High (User Communication)
**Last Updated**: 2025-11-23

---

## 📋 Overview

DiagnoLeadsのトランザクショナルメール送信サービス。SMTP経由でパスワードリセット、ウェルカムメール、リード通知等を配信します。

### ビジネス価値

- **ユーザー体験向上**: 自動メール通知で即座にアクション可能
- **セキュリティ**: パスワードリセットの安全な処理
- **営業効率化**: リード獲得時の即座通知
- **エンゲージメント**: ウェルカムメールで初期体験向上

---

## 🎯 主要機能

### 1. 送信メール種別（3種類）

| メール種別 | トリガー | 対象者 | 内容 |
|-----------|---------|--------|------|
| **パスワードリセット** | ユーザーがリセット要求 | エンドユーザー | リセットリンク（1時間有効） |
| **ウェルカムメール** | 新規ユーザー登録 | 新規ユーザー | サービス紹介、開始手順 |
| **リード通知** | 診断完了・リード獲得 | テナント管理者 | リード情報、スコア、アクション |

### 2. メール形式

- **HTML**: レスポンシブデザイン、ブランドカラー
- **プレーンテキスト**: フォールバック対応
- **マルチパート**: HTML/テキスト両方を含む

---

## 🔧 EmailService API

### send_email(to_email, subject, html_content, text_content=None) -> bool

基本メール送信

```python
email_service = EmailService()

success = email_service.send_email(
    to_email="user@example.com",
    subject="お知らせ",
    html_content="<h1>こんにちは</h1>",
    text_content="こんにちは",
)
```

**戻り値**: 送信成功時True、失敗時False

---

### send_password_reset_email(to_email, reset_token, user_name=None) -> bool

パスワードリセットメール

```python
success = email_service.send_password_reset_email(
    to_email="user@example.com",
    reset_token="abc123xyz",
    user_name="山田太郎",
)
```

**リセットリンク形式**: `{FRONTEND_URL}/reset-password?token={reset_token}`

**有効期限**: 1時間

**HTMLテンプレート**:
- ヘッダー: DiagnoLeadsブランディング
- 本文: リセット手順、ボタン
- フッター: 著作権表示

---

### send_welcome_email(to_email, user_name) -> bool

ウェルカムメール

```python
success = email_service.send_welcome_email(
    to_email="newuser@example.com",
    user_name="佐藤花子",
)
```

**内容**:
- 登録感謝メッセージ
- サービス概要
- 次のステップ（診断作成）

---

### send_lead_notification_email(to_email, lead_name, lead_email, assessment_title, score) -> bool

リード通知メール

```python
success = email_service.send_lead_notification_email(
    to_email="admin@company.com",
    lead_name="鈴木一郎",
    lead_email="suzuki@example.com",
    assessment_title="マーケティング成熟度診断",
    score=85,
)
```

**内容**:
- 🎉 新リード獲得の祝福
- リード基本情報（名前、メール、スコア）
- ダッシュボードへのリンク（未実装）

---

## ⚙️ SMTP設定

### 環境変数

```bash
# .env
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=noreply@diagnoleads.com
SMTP_PASSWORD=app_password_here
FROM_EMAIL=noreply@diagnoleads.com
FROM_NAME=DiagnoLeads
FRONTEND_URL=https://app.diagnoleads.com
```

### SMTP接続フロー

```
1. SMTP接続（SMTP_HOST:SMTP_PORT）
2. STARTTLS暗号化（port 587の場合）
3. ログイン認証（SMTP_USER/SMTP_PASSWORD）
4. メール送信
5. 接続クローズ
```

---

## 📧 メールテンプレート設計

### 共通デザイン要素

```html
<style>
body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
.container { max-width: 600px; margin: 0 auto; padding: 20px; }
.header { background-color: #3b82f6; color: white; padding: 20px; }
.content { padding: 20px; background-color: #f9fafb; }
.button {
    display: inline-block;
    padding: 12px 24px;
    background-color: #3b82f6;
    color: white;
    border-radius: 6px;
}
.footer { padding: 20px; font-size: 12px; color: #6b7280; }
</style>
```

### パスワードリセットテンプレート

```html
<div class="container">
    <div class="header"><h1>DiagnoLeads</h1></div>
    <div class="content">
        <h2>パスワードリセットのリクエスト</h2>
        <p>こんにちは、{user_name}さん</p>
        <p>パスワードリセットのリクエストを受け付けました。</p>
        <p><a href="{reset_link}" class="button">パスワードをリセット</a></p>
        <p>このリンクは1時間後に無効になります。</p>
    </div>
    <div class="footer">© 2025 DiagnoLeads</div>
</div>
```

---

## 🛡️ セキュリティ機能

### 1. SMTP設定未構成時の安全動作

```python
if not self.smtp_host or not self.smtp_user:
    logger.warning("SMTP not configured. Email not sent.")
    logger.info(f"Would send email to {to_email}: {subject}")
    return False
```

**開発環境**: SMTP未設定でもアプリケーションが動作（ログのみ）

### 2. エラーハンドリング

```python
try:
    # SMTP送信処理
    logger.info(f"Email sent successfully to {to_email}")
    return True
except Exception as e:
    logger.error(f"Failed to send email to {to_email}: {e}")
    return False
```

**失敗時**: エラーログ記録、False返却（例外は発生させない）

---

## 📊 使用統計（想定）

| メール種別 | 月間送信数 | 開封率 | クリック率 |
|-----------|-----------|--------|-----------|
| パスワードリセット | 120通 | 95% | 88% |
| ウェルカムメール | 45通 | 72% | 34% |
| リード通知 | 850通 | 98% | 76% |

---

## 🚀 将来の改善

### 1. メールテンプレートエンジン

Jinja2でテンプレート管理：

```python
from jinja2 import Environment, FileSystemLoader

env = Environment(loader=FileSystemLoader('templates/email'))
template = env.get_template('password_reset.html')
html_content = template.render(user_name=user_name, reset_link=reset_link)
```

### 2. 配信サービス統合

SendGrid/AWS SES等のクラウドサービスへの移行：

```python
class SendGridEmailService(EmailService):
    def send_email(self, to_email, subject, html_content, text_content=None):
        sg = sendgrid.SendGridAPIClient(api_key=settings.SENDGRID_API_KEY)
        message = Mail(...)
        sg.send(message)
```

### 3. メール開封・クリック追跡

```python
# トラッキングピクセル
<img src="{BACKEND_URL}/track/open/{email_id}" width="1" height="1" />

# トラッキングリンク
<a href="{BACKEND_URL}/track/click/{email_id}?url={target_url}">クリック</a>
```

### 4. テナント別カスタマイズ

テナントごとのブランディング：

```python
class TenantEmailService:
    def get_template(self, tenant_id, template_name):
        # テナント固有のロゴ、カラー、フッター
        tenant = db.query(Tenant).get(tenant_id)
        return {
            "logo_url": tenant.logo_url,
            "primary_color": tenant.brand_color,
            "from_name": tenant.company_name,
        }
```

### 5. 配信スケジューリング

```python
class ScheduledEmailService:
    def schedule_email(self, to_email, subject, content, send_at):
        """指定時刻にメール送信"""
        task = ScheduledEmail(
            to_email=to_email,
            subject=subject,
            content=content,
            send_at=send_at,
            status="pending",
        )
        db.add(task)
```

### 6. A/Bテスト

```python
def send_with_ab_test(to_email, template_variant):
    """複数テンプレートで効果測定"""
    if random() < 0.5:
        return send_email(..., template="variant_a.html")
    else:
        return send_email(..., template="variant_b.html")
```

---

## 📂 実装ファイル

| ファイル | 説明 |
|---------|------|
| `/backend/app/services/email_service.py` | EmailServiceクラス（322行） |

---

## 🔗 関連仕様

- [Authentication](../auth/authentication.md) - パスワードリセット連携
- [Lead Management](../features/lead-management.md) - リード通知連携

---

**実装ステータス**: ✅ 完全実装済み（基本機能）
**拡張機能**: ⏳ テンプレートエンジン、配信サービス統合、追跡機能は未実装
