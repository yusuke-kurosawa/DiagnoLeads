# Lead Nurturing & Marketing Automation

**Status**: Approved
**Priority**: High
**Phase**: 2 (Growth & Retention)
**Estimated Effort**: 10-12 weeks
**Dependencies**: Subscription System, Email Service, Lead Management

## Overview

リード育成・マーケティングオートメーション機能により、獲得したリードを自動的に育成し、商談化率を向上させます。ドリップメールキャンペーン、自動スコアリング、セグメント化、タスク管理により、営業・マーケティングチームの生産性を劇的に改善します。

## Business Value

- **商談化率向上**: +150%（適切なタイミングでのフォローアップ）
- **営業生産性**: +80%（自動化により手動作業削減）
- **顧客ROI**: リード獲得コストあたりの商談数 +200%
- **顧客満足度**: 解約率 -20%（価値提供の可視化）
- **LTV向上**: 顧客生涯価値 +60%

## Core Features

### 1. ドリップメールキャンペーン
- 診断後の自動フォローアップメール
- マルチステップキャンペーン
- トリガーベース配信（行動、スコア、日数）
- A/Bテスト対応

### 2. リードスコアリングルールエンジン
- カスタムスコアリングルール設定
- 行動ベーススコアリング（診断完了、メール開封、リンククリック）
- 属性ベーススコアリング（業界、役職、企業規模）
- 自動ホットリード判定

### 3. 自動セグメント化
- 動的セグメント（リアルタイム更新）
- 多軸セグメンテーション（スコア、業界、行動）
- セグメント別キャンペーン
- AIレコメンデーション

### 4. タスク管理・リマインダー
- 自動タスク生成（ホットリード検出時）
- 営業担当者への通知
- フォローアップリマインダー
- タスク完了トラッキング

### 5. リードライフサイクル管理
- ステージ自動遷移（新規 → MQL → SQL → 商談 → 成約）
- ステージ別自動アクション
- パイプライン可視化
- コンバージョン率追跡

## User Stories

### 1. ドリップメールキャンペーン作成

**As a** マーケティング担当者
**I want to** 診断完了後の自動フォローアップキャンペーンを設定
**So that** リードを継続的に育成できる

**Acceptance Criteria**:

**Given**: キャンペーンビルダーにアクセス
**When**: 新規キャンペーンを作成
**Then**:
- キャンペーン名・説明を入力
- トリガー設定:
  - 診断完了時
  - リードスコアが80以上
  - 特定の業界
- メールシーケンス設定:
  - Step 1: 診断完了直後（お礼メール）
  - Step 2: 1日後（詳細レポート）
  - Step 3: 3日後（ケーススタディ）
  - Step 4: 7日後（デモ案内）
  - Step 5: 14日後（期間限定オファー）
- 各ステップに遅延時間・条件分岐設定
- プレビュー・テスト送信
- 有効化

**Given**: キャンペーンが有効化されている
**When**: リードが診断を完了
**Then**:
- 条件に一致するリードが自動的にキャンペーンに登録
- Step 1のメールが即座に送信
- 以降のステップがスケジュール通りに配信
- キャンペーンダッシュボードに統計表示（開封率、クリック率）

**Given**: リードがメール内のリンクをクリック
**When**: 高エンゲージメントを検出
**Then**:
- リードスコアが自動的に+10ポイント
- 営業担当者に即座に通知
- オプション: 次のステップを前倒し

### 2. カスタムスコアリングルール設定

**As a** セールスディレクター
**I want to** 自社に最適なリードスコアリングルールを設定
**So that** 本当に商談化しやすいリードを優先できる

**Acceptance Criteria**:

**Given**: スコアリング設定ページにアクセス
**When**: 新規ルールを追加
**Then**:
- ルールタイプ選択:
  - 行動ベース
  - 属性ベース
  - マイナススコア
- 行動ルール例:
  - 診断完了: +20点
  - メール開封: +5点
  - メールクリック: +10点
  - サイト再訪: +15点
  - 資料ダウンロード: +25点
  - デモ申込: +50点
- 属性ルール例:
  - 企業規模 500名以上: +30点
  - 役職 部長以上: +25点
  - 業界 IT/SaaS: +20点
  - 予算権限あり: +40点
