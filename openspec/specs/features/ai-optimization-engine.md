# AI-Powered Conversion Optimization Engine

**Status**: Approved  
**Priority**: Critical  
**Phase**: 1 (MVP+)  
**Estimated Effort**: 8 weeks  
**Dependencies**: Claude API, Statistical Analysis Libraries

## Overview

AIが診断のコンバージョン率を自動的に最適化するエンジン。A/Bテスト、コピーライティング提案、予測分析により、人手をかけずに継続的にパフォーマンスを改善します。

## Business Value

- **CVR改善**: 平均 +50%（自動最適化）
- **工数削減**: マーケターの最適化作業 80%削減
- **ROI向上**: 広告費用対効果 +120%
- **競争優位**: AIネイティブ最適化は業界初

## Core Features

### 1. Intelligent A/B Testing
- マルチバリエーション自動テスト
- マルチアームバンディットアルゴリズム
- リアルタイム勝者判定

### 2. AI Copywriting
- 質問文の自動改善提案
- 代替文言生成（A/Bテスト用）
- 感情分析とトーン最適化

### 3. Predictive Analytics
- コンバージョン率予測
- リード品質スコア予測
- チャーン予測

## User Stories

### 1. 自動A/Bテスト実行

**As a** マーケティング担当者  
**I want to** 診断の複数バリエーションを自動テスト  
**So that** 最も効果的なバージョンを見つけられる

**Acceptance Criteria**:

**Given**: 診断に2つ以上のバリエーションが設定されている  
**When**: A/Bテストを開始  
**Then**:
- トラフィックが各バリエーションに均等配分される（初期）
- 各バリエーションの完了率、リード獲得率をトラッキング
- 統計的有意差が出たら（p<0.05）、優勝バリエーションに80%配分
- ダッシュボードに結果をリアルタイム表示
- 自動的に勝者を採用（オプション）

**Given**: 3つ以上のバリエーションがある  
**When**: マルチアームバンディットモードで実行  
**Then**:
- 初期は均等配分（Exploration）
- 早期に劣っているバリエーションの配分を減らす（Exploitation）
- 最適バリエーションに収束

### 2. AIコピーライティング支援

**As a** コンテンツ担当者  
**I want to** AIに質問文の改善提案をしてもらう  
**So that** より魅力的な文言でCV率を上げられる

**Acceptance Criteria**:

**Given**: 質問を選択している  
**When**: 「AI改善提案」ボタンをクリック  
**Then**:
- Claude APIが3つの代替文言を生成
- 各提案に改善理由を表示（例: 「より具体的」「感情に訴える」「簡潔」）
- 提案を採用してバリエーション作成
- 自動的にA/Bテスト設定

**Given**: 質問文が長すぎる（200文字以上）  
**When**: AI分析を実行  
**Then**:
- 「質問が長すぎます（離脱リスク）」と警告
- 短縮版を3つ提案
- 可読性スコアを表示

### 3. 予測分析ダッシュボード

**As a** マーケティングマネージャー  
**I want to** 将来のCV率とリード数を予測  
**So that** KPI達成の見込みを把握できる

**Acceptance Criteria**:

**Given**: 診断が2週間以上運用されている  
**When**: 予測分析ダッシュボードを開く  
**Then**:
- 今後4週間のCV率予測を表示（信頼区間付き）
- 季節性、曜日、時間帯の影響を可視化
- 「このペースだと月間目標に対して-15%」などのアラート
- 改善アクション提案（例: 「火曜午前のトラフィック増やすべき」）

### 4. リード品質予測スコア

**As a** 営業マネージャー  
**I want to** 各リードの成約確率を知りたい  
**So that** 優先順位をつけてフォローアップできる

**Acceptance Criteria**:

**Given**: リードが獲得される  
**When**: AIが過去データを分析  
**Then**:
- 成約確率スコア（0-100%）を自動算出
- 予測根拠を表示（例: 「業種、企業規模、回答パターンから判定」）
- 優先度ランク（A, B, C）を自動付与
- 「今日中に連絡すべき」などのアクション提案

## Technical Architecture

### A/Bテストエンジン

