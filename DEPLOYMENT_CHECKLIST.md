# 本番環境デプロイ チェックリスト

**デプロイ日時**: _______________  
**デプロイ環境**: ☐ Railway (推奨) ☐ その他: _______________  
**担当者**: _______________

---

## ✅ ステップ 1: 事前準備 (デプロイ1日前)

### コード品質

- [ ] すべてのテスト合格確認: `docker exec diagnoleads-backend python test_production_readiness.py`
- [ ] Git リポジトリがクリーンな状態 (コミット漏れなし): `git status`
- [ ] Main ブランチが最新版: `git log --oneline -1`
- [ ] Linter チェック実行 (存在する場合)

### セキュリティレビュー

- [ ] `.env.production` ファイルが `.gitignore` に含まれている
- [ ] 機密情報（API キー、パスワード）がコード内にハードコードされていない
- [ ] SECRET_KEY が十分に強力（最小 32 文字のランダム文字列）
- [ ] HTTPS/TLS が有効化される予定

### データベース準備

- [ ] PostgreSQL 本番インスタンスが準備完了
- [ ] データベースのバックアップ戦略が決定
  - ☐ 自動バックアップ設定
  - ☐ バックアップリカバリープロセス документ化
- [ ] マイグレーション準備: `alembic current` で確認
- [ ] 初期データ（デモテナント等）の準備

---

## ✅ ステップ 2: デプロイ前チェック (デプロイ数時間前)

### 環境変数確認

```bash
# 必須環境変数をすべて確認
✓ ENVIRONMENT=production
✓ DEBUG=False
✓ DATABASE_URL=postgresql://...
✓ REDIS_URL=redis://...
✓ SECRET_KEY=... (32字以上ランダム)
✓ ALGORITHM=HS256
✓ ACCESS_TOKEN_EXPIRE_MINUTES=1440
✓ ANTHROPIC_API_KEY=sk-ant-... (AI 機能が不要な場合は空でもOK)
✓ ALLOWED_ORIGINS=[...] (ドメイン指定)
✓ FRONTEND_URL=https://...
✓ BACKEND_URL=https://...
```

チェック方法:
```bash
# .env.production が正しく作成されているか確認
cat .env.production | grep -E "^[A-Z_]+=" | wc -l
# 期待値: 15個以上
```

### ネットワーク・インフラ確認

- [ ] データベースホストに接続できるか確認: `psql -h HOST -U user -d diagnoleads -c "SELECT 1;"`
- [ ] Redis ホストに接続できるか確認: `redis-cli -h HOST ping`
- [ ] CORS ドメインが正しく設定される予定
- [ ] SSL/TLS 証明書が有効期限内
- [ ] API エンドポイント URL が確定（例: api.example.com）

### Docker イメージ準備

```bash
# バックエンドイメージ最新化
docker build -t diagnoleads-backend:latest ./backend
docker build -t diagnoleads-frontend:latest ./frontend

# イメージがコンテナレジストリにプッシュされているか確認
docker images | grep diagnoleads
```

- [ ] Docker イメージビルドが成功
- [ ] レジストリへのプッシュが完了 (Vercel/Railway の場合は自動)

---

## ✅ ステップ 3: デプロイ実行

### Railway へのデプロイ (推奨)

#### 3.1 Railway CLI インストール
```bash
npm install -g @railway/cli
railway login
```

- [ ] Railway CLI がインストール済み
- [ ] Railway にログイン完了

#### 3.2 本番プロジェクト作成
```bash
# Railway ダッシュボードで新規プロジェクト作成
# または CLI から:
railway init

# サービス追加
railway add --service postgres
railway add --service redis
```

- [ ] PostgreSQL サービス追加
- [ ] Redis サービス追加
- [ ] バックエンド デプロイ設定
- [ ] フロントエンド デプロイ設定 (Vercel)

#### 3.3 環境変数セット
```bash
# Railway ダッシュボードで環境変数を入力
# または CLI から:
railway variables set ENVIRONMENT=production
railway variables set DEBUG=False
railway variables set DATABASE_URL=postgresql://...
# ... (他の環境変数)
```

- [ ] すべての必須環境変数が Railway に設定
- [ ] 機密情報は Railway のシークレット変数として設定

#### 3.4 デプロイ実行
```bash
git push origin main
# Railway はメインブランチへの push で自動デプロイ
```

- [ ] デプロイが開始
- [ ] ビルド完了
- [ ] コンテナが起動

### Vercel へのフロントエンド デプロイ

```bash
# Vercel CLI
npm install -g vercel

# デプロイ
vercel --prod --env-file=.env.production
```

- [ ] フロントエンドのビルド成功
- [ ] Vercel へのデプロイ完了
- [ ] カスタムドメイン設定完了

---

## ✅ ステップ 4: デプロイ後検証

### ヘルスチェック

```bash
# バックエンド
curl -X GET https://api.example.com/health
# 期待レスポンス: {"status":"healthy","service":"diagnoleads-api","version":"0.1.0"}

# フロントエンド
curl -X GET https://app.example.com/
# 期待: ステータス 200、HTML が返される
```

- [ ] バックエンド `/health` エンドポイント: 200 OK
- [ ] フロントエンドが起動: 200 OK
- [ ] ログ出力が正常: Docker ログで エラーなし

### API エンドポイント検証

```bash
# ユーザーログイン テスト
curl -X POST https://api.example.com/api/v1/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=test@example.com&password=TestPassword123!"

# 期待: 200 OK + access_token が返される
```

- [ ] ログインエンドポイント: 200 OK
- [ ] トークン生成: 成功
- [ ] データベース接続: 正常
- [ ] Redis キャッシュ: 動作中

### エラーログ確認

