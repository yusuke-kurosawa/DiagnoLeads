# Multi-Channel Assessment Distribution

**Status**: Approved  
**Priority**: High  
**Phase**: 1 (MVP+)  
**Estimated Effort**: 8 weeks  
**Dependencies**: LINE Messaging API, Twilio, SendGrid, QR Code Generator

## Overview

Web埋め込みだけでなく、LINE、SMS、Email、QRコード、NFCなど、あらゆるチャネルで診断を配信できるようにします。顧客接点を最大化し、リード獲得機会を劇的に増やします。

## Business Value

- **リーチ拡大**: 配信チャネル +600%（Web→7チャネル）
- **CV増加**: チャネル多様化により総リード数 +250%
- **オフライン連携**: 展示会・セミナーでのリード獲得を効率化
- **国際展開**: WhatsApp対応でグローバル市場へ

## Supported Channels

| チャネル | 優先度 | ターゲット | 予想CV率 |
|---------|--------|-----------|----------|
| LINE Official Account | Critical | 日本市場（9,500万ユーザー） | 35% |
| SMS | High | モバイル重視、グローバル | 25% |
| Email | High | BtoB、既存リスト | 15% |
| QRコード | High | オフラインイベント | 40% |
| WhatsApp Business | Medium | グローバル（20億ユーザー） | 30% |
| NFC | Low | 近接マーケティング | 45% |
| WeChat | Low | 中国市場 | 28% |

## User Stories

### 1. LINE Official Accountでの診断配信

**As a** マーケティング担当者  
**I want to** LINE公式アカウントで診断を配信  
**So that** 日本の顧客に最も使われているチャネルでリーチできる

**Acceptance Criteria**:

**Given**: テナントがLINE連携を有効化している  
**When**: ダッシュボードから「LINEで配信」をクリック  
**Then**:
- LINE友達にブロードキャストメッセージを送信
- Flex Message形式で診断カードを表示
- リッチメニューに診断リンクを追加可能
- ユーザーがLINE内で診断を完了
- 回答データがダッシュボードに即座に反映

**Given**: ユーザーがLINE Botにメッセージ送信  
**When**: 「診断」とキーワード入力  
**Then**:
- 利用可能な診断リストを表示（カルーセル形式）
- 診断選択後、質問を1つずつ送信
- Quick Replyボタンで回答
- 完了後、結果カードと詳細レポートリンクを表示

### 2. SMS診断キャンペーン

**As a** イベントマーケター  
**I want to** セミナー参加者にSMSで診断を送信  
**So that** その場でリードを獲得できる

**Acceptance Criteria**:

**Given**: 電話番号リストがアップロードされている  
**When**: SMSキャンペーンを作成・送信  
**Then**:
- 短縮URL付きSMSが配信される
- 「あなたの営業課題を3分で診断 → https://dgl.ai/abc123」
- URLクリック数をトラッキング
- モバイル最適化されたランディングページに誘導
- 完了率をダッシュボードで確認

### 3. QRコード生成（オフラインイベント用）

**As a** 展示会担当者  
**I want to** 診断のQRコードを生成  
**So that** ブースに掲示して来場者に診断してもらえる

**Acceptance Criteria**:

**Given**: 診断を選択  
**When**: 「QRコード生成」をクリック  
**Then**:
- 高解像度QRコードが生成される（PNG, SVG, PDF）
- QRコードに診断タイトル、ロゴを含むポスターテンプレート提供
- スキャン数をリアルタイムトラッキング
- UTMパラメータ付きURL（トラッキング用）
- 印刷用ガイド（A4, A3, 名刺サイズ）

### 4. Email診断キャンペーン

**As a** メールマーケター  
**I want to** 既存メールリストに診断を配信  
**So that** 休眠顧客を再活性化できる

**Acceptance Criteria**:

**Given**: メールリストがインポートされている  
**When**: Emailキャンペーンを作成  
**Then**:
- HTMLメールテンプレートが提供される
- 診断カードプレビュー、CTAボタン付き
- パーソナライゼーション（{{name}}様）
- 開封率、クリック率トラッキング
- SendGrid/Resend経由で配信

### 5. NFCタグ対応

**As a** 店舗マーケター  
**I want to** NFCタグに診断リンクを埋め込み  
**So that** 来店客がスマホをかざすだけで診断できる

**Acceptance Criteria**:

**Given**: 診断URLが生成されている  
**When**: NFCタグに書き込み  
**Then**:
- NFCタグデータ（NDEF形式）を生成
- スマホをかざすと自動的にブラウザが起動
- 診断ページに直接遷移
- タップ数をトラッキング

## Technical Architecture

### LINE Messaging API統合

```python
# backend/app/integrations/line/line_client.py
from linebot import LineBotApi, WebhookHandler
from linebot.models import (
    FlexSendMessage, 
    QuickReply, 
    QuickReplyButton,
    MessageAction
)

class LineClient:
    def __init__(self, channel_access_token: str, channel_secret: str):
        self.api = LineBotApi(channel_access_token)
        self.handler = WebhookHandler(channel_secret)
    
    async def send_assessment_card(
        self, 
        user_id: str, 
        assessment: Assessment
    ):
        """Flex Messageで診断カードを送信"""
        flex_message = {
            "type": "bubble",
            "hero": {
                "type": "image",
                "url": assessment.thumbnail_url or "https://placekitten.com/400/200",
                "size": "full",
                "aspectRatio": "20:13"
            },
            "body": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "text",
                        "text": assessment.title,
                        "weight": "bold",
                        "size": "xl"
                    },
                    {
                        "type": "text",
                        "text": assessment.description,
                        "size": "sm",
                        "color": "#aaaaaa",
                        "wrap": True
                    },
                    {
                        "type": "box",
                        "layout": "baseline",
                        "margin": "md",
                        "contents": [
                            {
                                "type": "icon",
                                "url": "https://scdn.line-apps.com/n/channel_devcenter/img/fx/review_gold_star_28.png"
                            },
                            {
                                "type": "text",
                                "text": f"所要時間: {assessment.estimated_minutes}分",
                                "size": "sm",
                                "color": "#999999"
                            }
                        ]
                    }
                ]
            },
            "footer": {
                "type": "box",
                "layout": "vertical",
                "contents": [{
                    "type": "button",
                    "action": {
                        "type": "uri",
                        "label": "診断を開始",
                        "uri": f"https://app.diagnoleads.com/a/{assessment.short_id}"
                    },
                    "style": "primary"
                }]
            }
        }
        
        self.api.push_message(
            user_id,
            FlexSendMessage(alt_text="診断のご案内", contents=flex_message)
        )
    
    async def send_question(
        self,
        user_id: str,
        question: Question,
        session_id: str
    ):
        """質問を送信（Quick Reply付き）"""
        quick_reply = QuickReply(items=[
            QuickReplyButton(action=MessageAction(
                label=choice.text[:20],
                text=f"ANSWER:{session_id}:{choice.id}"
            ))
            for choice in question.choices
        ])
        
        self.api.push_message(
            user_id,
            TextSendMessage(
                text=f"Q{question.order}. {question.text}",
                quick_reply=quick_reply
            )
        )
```

### SMS配信（Twilio）

```python
# backend/app/integrations/sms/twilio_client.py
from twilio.rest import Client

class SMSClient:
    def __init__(self, account_sid: str, auth_token: str, from_number: str):
        self.client = Client(account_sid, auth_token)
        self.from_number = from_number
    
    async def send_assessment_link(
        self,
        to_number: str,
        assessment: Assessment,
        short_url: str
    ):
        """診断リンク付きSMSを送信"""
        message = f"""
{assessment.title}

あなたの課題を3分で診断します
{short_url}

DiagnoLeads
        """.strip()
        
        result = self.client.messages.create(
            body=message,
            from_=self.from_number,
            to=to_number
        )
        
        return {
            "sid": result.sid,
            "status": result.status,
            "to": to_number
        }
    
    async def send_bulk(
        self,
        phone_numbers: List[str],
        assessment: Assessment
    ):
        """一括SMS送信"""
        short_url = await self._generate_short_url(assessment)
        
        results = []
        for phone in phone_numbers:
            try:
                result = await self.send_assessment_link(
                    phone, assessment, short_url
                )
                results.append({"phone": phone, "success": True, **result})
            except Exception as e:
                results.append({"phone": phone, "success": False, "error": str(e)})
        
        return results
```