```python
# backend/app/services/optimization/ab_test_engine.py
from scipy import stats
import numpy as np

class ABTestEngine:
    def __init__(self):
        self.min_sample_size = 100  # 最小サンプル数
        self.significance_level = 0.05  # 有意水準
    
    def assign_variant(
        self, 
        test_id: str, 
        user_id: str,
        algorithm: str = "thompson_sampling"  # or "epsilon_greedy"
    ) -> str:
        """ユーザーにバリエーションを割り当て"""
        test = self._get_test(test_id)
        
        if algorithm == "thompson_sampling":
            return self._thompson_sampling(test)
        elif algorithm == "epsilon_greedy":
            return self._epsilon_greedy(test, epsilon=0.1)
        else:
            # 均等配分（初期フェーズ）
            return random.choice(test.variants)
    
    def _thompson_sampling(self, test: ABTest) -> str:
        """トンプソンサンプリング（マルチアームバンディット）"""
        samples = []
        for variant in test.variants:
            # Beta分布からサンプリング
            alpha = variant.conversions + 1
            beta = variant.trials - variant.conversions + 1
            sample = np.random.beta(alpha, beta)
            samples.append((sample, variant.id))
        
        # 最大値を持つバリエーションを選択
        return max(samples)[1]
    
    def calculate_significance(
        self,
        variant_a: Variant,
        variant_b: Variant
    ) -> dict:
        """統計的有意差を計算"""
        # Z検定（比率の差）
        p1 = variant_a.conversions / variant_a.trials
        p2 = variant_b.conversions / variant_b.trials
        
        pooled_p = (variant_a.conversions + variant_b.conversions) / \
                   (variant_a.trials + variant_b.trials)
        
        se = np.sqrt(pooled_p * (1 - pooled_p) * 
                     (1/variant_a.trials + 1/variant_b.trials))
        
        z_score = (p1 - p2) / se
        p_value = stats.norm.sf(abs(z_score)) * 2  # 両側検定
        
        return {
            "p_value": p_value,
            "significant": p_value < self.significance_level,
            "confidence": 1 - p_value,
            "lift": (p1 - p2) / p2 * 100  # 改善率（%）
        }
    
    async def check_and_declare_winner(self, test_id: str):
        """勝者判定"""
        test = await self._get_test(test_id)
        
        # 最小サンプルサイズチェック
        if any(v.trials < self.min_sample_size for v in test.variants):
            return None
        
        # 各ペアで有意差チェック
        variants_sorted = sorted(
            test.variants, 
            key=lambda v: v.conversions / v.trials,
            reverse=True
        )
        
        best = variants_sorted[0]
        for variant in variants_sorted[1:]:
            result = self.calculate_significance(best, variant)
            if not result["significant"]:
                return None  # まだ有意差なし
        
        # 勝者確定
        await self._declare_winner(test, best)
        return best
```

### AIコピーライティング

```python
# backend/app/services/optimization/ai_copywriter.py
from anthropic import Anthropic

class AICopywriter:
    def __init__(self):
        self.client = Anthropic(api_key=settings.ANTHROPIC_API_KEY)
    
    async def improve_question(
        self,
        question: Question,
        context: dict = None
    ) -> List[dict]:
        """質問文の改善提案"""
        prompt = f"""
あなたはマーケティングコピーライターです。以下の診断質問をより効果的にしてください。

【現在の質問】
{question.text}

【診断のコンテキスト】
業界: {context.get('industry', '不明')}
ターゲット: {context.get('target_audience', '不明')}
目的: {context.get('goal', '不明')}

【改善方針】
1. より具体的で明確な表現
2. 感情に訴える（ただし適切に）
3. 簡潔で読みやすい（推奨: 30-80文字）
4. アクションを促す

3つの改善案を提案してください。各案に改善理由も添えてください。

【出力形式】
JSON:
{{
  "suggestions": [
    {{
      "text": "改善後の質問文",
      "reason": "改善理由",
      "tone": "professional|friendly|urgent",
      "estimated_improvement": "+15%"
    }}
  ]
}}
"""
        
        response = self.client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=2000,
            messages=[{"role": "user", "content": prompt}]
        )
        
        result = json.loads(response.content[0].text)
        return result["suggestions"]
    
    async def analyze_readability(self, text: str) -> dict:
        """可読性分析"""
        # Flesch Reading Ease Score
        sentences = text.count('。') + text.count('！') + text.count('？')
        words = len(text)
        syllables = self._count_syllables(text)
        
        fre_score = 206.835 - 1.015 * (words / sentences) - \
                    84.6 * (syllables / words)
        
        return {
            "score": fre_score,
            "level": self._get_readability_level(fre_score),
            "word_count": words,
            "sentence_count": sentences,
            "avg_sentence_length": words / sentences if sentences > 0 else 0,
            "recommendations": self._get_recommendations(fre_score, text)
        }
```

