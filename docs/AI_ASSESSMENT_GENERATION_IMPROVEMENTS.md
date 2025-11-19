# AI診断生成機能の改善 - 実装サマリー

## 📅 実装日
**日付:** 2025-11-18
**ブランチ:** `claude/integrate-google-analytics-01QFrt9C6sV4Zj9ZY3nbKAzq`
**状態:** ✅ 完了

---

## 🎯 概要

DiagnoLeadsのAI診断生成機能を大幅に改善しました。業界別テンプレート、改善されたプロンプトエンジニアリング、質問の検証機能を追加し、より高品質で実用的な診断を生成できるようになりました。

---

## ✅ 実装した機能

### 1. 業界別テンプレートシステム ✅

**ファイル:** `backend/app/services/ai/industry_templates.py`

9つの業界テンプレートを実装：

| 業界 | テンプレートキー | 説明 |
|-----|---------------|------|
| IT/SaaS | `it_saas` | Software as a Service and IT solutions |
| コンサルティング | `consulting` | Business consulting and professional services |
| 製造業 | `manufacturing` | Manufacturing and production industries |
| EC/小売 | `ecommerce` | E-commerce and retail businesses |
| ヘルスケア | `healthcare` | Healthcare and medical services |
| 教育 | `education` | Education and e-learning |
| マーケティング | `marketing` | Marketing and advertising |
| 人事・採用 | `hr` | Human resources and recruitment |
| 金融・FinTech | `finance` | Financial services and FinTech |
| 一般企業 | `general` | General business (fallback) |

**各テンプレートに含まれる情報:**
- 業界名と説明
- 一般的な課題（pain points）
- 質問テーマ
- スコアリングガイドライン
- 質の高い質問の例

**使用例:**
```python
from app.services.ai.industry_templates import get_industry_template, list_available_industries

# 業界テンプレートを取得
template = get_industry_template("it_saas")
print(template.common_pain_points)
# ['スケーラビリティの課題', 'セキュリティとコンプライアンス', ...]

# 利用可能な業界リストを取得
industries = list_available_industries()
# [{'key': 'it_saas', 'name': 'IT/SaaS', 'description': '...'}, ...]
```

---

### 2. 改善されたプロンプトエンジニアリング ✅

**ファイル:** `backend/app/services/ai_service.py`

**主な改善点:**

#### Before（旧プロンプト）:
```python
prompt = f"""Generate a professional assessment/quiz in JSON format...
Topic: {topic}
Industry: {industry}
Number of Questions: {num_questions}
...
```
- シンプルで汎用的
- 業界特有の文脈なし
- 質問の質に関するガイドラインが不足

#### After（新プロンプト）:
```python
prompt = f"""あなたは{industry_template.name}業界のエキスパートです。
以下の要件に基づいて、プロフェッショナルな診断を生成してください。

## 診断の要件
**トピック**: {topic}
**業界**: {industry_template.name} - {industry_template.description}
**質問数**: {num_questions}問

## 業界特有の課題（参考情報）
{業界別の課題リスト}

## 質問テーマ（これらを参考に質問を作成）
{業界別の質問テーマ}

## スコアリングガイドライン
{業界別のスコアリング基準}

## 質問作成の重要なガイドライン
1. **具体性**: 曖昧な質問を避け、回答者が明確に答えられる質問にする
2. **段階的な選択肢**: 選択肢は段階的で、現実的な状況を反映する
3. **スコアリングロジック**:
   - 0点: 課題が深刻、または全く対応できていない状態
   - 33点: 基本的な対応はしているが改善の余地が大きい
   - 67点: かなり良い状態だが、さらに最適化できる
   - 100点: ベストプラクティスを実践している理想的な状態
...
```

**改善効果:**
- ✅ 業界特有の文脈を提供
- ✅ 具体的な質問作成ガイドライン
- ✅ スコアリングロジックの明確化
- ✅ 質の高い質問例の提示
- ✅ 質問のカテゴリー分類と重み付けをサポート

---

### 3. 質問の品質検証機能 ✅

