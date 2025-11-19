# White Label & Custom Branding

**Status**: Approved
**Priority**: High
**Phase**: 1.5 (Enterprise Differentiation)
**Estimated Effort**: 6-8 weeks
**Dependencies**: Subscription System, CDN, Domain Management

## Overview

ホワイトラベル・カスタムブランディング機能により、Business・Enterpriseプランのテナントが、DiagnoLeadsプラットフォームを自社ブランドとして提供できます。カスタムドメイン、ロゴ、カラースキーム、メール通知のカスタマイズにより、シームレスなブランド体験を実現します。

## Business Value

- **エンタープライズ獲得**: 大企業の80%がホワイトラベル機能を要求
- **単価向上**: Business/Enterpriseプラン契約率 +60%
- **解約率低減**: ブランド投資により解約率 -40%
- **競争優位**: 主要競合との差別化ポイント
- **パートナー収益**: 代理店・再販パートナーモデルが可能

## Core Features

### 1. カスタムドメイン
- 独自ドメイン設定（assessments.yourcompany.com）
- SSL証明書自動発行（Let's Encrypt）
- CNAMEレコード検証
- サブドメイン無制限

### 2. ブランディング
- ロゴアップロード（ヘッダー、ファビコン）
- カラースキームカスタマイズ（プライマリ、セカンダリ、アクセント）
- カスタムフォント
- ブランドガイドライン適用

### 3. UI/UXカスタマイズ
- ヘッダー・フッターHTML/CSS編集
- カスタムCSS注入
- JavaScript カスタマイズ（高度なユーザー向け）
- レスポンシブプレビュー

### 4. メール通知カスタマイズ
- メールテンプレート編集
- From名・アドレスカスタマイズ
- メールフッター（会社情報、SNSリンク）
- HTML/テキスト両対応

### 5. 埋め込みウィジェットブランディング
- ウィジェット外観カスタマイズ
- ブランドカラー自動適用
- ロゴ表示・非表示設定
- 「Powered by DiagnoLeads」ラベル削除（Enterprise）

### 6. 法的文書カスタマイズ
- 利用規約カスタマイズ
- プライバシーポリシー差し替え
- Cookie同意バナーカスタマイズ

## User Stories

### 1. カスタムドメイン設定

**As a** Enterprise管理者
**I want to** 独自ドメインで診断を提供
**So that** 顧客に一貫したブランド体験を提供できる

**Acceptance Criteria**:

**Given**: Businessプラン以上に契約中
**When**: 「カスタムドメイン設定」ページにアクセス
**Then**:
- ドメイン入力フィールド表示（例: assessments.mycompany.com）
- DNS設定手順を表示:
  - CNAMEレコード: `cname.diagnoleads.com`
  - TXTレコード（検証用）
- 「ドメインを検証」ボタンをクリック
- DNS伝播を確認（最大48時間）
- 検証成功後、SSL証明書を自動発行
- ステータス: 「アクティブ」に変更
- 以降、カスタムドメインでアクセス可能

**Given**: DNS設定が不正確
**When**: 「ドメインを検証」をクリック
**Then**:
- エラーメッセージ表示: 「DNSレコードが見つかりません」
- 再試行手順を提示
- サポートへの連絡リンク

### 2. ブランディングカスタマイズ

**As a** ブランドマネージャー
**I want to** 診断サイトを自社ブランドに合わせる
**So that** 顧客が違和感なく利用できる

**Acceptance Criteria**:

**Given**: ブランド設定ページにアクセス
**When**: ロゴをアップロード（PNG, SVG, 最大2MB）
**Then**:
- ロゴが即座にプレビュー表示
- ヘッダー、ファビコン、OGPイメージに自動適用
- 推奨サイズガイド表示（ヘッダー: 200x50px）
- 背景透過推奨の提案

**When**: カラースキームを編集
**Then**:
- カラーピッカーでプライマリカラー選択
- 自動的に補色・グラデーションを生成
- リアルタイムプレビュー（ボタン、リンク、背景に反映）
- WCAGアクセシビリティチェック（コントラスト比）
- 警告: 「このカラーは読みにくい可能性があります」