- マイナスルール例:
  - 無料メールアドレス: -10点
  - 学生: -50点
  - 7日間無活動: -5点
- 各ルールに重み付け設定
- ホットリード閾値設定（例: 80点以上）

**Given**: スコアリングルールが設定されている
**When**: リードが行動を起こす
**Then**:
- スコアがリアルタイムで更新
- スコア履歴が記録される
- ホットリード閾値を超えた場合:
  - 営業に即座に通知（メール、Slack、Teams）
  - 自動タスク作成
  - ダッシュボードで強調表示

### 3. 動的セグメント作成

**As a** マーケティングマネージャー
**I want to** リードを自動的にセグメント化
**So that** パーソナライズされたキャンペーンを実施できる

**Acceptance Criteria**:

**Given**: セグメントビルダーにアクセス
**When**: 新規セグメントを作成
**Then**:
- セグメント名・説明入力
- 条件設定（ANDやOR で複数条件）:
  - スコア範囲（例: 60-79点）
  - 業界（例: 製造業、IT）
  - 企業規模（例: 100-500名）
  - 診断完了日（例: 過去7日以内）
  - エンゲージメント（例: メール開封あり）
  - カスタムフィールド
- 動的 vs 静的セグメント選択
  - 動的: 条件に一致するリードが自動追加/削除
  - 静的: 作成時点のスナップショット
- プレビュー: マッチするリード数表示
- 保存

**Given**: 動的セグメントが作成されている
**When**: リードの属性やスコアが変化
**Then**:
- 条件に一致すれば自動的にセグメントに追加
- 条件から外れれば自動的に削除
- セグメント統計がリアルタイムで更新

**Given**: セグメントが作成されている
**When**: セグメントからキャンペーンを起動
**Then**:
- セグメント内の全リードに一括送信
- またはドリップキャンペーンに登録
- セグメント専用のランディングページ生成可能

### 4. 自動タスク生成・営業通知

**As a** 営業担当者
**I want to** ホットリード発生時に自動的にタスクが作成される
**So that** フォローアップを忘れない

**Acceptance Criteria**:

**Given**: 自動化ルールが設定されている
**When**: リードがホットリード（80点以上）になる
**Then**:
- 営業担当者に即座に通知:
  - メール通知（リード詳細含む）
  - Slackメンション
  - Teamsメンション（統合済みの場合）
  - アプリ内通知
- 自動タスク作成:
  - タスク名: 「【ホットリード】[会社名] [担当者名]さんへの架電」
  - 期日: 24時間以内
  - 優先度: 高
  - 担当者: 自動割当（ラウンドロビンまたは地域別）
- タスク詳細:
  - リード情報（会社名、担当者、役職、電話、メール）
  - 診断結果サマリー
  - スコア内訳
  - 推奨アクション（AI生成）

**Given**: タスクが作成されている
**When**: タスクページにアクセス
**Then**:
- タスク一覧表示（優先度・期日順）
- フィルター（担当者、優先度、ステータス）
- タスク詳細モーダル
- 「完了」ボタンで完了マーク
- メモ・活動記録追加
- 次回フォローアップ設定

**Given**: タスクの期日が近づいている
**When**: 期日24時間前
**Then**:
- リマインダー通知送信
- 未完了の場合、期日後にエスカレーション通知（上司へ）

### 5. リードライフサイクル管理

**As a** セールスディレクター
**I want to** リードのステージを自動的に管理
**So that** パイプラインを可視化できる

**Acceptance Criteria**:

**Given**: ライフサイクルステージが定義されている
**When**: リードが条件を満たす
**Then**:
- ステージが自動遷移:
  - **新規リード**: 診断完了時
  - **MQL (Marketing Qualified Lead)**: スコア60点以上
  - **SQL (Sales Qualified Lead)**: スコア80点以上 + 営業コンタクト
  - **商談**: 提案書送付
  - **成約**: 契約締結
  - **失注**: 断られた
  - **ナーチャリング中**: スコア低下

