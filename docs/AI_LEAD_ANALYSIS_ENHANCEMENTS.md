# AI Lead Analysis Enhancements

**実装日**: 2025-11-18
**ステータス**: ✅ 完了
**関連機能**: E - AIリード分析の拡張

## 概要

DiagnoLeadsのAIリード分析機能を大幅に拡張し、業界特化型のインサイト生成、予測的フォローアップ提案、自動優先順位付けを実装しました。これにより、営業チームはより質の高い、実用的なリード情報を取得できます。

## 実装内容

### 1. 業界別リード分析テンプレート

**ファイル**: `backend/app/services/ai/lead_analysis_templates.py`

業界ごとに最適化されたリード分析テンプレートを作成しました。

#### テンプレート構造

```python
@dataclass
class LeadAnalysisTemplate:
    """業界特化型リード分析テンプレート"""
    industry: str                          # 業界名
    key_signals: List[str]                 # 重要シグナル（注目すべき回答パターン）
    qualification_criteria: List[str]      # リード評価基準
    recommended_actions: Dict[str, str]    # スコア別推奨アクション
    talking_points_themes: List[str]       # 営業トークテーマ
```

#### 対応業界（5業界 + 汎用）

1. **IT/SaaS** (`it_saas`)
   - 重要シグナル: システム課題、技術スタック、予算、導入タイムライン、セキュリティ要件、チームサイズ
   - 評価基準: 課題認識、予算・権限、短期導入検討、競合比較、技術理解度
   - トークテーマ: システム統合、スケーラビリティ、セキュリティ認証、TCO削減、導入事例

2. **コンサルティング** (`consulting`)
   - 重要シグナル: プロジェクト管理課題、顧客獲得コスト、品質管理、スキルギャップ、成長目標
   - 評価基準: 業務課題、年間10+プロジェクト、品質投資意欲、10+名チーム、デジタル化意欲
   - トークテーマ: プロジェクト効率化、品質標準化、ナレッジマネジメント、チーム協業

3. **製造業** (`manufacturing`)
   - 重要シグナル: 生産効率、品質不良率、設備保全、在庫管理、デジタル化進捗
   - 評価基準: 3+生産ライン、売上10億+、IoT/DX予算、品質課題、経営層理解
   - トークテーマ: 生産性向上、品質安定化、予知保全、在庫最適化、スマートファクトリー

4. **EC/小売** (`ecommerce`)
   - 重要シグナル: 月間売上、カート放棄率、顧客獲得コスト、リピート率、マルチチャネル対応
   - 評価基準: 月商1000万+、CVR課題、データ活用意欲、成長フェーズ、マーケティング予算
   - トークテーマ: CVR向上、LTV最大化、パーソナライゼーション、オムニチャネル

5. **マーケティング** (`marketing`)
   - 重要シグナル: マーケティング予算、ROI測定課題、ツールスタック、リード獲得CV率、データ統合
   - 評価基準: 月間100万+予算、ROI課題、MA導入検討、5+名チーム、データ活用意欲
   - トークテーマ: ROI測定、マーケティングオートメーション、データ可視化、リード育成

6. **一般企業** (`general`) - フォールバックテンプレート

#### スコア別推奨アクション

各業界で4段階のアクション推奨を提供：

- **80-100点**: 即座の商談設定、デモ提案、ROI試算
- **60-79点**: 詳細資料送付、ユースケース共有、1週間以内フォロー
- **40-59点**: ナーチャリングシーケンス追加、定期的な成功事例共有
- **0-39点**: 情報提供のみ、四半期ごとチェックイン

### 2. 改善されたリード分析プロンプト

**ファイル**: `backend/app/services/ai_service.py` (lines 279-407)

#### 主要な改善点

1. **業界コンテキストの注入**
   - 業界エキスパートとしてのペルソナ設定
   - 業界固有の重要シグナルを明示的に提示
   - 業界特有の評価基準を組み込み

2. **構造化された分析ガイドライン**
   ```
   1. スコアリング精度: 予算・権限・ニーズ・タイムラインの総合評価
   2. ニーズの具体化: 抽象的でない、具体的な課題の特定
   3. 緊急性の判断: 導入タイミングと課題深刻度からの優先度判定
   4. トークポイントの実用性: 実際の商談で使える具体的提案
   5. 業界文脈: 業界特有の課題・用語の考慮
   ```

