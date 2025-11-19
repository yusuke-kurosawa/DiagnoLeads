# データベースマイグレーションガイド

## AI Usage Log テーブルの追加 (2025-11-18)

### 概要

AI APIの使用量追跡とコスト管理のための新しいテーブル `ai_usage_logs` を追加します。

### マイグレーション情報

- **Revision ID**: `b2c3d4e5f6g7`
- **Previous**: `a1b2c3d4e5f6` (Google Analytics integration)
- **作成日**: 2025-11-18

### 追加されるテーブル

#### `ai_usage_logs`

AI APIの使用履歴を記録するテーブル。

**カラム**:
- `id` (UUID): 主キー
- `tenant_id` (UUID): テナントID（外部キー: tenants.id）
- `user_id` (UUID): ユーザーID（外部キー: users.id、SET NULL）
- `operation` (VARCHAR 100): 操作種別（generate_assessment, analyze_lead_insights等）
- `model` (VARCHAR 100): 使用したAIモデル（claude-3-5-sonnet-20241022等）
- `input_tokens` (INTEGER): 入力トークン数
- `output_tokens` (INTEGER): 出力トークン数
- `total_tokens` (INTEGER): 合計トークン数
- `cost_usd` (FLOAT): 推定コスト（USD）
- `assessment_id` (UUID): 関連するアセスメントID（外部キー: assessments.id、SET NULL）
- `lead_id` (UUID): 関連するリードID（外部キー: leads.id、SET NULL）
- `duration_ms` (INTEGER): 実行時間（ミリ秒）
- `success` (VARCHAR 20): 実行結果（success/failure）
- `created_at` (TIMESTAMP): 作成日時

**インデックス**:
- `idx_ai_usage_logs_tenant_id`: tenant_id単独
- `idx_ai_usage_logs_operation`: operation単独
- `idx_ai_usage_logs_created_at`: created_at単独
- `idx_ai_usage_logs_tenant_created`: tenant_id + created_at複合（コスト集計用）

### マイグレーション実行手順

#### 1. 事前準備

```bash
# バックエンドディレクトリに移動
cd /home/user/DiagnoLeads/backend

# データベースバックアップ（推奨）
# PostgreSQLの場合
pg_dump -U postgres -d diagnoleads > backup_$(date +%Y%m%d_%H%M%S).sql
```

#### 2. 現在のマイグレーション状態を確認

```bash
# Alembic経由でPythonスクリプトを実行
python << 'EOF'
from alembic.config import Config
from alembic import command

alembic_cfg = Config("alembic.ini")
command.current(alembic_cfg)
EOF
```

または、直接SQLで確認:

```sql
SELECT * FROM alembic_version;
```

#### 3. マイグレーション実行

```bash
# Pythonスクリプトでマイグレーション実行
python << 'EOF'
from alembic.config import Config
from alembic import command

alembic_cfg = Config("alembic.ini")
command.upgrade(alembic_cfg, "head")
EOF
```

または、環境によってはalembicコマンドが利用可能:

```bash
alembic upgrade head
```

#### 4. マイグレーション確認

```sql
-- テーブルが作成されたか確認
\dt ai_usage_logs

-- インデックスが作成されたか確認
\di idx_ai_usage_logs*

-- テーブル構造を確認
\d ai_usage_logs
```

### ロールバック手順

問題が発生した場合、以下のコマンドでロールバック可能:

```bash
# Pythonスクリプトでダウングレード
python << 'EOF'
from alembic.config import Config
from alembic import command

alembic_cfg = Config("alembic.ini")
command.downgrade(alembic_cfg, "a1b2c3d4e5f6")
EOF
```

または:

```bash
alembic downgrade a1b2c3d4e5f6
```

### 動作確認

マイグレーション後、以下のSQLで動作確認:

```sql
-- サンプルデータを挿入
INSERT INTO ai_usage_logs (
    id, tenant_id, operation, model,
    input_tokens, output_tokens, total_tokens, success
) VALUES (
    gen_random_uuid(),
    (SELECT id FROM tenants LIMIT 1),
    'generate_assessment',
    'claude-3-5-sonnet-20241022',
    1000, 2000, 3000, 'success'
);

-- データを確認
SELECT * FROM ai_usage_logs;

-- 削除
DELETE FROM ai_usage_logs WHERE operation = 'generate_assessment';
```

### パフォーマンスへの影響

- **新規テーブル追加**: 既存テーブルには影響なし
- **インデックス**: 4つのインデックスを作成（実行時間: 小規模DBで1秒未満）
- **外部キー制約**: ON DELETE SET NULL設定により、親レコード削除時も整合性を保持
- **ダウンタイム**: 通常は不要（テーブル追加のみ）

### 注意事項

1. **外部キー制約**: tenants, users, assessments, leadsテーブルが存在している必要があります
2. **データ保持**: ユーザーやアセスメントが削除されても、ai_usage_logsのレコードは残ります（SET NULL）
3. **コスト計算**: cost_usdはアプリケーション側で計算・設定されます（モデル料金の変動に注意）

### トラブルシューティング

#### エラー: "relation 'assessments' does not exist"

アセスメントテーブルのマイグレーションが実行されていません:

```bash
# マイグレーション履歴を確認
python -c "from alembic.config import Config; from alembic import command; command.history(Config('alembic.ini'))"

# 必要なマイグレーションを実行
python -c "from alembic.config import Config; from alembic import command; command.upgrade(Config('alembic.ini'), 'head')"
```

#### エラー: "duplicate key value violates unique constraint"

alembic_versionテーブルに既に同じrevisionが存在:

```sql
-- 現在のバージョンを確認
SELECT * FROM alembic_version;

-- 必要に応じて手動で更新
UPDATE alembic_version SET version_num = 'b2c3d4e5f6g7';
```

### 関連ドキュメント

- [AGENTS_REFACTORING.md](./AGENTS_REFACTORING.md) - AI Agentsリファクタリングの詳細
- [AIUsageLog モデル](./app/models/ai_usage.py) - モデル定義

### 次のステップ

マイグレーション完了後:

1. アプリケーションを再起動
2. AI API呼び出しを実行して、ログが正しく記録されるか確認
3. テナント別の使用量レポート機能を実装（オプション）

```sql
-- テナント別の今月のトークン使用量を確認
SELECT
    tenant_id,
    COUNT(*) as api_calls,
    SUM(input_tokens) as total_input_tokens,
    SUM(output_tokens) as total_output_tokens,
    SUM(total_tokens) as total_tokens,
    SUM(cost_usd) as total_cost_usd
FROM ai_usage_logs
WHERE created_at >= date_trunc('month', CURRENT_DATE)
GROUP BY tenant_id
ORDER BY total_cost_usd DESC;
```