**Given**: ステージが変更された
**When**: 自動化ルールが設定されている
**Then**:
- ステージ別アクション実行:
  - MQL → 営業に通知 + 自動タスク作成
  - SQL → CRMに自動同期 + マネージャーに報告
  - 商談 → 提案テンプレート送信
  - 成約 → ウェルカムメール + オンボーディング開始
  - 失注 → ナーチャリングキャンペーンに登録

**Given**: ライフサイクルレポートにアクセス
**When**: ダッシュボードを開く
**Then**:
- パイプライン可視化（ファネルチャート）
- 各ステージのリード数
- ステージ間のコンバージョン率
- 平均滞在日数
- ボトルネック分析

## Technical Architecture

### Campaign Builder Service

```python
# backend/app/services/automation/campaign_service.py
from typing import List, Dict
from app.models import Campaign, CampaignStep, Lead
from app.services.email.email_service import EmailService

class CampaignService:
    """ドリップキャンペーン管理"""

    async def create_campaign(
        self,
        tenant_id: str,
        name: str,
        trigger_type: str,
        trigger_conditions: Dict,
        steps: List[Dict]
    ) -> Campaign:
        """キャンペーン作成"""

        campaign = await Campaign.create(
            tenant_id=tenant_id,
            name=name,
            trigger_type=trigger_type,  # assessment_completed, score_threshold, etc.
            trigger_conditions=trigger_conditions,
            status="active"
        )

        # ステップ作成
        for idx, step_data in enumerate(steps):
            await CampaignStep.create(
                campaign_id=campaign.id,
                step_order=idx + 1,
                delay_value=step_data["delay_value"],
                delay_unit=step_data["delay_unit"],  # minutes, hours, days
                email_template_id=step_data["email_template_id"],
                conditions=step_data.get("conditions", {})
            )

        return campaign

    async def enroll_lead(self, campaign_id: str, lead_id: str):
        """リードをキャンペーンに登録"""

        campaign = await Campaign.get(campaign_id)
        lead = await Lead.get(lead_id)

        # 既存登録チェック
        existing = await CampaignEnrollment.get_by_campaign_and_lead(
            campaign_id, lead_id
        )
        if existing:
            return existing

        # 登録
        enrollment = await CampaignEnrollment.create(
            campaign_id=campaign_id,
            lead_id=lead_id,
            current_step=1,
            status="active",
            enrolled_at=datetime.utcnow()
        )

        # 最初のステップを即座に実行
        await self._execute_step(enrollment, 1)

        return enrollment

    async def _execute_step(self, enrollment: CampaignEnrollment, step_number: int):
        """ステップ実行"""

        step = await CampaignStep.get_by_campaign_and_order(
            enrollment.campaign_id, step_number
        )

        if not step:
            # キャンペーン完了
            enrollment.status = "completed"
            enrollment.completed_at = datetime.utcnow()
            await enrollment.save()
            return

        lead = await Lead.get(enrollment.lead_id)

        # 条件チェック
        if step.conditions and not self._check_conditions(lead, step.conditions):
            # 条件未達: スキップして次へ
            await self._schedule_next_step(enrollment, step_number + 1)
            return

        # メール送信
        email_service = EmailService()
        await email_service.send_campaign_email(
            lead=lead,
            template_id=step.email_template_id,
            campaign_id=enrollment.campaign_id,
            step_number=step_number
        )

        # ステップ記録
        await CampaignStepExecution.create(
            enrollment_id=enrollment.id,
            step_id=step.id,
            executed_at=datetime.utcnow(),
            status="sent"
        )

        # 次のステップをスケジュール
        await self._schedule_next_step(enrollment, step_number + 1, step.delay_value, step.delay_unit)

    async def _schedule_next_step(
        self,
        enrollment: CampaignEnrollment,
        next_step: int,
        delay_value: int = 0,
        delay_unit: str = "days"
    ):
        """次のステップをスケジュール"""

        # 遅延時間計算
        delay_seconds = self._calculate_delay(delay_value, delay_unit)

        # バックグラウンドジョブでスケジュール（Trigger.dev or Celery）
        from app.tasks import execute_campaign_step

        execute_campaign_step.apply_async(
            args=[enrollment.id, next_step],
            countdown=delay_seconds
        )
```

### Lead Scoring Engine