### QRコード生成

```python
# backend/app/services/qr_service.py
import qrcode
from qrcode.image.styledpil import StyledPilImage
from qrcode.image.styles.moduledrawers import RoundedModuleDrawer

class QRCodeService:
    def generate_assessment_qr(
        self,
        assessment: Assessment,
        size: str = "medium",  # small, medium, large, xlarge
        include_logo: bool = True
    ) -> bytes:
        """診断用QRコードを生成"""
        # UTMパラメータ付きURL
        url = self._build_tracking_url(assessment, source="qrcode")
        
        # QRコード生成
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=self._get_box_size(size),
            border=4,
        )
        qr.add_data(url)
        qr.make(fit=True)
        
        # スタイリング
        img = qr.make_image(
            image_factory=StyledPilImage,
            module_drawer=RoundedModuleDrawer()
        )
        
        # ロゴ追加
        if include_logo and assessment.tenant.logo_url:
            logo = Image.open(requests.get(assessment.tenant.logo_url, stream=True).raw)
            img = self._add_logo(img, logo)
        
        # バイトストリームに変換
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        return buffer.getvalue()
    
    def generate_poster(
        self,
        assessment: Assessment,
        template: str = "modern"  # modern, minimal, corporate
    ) -> bytes:
        """QRコード付きポスター生成（A4 PDF）"""
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import A4
        
        buffer = io.BytesIO()
        pdf = canvas.Canvas(buffer, pagesize=A4)
        
        # タイトル
        pdf.setFont("Helvetica-Bold", 32)
        pdf.drawCentredString(297, 700, assessment.title)
        
        # 説明
        pdf.setFont("Helvetica", 16)
        pdf.drawCentredString(297, 650, assessment.description[:100])
        
        # QRコード
        qr_image = self.generate_assessment_qr(assessment, size="large")
        pdf.drawInlineImage(qr_image, 200, 300, width=200, height=200)
        
        # CTA
        pdf.setFont("Helvetica-Bold", 24)
        pdf.drawCentredString(297, 250, "スマホで今すぐスキャン！")
        
        pdf.save()
        return buffer.getvalue()
```

## API Endpoints

### LINE連携

```
POST   /api/v1/channels/line/install
       - LINE公式アカウント連携
       - Request: { channel_id, channel_secret, access_token }

POST   /api/v1/channels/line/send
       - LINE友達にブロードキャスト
       - Request: { assessment_id, target_segments[] }

POST   /api/v1/channels/line/webhook
       - LINE Webhook受信

GET    /api/v1/channels/line/friends
       - 友達リスト取得
```

### SMS配信

```
POST   /api/v1/channels/sms/send
       - SMS送信
       - Request: { 
           assessment_id, 
           phone_numbers[], 
           message: "optional custom text" 
         }

POST   /api/v1/channels/sms/send-bulk
       - 一括SMS送信（CSV対応）
       - Request: multipart/form-data (CSV file)

GET    /api/v1/channels/sms/delivery-status/{campaign_id}
       - 配信ステータス確認
```

### Email配信

```
POST   /api/v1/channels/email/send
       - メール送信
       - Request: { 
           assessment_id, 
           emails[], 
           subject, 
           template_id 
         }

GET    /api/v1/channels/email/templates
       - メールテンプレート一覧

POST   /api/v1/channels/email/preview
       - プレビュー生成
```

### QRコード