**When**: カスタムフォント追加（Google Fonts）
**Then**:
- Google Fonts一覧から選択
- または、カスタムフォントURL指定
- 見出し・本文フォントを個別設定
- プレビューで確認

### 3. メール通知カスタマイズ

**As a** マーケティング担当者
**I want to** メール通知を自社ブランドに統一
**So that** プロフェッショナルな印象を与えられる

**Acceptance Criteria**:

**Given**: メールテンプレートエディターにアクセス
**When**: リード獲得通知テンプレートを編集
**Then**:
- WYSIWYGエディターで編集
- 変数挿入: `{{lead_name}}`, `{{assessment_title}}`
- From名設定: 「株式会社Example マーケティング部」
- From アドレス: `marketing@example.com`（ドメイン認証必要）
- カスタムフッター: 会社住所、電話番号、配信停止リンク
- プレビュー機能（デスクトップ・モバイル）
- テストメール送信

**Given**: カスタムFrom アドレス未認証
**When**: From アドレスを変更
**Then**:
- 認証メールが送信される
- 「メールアドレスを認証してください」と警告表示
- 認証リンクをクリック → ステータス「認証済み」

### 4. ウィジェットブランディング

**As a** Webサイト管理者
**I want to** 埋め込みウィジェットを自社デザインに合わせる
**So that** サイトに自然に溶け込む

**Acceptance Criteria**:

**Given**: 診断の埋め込みコードを生成
**When**: 「ウィジェットカスタマイズ」を開く
**Then**:
- カラースキーム自動適用（テナント設定から継承）
- ロゴ表示・非表示トグル
- ボーダー半径調整（角丸）
- シャドウ強度調整
- アニメーション速度設定
- リアルタイムプレビュー
- カスタムCSS注入（上級者向け）

**Given**: Enterpriseプラン
**When**: 「Powered by DiagnoLeads」ラベル設定
**Then**:
- 「ラベルを非表示」オプションが有効
- チェックを入れると完全に非表示

**Given**: Business プラン（非Enterprise）
**When**: 「Powered by DiagnoLeads」ラベル設定
**Then**:
- 「ラベルを非表示」オプションがグレーアウト
- ツールチップ: 「Enterpriseプランで利用可能」
- アップグレードリンク表示

### 5. 完全カスタムCSS（上級者向け）

**As a** フロントエンドエンジニア
**I want to** CSSを完全にコントロール
**So that** 既存サイトに完璧にマッチさせられる

**Acceptance Criteria**:

**Given**: 「カスタムCSS」エディターにアクセス
**When**: CSSコードを記述
**Then**:
- シンタックスハイライト
- オートコンプリート
- エラー検出・警告
- リアルタイムプレビュー
- バージョン履歴（最大10世代）
- セーフモード（無効化機能）

**Given**: 不正なCSSを保存
**When**: 保存ボタンをクリック
**Then**:
- 警告ダイアログ表示
- エラー箇所をハイライト
- 「セーフモードで保存」オプション提示
- セーフモード: 問題があればデフォルトCSSにフォールバック

## Technical Architecture

### Custom Domain Management

