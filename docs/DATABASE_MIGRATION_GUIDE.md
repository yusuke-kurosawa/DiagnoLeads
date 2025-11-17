# データベースマイグレーションガイド

このドキュメントでは、DiagnoLeadsプロジェクトのデータベースマイグレーションを安全に実行する方法を説明します。

## 📋 目次

1. [概要](#概要)
2. [マイグレーションファイル一覧](#マイグレーションファイル一覧)
3. [ローカル環境での実行](#ローカル環境での実行)
4. [本番環境での実行](#本番環境での実行)
5. [ロールバック手順](#ロールバック手順)
6. [トラブルシューティング](#トラブルシューティング)

---

## 概要

DiagnoLeadsは**Alembic**を使用してデータベースマイグレーションを管理しています。

### 最新のマイグレーション

Phase 1の機能追加に伴い、以下の新しいテーブルが追加されました：

- **SMSキャンペーン**: `sms_campaigns`, `sms_messages`
- **A/Bテスト**: `ab_tests`, `ab_test_variants`

---

## マイグレーションファイル一覧

### 既存のマイグレーション

1. `0f18384ca39a` - 初期テーブル（tenants, users）
2. `d724f366bbf2` - 診断モデル（assessments）
3. `e33568d0d2e9` - リードモデル（leads）
4. `f5a2c3d8e9b1` - Row-Level Security
5. `f7e1c2d9b3a4` - 認証機能強化（パスワードリセット、ログイン制限）

### 新規マイグレーション（Phase 1）

6. **`a1b2c3d4e5f6`** - SMSキャンペーンテーブル追加
   - テーブル: `sms_campaigns`, `sms_messages`
   - Enum: `SMSStatus` (pending, sent, delivered, failed, undelivered)
   - インデックス: tenant_id, campaign_id, status, twilio_sid

7. **`b2c3d4e5f6a7`** - A/Bテストテーブル追加
   - テーブル: `ab_tests`, `ab_test_variants`
   - Enum: `ABTestStatus`, `ABTestType`
   - インデックス: tenant_id, assessment_id, status

---

## ローカル環境での実行

### 前提条件

- Python 3.11+がインストールされている
- PostgreSQLデータベースが起動している
- 環境変数が設定されている（`.env`ファイル）

### 手順

```bash
# 1. バックエンドディレクトリに移動
cd backend

# 2. 仮想環境の有効化
source venv/bin/activate  # macOS/Linux
# または
venv\Scripts\activate  # Windows

# 3. 現在のマイグレーション状態を確認
alembic current

# 4. 保留中のマイグレーションを確認
alembic history

# 5. 最新のマイグレーションまで適用
alembic upgrade head

# 6. 特定のマイグレーションまで適用（オプション）
alembic upgrade a1b2c3d4e5f6  # SMSテーブルのみ
```

### 実行結果の確認

```bash
# PostgreSQLに接続
psql $DATABASE_URL

# テーブルが作成されているか確認
\dt

# SMSテーブルの確認
SELECT * FROM alembic_version;
SELECT table_name FROM information_schema.tables
WHERE table_name IN ('sms_campaigns', 'sms_messages', 'ab_tests', 'ab_test_variants');
```

---

## 本番環境での実行

### ⚠️ 重要: 本番環境での注意事項

1. **必ずバックアップを取得**してからマイグレーションを実行
2. **ダウンタイムウィンドウ**を設定（可能であれば）
3. **ロールバックプランを準備**
4. **ステージング環境で事前テスト**

### バックアップ手順

```bash
# PostgreSQLのバックアップ（本番DB URLを使用）
pg_dump $DATABASE_URL > backup_$(date +%Y%m%d_%H%M%S).sql

# バックアップの確認
ls -lh backup_*.sql
```

### 本番マイグレーション実行

```bash
# 1. Railwayにデプロイ済みの場合、コンテナ内で実行
railway run alembic upgrade head

# 2. または、SSH接続して実行
railway shell
cd backend
alembic upgrade head

# 3. Herokuの場合
heroku run -a your-app-name alembic upgrade head

# 4. 手動デプロイの場合
ssh user@your-server
cd /path/to/DiagnoLeads/backend
source venv/bin/activate
alembic upgrade head
```

### 実行後の確認

```bash
# マイグレーション状態の確認
alembic current

# 期待値: b2c3d4e5f6a7 (head)

# テーブル数の確認
psql $DATABASE_URL -c "\dt" | wc -l

# 新しいテーブルのレコード数（初期は0）
psql $DATABASE_URL -c "SELECT COUNT(*) FROM sms_campaigns;"
psql $DATABASE_URL -c "SELECT COUNT(*) FROM ab_tests;"
```

---

## ロールバック手順

### 緊急時のロールバック

マイグレーション後に問題が発生した場合、以下の手順でロールバックします。

```bash
# 1. 直前のマイグレーションにロールバック
alembic downgrade -1

# 2. 特定のマイグレーションまでロールバック
alembic downgrade f7e1c2d9b3a4  # 認証機能強化まで戻す

# 3. すべてのマイグレーションを取り消し（危険！）
alembic downgrade base
```

### ロールバック後の確認

```bash
# マイグレーション状態を確認
alembic current

# テーブルが削除されているか確認
psql $DATABASE_URL -c "\dt" | grep sms
psql $DATABASE_URL -c "\dt" | grep ab_test
```

### バックアップからの復元

最悪の場合、バックアップから復元します。

```bash
# データベースを削除して再作成
dropdb diagno_leads_prod
createdb diagno_leads_prod

# バックアップを復元
psql $DATABASE_URL < backup_20251117_120000.sql

# マイグレーション状態を確認
alembic current
```

---

## トラブルシューティング

### エラー: "Can't locate revision identified by 'xxx'"

**原因**: マイグレーションファイルが見つからない

**解決策**:
```bash
# マイグレーションファイルがあるか確認
ls -la backend/alembic/versions/

# Gitで最新のマイグレーションファイルを取得
git pull origin main
```

### エラー: "Target database is not up to date"

**原因**: alembic_versionテーブルの状態が不整合

**解決策**:
```bash
# 現在のバージョンを確認
alembic current

# 手動でバージョンテーブルを更新（最終手段）
psql $DATABASE_URL -c "UPDATE alembic_version SET version_num = 'f7e1c2d9b3a4';"

# 再度マイグレーション実行
alembic upgrade head
```

### エラー: "relation already exists"

**原因**: テーブルが既に存在している

**解決策**:
```bash
# オプション1: 既存テーブルを削除（開発環境のみ！）
psql $DATABASE_URL -c "DROP TABLE IF EXISTS sms_campaigns CASCADE;"
alembic upgrade head

# オプション2: マイグレーションをスキップ（本番環境）
alembic stamp b2c3d4e5f6a7  # 手動でマイグレーション済みとマーク
```

### エラー: "could not connect to server"

**原因**: データベース接続エラー

**解決策**:
```bash
# 環境変数を確認
echo $DATABASE_URL

# データベースが起動しているか確認
psql $DATABASE_URL -c "SELECT version();"

# .envファイルを確認
cat backend/.env | grep DATABASE_URL
```

### パフォーマンス問題: マイグレーションが遅い

**原因**: 大量のデータに対するインデックス作成

**解決策**:
```bash
# CONCURRENTLYオプションでインデックス作成（PostgreSQL）
# マイグレーションファイルを編集して以下を追加:
op.create_index(
    'idx_sms_campaigns_tenant_id',
    'sms_campaigns',
    ['tenant_id'],
    postgresql_concurrently=True
)

# マイグレーション実行
alembic upgrade head
```

---

## 追加リソース

### 新しいマイグレーションの作成

```bash
# 自動生成（モデル変更を検出）
alembic revision --autogenerate -m "Add new feature"

# 手動作成
alembic revision -m "Custom migration"
```

### マイグレーション履歴の確認

```bash
# すべてのマイグレーションを表示
alembic history --verbose

# 現在のバージョンから最新までの差分を表示
alembic history --indicate-current
```

### データベーススキーマのエクスポート

```bash
# スキーマのみをエクスポート（データなし）
pg_dump --schema-only $DATABASE_URL > schema.sql

# ERD図の生成（postgresql_autodocを使用）
postgresql_autodoc -d diagno_leads_prod -t dot
```

---

## サポート

マイグレーション実行中に問題が発生した場合は、以下を確認してください：

1. [Alembic公式ドキュメント](https://alembic.sqlalchemy.org/)
2. [PostgreSQL公式ドキュメント](https://www.postgresql.org/docs/)
3. プロジェクトの`CLAUDE.md` - 開発規約
4. GitHubイシュー - 既知の問題

**緊急時の連絡**: システム管理者に連絡してください。