**メソッド:** `_validate_assessment()`

生成された診断の構造と内容を自動検証：

**検証項目:**
1. 必須フィールドの存在確認（title, description, questions）
2. 質問リストの妥当性（空でない配列）
3. 各質問の構造確認（text, optionsフィールド）
4. 選択肢の数（最低2つ以上）
5. スコアの妥当性（0-100の範囲、数値型）

**検証コード例:**
```python
def _validate_assessment(self, assessment_data: Dict[str, Any]) -> Dict[str, Any]:
    # 必須フィールドチェック
    if "title" not in assessment_data:
        return {"valid": False, "error": "Missing 'title' field"}

    # 質問の検証
    for i, question in enumerate(questions):
        if "text" not in question:
            return {"valid": False, "error": f"Question {i+1}: Missing 'text' field"}

        # スコアの検証
        scores = [opt.get("score", 0) for opt in question["options"]]
        if not (min(scores) >= 0 and max(scores) <= 100):
            return {"valid": False, "error": f"Question {i+1}: Scores must be between 0 and 100"}

    return {"valid": True, "error": None}
```

---

### 4. APIの拡張 ✅

**新しいエンドポイント:**

#### `GET /api/v1/ai/industries`
利用可能な業界リストを取得

**レスポンス:**
```json
{
  "success": true,
  "industries": [
    {
      "key": "it_saas",
      "name": "IT/SaaS",
      "description": "Software as a Service and IT solutions"
    },
    {
      "key": "consulting",
      "name": "コンサルティング",
      "description": "Business consulting and professional services"
    },
    ...
  ]
}
```

**既存エンドポイントの改善:**

#### `POST /api/v1/tenants/{tenant_id}/ai/assessments`

**改善点:**
- `max_tokens`: 2000 → 4000（より詳細な診断生成）
- JSONマークダウンコードブロックの自動抽出
- 診断構造の自動検証
- メタデータの自動付与

**レスポンスに追加されたメタデータ:**
```json
{
  "success": true,
  "data": {
    "title": "...",
    "description": "...",
    "questions": [...],
    "metadata": {
      "industry": "it_saas",
      "industry_template": "IT/SaaS",
      "topic": "マーケティングオートメーション",
      "generated_at": "auto",
      "version": "2.0"
    }
  },
  "usage": {
    "input_tokens": 1234,
    "output_tokens": 2345
  }
}
```

---

## 📊 Before / After 比較

### 生成される診断の質

| 項目 | Before（旧版） | After（新版） |
|-----|-------------|------------|
| **業界特化性** | 汎用的 | 業界ごとに最適化 |
| **質問の具体性** | やや曖昧 | 明確で具体的 |
| **スコアリング** | 基本的 | 段階的で論理的 |
| **質問の例** | なし | 業界別の例を提示 |
| **検証** | なし | 自動検証機能あり |
| **メタデータ** | なし | 業界・バージョン情報 |
| **max_tokens** | 2000 | 4000 |

### 使用例

#### Before（旧版）:
```
質問: 御社の課題は何ですか？
選択肢:
- 課題がある (score: 0)
- 少し課題がある (score: 50)
- 課題はない (score: 100)
```
→ 曖昧で回答しにくい

#### After（新版 - IT/SaaS業界の場合）:
```
質問: 現在のITインフラで最も大きな課題は何ですか？
選択肢:
- レガシーシステムが多く、拡張性が低い (score: 0)
  説明: モダン化が必要で、ビジネスのスピードに追いついていない
- 一部モダン化されているが、まだレガシーが残っている (score: 33)
  説明: 段階的な移行が進行中だが、完全ではない
- 大部分がクラウドベースで、拡張性が高い (score: 67)
  説明: 良好な状態だが、さらに最適化の余地がある
- フルマネージドのクラウドネイティブ構成 (score: 100)
  説明: ベストプラクティスに従った理想的な構成
```
→ 具体的で回答しやすく、スコアの根拠が明確

---

## 🚀 使用方法

### バックエンド（Python）