```python
# backend/app/services/branding/domain_service.py
from typing import Optional
import dns.resolver
import ssl
import certbot
from app.models import TenantDomain

class DomainService:
    """カスタムドメイン管理"""

    async def add_custom_domain(
        self,
        tenant_id: str,
        domain: str
    ) -> TenantDomain:
        """カスタムドメイン追加"""

        # ドメインバリデーション
        if not self._is_valid_domain(domain):
            raise ValueError("Invalid domain format")

        # 既存ドメインチェック
        existing = await TenantDomain.get_by_domain(domain)
        if existing:
            raise ValueError("Domain already in use")

        # DNS検証トークン生成
        verification_token = self._generate_verification_token()

        # DB登録
        tenant_domain = await TenantDomain.create(
            tenant_id=tenant_id,
            domain=domain,
            verification_token=verification_token,
            status="pending_verification"
        )

        return tenant_domain

    async def verify_domain(self, tenant_domain: TenantDomain) -> bool:
        """DNSレコード検証"""

        try:
            # CNAMEレコード確認
            cname_records = dns.resolver.resolve(tenant_domain.domain, 'CNAME')
            cname_valid = any(
                str(r.target).rstrip('.') == 'cname.diagnoleads.com'
                for r in cname_records
            )

            # TXTレコード確認（検証用）
            txt_records = dns.resolver.resolve(
                f'_diagnoleads-verify.{tenant_domain.domain}', 'TXT'
            )
            txt_valid = any(
                tenant_domain.verification_token in str(r)
                for r in txt_records
            )

            if cname_valid and txt_valid:
                tenant_domain.status = "verified"
                await tenant_domain.save()

                # SSL証明書発行
                await self._issue_ssl_certificate(tenant_domain)

                return True

        except dns.resolver.NXDOMAIN:
            raise ValueError("Domain not found")
        except dns.resolver.NoAnswer:
            raise ValueError("No DNS records found")

        return False

    async def _issue_ssl_certificate(self, tenant_domain: TenantDomain):
        """SSL証明書発行（Let's Encrypt）"""

        # Certbot経由でSSL証明書発行
        # 実装はインフラ構成により異なる（Cloudflare, AWS ACM, etc.）

        cert_path = certbot.obtain_cert(
            domain=tenant_domain.domain,
            email=tenant_domain.tenant.admin_email
        )

        tenant_domain.ssl_cert_path = cert_path
        tenant_domain.ssl_issued_at = datetime.utcnow()
        tenant_domain.status = "active"
        await tenant_domain.save()

        # CDN/ロードバランサーに証明書登録
        await self._register_ssl_to_cdn(tenant_domain)
```

### Branding Configuration Service

```python
# backend/app/services/branding/branding_service.py
from PIL import Image
from app.models import TenantBranding
from app.core.storage import upload_to_cdn

class BrandingService:
    """ブランディング管理"""

    async def upload_logo(
        self,
        tenant_id: str,
        logo_file: bytes,
        logo_type: str = "header"  # header, favicon, og_image
    ) -> str:
        """ロゴアップロード"""

        # 画像検証
        image = Image.open(logo_file)

        # サイズ検証
        max_size = 2 * 1024 * 1024  # 2MB
        if len(logo_file) > max_size:
            raise ValueError("File size exceeds 2MB")

        # フォーマット検証
        if image.format not in ['PNG', 'JPEG', 'SVG']:
            raise ValueError("Invalid image format. Use PNG, JPEG, or SVG")

        # 推奨サイズチェック
        recommended_sizes = {
            "header": (200, 50),
            "favicon": (32, 32),
            "og_image": (1200, 630)
        }

        if logo_type in recommended_sizes:
            rec_width, rec_height = recommended_sizes[logo_type]
            if abs(image.width - rec_width) > 50 or abs(image.height - rec_height) > 50:
                # 警告（エラーではない）
                print(f"Warning: Recommended size is {rec_width}x{rec_height}")

        # CDNにアップロード
        cdn_url = await upload_to_cdn(
            file=logo_file,
            path=f"tenants/{tenant_id}/branding/{logo_type}.{image.format.lower()}"
        )

        # DB更新
        branding = await TenantBranding.get_or_create(tenant_id=tenant_id)
        setattr(branding, f"{logo_type}_url", cdn_url)
        await branding.save()

        return cdn_url

    async def update_color_scheme(
        self,
        tenant_id: str,
        primary_color: str,
        secondary_color: Optional[str] = None,
        accent_color: Optional[str] = None
    ):
        """カラースキーム更新"""

        # カラーバリデーション
        if not self._is_valid_hex_color(primary_color):
            raise ValueError("Invalid hex color format")

        # アクセシビリティチェック（コントラスト比）
        contrast_ratio = self._calculate_contrast_ratio(primary_color, "#FFFFFF")
        if contrast_ratio < 4.5:  # WCAG AA基準
            print(f"Warning: Low contrast ratio ({contrast_ratio:.2f})")

        # 補色自動生成（未指定の場合）
        if not secondary_color:
            secondary_color = self._generate_complementary_color(primary_color)
        if not accent_color:
            accent_color = self._generate_accent_color(primary_color)

        # 保存
        branding = await TenantBranding.get_or_create(tenant_id=tenant_id)
        branding.primary_color = primary_color
        branding.secondary_color = secondary_color
        branding.accent_color = accent_color
        await branding.save()

        # CSSファイル生成
        await self._generate_custom_css(tenant_id, branding)

    async def _generate_custom_css(self, tenant_id: str, branding: TenantBranding):
        """カスタムCSS生成"""

        css_template = f"""
        :root {{
            --primary-color: {branding.primary_color};
            --secondary-color: {branding.secondary_color};
            --accent-color: {branding.accent_color};
            --font-family: {branding.custom_font or 'Inter, sans-serif'};
        }}

        .btn-primary {{
            background-color: var(--primary-color);
            border-color: var(--primary-color);
        }}

        .btn-primary:hover {{
            background-color: {self._darken_color(branding.primary_color, 10)};
        }}

        a {{
            color: var(--primary-color);
        }}

        /* カスタムCSS */
        {branding.custom_css or ''}
        """

        # CDNにアップロード
        css_url = await upload_to_cdn(
            file=css_template.encode(),
            path=f"tenants/{tenant_id}/branding/custom.css",
            content_type="text/css"
        )

        branding.custom_css_url = css_url
        await branding.save()

    def _calculate_contrast_ratio(self, color1: str, color2: str) -> float:
        """コントラスト比計算（WCAG）"""
        # RGB変換 → 輝度計算 → コントラスト比算出
        # 実装省略
        pass
```

