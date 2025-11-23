# Resilience & Retry Policy

**Feature ID**: OPS-RETRY-001
**Status**: Implemented
**Priority**: High (System Reliability)
**Last Updated**: 2025-11-23

---

## 📋 Overview

DiagnoLeadsのAI API呼び出しに対するレジリエンス機能。指数バックオフアルゴリズムによる自動リトライで、一時的なネットワーク障害やレート制限を吸収し、システムの可用性を向上させます。

### ビジネス価値

- **システム可用性向上**: 一時的な障害の自動復旧
- **ユーザー体験の向上**: エラー頻度の削減
- **コスト最適化**: レート制限の効率的な処理
- **運用負荷軽減**: 手動介入の削減

---

## 🎯 主要機能

### 1. 指数バックオフリトライ

Claude API呼び出しに対して、指数関数的に遅延を増やしながらリトライ：

| パラメータ | デフォルト値 | 説明 |
|-----------|------------|------|
| **max_retries** | 3 | 最大リトライ回数 |
| **initial_delay** | 1.0秒 | 初回リトライまでの待機時間 |
| **backoff_factor** | 2.0 | 遅延の倍率（指数） |

**遅延計算例**:
```
1回目の失敗後: 1.0秒 × 2.0 = 2.0秒待機
2回目の失敗後: 2.0秒 × 2.0 = 4.0秒待機
3回目の失敗後: 4.0秒 × 2.0 = 8.0秒待機
```

### 2. リトライ対象エラー

以下のエラーは自動的にリトライ：

| エラー種別 | 説明 | リトライ戦略 |
|-----------|------|------------|
| **RateLimitError** | レート制限超過 | 指数バックオフでリトライ |
| **APIConnectionError** | ネットワーク接続エラー | 指数バックオフでリトライ |
| **APITimeoutError** | タイムアウト | 指数バックオフでリトライ |

### 3. 非リトライエラー

以下のエラーは即座に失敗：

| エラー種別 | 説明 | 処理 |
|-----------|------|------|
| **APIError** | API鍵無効、パラメータエラー等 | 即座にAIAPIError例外を発生 |
| **ValueError/TypeError** | プログラムロジックエラー | 即座にAIAPIError例外を発生 |

### 4. 構造化エラーハンドリング

カスタム例外でエラーの種類を明確化：

```python
from app.services.ai.exceptions import AIRateLimitError, AIAPIError

try:
    result = await retry_with_backoff(api_call, ...)
except AIRateLimitError as e:
    # レート制限エラー - retry_after属性で待機時間を取得可能
    logger.error(f"Rate limit exceeded. Retry after: {e.retry_after}s")
except AIAPIError as e:
    # API接続エラー - original_errorで元のエラーを取得可能
    logger.error(f"API error: {e.message}, original: {e.original_error}")
```

---

## 🔧 実装仕様

### retry_with_backoff関数

**モジュール**: `app/services/ai/retry_helper.py`

```python
async def retry_with_backoff(
    func: Callable[..., Awaitable[T]],
    max_retries: int = 3,
    initial_delay: float = 1.0,
    backoff_factor: float = 2.0,
    *args,
    **kwargs,
) -> T:
    """
    非同期関数を指数バックオフでリトライ

    Args:
        func: リトライ対象の非同期関数
        max_retries: 最大リトライ回数（デフォルト: 3）
        initial_delay: 初回遅延（秒）（デフォルト: 1.0）
        backoff_factor: 遅延倍率（デフォルト: 2.0）
        *args: funcに渡す引数
        **kwargs: funcに渡すキーワード引数

    Returns:
        funcの戻り値

    Raises:
        AIRateLimitError: レート制限が全リトライ後も解決しない場合
        AIAPIError: API接続エラーが全リトライ後も解決しない場合
    """
```

### 使用例

#### 基本的な使用

```python
from app.services.ai.retry_helper import retry_with_backoff

async def call_claude_api(prompt: str) -> dict:
    """Claude APIを呼び出す"""
    response = await client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=4000,
        messages=[{"role": "user", "content": prompt}]
    )
    return response

# リトライ付きで実行（デフォルト: 最大3回、1秒→2秒→4秒の遅延）
result = await retry_with_backoff(
    call_claude_api,
    prompt="診断を生成してください"
)
```