#### 1. 業界リストの取得
```python
from app.services.ai.industry_templates import list_available_industries

industries = list_available_industries()
for industry in industries:
    print(f"{industry['key']}: {industry['name']}")
```

#### 2. AI診断の生成
```python
from app.services.ai_service import AIService

ai_service = AIService()

result = await ai_service.generate_assessment(
    topic="マーケティングオートメーション",
    industry="it_saas",  # または "marketing", "ecommerce"など
    num_questions=5
)

if result["success"]:
    assessment = result["data"]
    print(f"Title: {assessment['title']}")
    print(f"Questions: {len(assessment['questions'])}")
    print(f"Industry: {assessment['metadata']['industry']}")
else:
    print(f"Error: {result['error']}")
```

### API経由

#### 1. 業界リストを取得
```bash
GET /api/v1/ai/industries
Authorization: Bearer {token}
```

**レスポンス:**
```json
{
  "success": true,
  "industries": [
    {"key": "it_saas", "name": "IT/SaaS", "description": "..."},
    {"key": "consulting", "name": "コンサルティング", "description": "..."}
  ]
}
```

#### 2. AI診断を生成
```bash
POST /api/v1/tenants/{tenant_id}/ai/assessments
Authorization: Bearer {token}
Content-Type: application/json

{
  "topic": "マーケティングオートメーション",
  "industry": "marketing",
  "num_questions": 7
}
```

**レスポンス:**
```json
{
  "success": true,
  "data": {
    "title": "マーケティングオートメーション成熟度診断",
    "description": "...",
    "questions": [
      {
        "id": 1,
        "text": "...",
        "type": "single_choice",
        "options": [...],
        "category": "現状把握",
        "weight": 1.0
      },
      ...
    ],
    "metadata": {
      "industry": "marketing",
      "industry_template": "マーケティング",
      "topic": "マーケティングオートメーション",
      "generated_at": "auto",
      "version": "2.0"
    }
  },
  "usage": {
    "input_tokens": 1500,
    "output_tokens": 3000
  }
}
```

---

## 📂 変更されたファイル

```
backend/app/
├── services/
│   ├── ai_service.py                      # UPDATED: 改善されたプロンプト、検証機能追加
│   └── ai/
│       ├── __init__.py                    # NEW: モジュール初期化
│       └── industry_templates.py          # NEW: 業界別テンプレート定義
└── api/v1/
    └── ai.py                              # UPDATED: 業界リストエンドポイント追加

docs/
└── AI_ASSESSMENT_GENERATION_IMPROVEMENTS.md  # NEW: このファイル
```

---

## 🎨 フロントエンド統合のヒント

### 業界選択UIの実装例

```tsx
import { useState, useEffect } from 'react';
import { aiService } from '../services/aiService';

function AssessmentGeneratorForm() {
  const [industries, setIndustries] = useState([]);
  const [selectedIndustry, setSelectedIndustry] = useState('');
  const [topic, setTopic] = useState('');
  const [numQuestions, setNumQuestions] = useState(5);

  useEffect(() => {
    // 業界リストを取得
    aiService.getIndustries().then(response => {
      setIndustries(response.industries);
    });
  }, []);

  const handleGenerate = async () => {
    const result = await aiService.generateAssessment({
      topic,
      industry: selectedIndustry,
      num_questions: numQuestions,
    });

    if (result.success) {
      // 生成された診断を表示
      console.log(result.data);
    }
  };

  return (
    <div>
      <h2>AI診断生成</h2>

      {/* 業界選択 */}
      <label>業界</label>
      <select value={selectedIndustry} onChange={e => setSelectedIndustry(e.target.value)}>
        <option value="">業界を選択...</option>
        {industries.map(industry => (
          <option key={industry.key} value={industry.key}>
            {industry.name} - {industry.description}
          </option>
        ))}
      </select>

      {/* トピック入力 */}
      <label>トピック</label>
      <input
        type="text"
        value={topic}
        onChange={e => setTopic(e.target.value)}
        placeholder="例：マーケティングオートメーション"
      />

      {/* 質問数 */}
      <label>質問数</label>
      <input
        type="number"
        value={numQuestions}
        onChange={e => setNumQuestions(parseInt(e.target.value))}
        min={3}
        max={10}
      />

      <button onClick={handleGenerate}>診断を生成</button>
    </div>
  );
}
```