### Email Template Customization

```python
# backend/app/services/branding/email_template_service.py
from jinja2 import Template
from app.models import EmailTemplate

class EmailTemplateService:
    """メールテンプレート管理"""

    async def customize_template(
        self,
        tenant_id: str,
        template_name: str,
        subject: str,
        html_body: str,
        text_body: Optional[str] = None,
        from_name: Optional[str] = None,
        from_email: Optional[str] = None
    ):
        """テンプレートカスタマイズ"""

        # テンプレート取得または作成
        template = await EmailTemplate.get_or_create(
            tenant_id=tenant_id,
            name=template_name
        )

        # 変数検証（必須変数が含まれているか）
        required_vars = self._get_required_vars(template_name)
        if not all(f"{{{{{var}}}}}" in html_body for var in required_vars):
            raise ValueError(f"Missing required variables: {required_vars}")

        # Jinja2テンプレート検証
        try:
            Template(html_body)
        except Exception as e:
            raise ValueError(f"Invalid template syntax: {e}")

        # 保存
        template.subject = subject
        template.html_body = html_body
        template.text_body = text_body or self._html_to_text(html_body)
        template.from_name = from_name
        template.from_email = from_email
        await template.save()

    async def verify_sender_email(self, tenant_id: str, email: str):
        """送信元メールアドレス認証"""

        # 認証トークン生成
        verification_token = self._generate_token()

        # 認証メール送信
        await self._send_verification_email(email, verification_token)

        # DB記録
        await EmailSenderVerification.create(
            tenant_id=tenant_id,
            email=email,
            verification_token=verification_token,
            status="pending"
        )

    async def render_email(
        self,
        tenant_id: str,
        template_name: str,
        context: Dict
    ) -> Dict[str, str]:
        """メールレンダリング"""

        template = await EmailTemplate.get_by_tenant_and_name(tenant_id, template_name)

        # カスタムテンプレートがなければデフォルト使用
        if not template or not template.html_body:
            template = await EmailTemplate.get_default(template_name)

        # ブランディング適用
        branding = await TenantBranding.get_by_tenant(tenant_id)
        context.update({
            "logo_url": branding.header_logo_url,
            "primary_color": branding.primary_color,
            "company_name": branding.company_name or "DiagnoLeads"
        })

        # レンダリング
        html_template = Template(template.html_body)
        text_template = Template(template.text_body)

        return {
            "subject": Template(template.subject).render(context),
            "html": html_template.render(context),
            "text": text_template.render(context),
            "from_name": template.from_name or "DiagnoLeads",
            "from_email": template.from_email or "noreply@diagnoleads.com"
        }
```