3. **日本語による詳細なプロンプト**
   - 営業担当者が理解しやすい日本語出力
   - 業界用語を含む実践的なアドバイス

4. **max_tokens増加**
   - 1000 → 1500トークンに増加
   - より詳細な分析結果の生成が可能

#### プロンプト構造

```
あなたは{業界}のセールスエキスパートです。

## 診断情報
- 診断名、業界、回答データ

## 業界固有の重要シグナル
- {業界テンプレートのkey_signals}

## リード評価基準
- {業界テンプレートのqualification_criteria}

## 重点トークテーマ
- {業界テンプレートのtalking_points_themes}

## 分析ガイドライン
- スコアリング精度、ニーズ具体化、緊急性判断、トークポイント実用性、業界文脈

## 出力形式
- JSON形式での構造化された分析結果
```

### 3. 予測的フォローアップ提案

**機能**: `_calculate_follow_up_timing()` メソッド (lines 259-277)

リードのスコアと優先度レベルに基づいて、最適なフォローアップタイミングを自動提案します。

#### フォローアップタイミング

| 優先度 | タイミング |
|--------|-----------|
| Critical | 即座に（1時間以内） |
| High | 24時間以内 |
| Medium | 3-5営業日以内 |
| Low | 2週間以内または次回キャンペーン時 |

**利点**:
- 営業担当者の判断負荷を軽減
- フォローアップ漏れを防止
- タイミングの最適化による成約率向上

### 4. 自動リード優先順位付け

**機能**: `_calculate_priority_level()` メソッド (lines 239-257)

リードスコアとホットリードステータスに基づいて、4段階の優先度を自動計算します。

#### 優先度ロジック

```python
if hot_lead and score >= 90:
    return "critical"  # 最優先：ホットリード＋超高スコア
elif score >= 80:
    return "high"      # 高優先：高スコア
elif score >= 60:
    return "medium"    # 中優先：中スコア
else:
    return "low"       # 低優先：低スコア
```

**利点**:
- 営業リソースの効率的配分
- 高価値リードへの即座の対応
- 客観的な優先順位付け基準

### 5. APIスキーマの拡張

**ファイル**: `backend/app/schemas/ai.py`

#### LeadAnalysisRequest に追加

```python
industry: Optional[str] = Field(
    default="general",
    description="Target industry for analysis context"
)
```

#### LeadInsights に追加

```python
recommended_action: Optional[str] = Field(
    None,
    description="Industry-specific recommended next action"
)
priority_level: Optional[str] = Field(
    None,
    description="Automatic priority level: critical|high|medium|low"
)
follow_up_timing: Optional[str] = Field(
    None,
    description="Recommended follow-up timing"
)
```

### 6. APIエンドポイントの更新

**ファイル**: `backend/app/api/v1/ai.py` (line 128)

`analyze_lead_insights()` 呼び出しに `industry` パラメータを追加：

```python
result = await ai_service.analyze_lead_insights(
    assessment_responses=request.assessment_responses,
    assessment_title=request.assessment_title,
    industry=request.industry,  # 新規追加
)
```

## 使用方法

### バックエンドAPI

```python
# リード分析リクエスト
POST /api/v1/tenants/{tenant_id}/ai/insights

# リクエストボディ
{
  "assessment_responses": {
    "question_1": "現在のマーケティングツールは使いにくい",
    "question_2": "月間予算は200万円",
    "question_3": "ROI測定が困難"
  },
  "assessment_title": "マーケティングオートメーション成熟度診断",
  "industry": "marketing"  // 新規: 業界指定
}

# レスポンス（拡張版）
{
  "success": true,
  "data": {
    "overall_score": 85,
    "hot_lead": true,
    "identified_needs": [
      {
        "area": "ROI測定",
        "description": "マーケティング施策の効果測定が困難で、予算配分の最適化ができていない",
        "priority": "high"
      }
    ],
    "recommendation": "MA導入による自動化とROI可視化を提案。デモアカウント発行で実際の機能を体験いただく。",
    "key_talking_points": [
      "現在の月間予算200万円に対するROI改善効果のシミュレーション",
      "競合他社の導入事例とCV率向上実績",
      "既存ツールからのデータ移行サポート"
    ],
    "recommended_action": "マーケティング監査を提案。ROI改善プランを提示。",  // 新規
    "priority_level": "high",  // 新規
    "follow_up_timing": "24時間以内"  // 新規
  },
  "usage": {
    "input_tokens": 450,
    "output_tokens": 320
  }
}
```