---

## 🧪 テスト方法

### 1. 業界リストの取得テスト

```bash
curl -X GET "http://localhost:8000/api/v1/ai/industries" \
  -H "Authorization: Bearer {your_token}"
```

**期待される結果:** 9つの業界がリストで返される

---

### 2. 各業界での診断生成テスト

```bash
# IT/SaaS業界
curl -X POST "http://localhost:8000/api/v1/tenants/{tenant_id}/ai/assessments" \
  -H "Authorization: Bearer {your_token}" \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "クラウドインフラ最適化",
    "industry": "it_saas",
    "num_questions": 5
  }'

# マーケティング業界
curl -X POST "http://localhost:8000/api/v1/tenants/{tenant_id}/ai/assessments" \
  -H "Authorization: Bearer {your_token}" \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "デジタルマーケティング成熟度",
    "industry": "marketing",
    "num_questions": 7
  }'
```

**期待される結果:**
- 業界特有の質問が生成される
- スコアリングが0, 33, 67, 100の段階的な構成
- カテゴリーと重み付けが含まれる
- メタデータに業界情報が含まれる

---

### 3. 検証機能のテスト

```python
# 不正な診断データを検証
invalid_assessment = {
    "title": "Test",
    "description": "Test description",
    "questions": [
        {
            "text": "Question 1",
            "options": [
                {"text": "Option 1", "score": 150}  # 不正なスコア（100を超える）
            ]
        }
    ]
}

result = ai_service._validate_assessment(invalid_assessment)
assert result["valid"] == False
assert "Scores must be between 0 and 100" in result["error"]
```

---

## 📈 期待される効果

### 1. 診断の質の向上
- **Before**: 汎用的で曖昧な質問
- **After**: 業界特化で具体的な質問

### 2. ユーザー体験の改善
- **Before**: 回答しにくい、スコアの意味が不明確
- **After**: 回答しやすく、スコアの根拠が明確

### 3. リード品質の向上
- **Before**: 表面的な情報のみ
- **After**: 深い洞察と具体的な課題の特定

### 4. 開発効率の向上
- **Before**: 診断作成に時間がかかる
- **After**: AIが高品質な診断を数秒で生成

---

## 🔄 今後の拡張案

### 短期（1-2週間）
- [ ] より多くの業界テンプレートを追加（不動産、物流、農業など）
- [ ] 質問の難易度設定（初級、中級、上級）
- [ ] 多言語対応（英語、中国語など）

### 中期（1-2ヶ月）
- [ ] 診断結果レポートのAI生成
- [ ] 改善提案の自動生成
- [ ] ベンチマークデータとの比較

### 長期（3-6ヶ月）
- [ ] 業界別のベストプラクティスデータベース
- [ ] AIによる診断の自動最適化
- [ ] リアルタイムフィードバックとA/Bテスト

---

## ✅ チェックリスト

実装完了項目:
- [x] 業界別テンプレートシステム（9業界）
- [x] 改善されたプロンプトエンジニアリング
- [x] 質問の品質検証機能
- [x] 業界リスト取得APIエンドポイント
- [x] メタデータの自動付与
- [x] JSONマークダウンコードブロックの自動抽出
- [x] max_tokensの増加（2000 → 4000）
- [x] ドキュメント作成

---

## 📚 参考資料

- [Claude API Documentation](https://docs.anthropic.com/claude/reference)
- [Prompt Engineering Guide](https://www.promptingguide.ai/)
- [Assessment Design Best Practices](https://www.questionmark.com/resources/blog/best-practices-for-assessment-design/)

---

**実装完了日:** 2025-11-18
**実装者:** Claude Code
**バージョン:** 2.0
**ステータス:** ✅ 完了