## API Endpoints

### カスタムドメイン管理

```
POST   /api/v1/branding/domains
       - カスタムドメイン追加
       - Request: { domain: "assessments.example.com" }
       - Response: { id, domain, verification_token, dns_records, status }

GET    /api/v1/branding/domains
       - カスタムドメイン一覧

POST   /api/v1/branding/domains/{id}/verify
       - ドメイン検証実行
       - Response: { verified: true/false, error_message }

DELETE /api/v1/branding/domains/{id}
       - カスタムドメイン削除
```

### ブランディング

```
GET    /api/v1/branding
       - 現在のブランディング設定取得

PUT    /api/v1/branding
       - ブランディング設定更新
       - Request: {
           company_name,
           primary_color,
           secondary_color,
           custom_font
         }

POST   /api/v1/branding/logo
       - ロゴアップロード
       - Request: FormData with file
       - Query: ?type=header|favicon|og_image

POST   /api/v1/branding/css
       - カスタムCSS更新
       - Request: { css_code }

GET    /api/v1/branding/preview
       - プレビュー取得（iframe用）
```

### メールテンプレート

```
GET    /api/v1/branding/email-templates
       - テンプレート一覧

GET    /api/v1/branding/email-templates/{name}
       - 特定テンプレート取得

PUT    /api/v1/branding/email-templates/{name}
       - テンプレート更新
       - Request: { subject, html_body, text_body, from_name, from_email }

POST   /api/v1/branding/email-templates/{name}/preview
       - プレビューメール送信
       - Request: { recipient_email, test_data }

POST   /api/v1/branding/sender-email/verify
       - 送信元メール認証
       - Request: { email }
```

## Database Schema

```sql
-- テナントドメイン
CREATE TABLE tenant_domains (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,

    domain VARCHAR(255) NOT NULL UNIQUE,
    verification_token VARCHAR(255) NOT NULL,

    -- SSL証明書
    ssl_cert_path TEXT,
    ssl_issued_at TIMESTAMP,
    ssl_expires_at TIMESTAMP,

    status VARCHAR(50) DEFAULT 'pending_verification',
    -- pending_verification, verified, active, failed

    verified_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),

    INDEX idx_tenant_domains_tenant (tenant_id),
    INDEX idx_tenant_domains_domain (domain)
);

-- ブランディング設定
CREATE TABLE tenant_branding (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL UNIQUE REFERENCES tenants(id) ON DELETE CASCADE,

    -- 会社情報
    company_name VARCHAR(255),
    tagline TEXT,

    -- ロゴ
    header_logo_url TEXT,
    favicon_url TEXT,
    og_image_url TEXT,

    -- カラースキーム
    primary_color VARCHAR(7),  -- #RRGGBB
    secondary_color VARCHAR(7),
    accent_color VARCHAR(7),

    -- フォント
    custom_font VARCHAR(255),  -- Google Fonts名 or URL

    -- カスタムCSS/JS
    custom_css TEXT,
    custom_css_url TEXT,
    custom_js TEXT,

    -- ウィジェット設定
    widget_show_logo BOOLEAN DEFAULT TRUE,
    widget_show_powered_by BOOLEAN DEFAULT TRUE,

    -- メタデータ
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- メールテンプレート
CREATE TABLE email_templates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,

    name VARCHAR(100) NOT NULL,  -- lead_notification, welcome_email, etc.
    subject VARCHAR(255) NOT NULL,
    html_body TEXT NOT NULL,
    text_body TEXT,

    -- 送信者情報
    from_name VARCHAR(255),
    from_email VARCHAR(255),

    -- バージョン管理
    version INTEGER DEFAULT 1,
    is_active BOOLEAN DEFAULT TRUE,

    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),

    UNIQUE(tenant_id, name, version)
);

-- 送信元メール認証
CREATE TABLE email_sender_verifications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,

    email VARCHAR(255) NOT NULL,
    verification_token VARCHAR(255) NOT NULL,

    status VARCHAR(50) DEFAULT 'pending',  -- pending, verified, failed
    verified_at TIMESTAMP,

    created_at TIMESTAMP DEFAULT NOW(),

    UNIQUE(tenant_id, email)
);

-- CSS/JSバージョン履歴
CREATE TABLE branding_versions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,

    version_number INTEGER NOT NULL,
    css_code TEXT,
    js_code TEXT,

    created_by UUID REFERENCES users(id),
    created_at TIMESTAMP DEFAULT NOW(),

    INDEX idx_branding_versions_tenant (tenant_id, version_number DESC)
);
```