#### カスタムパラメータ

```python
# より積極的なリトライ（5回、短い初回遅延）
result = await retry_with_backoff(
    call_claude_api,
    max_retries=5,
    initial_delay=0.5,
    backoff_factor=2.0,
    prompt="診断を生成してください"
)

# より慎重なリトライ（2回、長い遅延、大きい倍率）
result = await retry_with_backoff(
    call_claude_api,
    max_retries=2,
    initial_delay=2.0,
    backoff_factor=3.0,
    prompt="診断を生成してください"
)
```

#### AIServiceでの統合

```python
class AIService:
    async def generate_assessment(self, topic: str, ...):
        """診断生成（リトライ付き）"""
        prompt = PromptTemplates.build_assessment_generation_prompt(...)

        # リトライ機能を統合
        message = await retry_with_backoff(
            self._call_claude_api,
            prompt=prompt,
            max_tokens=AIConfig.MAX_TOKENS_ASSESSMENT,
        )

        return message
```

---

## 📊 リトライフロー

### 成功ケース（1回目で成功）

```
┌─────────────────────────────────────┐
│ retry_with_backoff()                │
├─────────────────────────────────────┤
│ Attempt 1: func() を実行             │
│ → 成功 ✅                            │
│ → 結果を返す                         │
└─────────────────────────────────────┘

実行時間: ~2秒（API呼び出しのみ）
```

### リトライ成功ケース（2回目で成功）

```
┌─────────────────────────────────────┐
│ retry_with_backoff()                │
├─────────────────────────────────────┤
│ Attempt 1: func() を実行             │
│ → RateLimitError ❌                 │
│ → log: "Rate limit hit on attempt 1"│
│                                     │
│ 2.0秒待機（initial_delay * factor）   │
│                                     │
│ Attempt 2: func() を実行             │
│ → 成功 ✅                            │
│ → log: "Retry succeeded on attempt 2"│
│ → 結果を返す                         │
└─────────────────────────────────────┘

実行時間: ~4秒（API 2回 + 2秒待機）
```

### 全リトライ失敗ケース

```
┌─────────────────────────────────────┐
│ retry_with_backoff(max_retries=2)   │
├─────────────────────────────────────┤
│ Attempt 1: func() を実行             │
│ → ConnectionError ❌                │
│ → log: "Connection error on attempt 1"│
│                                     │
│ 2.0秒待機                            │
│                                     │
│ Attempt 2: func() を実行             │
│ → ConnectionError ❌                │
│ → log: "Connection error on attempt 2"│
│                                     │
│ 4.0秒待機                            │
│                                     │
│ Attempt 3: func() を実行             │
│ → ConnectionError ❌                │
│ → log: "Connection error on attempt 3"│
│                                     │
│ → raise AIAPIError("API connection  │
│   failed after 2 retries")          │
└─────────────────────────────────────┘

実行時間: ~8秒（API 3回 + 6秒待機）
エラー: AIAPIError例外
```

---

## 🔒 エラー分類とハンドリング

### 1. RateLimitError（レート制限）

**発生条件**: Claude APIのレート制限を超過

**リトライ戦略**: 指数バックオフでリトライ

**最終処理**: 全リトライ失敗時はAIRateLimitError例外

```python
except RateLimitError as e:
    logger.warning(f"Rate limit hit on attempt {attempt}")
    if attempt == max_retries:
        raise AIRateLimitError(
            f"Rate limit exceeded after {max_retries} retries",
            retry_after=getattr(e, "retry_after", None)
        )
    delay *= backoff_factor
```

**retry_after属性**: Claude APIが推奨する待機時間（秒）を含む場合あり

---

### 2. APIConnectionError（接続エラー）

**発生条件**: ネットワーク接続の失敗

**リトライ戦略**: 指数バックオフでリトライ

**最終処理**: 全リトライ失敗時はAIAPIError例外