```python
# backend/app/services/automation/scoring_service.py
from typing import List, Dict
from app.models import Lead, ScoringRule, ScoreHistory

class LeadScoringService:
    """リードスコアリングエンジン"""

    async def apply_scoring_rules(
        self,
        lead: Lead,
        event_type: str,
        event_data: Dict = None
    ):
        """スコアリングルール適用"""

        # テナントのスコアリングルール取得
        rules = await ScoringRule.get_active_by_tenant(lead.tenant_id)

        total_score_change = 0

        for rule in rules:
            # ルールに一致するか判定
            if self._matches_rule(lead, event_type, event_data, rule):
                score_change = rule.points

                # スコア更新
                lead.score += score_change
                total_score_change += score_change

                # 履歴記録
                await ScoreHistory.create(
                    lead_id=lead.id,
                    rule_id=rule.id,
                    event_type=event_type,
                    score_change=score_change,
                    old_score=lead.score - score_change,
                    new_score=lead.score,
                    event_data=event_data
                )

        # スコア上下限チェック
        lead.score = max(0, min(100, lead.score))
        await lead.save()

        # ホットリード判定
        if total_score_change > 0:
            await self._check_hot_lead_threshold(lead)

    async def _check_hot_lead_threshold(self, lead: Lead):
        """ホットリード閾値チェック"""

        tenant_settings = await TenantSettings.get_by_tenant(lead.tenant_id)
        hot_lead_threshold = tenant_settings.hot_lead_threshold or 80

        # 以前はホットリードではなかったが、今回超えた
        if lead.score >= hot_lead_threshold and not lead.is_hot_lead:
            lead.is_hot_lead = True
            lead.became_hot_at = datetime.utcnow()
            await lead.save()

            # ホットリードアクショントリガー
            await self._trigger_hot_lead_actions(lead)

    async def _trigger_hot_lead_actions(self, lead: Lead):
        """ホットリード検出時のアクション"""

        # 1. 営業通知
        from app.services.notifications.notification_service import NotificationService
        notification_service = NotificationService()

        await notification_service.send_hot_lead_alert(
            lead=lead,
            channels=["email", "slack", "teams", "in_app"]
        )

        # 2. 自動タスク作成
        from app.services.tasks.task_service import TaskService
        task_service = TaskService()

        await task_service.create_hot_lead_task(
            lead=lead,
            due_in_hours=24
        )

        # 3. ライフサイクルステージ更新（MQL → SQL）
        if lead.lifecycle_stage == "mql":
            lead.lifecycle_stage = "sql"
            await lead.save()

        # 4. CRM同期（設定されている場合）
        if lead.tenant.has_crm_integration:
            from app.services.integrations.crm_sync import CRMSyncService
            crm_service = CRMSyncService()
            await crm_service.sync_hot_lead(lead)

    def _matches_rule(
        self,
        lead: Lead,
        event_type: str,
        event_data: Dict,
        rule: ScoringRule
    ) -> bool:
        """ルールマッチング判定"""

        # イベントタイプチェック
        if rule.event_type != event_type:
            return False

        # 属性条件チェック
        if rule.attribute_conditions:
            for attr, condition in rule.attribute_conditions.items():
                lead_value = getattr(lead, attr, None)

                if not self._evaluate_condition(lead_value, condition):
                    return False

        return True
```

### Segmentation Engine