```
GET    /api/v1/channels/qr-code/{assessment_id}
       - QRコード画像取得
       - Query: size=medium&format=png&logo=true

GET    /api/v1/channels/qr-code/{assessment_id}/poster
       - ポスターPDF生成
       - Query: template=modern&size=a4

GET    /api/v1/channels/qr-code/{assessment_id}/stats
       - スキャン統計
```

### NFC

```
GET    /api/v1/channels/nfc/{assessment_id}/ndef
       - NDEFデータ生成
       - Response: { ndef_payload, instructions }
```

### 統合トラッキング

```
GET    /api/v1/channels/analytics
       - 全チャネルの統計
       - Response: {
           channels: {
             web: { views, starts, completions },
             line: { ... },
             sms: { ... }
           }
         }
```

## Database Schema

```sql
-- チャネル配信キャンペーン
CREATE TABLE channel_campaigns (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    assessment_id UUID NOT NULL REFERENCES assessments(id) ON DELETE CASCADE,
    
    channel VARCHAR(50) NOT NULL,  -- line, sms, email, qrcode, nfc, whatsapp
    name VARCHAR(255) NOT NULL,
    
    -- ターゲット
    target_list JSONB,  -- [phone_numbers] or [emails] or [line_user_ids]
    target_count INTEGER,
    
    -- メッセージ
    message_template TEXT,
    custom_message TEXT,
    
    -- トラッキング
    short_url VARCHAR(255),
    utm_source VARCHAR(100),
    utm_medium VARCHAR(100),
    utm_campaign VARCHAR(100),
    
    -- 配信ステータス
    status VARCHAR(50) DEFAULT 'draft',  -- draft, scheduled, sending, completed, failed
    scheduled_at TIMESTAMP,
    sent_at TIMESTAMP,
    
    -- 統計
    sent_count INTEGER DEFAULT 0,
    delivered_count INTEGER DEFAULT 0,
    opened_count INTEGER DEFAULT 0,
    clicked_count INTEGER DEFAULT 0,
    completed_count INTEGER DEFAULT 0,
    
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    
    INDEX(tenant_id, channel),
    INDEX(assessment_id)
);

-- QRコードスキャントラッキング
CREATE TABLE qr_code_scans (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    assessment_id UUID NOT NULL REFERENCES assessments(id) ON DELETE CASCADE,
    campaign_id UUID REFERENCES channel_campaigns(id) ON DELETE SET NULL,
    
    scanned_at TIMESTAMP DEFAULT NOW(),
    ip_address INET,
    user_agent TEXT,
    location JSONB,  -- {country, city, lat, lng}
    device_type VARCHAR(50),  -- mobile, tablet, desktop
    
    -- セッショントラッキング
    session_id UUID,
    completed BOOLEAN DEFAULT FALSE,
    
    INDEX(assessment_id, scanned_at),
    INDEX(campaign_id)
);

-- LINE Bot セッション
CREATE TABLE line_bot_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    assessment_id UUID NOT NULL REFERENCES assessments(id) ON DELETE CASCADE,
    
    line_user_id VARCHAR(255) NOT NULL,
    current_question_index INTEGER DEFAULT 0,
    responses JSONB DEFAULT '[]',
    
    status VARCHAR(50) DEFAULT 'active',
    started_at TIMESTAMP DEFAULT NOW(),
    completed_at TIMESTAMP,
    
    UNIQUE(line_user_id, assessment_id, started_at)
);
```

## Success Metrics

- **LINE経由CV率**: 35%以上（業界平均30%）
- **SMS到達率**: 98%以上
- **QRコードスキャン率**: イベント参加者の40%以上
- **マルチチャネルリード増加**: 総リード数 +250%（6ヶ月後）

## Related Specifications

- [Microsoft Teams Integration](./microsoft-teams-integration.md)
- [AI Optimization Engine](./ai-optimization-engine.md)
- [QR Code Distribution](./qr-code-distribution.md)
- [Integrations](./integrations.md)
