# Microsoft Teams Bot統合 Phase 2 - 技術調査レポート

**Status**: Technical Research Complete  
**Priority**: Medium  
**Target Timeline**: Phase 2 (3-4 weeks implementation)  
**Estimated Cost**: $50-200/month  
**Created**: 2025-11-11

## 📋 目次

1. [エグゼクティブサマリー](#エグゼクティブサマリー)
2. [技術スタック](#技術スタック)
3. [アーキテクチャ設計](#アーキテクチャ設計)
4. [認証フロー](#認証フロー)
5. [実装詳細](#実装詳細)
6. [コスト分析](#コスト分析)
7. [リスクと対策](#リスクと対策)
8. [実装計画](#実装計画)

---

## エグゼクティブサマリー

### 現状 (Phase 1)
- ✅ Incoming Webhook統合完了
- ✅ Adaptive Cards対応
- ✅ リード通知機能実装済み

### 目標 (Phase 2)
Microsoft Teams Bot統合により、以下を実現：
- **インタラクティブな診断配信**: Teamsチャット内で診断を直接実施
- **Bot Commands**: `/diagnoleads` コマンドでリード情報取得
- **双方向コミュニケーション**: ユーザーとのリアルタイム対話
- **エンタープライズ機能**: SSO、Graph API統合

### 結論
✅ **技術的に実現可能**  
✅ **コストは月$50-200（中小規模）**  
✅ **推定工数: 3-4週間**  
⚠️ **Azure Bot Service必須（追加インフラ）**

---

## 技術スタック

### 必須コンポーネント

#### 1. Microsoft Bot Framework SDK (Python)
**バージョン**: v4 (最新)  
**ライブラリ**: `botbuilder-core`, `botbuilder-schema`

```python
# requirements.txt
botbuilder-core==4.15.0
botbuilder-schema==4.15.0
botbuilder-dialogs==4.15.0
botbuilder-ai==4.15.0  # AI機能（オプション）
```

**主要クラス**:
- `ActivityHandler`: イベント処理のベースクラス
- `TeamsActivityHandler`: Teams特化のハンドラー
- `DialogBot`: 対話フロー管理
- `UserState`, `ConversationState`: 状態管理

**公式ドキュメント**:
- [Bot Framework Python SDK](https://github.com/Microsoft/botbuilder-python)
- [Teams Samples (Python)](https://github.com/OfficeDev/Microsoft-Teams-Samples/tree/main/samples)

---

#### 2. Azure Bot Service
**必要性**: 必須  
**役割**: Bot登録、チャネル管理、認証

**機能**:
- Bot Registration（無料）
- Teams Channel接続
- OAuth 2.0プロバイダー
- Application Insights統合

**代替案**: なし（Teamsと統合するには必須）

---

#### 3. Microsoft Graph API
**用途**: Teams情報取得、ユーザー情報、カレンダー等

**主要API**:
- `/me/profile`: ユーザー情報
- `/teams/{id}/channels`: チャネル一覧
- `/users/{id}`: ユーザー詳細
- `/me/events`: カレンダー（Phase 3で使用）

**ライブラリ**: `msal` (Microsoft Authentication Library)

```python
# requirements.txt
msal==1.25.0
microsoft-graph==0.2.0  # Graphクライアント
```

---

#### 4. Azure App Service
**必要性**: 必須  
**用途**: Botアプリケーションのホスティング

**要件**:
- Python 3.11+ サポート
- HTTPS必須（Bot Frameworkの要件）
- Public IPアドレス

**代替案**:
- **Fly.io**: 可能（HTTPSサポート）
- **Railway**: 可能（HTTPSサポート）
- **Heroku**: 可能

---

### オプショナルコンポーネント

#### 5. Azure Storage（状態管理）
**用途**: 会話状態の永続化

**代替案**:
- **PostgreSQL**: 既存DBを活用可能
- **Redis**: 既存キャッシュを活用可能

---

## アーキテクチャ設計

### 全体構成図

```
┌─────────────────────────────────────────────────────┐
│                 Microsoft Teams                     │
│  ┌──────────────┐        ┌──────────────┐          │
│  │ User Chat    │───────▶│ Teams Bot    │          │
│  │ "/diagnoleads"        │ (Frontend)   │          │
│  └──────────────┘        └──────┬───────┘          │
└────────────────────────────────┼────────────────────┘
                                 │ HTTPS
                                 ▼
┌─────────────────────────────────────────────────────┐
│          Azure Bot Service (Channel Manager)        │
│  • Bot Registration                                 │
│  • OAuth 2.0                                        │
│  • Channel Routing                                  │
└────────────────────────┬────────────────────────────┘
                         │ Bot Connector API
                         ▼
┌─────────────────────────────────────────────────────┐
│      DiagnoLeads Backend (Bot Application)          │
│  ┌────────────────────────────────────┐             │
│  │  TeamsActivityHandler              │             │
│  │  • onMessage()                     │             │
│  │  • onInvoke()                      │             │
│  │  • onTeamsSigninVerifyState()      │             │
│  └────────────────────────────────────┘             │
│                                                     │
│  ┌────────────────────────────────────┐             │
│  │  DialogBot (Conversation Flow)     │             │
│  │  • AssessmentDialog                │             │
│  │  • LeadInfoDialog                  │             │
│  └────────────────────────────────────┘             │
│                                                     │
│  ┌────────────────────────────────────┐             │
│  │  Bot Services                      │             │
│  │  • QRCodeService                   │             │
│  │  • LeadService                     │             │
│  │  • AssessmentService               │             │
│  └────────────────────────────────────┘             │
└─────────────────────────┬───────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────┐
│          PostgreSQL (Data Storage)                  │
│  • Assessments                                      │
│  • Leads                                            │
│  • User Sessions                                    │
│  • Conversation States                              │
└─────────────────────────────────────────────────────┘
```

---

### データフロー

#### 1. ユーザーがBotにメッセージ送信

```
User (Teams) 
  → Teams Client 
  → Bot Framework Service (Azure) 
  → DiagnoLeads Bot Endpoint (/api/messages)
  → TeamsActivityHandler.onMessage()
  → 診断開始
```

#### 2. Botがユーザーに質問送信

```
DiagnoLeads Bot
  → Adaptive Card生成
  → Bot Connector API
  → Teams Client
  → User
```

#### 3. ユーザーが回答

```
User (ボタンクリック)
  → Invoke Activity (Action.Submit)
  → TeamsActivityHandler.onInvoke()
  → 回答を保存
  → 次の質問を送信
```

---

## 認証フロー

### OAuth 2.0 認証 (SSO)

#### フロー図

```
1. User opens bot in Teams
   ↓
2. Bot sends OAuthCard (Sign-in button)
   ↓
3. User clicks "Sign in"
   ↓
4. Teams opens Microsoft Entra ID login
   ↓
5. User authenticates
   ↓
6. Microsoft Entra ID returns Authorization Code
   ↓
7. Bot exchanges code for Access Token
   ↓
8. Bot calls Graph API with Access Token
   ↓
9. Bot receives user profile
   ↓
10. Bot stores token in session
```

#### 実装コード（概要）

```python
from botbuilder.core import TurnContext
from botbuilder.schema import OAuthCard, CardAction, ActionTypes

class TeamsAuthBot(TeamsActivityHandler):
    async def on_teams_signin_verify_state(self, turn_context: TurnContext):
        """認証完了時のコールバック"""
        # トークンを取得
        token_response = await turn_context.adapter.get_user_token(
            turn_context,
            self.connection_name,
            magic_code=None
        )
        
        if token_response:
            # トークンを使ってGraph APIを呼び出し
            user_profile = await self.graph_client.get_user_profile(
                token_response.token
            )
            
            # セッションに保存
            await self.user_state.set(turn_context, user_profile)
            
            # 診断開始
            await turn_context.send_activity("認証成功！診断を開始します。")
        else:
            await turn_context.send_activity("認証に失敗しました。")
```

#### 必要な設定

**Azure Portal (Bot Registration):**
1. OAuth Connection Settingsを作成
   - Connection Name: `DiagnoLeadsAuth`
   - Service Provider: `Azure Active Directory v2`
   - Scopes: `User.Read`, `openid`, `profile`, `email`

2. Client IDとSecretを取得
   - Microsoft Entra IDでアプリ登録
   - Redirect URI設定: `https://token.botframework.com/.auth/web/redirect`

**環境変数:**
```bash
MICROSOFT_APP_ID=<bot-app-id>
MICROSOFT_APP_PASSWORD=<bot-app-password>
CONNECTION_NAME=DiagnoLeadsAuth
```

---

## 実装詳細

### 1. Botエンドポイント

```python
# backend/app/api/v1/bot.py
from fastapi import APIRouter, Request
from botbuilder.core import BotFrameworkAdapter, TurnContext
from botbuilder.schema import Activity

router = APIRouter()

# Bot Framework Adapter
adapter = BotFrameworkAdapter(settings)

# Bot Instance
bot = DiagnoLeadsBot()

@router.post("/api/messages")
async def messages(request: Request):
    """Bot Framework からのメッセージを受信"""
    
    # リクエストボディを取得
    body = await request.json()
    activity = Activity().deserialize(body)
    
    # 認証ヘッダーを取得
    auth_header = request.headers.get("Authorization", "")
    
    # Bot Framework Adapterで処理
    await adapter.process_activity(activity, auth_header, bot.on_turn)
    
    return {"status": "ok"}
```

---

### 2. TeamsActivityHandler

```python
# backend/app/bots/diagnoleads_bot.py
from botbuilder.core import ActivityHandler, TurnContext, MessageFactory
from botbuilder.schema import ChannelAccount, Activity, ActivityTypes
from botbuilder.schema.teams import TeamsChannelAccount

class DiagnoLeadsBot(ActivityHandler):
    
    async def on_message_activity(self, turn_context: TurnContext):
        """ユーザーからのメッセージを処理"""
        
        text = turn_context.activity.text.strip().lower()
        
        # コマンド処理
        if text == "/diagnoleads":
            await self.show_assessment_list(turn_context)
        
        elif text.startswith("/lead"):
            await self.show_lead_info(turn_context)
        
        elif text == "/help":
            await self.show_help(turn_context)
        
        else:
            # 通常のメッセージ
            await turn_context.send_activity(
                f"メッセージを受信: {text}\n"
                f"コマンド一覧は /help で確認できます。"
            )
    
    async def on_teams_members_added(
        self, 
        members_added: list[TeamsChannelAccount],
        turn_context: TurnContext
    ):
        """新しいメンバーがBotを追加した時"""
        
        for member in members_added:
            if member.id != turn_context.activity.recipient.id:
                await turn_context.send_activity(
                    f"こんにちは {member.name} さん！\n"
                    f"DiagnoLeadsボットへようこそ。\n"
                    f"/help でコマンド一覧を確認できます。"
                )
    
    async def on_invoke_activity(self, turn_context: TurnContext):
        """Adaptive Cardのアクション処理"""
        
        if turn_context.activity.name == "adaptiveCard/action":
            # ユーザーの選択を取得
            data = turn_context.activity.value
            
            if data.get("action") == "start_assessment":
                assessment_id = data.get("assessment_id")
                await self.start_assessment(turn_context, assessment_id)
            
            elif data.get("action") == "submit_answer":
                await self.handle_answer(turn_context, data)
            
            return {"statusCode": 200, "type": "application/vnd.microsoft.card.adaptive"}
        
        return await super().on_invoke_activity(turn_context)
    
    async def show_assessment_list(self, turn_context: TurnContext):
        """診断一覧を表示"""
        
        # テナントIDを取得（ユーザー情報から）
        tenant_id = await self.get_tenant_id(turn_context)
        
        # 診断一覧を取得
        assessments = await assessment_service.get_assessments(tenant_id)
        
        # Adaptive Cardを生成
        card = self.create_assessment_list_card(assessments)
        
        # 送信
        await turn_context.send_activity(
            MessageFactory.attachment(card)
        )
    
    def create_assessment_list_card(self, assessments):
        """診断一覧のAdaptive Card"""
        
        return {
            "type": "AdaptiveCard",
            "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
            "version": "1.4",
            "body": [
                {
                    "type": "TextBlock",
                    "text": "診断一覧",
                    "weight": "Bolder",
                    "size": "Large"
                },
                *[
                    {
                        "type": "Container",
                        "items": [
                            {
                                "type": "TextBlock",
                                "text": assessment["title"],
                                "weight": "Bolder"
                            },
                            {
                                "type": "TextBlock",
                                "text": assessment["description"],
                                "wrap": True
                            }
                        ],
                        "selectAction": {
                            "type": "Action.Submit",
                            "data": {
                                "action": "start_assessment",
                                "assessment_id": assessment["id"]
                            }
                        }
                    }
                    for assessment in assessments
                ]
            ]
        }
```

---

### 3. 対話フロー（Dialogs）

```python
# backend/app/bots/dialogs/assessment_dialog.py
from botbuilder.dialogs import (
    ComponentDialog, 
    WaterfallDialog, 
    WaterfallStepContext,
    DialogTurnResult
)
from botbuilder.dialogs.prompts import ChoicePrompt, TextPrompt
from botbuilder.core import MessageFactory

class AssessmentDialog(ComponentDialog):
    
    def __init__(self, dialog_id: str):
        super().__init__(dialog_id)
        
        # プロンプトを追加
        self.add_dialog(ChoicePrompt(ChoicePrompt.__name__))
        self.add_dialog(TextPrompt(TextPrompt.__name__))
        
        # ウォーターフォールダイアログ
        self.add_dialog(
            WaterfallDialog(
                "AssessmentWaterfall",
                [
                    self.intro_step,
                    self.question_step,
                    self.answer_step,
                    self.result_step
                ]
            )
        )
        
        self.initial_dialog_id = "AssessmentWaterfall"
    
    async def intro_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        """診断開始"""
        
        assessment_id = step_context.options.get("assessment_id")
        
        # 診断情報を取得
        assessment = await assessment_service.get_assessment(assessment_id)
        
        # 状態に保存
        step_context.values["assessment"] = assessment
        step_context.values["current_question"] = 0
        step_context.values["answers"] = []
        
        # 最初の質問へ
        return await step_context.next([])
    
    async def question_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        """質問を表示"""
        
        assessment = step_context.values["assessment"]
        current_q = step_context.values["current_question"]
        
        if current_q >= len(assessment["questions"]):
            # 全質問完了
            return await step_context.next([])
        
        question = assessment["questions"][current_q]
        
        # Adaptive Cardで質問を表示
        card = self.create_question_card(question)
        
        await step_context.context.send_activity(
            MessageFactory.attachment(card)
        )
        
        # 回答待ち
        return await step_context.prompt(
            ChoicePrompt.__name__,
            {"choices": [opt["text"] for opt in question["options"]]}
        )
    
    async def answer_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        """回答を処理"""
        
        # 回答を保存
        answer = step_context.result
        step_context.values["answers"].append(answer)
        
        # 次の質問へ
        step_context.values["current_question"] += 1
        
        # 質問ステップに戻る
        return await step_context.replace_dialog(self.id)
    
    async def result_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        """結果を表示"""
        
        assessment = step_context.values["assessment"]
        answers = step_context.values["answers"]
        
        # スコアを計算
        score = self.calculate_score(assessment, answers)
        
        # リードを作成
        lead = await lead_service.create_lead({
            "assessment_id": assessment["id"],
            "score": score,
            "answers": answers,
            "source": "teams_bot"
        })
        
        # 結果Cardを送信
        card = self.create_result_card(score, lead)
        
        await step_context.context.send_activity(
            MessageFactory.attachment(card)
        )
        
        return await step_context.end_dialog()
```

---

## コスト分析

### Azure Bot Service料金（2024年）

| 項目 | 無料枠 | 有料プラン |
|------|--------|-----------|
| **Bot Registration** | 無料 | 無料 |
| **Standard Channels** (Teams, Slack, etc.) | 無制限メッセージ | 無制限メッセージ |
| **Premium Channels** | 10,000メッセージ/月 | $0.50 / 1,000メッセージ |

**DiagnoLeadsの想定**:
- Standard Channel (Teams)使用 → **無料**
- Premium Channel不使用 → **$0/月**

---

### Azure App Service料金

| プラン | 仕様 | 月額料金 |
|--------|------|----------|
| **Free** | 60 CPU分/日, 1GB RAM | $0 |
| **B1 (Basic)** | 1 Core, 1.75GB RAM | $13 |
| **S1 (Standard)** | 1 Core, 1.75GB RAM, オートスケール | $70 |

**DiagnoLeadsの推奨**:
- 開発/ステージング: Free ($0)
- 本番（~100テナント）: B1 ($13/月)
- 本番（100+テナント）: S1 ($70/月)

---

### Microsoft Graph API

- **料金**: 無料
- **レート制限**: 1,200 requests/min（テナントあたり）
- **十分な余裕あり**

---

### 総コスト見積もり

| 環境 | Bot Service | App Service | 合計 |
|------|-------------|-------------|------|
| **開発/テスト** | $0 | $0 | **$0/月** |
| **本番（~100テナント）** | $0 | $13 | **$13/月** |
| **本番（100-500テナント）** | $0 | $70 | **$70/月** |
| **本番（500+テナント）** | $0 | $150 | **$150/月** |

**Phase 2の追加コスト**: **$0-70/月**（規模による）

---

### 代替ホスティング（Azure以外）

| プロバイダ | 月額料金 | 備考 |
|-----------|---------|------|
| **Railway** | $5-20 | Bot Service登録は必要 |
| **Fly.io** | $0-10 | Bot Service登録は必要 |
| **Heroku** | $7-25 | Bot Service登録は必要 |

**結論**: Railway/Fly.ioで十分（Bot Service登録は別途必要）

---

## リスクと対策

### リスク1: Azure依存
**確率**: 高  
**影響**: 中  
**対策**:
- Bot登録はAzure必須だが、アプリ自体はどこでもホスト可能
- Railway/Fly.ioで十分動作
- コストは最小限（$0-13/月）

### リスク2: 認証の複雑性
**確率**: 中  
**影響**: 高  
**対策**:
- Bot Framework SDKが大部分を自動処理
- 公式サンプルコードが充実
- 段階的実装（認証なし → OAuth追加）

### リスク3: Teams APIの変更
**確率**: 低  
**影響**: 中  
**対策**:
- Bot Framework v4は安定版
- Microsoftの長期サポート
- 後方互換性あり

### リスク4: ユーザーの学習コスト
**確率**: 中  
**影響**: 低  
**対策**:
- `/help` コマンドで使い方説明
- オンボーディングメッセージ
- Webhook統合と併用可能（移行期間）

---

## 実装計画

### Week 1: セットアップと基本機能

#### Day 1: Azure Bot Service設定
- [ ] Azure Bot Registration作成
- [ ] Bot App IDとPasswordを取得
- [ ] Teams Channelを有効化
- [ ] ngrokでローカル開発環境構築

#### Day 2: Bot Frameworkセットアップ
- [ ] `botbuilder-core`等のライブラリインストール
- [ ] `/api/messages` エンドポイント作成
- [ ] TeamsActivityHandler実装
- [ ] 簡単なエコーボット動作確認

#### Day 3: コマンド実装
- [ ] `/diagnoleads` コマンド
- [ ] `/help` コマンド
- [ ] `/lead {id}` コマンド
- [ ] Adaptive Card表示

#### Day 4-5: 診断フロー実装
- [ ] 診断一覧表示
- [ ] 診断開始
- [ ] 質問→回答の対話フロー
- [ ] 結果表示

### Week 2: 認証とGraph API

#### Day 6-7: OAuth 2.0認証
- [ ] OAuth Connection Settings設定
- [ ] OAuthCard実装
- [ ] トークン取得ロジック
- [ ] 認証フロー動作確認

#### Day 8-9: Graph API統合
- [ ] ユーザープロファイル取得
- [ ] Teams情報取得
- [ ] リード作成時にユーザー情報を自動入力

#### Day 10: テストとバグ修正
- [ ] 統合テスト
- [ ] E2Eテスト（Teams実機）
- [ ] バグ修正

### Week 3: 高度な機能

#### Day 11-12: Proactive Messaging
- [ ] ホットリード発生時にBot通知
- [ ] スケジュール通知（週次レポート）

#### Day 13-14: リッチカード
- [ ] Hero Card、Thumbnail Card
- [ ] Carousel Card（複数診断表示）

#### Day 15: ドキュメントと研修
- [ ] ユーザーガイド作成
- [ ] 管理者ガイド作成
- [ ] チーム研修

### Week 4: デプロイと監視

#### Day 16-17: 本番デプロイ
- [ ] App Service/Railwayへデプロイ
- [ ] 環境変数設定
- [ ] HTTPS設定

#### Day 18-19: 監視とアラート
- [ ] Application Insights設定
- [ ] エラーアラート
- [ ] 使用状況ダッシュボード

#### Day 20: 本番リリース
- [ ] ベータテスト（5-10テナント）
- [ ] フィードバック収集
- [ ] 全テナントへ展開

---

## 必要なリソース

### 開発チーム
- **Backend Developer**: 1名（3-4週間フルタイム）
- **QA Engineer**: 0.5名（Week 2-4）
- **DevOps**: 0.5名（Week 4）

### 技術スキル
- Python (中級以上)
- Bot Framework経験（初級可、学習しながら）
- Azure基礎知識
- Teams API理解

### インフラ
- Azure Bot Service（無料）
- App Service または Railway（$0-70/月）
- 既存PostgreSQL
- 既存Redis（オプション）

---

## 技術的依存関係

### 必須ライブラリ

```python
# requirements.txt (追加分)

# Bot Framework
botbuilder-core==4.15.0
botbuilder-schema==4.15.0
botbuilder-dialogs==4.15.0
botbuilder-integration-aiohttp==4.15.0

# Microsoft Graph
msal==1.25.0
microsoft-graph==0.2.0

# Azure Storage (状態管理 - オプション)
azure-storage-blob==12.19.0

# 合計追加サイズ: 約15MB
```

### システム要件
- Python 3.11+
- HTTPS必須
- Public IPアドレス
- Webhook受信可能

---

## 次のステップ

### 即座に実施
1. ✅ 技術調査完了（このドキュメント）
2. → プロダクトオーナーへの提案
3. → 優先度とタイムライン決定

### Phase 2開始前
1. Azure Bot Serviceアカウント準備
2. 開発環境セットアップ（ngrok）
3. Bot Framework SDKの学習（1-2日）

### Phase 2実装時
1. Week 1: 基本機能
2. Week 2: 認証・Graph API
3. Week 3: 高度な機能
4. Week 4: デプロイ・監視

---

## 参考資料

### 公式ドキュメント
- [Bot Framework Python SDK](https://github.com/Microsoft/botbuilder-python)
- [Teams Bot Samples (Python)](https://github.com/OfficeDev/Microsoft-Teams-Samples/tree/main/samples)
- [Azure Bot Service Documentation](https://learn.microsoft.com/en-us/azure/bot-service/)
- [Microsoft Graph API](https://learn.microsoft.com/en-us/graph/)

### コードサンプル
- [Teams Conversation Bot (Python)](https://github.com/OfficeDev/Microsoft-Teams-Samples/tree/main/samples/bot-conversation/python)
- [Teams Auth Bot (Python)](https://github.com/OfficeDev/Microsoft-Teams-Samples/tree/main/samples/bot-teams-authentication/python)

### チュートリアル
- [Bot Framework Quickstart](https://learn.microsoft.com/en-us/azure/bot-service/bot-service-quickstart)
- [OAuth 2.0 in Bot Framework](https://learn.microsoft.com/en-us/microsoftteams/platform/bots/how-to/authentication/auth-flow-bot)

---

**Status**: ✅ Research Complete, Ready for Planning  
**Recommendation**: **Proceed to Phase 2 implementation**  
**Estimated Start Date**: After QR Code implementation (Week 3-4)

---

**調査者**: Factory Droid  
**レビュー待ち**: Tech Lead, Product Owner  
**作成日**: 2025-11-11
