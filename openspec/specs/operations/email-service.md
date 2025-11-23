# Email Service

**Feature ID**: OPS-EMAIL-001
**Status**: Implemented
**Priority**: High (User Communication)
**Last Updated**: 2025-11-23

---

## 📋 Overview

DiagnoLeadsのトランザクショナルメール送信サービス。SMTP経由でパスワードリセット、ウェルカムメール、リード通知等を配信します。**Jinja2テンプレートエンジン**を使用して、カスタマイズ可能なHTMLメールを生成します。

### ビジネス価値

- **ユーザー体験向上**: 自動メール通知で即座にアクション可能
- **セキュリティ**: パスワードリセットの安全な処理
- **営業効率化**: リード獲得時の即座通知
- **エンゲージメント**: ウェルカムメールで初期体験向上
- **ブランディング**: テナントごとのロゴ、カラーでカスタマイズ可能

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

### send_password_reset_email(to_email, reset_token, user_name=None, brand_color=None, logo_url=None) -> bool

パスワードリセットメール（Jinja2テンプレート使用）

```python
success = email_service.send_password_reset_email(
    to_email="user@example.com",
    reset_token="abc123xyz",
    user_name="山田太郎",
    brand_color="#3b82f6",  # オプション: カスタムブランドカラー
    logo_url="https://cdn.example.com/logo.png",  # オプション: テナントロゴ
)
```

**リセットリンク形式**: `{FRONTEND_URL}/reset-password?token={reset_token}`

**有効期限**: 1時間

**HTMLテンプレート**:
- ヘッダー: DiagnoLeadsブランディング
- 本文: リセット手順、ボタン
- フッター: 著作権表示

---

### send_welcome_email(to_email, user_name, brand_color=None, brand_color_secondary=None, logo_url=None, dashboard_url=None) -> bool

ウェルカムメール（Jinja2テンプレート使用）

```python
success = email_service.send_welcome_email(
    to_email="newuser@example.com",
    user_name="佐藤花子",
    brand_color="#3b82f6",  # オプション: メインカラー
    brand_color_secondary="#2563eb",  # オプション: グラデーション用
    logo_url="https://cdn.example.com/logo.png",  # オプション: テナントロゴ
    dashboard_url="https://app.diagnoleads.com/dashboard",  # オプション
)
```

**内容**:
- 登録感謝メッセージ
- サービス概要（3つの主要機能）
- ダッシュボードへのリンク
- 次のステップ（診断作成）

---

### send_lead_notification_email(to_email, lead_name, lead_email, assessment_title, score, lead_company=None, recommended_actions=None, logo_url=None, dashboard_url=None) -> bool

リード通知メール（Jinja2テンプレート使用）

```python
success = email_service.send_lead_notification_email(
    to_email="admin@company.com",
    lead_name="鈴木一郎",
    lead_email="suzuki@example.com",
    assessment_title="マーケティング成熟度診断",
    score=85,
    lead_company="株式会社サンプル",  # オプション: 会社名
    recommended_actions="即座にデモを提案。意思決定者との商談を設定。",  # オプション: AI推奨アクション
    logo_url="https://cdn.example.com/logo.png",  # オプション: テナントロゴ
    dashboard_url="https://app.diagnoleads.com/dashboard/leads",  # オプション
)
```

**内容**:
- 🎉 新リード獲得の祝福
- リード基本情報（名前、メール、会社、診断名、スコア）
- スコアバッジ（🔥ホット/⚡ウォーム/❄️コールド）
- AI推奨アクション
- ダッシュボードへのリンク

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

## 🎨 Jinja2テンプレートエンジン（実装済み）

### テンプレート管理

EmailServiceはJinja2テンプレートエンジンを使用して、HTMLメールを生成します。

```python
from jinja2 import Environment, FileSystemLoader

# EmailService.__init__()で初期化
template_dir = Path(__file__).parent.parent / "templates" / "emails"
self.template_env = Environment(
    loader=FileSystemLoader(str(template_dir)),
    autoescape=select_autoescape(["html", "xml"]),
)

# テンプレートレンダリング
def render_template(self, template_name: str, context: Dict[str, Any]) -> str:
    template = self.template_env.get_template(template_name)
    return template.render(**context)
```

### テンプレートファイル

| テンプレート | ファイル | 主要変数 |
|------------|---------|---------|
| パスワードリセット | `password_reset.html` | `reset_link`, `user_name`, `brand_color`, `logo_url` |
| ウェルカム | `welcome.html` | `user_name`, `brand_color`, `brand_color_secondary`, `logo_url`, `dashboard_url` |
| リード通知 | `lead_notification.html` | `lead_name`, `lead_email`, `lead_company`, `assessment_title`, `score`, `recommended_actions` |

**テンプレート場所**: `/backend/app/templates/emails/`

### テナントカスタマイズ

各メールメソッドは以下のカスタマイズオプションをサポート：

- `brand_color`: メインブランドカラー（デフォルト: `#3b82f6`）
- `brand_color_secondary`: セカンダリカラー（グラデーション用）
- `logo_url`: テナントロゴURL
- `dashboard_url`: ダッシュボードURL

---

## 🚀 将来の改善

### 1. 配信サービス統合

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

### 4. 配信スケジューリング

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

### 5. A/Bテスト

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
| `/backend/app/services/email_service.py` | EmailServiceクラス（320行、Jinja2統合済み） |
| `/backend/app/templates/emails/password_reset.html` | パスワードリセットHTMLテンプレート |
| `/backend/app/templates/emails/welcome.html` | ウェルカムメールHTMLテンプレート |
| `/backend/app/templates/emails/lead_notification.html` | リード通知HTMLテンプレート |
| `/backend/requirements.txt` | Jinja2==3.1.4 依存関係追加 |

---

## 🔗 関連仕様

- [Authentication](../auth/authentication.md) - パスワードリセット連携
- [Lead Management](../features/lead-management.md) - リード通知連携

---

**実装ステータス**: ✅ 完全実装済み（基本機能 + Jinja2テンプレートエンジン）
**拡張機能**: ⏳ 配信サービス統合（SendGrid/AWS SES）、メール追跡、スケジューリング、A/Bテストは未実装