```python
# backend/app/services/automation/segmentation_service.py
from sqlalchemy import and_, or_
from app.models import Segment, Lead

class SegmentationService:
    """セグメンテーションエンジン"""

    async def create_segment(
        self,
        tenant_id: str,
        name: str,
        description: str,
        conditions: List[Dict],
        is_dynamic: bool = True
    ) -> Segment:
        """セグメント作成"""

        segment = await Segment.create(
            tenant_id=tenant_id,
            name=name,
            description=description,
            conditions=conditions,
            is_dynamic=is_dynamic
        )

        # 静的セグメントの場合、現在のマッチリードをスナップショット
        if not is_dynamic:
            leads = await self.get_matching_leads(segment)
            await SegmentMembership.bulk_create([
                {"segment_id": segment.id, "lead_id": lead.id}
                for lead in leads
            ])

        return segment

    async def get_matching_leads(self, segment: Segment) -> List[Lead]:
        """セグメント条件にマッチするリード取得"""

        query = Lead.query.filter(Lead.tenant_id == segment.tenant_id)

        # 条件を動的にSQLクエリに変換
        for condition_group in segment.conditions:
            group_filters = []

            for condition in condition_group["conditions"]:
                field = condition["field"]
                operator = condition["operator"]
                value = condition["value"]

                filter_clause = self._build_filter_clause(field, operator, value)
                group_filters.append(filter_clause)

            # ANDまたはOR結合
            if condition_group["logic"] == "AND":
                query = query.filter(and_(*group_filters))
            else:
                query = query.filter(or_(*group_filters))

        leads = await query.all()
        return leads

    def _build_filter_clause(self, field: str, operator: str, value):
        """フィルター条件構築"""

        field_obj = getattr(Lead, field)

        operators = {
            "equals": lambda f, v: f == v,
            "not_equals": lambda f, v: f != v,
            "greater_than": lambda f, v: f > v,
            "less_than": lambda f, v: f < v,
            "contains": lambda f, v: f.contains(v),
            "in": lambda f, v: f.in_(v),
            "between": lambda f, v: f.between(v[0], v[1])
        }

        return operators[operator](field_obj, value)

    async def refresh_dynamic_segments(self, tenant_id: str):
        """動的セグメントの更新（定期実行）"""

        segments = await Segment.get_dynamic_by_tenant(tenant_id)

        for segment in segments:
            # 現在のマッチリード取得
            current_leads = await self.get_matching_leads(segment)
            current_lead_ids = {lead.id for lead in current_leads}

            # 既存メンバーシップ取得
            existing_memberships = await SegmentMembership.get_by_segment(segment.id)
            existing_lead_ids = {m.lead_id for m in existing_memberships}

            # 追加・削除を計算
            to_add = current_lead_ids - existing_lead_ids
            to_remove = existing_lead_ids - current_lead_ids

            # 追加
            if to_add:
                await SegmentMembership.bulk_create([
                    {"segment_id": segment.id, "lead_id": lead_id}
                    for lead_id in to_add
                ])

            # 削除
            if to_remove:
                await SegmentMembership.bulk_delete(segment.id, list(to_remove))

            # 統計更新
            segment.member_count = len(current_lead_ids)
            segment.last_refreshed_at = datetime.utcnow()
            await segment.save()
```

## API Endpoints

### キャンペーン管理

```
POST   /api/v1/automation/campaigns
       - ドリップキャンペーン作成
       - Request: { name, trigger_type, trigger_conditions, steps[] }

GET    /api/v1/automation/campaigns
       - キャンペーン一覧

GET    /api/v1/automation/campaigns/{id}
       - キャンペーン詳細

PUT    /api/v1/automation/campaigns/{id}
       - キャンペーン更新

DELETE /api/v1/automation/campaigns/{id}
       - キャンペーン削除

POST   /api/v1/automation/campaigns/{id}/activate
       - キャンペーン有効化

POST   /api/v1/automation/campaigns/{id}/pause
       - キャンペーン一時停止

GET    /api/v1/automation/campaigns/{id}/analytics
       - キャンペーン分析（開封率、クリック率、コンバージョン率）
```

### スコアリング管理

```
GET    /api/v1/automation/scoring-rules
       - スコアリングルール一覧

POST   /api/v1/automation/scoring-rules
       - ルール作成
       - Request: { name, event_type, attribute_conditions, points }

PUT    /api/v1/automation/scoring-rules/{id}
       - ルール更新

DELETE /api/v1/automation/scoring-rules/{id}
       - ルール削除

GET    /api/v1/leads/{id}/score-history
       - リードのスコア履歴取得
```

### セグメント管理

```
POST   /api/v1/automation/segments
       - セグメント作成
       - Request: { name, description, conditions[], is_dynamic }

GET    /api/v1/automation/segments
       - セグメント一覧

GET    /api/v1/automation/segments/{id}
       - セグメント詳細

GET    /api/v1/automation/segments/{id}/leads
       - セグメント内のリード一覧

POST   /api/v1/automation/segments/{id}/refresh
       - 動的セグメント手動更新

POST   /api/v1/automation/segments/{id}/export
       - セグメントCSVエクスポート
```