```bash
# Railway ダッシュボールから ログを確認
railway logs
```

- [ ] ERROR レベルのログがない
- [ ] 起動エラーがない
- [ ] データベース接続エラーがない

### マイグレーション実行確認

```bash
# 本番データベースでマイグレーション実行
# (Railway: コンテナシェルから実行)
railway shell
alembic upgrade head
```

- [ ] マイグレーション成功 (最新リビジョンは `f7e1c2d9b3a4`)
- [ ] テーブルが作成されている
- [ ] 初期データ（必要に応じて）セット済み

---

## ✅ ステップ 5: 本番環境検証テスト

本番環境テストスイート実行:

```bash
# 本番環境での smoke テスト
curl -X GET https://api.example.com/health
curl -X POST https://api.example.com/api/v1/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=prod-test@example.com&password=ProdTestPassword123!"
```

### テスト項目

- [ ] Health Check: 200 OK
- [ ] ユーザーログイン: 200 OK
- [ ] トークン取得: 成功
- [ ] マルチテナント分離: テスト済み
- [ ] レート制限: テスト済み
- [ ] エラーハンドリング: 正常

---

## ✅ ステップ 6: モニタリング・ロギング設定

### エラー監視

- [ ] Sentry を設定 (または同等のエラー追跡サービス)
- [ ] アラート設定: エラーレート > X% で通知
- [ ] ダッシュボードが閲覧可能

### ログ集約

- [ ] ログがセンター化されている
  - ☐ CloudWatch
  - ☐ DataDog
  - ☐ Sentry
  - ☐ その他: _______________

### ステータスページ (オプション)

- [ ] ステータスページが公開されている (例: status.example.com)
- [ ] 定期的な健全性チェックが構成済み

---

## ✅ ステップ 7: ドメイン・DNS 設定

### DNS レコード確認

```bash
# 設定確認
nslookup api.example.com
nslookup app.example.com

# 期待: Railway/Vercel のホスト IP アドレスが返される
```

- [ ] API ドメイン (api.example.com) が Railway を指している
- [ ] APP ドメイン (app.example.com) が Vercel を指している
- [ ] DNS キャッシュが反映されている (最大 24 時間)

### SSL/TLS 証明書

- [ ] HTTPS が有効 (自動発行: Let's Encrypt)
- [ ] 証明書が有効期限内
- [ ] Mixed Content エラーがない (すべて HTTPS)

---

## ✅ ステップ 8: バックアップ・ディザスタリカバリ

### バックアップ戦略

- [ ] 自動バックアップが有効
  - ☐ 日次バックアップ
  - ☐ 週次バックアップ
  - ☐ 月次バックアップ
- [ ] バックアップ保持ポリシーが決定
- [ ] リストア手順がドキュメント化

### ディザスタリカバリテスト (オプション)

- [ ] バックアップからのリストア テスト実施
- [ ] リカバリ時間目標 (RTO): _______________
- [ ] リカバリ ポイント目標 (RPO): _______________

---

## ✅ ステップ 9: ユーザーアクセス テスト

### ユーザー検証

テストユーザーで以下をテスト:
1. アカウント作成
2. ログイン
3. 診断コンテンツ閲覧
4. リード データ入力
5. ダッシュボード表示
6. データエクスポート

進行状況:

- [ ] アカウント作成: OK
- [ ] ログイン: OK
- [ ] コンテンツ閲覧: OK
- [ ] リード入力: OK
- [ ] ダッシュボード: OK

---

## ✅ ステップ 10: ドキュメント・チームへの通知

### ドキュメント更新

- [ ] README.md に本番環境 URL を記載
- [ ] デプロイ手順書 更新
- [ ] API ドキュメント 最新化 (Swagger/OpenAPI)
- [ ] アーキテクチャ図 更新 (必要に応じて)

### チーム通知

- [ ] エンジニアチーム: デプロイ完了通知
- [ ] 営業・マーケティング: 本番環境 URL 通知
- [ ] サポートチーム: トラブルシューティングガイド配布

---

## 🚨 ロールバック計画

何か問題が発生した場合のロールバック手順:

### ロールバック手順

```bash
# 前のデプロイに戻す
git revert HEAD
git push origin main

# または特定のコミットに戻す
git checkout [previous-commit-hash]
git push origin main --force
```

**注意**: `--force` は慎重に使用 (チーム内で調整)

### ロールバック判定基準

以下のいずれかが発生した場合、即座にロールバック:

- [ ] ユーザーがログインできない
- [ ] データが保存されない
- [ ] エラーレートが異常に高い (> 5%)
- [ ] レスポンスタイムが異常 (> 5 秒)
- [ ] セキュリティの脆弱性が発見

---

## 📋 デプロイ結果

### デプロイ情報

- **デプロイ時刻**: _______________
- **デプロイ対象コミット**: _______________
- **デプロイ実行者**: _______________
- **所要時間**: _______________

### テスト結果

- **バックエンドテスト**: _______________
- **フロントエンドテスト**: _______________
- **エンドツーエンドテスト**: _______________

### 検出された問題

| 項目 | 重要度 | ステータス | 対応予定日 |
|-----|--------|----------|---------|
| | | | |
| | | | |

---

## ✅ 最終確認

- [ ] すべてのチェックリスト項目が完了
- [ ] 本番環境が正常に動作している
- [ ] ユーザーアクセスが可能
- [ ] モニタリング・ロギングが機能中
- [ ] バックアップが作成済み

**デプロイ承認者**: _______________  
**承認日時**: _______________

---

## 📞 サポート連絡先

デプロイ中に問題が発生した場合:

- **技術サポート**: [Slack チャネル] または [メール]
- **緊急対応**: [電話番号]
- **ドキュメント**: [Wiki/Notion リンク]