### 予測分析エンジン

```python
# backend/app/services/optimization/predictive_analytics.py
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
import pandas as pd

class PredictiveAnalytics:
    def __init__(self):
        self.model = None
        self.scaler = StandardScaler()
    
    async def train_conversion_model(self, tenant_id: str):
        """CV率予測モデルをトレーニング"""
        # 過去データ取得
        historical_data = await self._get_historical_data(tenant_id)
        
        df = pd.DataFrame(historical_data)
        
        # 特徴量エンジニアリング
        df['hour'] = pd.to_datetime(df['timestamp']).dt.hour
        df['day_of_week'] = pd.to_datetime(df['timestamp']).dt.dayofweek
        df['is_weekend'] = df['day_of_week'].isin([5, 6]).astype(int)
        df['week_of_year'] = pd.to_datetime(df['timestamp']).dt.isocalendar().week
        
        # 特徴量
        features = [
            'hour', 'day_of_week', 'is_weekend', 'week_of_year',
            'traffic_source_encoded', 'device_type_encoded'
        ]
        
        X = df[features]
        y = df['conversion_rate']
        
        # スケーリング
        X_scaled = self.scaler.fit_transform(X)
        
        # モデルトレーニング
        self.model = RandomForestRegressor(
            n_estimators=100,
            max_depth=10,
            random_state=42
        )
        self.model.fit(X_scaled, y)
        
        # モデル保存
        await self._save_model(tenant_id, self.model, self.scaler)
    
    async def predict_conversion_rate(
        self,
        tenant_id: str,
        future_dates: List[datetime]
    ) -> List[dict]:
        """将来のCV率を予測"""
        model, scaler = await self._load_model(tenant_id)
        
        predictions = []
        for date in future_dates:
            features = self._extract_features(date)
            X = scaler.transform([features])
            pred = model.predict(X)[0]
            
            # 信頼区間計算（Bootstrapping）
            confidence_interval = self._calculate_confidence_interval(
                model, X, confidence=0.95
            )
            
            predictions.append({
                "date": date.isoformat(),
                "predicted_cvr": round(pred, 4),
                "lower_bound": round(confidence_interval[0], 4),
                "upper_bound": round(confidence_interval[1], 4)
            })
        
        return predictions
    
    async def predict_lead_quality(self, lead: Lead) -> dict:
        """リード品質（成約確率）を予測"""
        # 特徴量抽出
        features = {
            "company_size": self._encode_company_size(lead.company_size),
            "industry": self._encode_industry(lead.industry),
            "job_title_seniority": self._extract_seniority(lead.job_title),
            "assessment_score": lead.assessment_score,
            "completion_time": lead.completion_time_seconds,
            "response_pattern": self._analyze_response_pattern(lead.responses),
            "engagement_level": self._calculate_engagement(lead)
        }
        
        # 過去の成約データでトレーニングしたモデル
        quality_model = await self._load_quality_model(lead.tenant_id)
        
        X = self._prepare_features(features)
        
        # 予測
        close_probability = quality_model.predict_proba(X)[0][1]
        
        # ランク付け
        rank = self._assign_rank(close_probability)
        
        return {
            "close_probability": round(close_probability, 4),
            "rank": rank,  # A, B, C
            "confidence": round(quality_model.predict_proba(X).max(), 4),
            "key_factors": self._get_key_factors(features, quality_model),
            "recommended_action": self._get_action_recommendation(
                close_probability, 
                lead
            )
        }
```

## API Endpoints

### A/Bテスト管理

```
POST   /api/v1/optimization/ab-tests
       - A/Bテスト作成
       - Request: {
           assessment_id,
           variants: [{variant_id, traffic_allocation}],
           algorithm: "thompson_sampling"
         }

GET    /api/v1/optimization/ab-tests/{test_id}
       - テスト結果取得

POST   /api/v1/optimization/ab-tests/{test_id}/declare-winner
       - 勝者を手動で確定

DELETE /api/v1/optimization/ab-tests/{test_id}
       - テスト終了
```

### AIコピーライティング