## Frontend Components

### Branding Dashboard

```typescript
// frontend/src/features/branding/BrandingDashboard.tsx
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { DomainSettings } from './DomainSettings'
import { LogoUploader } from './LogoUploader'
import { ColorSchemeEditor } from './ColorSchemeEditor'
import { EmailTemplateEditor } from './EmailTemplateEditor'

export function BrandingDashboard() {
  return (
    <div className="max-w-6xl mx-auto p-6">
      <h1 className="text-3xl font-bold mb-8">ブランディング設定</h1>

      <Tabs defaultValue="domain">
        <TabsList>
          <TabsTrigger value="domain">カスタムドメイン</TabsTrigger>
          <TabsTrigger value="branding">ロゴ・カラー</TabsTrigger>
          <TabsTrigger value="widget">ウィジェット</TabsTrigger>
          <TabsTrigger value="email">メールテンプレート</TabsTrigger>
          <TabsTrigger value="advanced">高度な設定</TabsTrigger>
        </TabsList>

        <TabsContent value="domain">
          <DomainSettings />
        </TabsContent>

        <TabsContent value="branding">
          <div className="grid md:grid-cols-2 gap-8">
            <div>
              <LogoUploader />
              <ColorSchemeEditor />
            </div>
            <div>
              <BrandingPreview />
            </div>
          </div>
        </TabsContent>

        <TabsContent value="email">
          <EmailTemplateEditor />
        </TabsContent>
      </Tabs>
    </div>
  )
}
```

### Domain Settings Component

```typescript
// frontend/src/features/branding/DomainSettings.tsx
import { useState } from 'react'
import { useMutation, useQuery } from '@tanstack/react-query'
import { Input } from '@/components/ui/input'
import { Button } from '@/components/ui/button'
import { Alert } from '@/components/ui/alert'

export function DomainSettings() {
  const [domain, setDomain] = useState('')

  const { data: domains } = useQuery({
    queryKey: ['branding', 'domains'],
    queryFn: () => fetch('/api/v1/branding/domains').then(r => r.json())
  })

  const addDomain = useMutation({
    mutationFn: (domain: string) =>
      fetch('/api/v1/branding/domains', {
        method: 'POST',
        body: JSON.stringify({ domain })
      }).then(r => r.json())
  })

  const verifyDomain = useMutation({
    mutationFn: (id: string) =>
      fetch(`/api/v1/branding/domains/${id}/verify`, {
        method: 'POST'
      }).then(r => r.json())
  })

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle>カスタムドメイン追加</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex gap-4">
            <Input
              placeholder="assessments.yourcompany.com"
              value={domain}
              onChange={(e) => setDomain(e.target.value)}
            />
            <Button onClick={() => addDomain.mutate(domain)}>
              追加
            </Button>
          </div>
        </CardContent>
      </Card>

      {domains?.map((d) => (
        <Card key={d.id}>
          <CardHeader>
            <CardTitle className="flex items-center justify-between">
              {d.domain}
              <Badge variant={d.status === 'active' ? 'success' : 'warning'}>
                {d.status}
              </Badge>
            </CardTitle>
          </CardHeader>
          <CardContent>
            {d.status === 'pending_verification' && (
              <Alert>
                <AlertTitle>DNS設定が必要です</AlertTitle>
                <AlertDescription>
                  <p>以下のDNSレコードを追加してください:</p>
                  <pre className="mt-2 p-4 bg-muted rounded">
                    {`CNAME  ${d.domain}  →  cname.diagnoleads.com\nTXT    _diagnoleads-verify.${d.domain}  →  ${d.verification_token}`}
                  </pre>
                  <Button
                    className="mt-4"
                    onClick={() => verifyDomain.mutate(d.id)}
                  >
                    ドメインを検証
                  </Button>
                </AlertDescription>
              </Alert>
            )}
          </CardContent>
        </Card>
      ))}
    </div>
  )
}
```