```python
except APIConnectionError as e:
    logger.warning(f"Connection error on attempt {attempt}")
    if attempt == max_retries:
        raise AIAPIError(
            f"API connection failed after {max_retries} retries",
            original_error=e
        )
    delay *= backoff_factor
```

---

### 3. APITimeoutError（タイムアウト）

**発生条件**: API呼び出しがタイムアウト

**リトライ戦略**: 接続エラーと同様に処理

```python
except APITimeoutError as e:
    logger.warning(f"Timeout on attempt {attempt}")
    # ConnectionErrorと同じ処理
```

---

### 4. APIError（非リトライエラー）

**発生条件**: 無効なAPI鍵、パラメータエラー等

**リトライ戦略**: リトライせず即座に失敗

**理由**: リトライしても成功しないエラー

```python
except APIError as e:
    logger.error(f"Non-retryable API error: {e}")
    raise AIAPIError(f"API error: {str(e)}", original_error=e)
```

---

### 5. 予期しないエラー

**発生条件**: プログラムロジックエラー等

**リトライ戦略**: リトライせず即座に失敗

```python
except Exception as e:
    logger.error(f"Unexpected error: {e}", exc_info=True)
    raise AIAPIError(f"Unexpected error: {str(e)}", original_error=e)
```

---

## 📈 パフォーマンス特性

### リトライ回数別の最大待機時間

| max_retries | backoff_factor | 最大累積待機時間 |
|------------|---------------|----------------|
| 1 | 2.0 | 2秒 (2s) |
| 2 | 2.0 | 6秒 (2s + 4s) |
| 3 | 2.0 | 14秒 (2s + 4s + 8s) |
| 5 | 2.0 | 62秒 (2s + 4s + 8s + 16s + 32s) |

**計算式**: 累積待機時間 = initial_delay × (2^1 + 2^2 + ... + 2^n)

### バックオフ倍率別の遅延

| backoff_factor | 1回目 | 2回目 | 3回目 | 累積 |
|---------------|-------|-------|-------|------|
| 1.5 | 1.5s | 2.25s | 3.375s | 7.125s |
| 2.0 | 2.0s | 4.0s | 8.0s | 14.0s |
| 3.0 | 3.0s | 9.0s | 27.0s | 39.0s |

---

## 🧪 テスト

### 実装済みテスト

**テストファイル**: `/backend/tests/test_ai_retry_helper.py`

**テストカバレッジ**: 95%

#### テストケース

1. **成功ケース**
   ```python
   def test_successful_on_first_attempt():
       """1回目で成功する場合"""

   def test_successful_after_retry():
       """リトライ後に成功する場合"""
   ```

2. **レート制限エラー**
   ```python
   def test_rate_limit_error_after_max_retries():
       """レート制限が全リトライ後も解決しない場合"""

   def test_rate_limit_with_retry_after():
       """retry_after属性を持つレート制限エラー"""
   ```

3. **接続・タイムアウトエラー**
   ```python
   def test_connection_error_retry():
       """接続エラーのリトライ"""

   def test_timeout_error_retry():
       """タイムアウトエラーのリトライ"""

   def test_connection_error_max_retries():
       """接続エラーが全リトライ後も解決しない場合"""
   ```

4. **非リトライエラー**
   ```python
   def test_non_retryable_api_error():
       """非リトライエラーは即座に失敗"""

   def test_unexpected_error():
       """予期しないエラーの処理"""
   ```

5. **バックオフロジック**
   ```python
   def test_exponential_backoff():
       """指数バックオフの遅延計算"""

   def test_custom_backoff_factor():
       """カスタムバックオフ倍率"""
   ```

6. **関数引数**
   ```python
   def test_function_with_args():
       """位置引数の受け渡し"""

   def test_function_with_kwargs():
       """キーワード引数の受け渡し"""
   ```

---

## 📊 モニタリングとログ

### ログ出力例

#### 成功ケース
```
INFO: AIService initialized with model: claude-3-5-sonnet-20241022
INFO: Generating assessment: topic='マーケティング診断', industry=it_saas
INFO: Assessment generated successfully: 500 input tokens, 2000 output tokens
```