### タスク管理

```
GET    /api/v1/tasks
       - タスク一覧（フィルター、ソート対応）
       - Query: ?assigned_to={user_id}&status={status}&priority={priority}

POST   /api/v1/tasks
       - タスク作成

PUT    /api/v1/tasks/{id}
       - タスク更新

POST   /api/v1/tasks/{id}/complete
       - タスク完了

GET    /api/v1/tasks/stats
       - タスク統計（完了率、平均対応時間）
```

## Database Schema

```sql
-- キャンペーン
CREATE TABLE campaigns (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,

    name VARCHAR(255) NOT NULL,
    description TEXT,

    -- トリガー設定
    trigger_type VARCHAR(50) NOT NULL,  -- assessment_completed, score_threshold, segment_entry
    trigger_conditions JSONB,

    status VARCHAR(50) DEFAULT 'draft',  -- draft, active, paused, completed

    -- 統計
    enrolled_count INTEGER DEFAULT 0,
    completed_count INTEGER DEFAULT 0,

    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),

    INDEX idx_campaigns_tenant (tenant_id),
    INDEX idx_campaigns_status (status)
);

-- キャンペーンステップ
CREATE TABLE campaign_steps (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    campaign_id UUID NOT NULL REFERENCES campaigns(id) ON DELETE CASCADE,

    step_order INTEGER NOT NULL,

    -- 遅延設定
    delay_value INTEGER NOT NULL,
    delay_unit VARCHAR(20) NOT NULL,  -- minutes, hours, days

    -- メール設定
    email_template_id UUID REFERENCES email_templates(id),

    -- 条件分岐
    conditions JSONB,  -- オプション: 特定条件でのみ実行

    created_at TIMESTAMP DEFAULT NOW(),

    INDEX idx_campaign_steps_campaign (campaign_id, step_order)
);

-- キャンペーン登録
CREATE TABLE campaign_enrollments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    campaign_id UUID NOT NULL REFERENCES campaigns(id) ON DELETE CASCADE,
    lead_id UUID NOT NULL REFERENCES leads(id) ON DELETE CASCADE,

    current_step INTEGER DEFAULT 1,
    status VARCHAR(50) DEFAULT 'active',  -- active, paused, completed, unsubscribed

    enrolled_at TIMESTAMP DEFAULT NOW(),
    completed_at TIMESTAMP,

    UNIQUE(campaign_id, lead_id),
    INDEX idx_enrollments_campaign (campaign_id),
    INDEX idx_enrollments_lead (lead_id),
    INDEX idx_enrollments_status (status)
);

-- ステップ実行履歴
CREATE TABLE campaign_step_executions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    enrollment_id UUID NOT NULL REFERENCES campaign_enrollments(id) ON DELETE CASCADE,
    step_id UUID NOT NULL REFERENCES campaign_steps(id),

    executed_at TIMESTAMP DEFAULT NOW(),
    status VARCHAR(50) DEFAULT 'sent',  -- sent, opened, clicked, bounced

    -- エンゲージメント
    opened_at TIMESTAMP,
    clicked_at TIMESTAMP,
    link_clicked VARCHAR(500),

    INDEX idx_step_executions_enrollment (enrollment_id)
);

-- スコアリングルール
CREATE TABLE scoring_rules (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,

    name VARCHAR(255) NOT NULL,
    description TEXT,

    -- ルール設定
    rule_type VARCHAR(50) NOT NULL,  -- behavioral, attribute, decay
    event_type VARCHAR(100),  -- assessment_completed, email_opened, etc.
    attribute_conditions JSONB,  -- { "industry": "IT", "company_size": ">100" }

    points INTEGER NOT NULL,  -- 加算ポイント（マイナス可）

    is_active BOOLEAN DEFAULT TRUE,

    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),

    INDEX idx_scoring_rules_tenant (tenant_id)
);

-- スコア履歴
CREATE TABLE score_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    lead_id UUID NOT NULL REFERENCES leads(id) ON DELETE CASCADE,
    rule_id UUID REFERENCES scoring_rules(id) ON DELETE SET NULL,

    event_type VARCHAR(100) NOT NULL,
    score_change INTEGER NOT NULL,
    old_score INTEGER NOT NULL,
    new_score INTEGER NOT NULL,

    event_data JSONB,

    created_at TIMESTAMP DEFAULT NOW(),

    INDEX idx_score_history_lead (lead_id, created_at DESC)
);

-- セグメント
CREATE TABLE segments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,

    name VARCHAR(255) NOT NULL,
    description TEXT,

    -- 条件定義
    conditions JSONB NOT NULL,  -- [{ logic: "AND", conditions: [{ field, operator, value }] }]

    is_dynamic BOOLEAN DEFAULT TRUE,  -- 動的 or 静的

    member_count INTEGER DEFAULT 0,
    last_refreshed_at TIMESTAMP,

    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),

    INDEX idx_segments_tenant (tenant_id)
);

-- セグメントメンバーシップ
CREATE TABLE segment_memberships (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    segment_id UUID NOT NULL REFERENCES segments(id) ON DELETE CASCADE,
    lead_id UUID NOT NULL REFERENCES leads(id) ON DELETE CASCADE,

    added_at TIMESTAMP DEFAULT NOW(),

    UNIQUE(segment_id, lead_id),
    INDEX idx_memberships_segment (segment_id),
    INDEX idx_memberships_lead (lead_id)
);

-- タスク
CREATE TABLE tasks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    lead_id UUID REFERENCES leads(id) ON DELETE SET NULL,

    title VARCHAR(255) NOT NULL,
    description TEXT,

    assigned_to UUID REFERENCES users(id),
    priority VARCHAR(20) DEFAULT 'medium',  -- low, medium, high, urgent

    status VARCHAR(50) DEFAULT 'open',  -- open, in_progress, completed, cancelled

    due_date TIMESTAMP,
    completed_at TIMESTAMP,

    task_type VARCHAR(50),  -- follow_up, demo, proposal, etc.

    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),

    INDEX idx_tasks_tenant (tenant_id),
    INDEX idx_tasks_assigned (assigned_to, status),
    INDEX idx_tasks_due_date (due_date)
);

-- Leadsテーブルに追加カラム
ALTER TABLE leads ADD COLUMN score INTEGER DEFAULT 0;
ALTER TABLE leads ADD COLUMN is_hot_lead BOOLEAN DEFAULT FALSE;
ALTER TABLE leads ADD COLUMN became_hot_at TIMESTAMP;
ALTER TABLE leads ADD COLUMN lifecycle_stage VARCHAR(50) DEFAULT 'new';
-- Lifecycle stages: new, mql, sql, opportunity, customer, churned
```