### Pythonコードでの使用

```python
from app.services.ai.lead_analysis_templates import (
    get_lead_analysis_template,
    get_recommended_action,
)

# 業界テンプレート取得
template = get_lead_analysis_template("it_saas")
print(template.key_signals)
# => ['現在のシステムの課題や不満', '技術スタックとツールの成熟度', ...]

# スコア別推奨アクション取得
action = get_recommended_action(score=85, industry="marketing")
print(action)
# => "マーケティング監査を提案。ROI改善プランを提示。"
```

## 技術仕様

### ファイル構成

```
backend/app/
├── services/ai/
│   ├── __init__.py                      # 拡張: lead_analysis_templates のエクスポート
│   ├── lead_analysis_templates.py       # 新規: 業界別リード分析テンプレート
│   └── industry_templates.py            # 既存: 診断生成用テンプレート
├── services/
│   └── ai_service.py                    # 更新: analyze_lead_insights() 拡張
├── schemas/
│   └── ai.py                            # 更新: LeadAnalysisRequest, LeadInsights 拡張
└── api/v1/
    └── ai.py                            # 更新: industry パラメータ追加
```

### データフロー

```
1. クライアント → POST /api/v1/tenants/{tenant_id}/ai/insights
   ↓ (assessment_responses, assessment_title, industry)

2. APIエンドポイント (ai.py)
   ↓

3. AIService.analyze_lead_insights()
   ↓ get_lead_analysis_template(industry)
   ↓

4. 業界テンプレート取得 (lead_analysis_templates.py)
   ↓ key_signals, qualification_criteria, talking_points_themes

5. Claude APIへのプロンプト送信
   ↓ 業界コンテキスト + 回答データ

6. Claude APIレスポンス（JSON）
   ↓ overall_score, hot_lead, identified_needs, recommendation, key_talking_points

7. 拡張情報の追加
   ↓ get_recommended_action(score, industry)
   ↓ _calculate_priority_level(score, hot_lead)
   ↓ _calculate_follow_up_timing(score, priority_level)

8. 最終レスポンス → クライアント
   ↓ 全ての分析結果 + 拡張情報
```

## 改善効果

### 1. 分析精度の向上

**Before**:
- 汎用的な分析のみ
- 業界文脈なし
- 抽象的なアドバイス

**After**:
- 業界特化型分析
- 業界固有シグナルの検出
- 具体的な営業アクション提案

### 2. 営業効率の改善

**新機能による効果**:
- **自動優先順位付け**: リード対応の順序が明確化
- **予測的フォローアップ**: タイミング判断の自動化
- **業界別推奨アクション**: 次のステップが即座に分かる

**想定される成果**:
- リード対応時間 30%削減
- ホットリード成約率 20%向上
- フォローアップ漏れ 80%削減

### 3. スケーラビリティ

- **テンプレート追加が容易**: 新業界の追加は`LEAD_ANALYSIS_TEMPLATES`にエントリ追加のみ
- **プロンプトの一貫性**: テンプレートベースで品質が安定
- **保守性の向上**: ビジネスロジックとAIプロンプトが分離

## テスト方法

### 1. 単体テスト（推奨）

```python
# tests/test_lead_analysis_templates.py
import pytest
from app.services.ai.lead_analysis_templates import (
    get_lead_analysis_template,
    get_recommended_action,
)

def test_get_it_saas_template():
    template = get_lead_analysis_template("it_saas")
    assert template.industry == "IT/SaaS"
    assert len(template.key_signals) > 0
    assert "80-100" in template.recommended_actions

def test_get_recommended_action_high_score():
    action = get_recommended_action(85, "marketing")
    assert "ROI" in action or "監査" in action

def test_fallback_to_general():
    template = get_lead_analysis_template("unknown_industry")
    assert template.industry == "一般"
```

### 2. APIテスト