## Security Considerations

- **ドメイン検証**: DNS検証により所有権を確認
- **SSL証明書**: Let's Encryptで自動発行、定期更新
- **XSS対策**: カスタムCSS/JSはサニタイズ、CSP適用
- **テナント分離**: ブランディング設定は必ずテナントIDでフィルタリング
- **送信元メール認証**: SPF/DKIM/DMARC設定ガイド提供
- **ファイルアップロード**: ウイルススキャン、サイズ制限

## Testing Strategy

### 単体テスト
- ドメイン検証ロジック
- カラーコントラスト計算
- CSS生成ロジック
- メールテンプレートレンダリング

### 統合テスト
- DNS検証フロー
- SSL証明書発行
- CDNアップロード
- メール送信

### E2Eテスト
- カスタムドメイン設定 → 検証 → SSL発行
- ロゴアップロード → プレビュー → 本番反映
- カラー変更 → CSS生成 → 埋め込みウィジェットに反映

## Performance Requirements

- **プレビュー更新**: リアルタイム（<100ms）
- **CSS生成**: 3秒以内
- **ロゴアップロード**: 5秒以内
- **ドメイン検証**: 10秒以内（DNS伝播除く）

## Rollout Plan

### Week 1-2: カスタムドメイン
- ドメイン追加・検証機能
- DNS検証ロジック
- SSL証明書発行（Let's Encrypt統合）

### Week 3-4: ブランディングUI
- ロゴアップロード
- カラースキーム編集
- リアルタイムプレビュー

### Week 5-6: メールテンプレート
- テンプレートエディター
- 送信元メール認証
- プレビュー・テスト送信

### Week 7-8: 高度なカスタマイズ
- カスタムCSS/JS
- ウィジェットブランディング
- ドキュメント・チュートリアル

## Success Metrics

- **機能利用率**: Business/Enterpriseプランの80%がブランディング設定
- **カスタムドメイン利用率**: Enterpriseプランの60%
- **解約率**: ブランディング設定済みテナントの解約率 <2%/月
- **アップグレード率**: ブランディング機能目的のアップグレード 月20件

## Related Specifications

- [Subscription & Billing](./subscription-billing.md) - Business/Enterpriseプラン
- [Embed Widget](./embed-widget.md) - ウィジェットブランディング
- [Analytics Dashboard](./analytics-dashboard.md) - カスタムドメインの分析

## References

- [Let's Encrypt Documentation](https://letsencrypt.org/docs/)
- [WCAG Contrast Guidelines](https://www.w3.org/WAI/WCAG21/Understanding/contrast-minimum.html)
- [Email Authentication (SPF/DKIM/DMARC)](https://www.dmarcanalyzer.com/)
- [CSS Custom Properties](https://developer.mozilla.org/en-US/docs/Web/CSS/Using_CSS_custom_properties)