## Frontend Components

### Campaign Builder

```typescript
// frontend/src/features/automation/CampaignBuilder.tsx
import { useState } from 'react'
import { DragDropContext, Droppable, Draggable } from '@hello-pangea/dnd'
import { Plus, Mail, Clock } from 'lucide-react'

export function CampaignBuilder() {
  const [steps, setSteps] = useState([])

  const addStep = () => {
    setSteps([...steps, {
      id: `step-${Date.now()}`,
      delay: { value: 1, unit: 'days' },
      emailTemplate: null
    }])
  }

  return (
    <div className="max-w-5xl mx-auto p-6">
      <h1 className="text-3xl font-bold mb-8">キャンペーンビルダー</h1>

      <Card className="mb-6">
        <CardHeader>
          <CardTitle>トリガー設定</CardTitle>
        </CardHeader>
        <CardContent>
          <Select>
            <SelectItem value="assessment_completed">診断完了時</SelectItem>
            <SelectItem value="score_threshold">スコア閾値到達時</SelectItem>
            <SelectItem value="segment_entry">セグメント追加時</SelectItem>
          </Select>
        </CardContent>
      </Card>

      <div className="space-y-4">
        <DragDropContext onDragEnd={handleDragEnd}>
          <Droppable droppableId="steps">
            {(provided) => (
              <div {...provided.droppableProps} ref={provided.innerRef}>
                {steps.map((step, index) => (
                  <Draggable key={step.id} draggableId={step.id} index={index}>
                    {(provided) => (
                      <Card
                        ref={provided.innerRef}
                        {...provided.draggableProps}
                        {...provided.dragHandleProps}
                        className="mb-4"
                      >
                        <CardHeader>
                          <CardTitle className="flex items-center">
                            <Mail className="mr-2" />
                            ステップ {index + 1}
                          </CardTitle>
                        </CardHeader>
                        <CardContent>
                          <div className="grid md:grid-cols-2 gap-4">
                            <div>
                              <Label>遅延時間</Label>
                              <div className="flex gap-2">
                                <Input
                                  type="number"
                                  value={step.delay.value}
                                  onChange={(e) => updateStepDelay(step.id, 'value', e.target.value)}
                                />
                                <Select
                                  value={step.delay.unit}
                                  onChange={(v) => updateStepDelay(step.id, 'unit', v)}
                                >
                                  <SelectItem value="minutes">分</SelectItem>
                                  <SelectItem value="hours">時間</SelectItem>
                                  <SelectItem value="days">日</SelectItem>
                                </Select>
                              </div>
                            </div>

                            <div>
                              <Label>メールテンプレート</Label>
                              <TemplateSelector
                                value={step.emailTemplate}
                                onChange={(template) => updateStepTemplate(step.id, template)}
                              />
                            </div>
                          </div>
                        </CardContent>
                      </Card>
                    )}
                  </Draggable>
                ))}
                {provided.placeholder}
              </div>
            )}
          </Droppable>
        </DragDropContext>

        <Button onClick={addStep} variant="outline" className="w-full">
          <Plus className="mr-2" size={16} />
          ステップを追加
        </Button>
      </div>
    </div>
  )
}
```