```
POST   /api/v1/optimization/ai-copywriting/improve-question
       - 質問文改善提案
       - Request: { question_id, context }
       - Response: { suggestions: [...] }

POST   /api/v1/optimization/ai-copywriting/analyze-readability
       - 可読性分析
       - Request: { text }
       - Response: { score, level, recommendations }

POST   /api/v1/optimization/ai-copywriting/generate-variants
       - A/Bテスト用バリエーション自動生成
       - Request: { question_id, num_variants: 3 }
```

### 予測分析

```
POST   /api/v1/optimization/predictions/train
       - 予測モデルをトレーニング
       - Request: { tenant_id, data_range }

GET    /api/v1/optimization/predictions/conversion-rate
       - CV率予測
       - Query: ?assessment_id=xxx&days_ahead=28
       - Response: { predictions: [{date, cvr, bounds}] }

GET    /api/v1/optimization/predictions/lead-quality/{lead_id}
       - リード品質予測
       - Response: { 
           close_probability, 
           rank, 
           key_factors, 
           action 
         }

GET    /api/v1/optimization/insights
       - AI洞察レポート
       - Query: ?assessment_id=xxx
       - Response: {
           performance_summary,
           opportunities: [...],
           recommendations: [...]
         }
```

## Database Schema

```sql
-- A/Bテスト
CREATE TABLE ab_tests (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    assessment_id UUID NOT NULL REFERENCES assessments(id) ON DELETE CASCADE,
    
    name VARCHAR(255) NOT NULL,
    algorithm VARCHAR(50) DEFAULT 'thompson_sampling',
    
    status VARCHAR(50) DEFAULT 'running',  -- running, paused, completed
    winner_variant_id UUID,
    
    started_at TIMESTAMP DEFAULT NOW(),
    ended_at TIMESTAMP,
    
    INDEX(tenant_id, status),
    INDEX(assessment_id)
);

CREATE TABLE ab_test_variants (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    test_id UUID NOT NULL REFERENCES ab_tests(id) ON DELETE CASCADE,
    
    name VARCHAR(255) NOT NULL,
    variant_data JSONB NOT NULL,  -- 変更内容
    
    -- 統計
    trials INTEGER DEFAULT 0,
    conversions INTEGER DEFAULT 0,
    revenue DECIMAL(10, 2) DEFAULT 0,
    
    -- トラフィック配分
    traffic_allocation DECIMAL(5, 2) DEFAULT 50.00,
    
    INDEX(test_id)
);

-- AI最適化履歴
CREATE TABLE optimization_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    assessment_id UUID REFERENCES assessments(id) ON DELETE CASCADE,
    
    optimization_type VARCHAR(50) NOT NULL,  -- ab_test, ai_copywriting, predictive
    action_taken TEXT NOT NULL,
    result JSONB,
    
    created_at TIMESTAMP DEFAULT NOW(),
    
    INDEX(tenant_id, optimization_type, created_at)
);

-- 予測モデルメタデータ
CREATE TABLE prediction_models (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    
    model_type VARCHAR(50) NOT NULL,  -- conversion_rate, lead_quality
    model_version VARCHAR(50),
    
    training_data_range JSONB,
    performance_metrics JSONB,  -- {accuracy, rmse, r2_score}
    
    model_file_path TEXT,  -- S3パス
    
    trained_at TIMESTAMP DEFAULT NOW(),
    is_active BOOLEAN DEFAULT TRUE,
    
    INDEX(tenant_id, model_type, is_active)
);
```

## Events

```javascript
optimization.ab_test.started
optimization.ab_test.winner_declared
optimization.ai_suggestion.generated
optimization.prediction.completed
```

## Performance Requirements

- **A/Bテスト割り当て**: 50ms以内
- **AI提案生成**: 5秒以内
- **予測分析**: 3秒以内
- **モデルトレーニング**: バックグラウンドジョブ（10分以内）

## Success Metrics

- **CVR改善**: 平均 +50%（導入6ヶ月後）
- **A/Bテスト利用率**: 70%のアクティブテナント
- **AI提案採用率**: 60%以上
- **予測精度**: MAE < 5%（CV率予測）

## Related Specifications

- [Microsoft Teams Integration](./microsoft-teams-integration.md)
- [Multi-Channel Distribution](./multi-channel-distribution.md)
- [Analytics Dashboard](./analytics-dashboard.md)