#### リトライ成功ケース
```
WARNING: Rate limit hit on attempt 1/4: Rate limit exceeded
INFO: Retry attempt 1/3 after 2.0s delay
INFO: Retry succeeded on attempt 1
INFO: Assessment generated successfully: 500 input tokens, 2000 output tokens
```

#### 全リトライ失敗ケース
```
WARNING: Connection error on attempt 1/4: Connection failed
INFO: Retry attempt 1/3 after 2.0s delay
WARNING: Connection error on attempt 2/4: Connection failed
INFO: Retry attempt 2/3 after 4.0s delay
WARNING: Connection error on attempt 3/4: Connection failed
INFO: Retry attempt 3/3 after 8.0s delay
WARNING: Connection error on attempt 4/4: Connection failed
ERROR: AI generation failed: API connection failed after 3 retries
```

### メトリクス収集（未実装）

```python
# Prometheus メトリクス例
ai_api_retry_total = Counter(
    "ai_api_retry_total",
    "Total number of retry attempts",
    ["error_type", "attempt"]
)

ai_api_retry_success = Counter(
    "ai_api_retry_success",
    "Number of successful retries",
    ["attempt"]
)

ai_api_backoff_duration_seconds = Histogram(
    "ai_api_backoff_duration_seconds",
    "Duration of backoff delays"
)
```

---

## 🚀 将来の改善

### 1. アダプティブリトライ

過去の成功率に基づいて動的にリトライパラメータを調整：

```python
class AdaptiveRetryPolicy:
    def __init__(self):
        self.success_rate_window = deque(maxlen=100)

    def get_retry_params(self) -> dict:
        """成功率に基づいてパラメータを調整"""
        success_rate = sum(self.success_rate_window) / len(self.success_rate_window)

        if success_rate < 0.5:
            # 成功率が低い → より慎重に
            return {"max_retries": 5, "initial_delay": 2.0}
        else:
            # 成功率が高い → 通常設定
            return {"max_retries": 3, "initial_delay": 1.0}
```

### 2. サーキットブレーカーパターン

連続失敗時にAPIへのアクセスを一時停止：

```python
class CircuitBreaker:
    def __init__(self, failure_threshold=5, timeout=60):
        self.failure_count = 0
        self.failure_threshold = failure_threshold
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN
        self.timeout = timeout

    async def call(self, func):
        if self.state == "OPEN":
            raise CircuitBreakerOpenError("Circuit breaker is open")

        try:
            result = await func()
            self.on_success()
            return result
        except Exception as e:
            self.on_failure()
            raise
```

### 3. ジッター追加

同時リトライによる雷鳴現象（Thundering Herd）を防ぐ：

```python
import random

delay = initial_delay * (backoff_factor ** attempt)
jittered_delay = delay * (0.5 + random.random() * 0.5)  # ±25%のランダム性
await asyncio.sleep(jittered_delay)
```

### 4. リトライバジェット

一定期間内のリトライ回数を制限：

```python
class RetryBudget:
    def __init__(self, max_retries_per_minute=100):
        self.budget = max_retries_per_minute
        self.window_start = time.time()

    def can_retry(self) -> bool:
        """リトライ可能かチェック"""
        if time.time() - self.window_start > 60:
            self.budget = self.max_retries_per_minute
            self.window_start = time.time()

        return self.budget > 0
```

### 5. テナント別リトライポリシー

テナントの優先度に応じたリトライ設定：

```python
TENANT_RETRY_POLICIES = {
    "enterprise": {"max_retries": 5, "initial_delay": 0.5},
    "pro": {"max_retries": 3, "initial_delay": 1.0},
    "free": {"max_retries": 1, "initial_delay": 2.0},
}
```

---

## 🔗 関連仕様

- [AI Support](../features/ai-support.md) - AI診断生成機能
- [Error Logging & Monitoring](./error-logging-monitoring.md) - エラーログシステム
- [Prompt Security](../ai/prompt-security.md) - プロンプトセキュリティ

---

**実装ステータス**: ✅ 完全実装済み（基本リトライ機能）
**拡張機能**: ⏳ サーキットブレーカー、ジッター、アダプティブリトライは未実装
