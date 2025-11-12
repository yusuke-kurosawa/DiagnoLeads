# 🚀 DiagnoLeads 本番環境デプロイ - クイックスタート

**所要時間**: 25 分  
**難易度**: 簡単 (コマンドコピペで実行可能)  
**対象プラットフォーム**: Railway (バックエンド) + Vercel (フロントエンド)

---

## 📋 5分以内の準備

### 1. 必要な情報を収集 (2分)

```bash
# SECRET_KEY を生成
python3 -c "import secrets; print('SECRET_KEY=' + secrets.token_urlsafe(32))"

# 出力例:
# SECRET_KEY=4GD-xZ9aBcD1eF2gHiJkL3mNoPqRsTuV

# 👆 この値をメモしておく
```

### 2. .env.production ファイル作成 (3分)

```bash
# リポジトリルートで実行
cp .env.production.template .env.production

# テキストエディタで以下を編集:
# nano .env.production
```

**編集項目** (最小限の設定):

```bash
ENVIRONMENT=production
DEBUG=False

# 本番データベース (Railroad/Supabase から)
DATABASE_URL=postgresql://USER:PASSWORD@HOST:5432/diagnoleads

# 本番 Redis (Railway から)
REDIS_URL=redis://:PASSWORD@HOST:6379/0

# 生成した SECRET_KEY
SECRET_KEY=4GD-xZ9aBcD1eF2gHiJkL3mNoPqRsTuV

ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# フロントエンドのドメイン
ALLOWED_ORIGINS=["https://app.example.com"]
FRONTEND_URL=https://app.example.com
BACKEND_URL=https://api.example.com

# Claude API (後で設定可能)
ANTHROPIC_API_KEY=

# その他はテンプレートのデフォルト値を使用
```

---

## 🚂 Railway デプロイ (10分)

### ステップ 1: Railway CLI セットアップ

```bash
# インストール
npm install -g @railway/cli

# ログイン (ブラウザが開きます)
railway login
```

### ステップ 2: プロジェクト初期化

```bash
# プロジェクトフォルダで実行
cd /path/to/DiagnoLeads

# Railway プロジェクト初期化
railway init

# プロンプト: Project name
# → diagnoleads-prod (Enter)
```

### ステップ 3: サービス追加

```bash
# PostgreSQL 追加
railway add --service postgres

# Redis 追加
railway add --service redis

# プロンプトに従って Enter キー
```

**✅ この時点で Railway が自動的に DATABASE_URL と REDIS_URL を作成します**

### ステップ 4: 環境変数を Railway に設定

```bash
# Railway ダッシュボール: https://railway.app/dashboard
# または CLI から:

railway variables set ENVIRONMENT=production
railway variables set DEBUG=False
railway variables set ALGORITHM=HS256
railway variables set ACCESS_TOKEN_EXPIRE_MINUTES=1440
railway variables set SECRET_KEY="4GD-xZ9aBcD1eF2gHiJkL3mNoPqRsTuV"
railway variables set ALLOWED_ORIGINS='["https://app.example.com"]'
railway variables set FRONTEND_URL=https://app.example.com
railway variables set BACKEND_URL=https://api.example.com
railway variables set ANTHROPIC_API_KEY=
```

### ステップ 5: バックエンドをデプロイ

```bash
# GitHub にプッシュ
git push origin main

# Railway が自動的にビルド・デプロイを開始
```

**ダッシュボールで進捗確認**:
```bash
# リアルタイムログ
railway logs

# 期待ログ:
# ✓ Building application...
# ✓ Installing dependencies...
# ✓ Starting uvicorn...
```

---

## 🌐 ドメイン設定 (5分)

### DNS レコード設定

**API ドメイン** (api.example.com → Railway)

DNS プロバイダー (Cloudflare など) で:
```
Type:  CNAME
Name:  api
Value: (Railway から提供される値)
       例: your-app.railway.app
TTL:   3600
```

**フロントエンド** は Vercel が自動管理

---

## ✅ ステップ 6: ヘルスチェック (5分)

### デプロイ成功確認

```bash
# バックエンド確認
curl https://api.example.com/health

# 期待:
# {"status":"healthy","service":"diagnoleads-api","version":"0.1.0"}

# ログイン確認
curl -X POST https://api.example.com/api/v1/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=test@example.com&password=TestPassword123!"

# 期待: 200 OK + access_token が返される
```

---

## ✨ デプロイ完了！

**すべてが正常に動作していることが確認できれば、本番環境は稼働中です。** 🎉

### 確認チェックリスト

- [x] ヘルスチェック: 200 OK
- [x] ログイン: 成功
- [x] ドメイン: 正常に稼働
- [x] ログ: エラーなし

---

## 🚨 トラブルシューティング

### 問題: ログイン 500 エラー

```bash
# 1. DATABASE_URL を確認
railway variables | grep DATABASE_URL

# 2. PostgreSQL が起動しているか確認
railway logs

# 3. バックエンド再デプロイ
railway redeploy
```

### 問題: CORS エラー

```bash
# Railway 環境変数を確認
railway variables | grep ALLOWED_ORIGINS

# 正しいドメインが設定されているか確認
# 例: ["https://app.example.com"]
```

### 問題: ホスト名で接続できない

```bash
# DNS が伝播されるまで待つ (最大 24 時間)
nslookup api.example.com

# または Railway が提供するドメインを一時的に使用:
https://your-app.railway.app/health
```

---

## 🎓 次のステップ

### 今すぐ (デプロイ後)
- [ ] 初期ユーザーアカウント作成
- [ ] 監視・ロギング確認 (Sentry など)
- [ ] バックアップ設定確認

### 明日 (1-2日後)
- [ ] AI 機能有効化 (ANTHROPIC_API_KEY 設定)
- [ ] パフォーマンス監視
- [ ] 営業チームへの展開

### 今週 (1週間)
- [ ] E2E テスト実施
- [ ] 初期ユーザーテスト
- [ ] 本番環境最適化

---

## 📞 ホットライン

**問題が発生した場合:**

1. **エラーログ確認**
   ```bash
   railway logs --tail 100
   ```

2. **ダッシュボール確認**
   - https://railway.app/dashboard

3. **ドキュメント参照**
   - `PRODUCTION_DEPLOYMENT_GUIDE.md` (詳細手順)
   - `DEPLOYMENT_CHECKLIST.md` (チェックリスト)

---

## 🎉 成功！

このクイックスタートで:

✅ バックエンド (FastAPI + PostgreSQL + Redis) が Railway で稼働  
✅ フロントエンド (React + Vite) が Vercel で稼働  
✅ API が https://api.example.com で応答  
✅ アプリが https://app.example.com でアクセス可能  
✅ セキュリティ (JWT + テナント分離) が有効  

**本番環境へのデプロイが完了しました！** 🚀

---

**デプロイ実行時刻**: _______________  
**デプロイ完了時刻**: _______________  
**デプロイ所要時間**: _______________