```bash
# リード分析（IT/SaaS業界）
curl -X POST http://localhost:8000/api/v1/tenants/{tenant_id}/ai/insights \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer {token}" \
  -d '{
    "assessment_responses": {
      "q1": "クラウド移行を検討中",
      "q2": "年間予算は1000万円",
      "q3": "3ヶ月以内に導入したい"
    },
    "assessment_title": "クラウド移行成熟度診断",
    "industry": "it_saas"
  }'

# レスポンス検証ポイント:
# - overall_score: 0-100の範囲内か
# - hot_lead: boolean値か
# - priority_level: critical|high|medium|low のいずれか
# - follow_up_timing: 日本語の推奨タイミングが含まれているか
# - recommended_action: 業界固有のアクションが含まれているか
```

### 3. 統合テスト

```python
# tests/test_ai_service_integration.py
import pytest
from app.services.ai_service import AIService

@pytest.mark.asyncio
async def test_analyze_lead_insights_with_industry():
    ai_service = AIService()

    result = await ai_service.analyze_lead_insights(
        assessment_responses={
            "q1": "マーケティングROIが測定できない",
            "q2": "月間予算200万円",
            "q3": "MA導入を検討中"
        },
        assessment_title="マーケティング成熟度診断",
        industry="marketing"
    )

    assert result["success"] is True
    data = result["data"]
    assert "overall_score" in data
    assert "priority_level" in data
    assert "follow_up_timing" in data
    assert "recommended_action" in data
```

## 今後の拡張案

### 1. 業界テンプレートの追加

優先度の高い業界:
- **不動産** (`real_estate`): 物件管理、契約プロセス、顧客管理
- **保険** (`insurance`): リスク評価、契約管理、顧客対応
- **物流** (`logistics`): 配送最適化、在庫管理、トラッキング
- **飲食** (`food_service`): 予約管理、在庫管理、顧客体験

### 2. 機械学習による最適化

- **スコアリングモデルの学習**: 成約データからスコアリングロジックを最適化
- **A/Bテスト**: 推奨アクションの効果測定と改善
- **予測精度向上**: 過去データから最適なフォローアップタイミングを学習

### 3. CRM連携の強化

- **Salesforce/HubSpot連携**: 優先度・推奨アクション・フォローアップタイミングを自動同期
- **タスク自動生成**: 優先度に基づいてCRMにタスクを自動作成
- **通知システム**: CriticalリードのSlack/メール通知

### 4. ダッシュボードの拡張

- **優先度別リードビュー**: Critical/High/Medium/Low でフィルタリング
- **フォローアップキュー**: タイミング別のリードリスト
- **業界別分析レポート**: 業界ごとのリード傾向分析

## トラブルシューティング

### よくある問題

**Q: "unknown_industry" エラーが発生する**
A: `industry` パラメータに存在しない業界キーを指定しています。利用可能な業界は GET `/api/v1/ai/industries` で確認できます。`general` がフォールバックとして使用されます。

**Q: `recommended_action` が空になる**
A: `get_recommended_action()` でエラーが発生している可能性があります。ログを確認してください。スコアが0-100の範囲外の場合に発生することがあります。

**Q: 日本語が文字化けする**
A: `json.dumps(..., ensure_ascii=False)` を使用していることを確認してください。また、レスポンスの `Content-Type: application/json; charset=utf-8` が正しく設定されていることを確認してください。

## まとめ

このAIリード分析拡張により、DiagnoLeadsは業界特化型の高精度なリード分析を提供できるようになりました。

**主要な成果**:
- ✅ 5業界 + 汎用テンプレート実装
- ✅ 業界コンテキストを含む改善されたプロンプト
- ✅ 自動優先順位付け（4段階）
- ✅ 予測的フォローアップタイミング提案
- ✅ 業界別推奨アクション
- ✅ APIスキーマ拡張とエンドポイント更新

**次のステップ**:
- F: カスタムレポート機能
- G: 埋め込みウィジェット実装
- リード分析機能のフロントエンド統合
- CRM連携の強化

---

**実装者**: Claude Code
**レビュー**: Pending
**関連ドキュメント**:
- [AI Assessment Generation Improvements](./AI_ASSESSMENT_GENERATION_IMPROVEMENTS.md)
- [Google Analytics Complete Summary](./GOOGLE_ANALYTICS_COMPLETE_SUMMARY.md)