## Security Considerations

- **配信停止リンク**: すべてのメールに配信停止リンクを含める（法的要件）
- **データプライバシー**: GDPR準拠（データ削除リクエスト対応）
- **テナント分離**: キャンペーン・セグメント・タスクは必ずテナントフィルタリング
- **レート制限**: メール配信のレート制限（1時間あたり上限）
- **スパム対策**: SPF/DKIM/DMARC設定、バウンス処理

## Testing Strategy

### 単体テスト
- スコアリングロジック
- セグメント条件評価
- キャンペーンステップ実行

### 統合テスト
- キャンペーンエンロール → メール送信
- スコア更新 → ホットリード検出 → タスク作成
- セグメント更新

### E2Eテスト
- キャンペーン作成 → リード登録 → メール配信 → 開封トラッキング
- スコアリングルール設定 → リード行動 → ホットリード化 → 営業通知

## Performance Requirements

- **セグメント更新**: 10,000リード/秒
- **スコア計算**: <50ms
- **キャンペーンエンロール**: <100ms
- **メール配信**: バックグラウンド処理（非同期）

## Rollout Plan

### Week 1-3: スコアリングエンジン
- スコアリングルール設定UI
- スコア計算ロジック
- ホットリード検出・通知

### Week 4-6: セグメンテーション
- セグメントビルダー
- 動的セグメント更新
- セグメント分析

### Week 7-9: キャンペーン管理
- キャンペーンビルダー
- ドリップメール配信
- エンゲージメントトラッキング

### Week 10-12: タスク管理・統合
- タスク自動生成
- 営業通知
- ライフサイクル管理
- CRM統合

## Success Metrics

- **キャンペーン利用率**: 70%のテナントが1つ以上のキャンペーンを運用
- **商談化率**: +150%（自動化前比）
- **平均対応時間**: ホットリード発生から初回コンタクトまで平均4時間以内
- **メール開封率**: 35%以上
- **メールクリック率**: 8%以上

## Related Specifications

- [Subscription & Billing](./subscription-billing.md) - プラン別機能制限
- [Analytics Dashboard](./analytics-dashboard.md) - キャンペーン分析
- [Integrations](./integrations.md) - CRM同期

## References

- [Marketing Automation Best Practices](https://www.hubspot.com/marketing-automation)
- [Lead Scoring Strategies](https://www.salesforce.com/resources/articles/lead-scoring/)
- [Drip Campaign Guide](https://mailchimp.com/resources/drip-campaigns/)
- [Email Marketing Regulations](https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business)
