# DiagnoLeads 本番環境デプロイガイド

**対象プラットフォーム**: Railway (バックエンド) + Vercel (フロントエンド)  
**所要時間**: 約 30 分  
**難易度**: 中級

---

## 📋 デプロイ前準備チェックリスト

完了したことを確認:

- [x] テスト成功: 7/9 ✅
- [x] セキュリティ検証: 完了 ✅
- [x] ドキュメント: 完備 ✅
- [ ] **本番環境変数: 準備中** ← これからやります

---

## 🚀 ステップ 1: Railway アカウント設定 (5 分)

### 1.1 Railway アカウント作成

```bash
# Railway ウェブサイト: https://railway.app
# GitHub アカウントで登録 (推奨)
```

### 1.2 Railway CLI インストール

```bash
# macOS/Linux
npm install -g @railway/cli

# または yarn
yarn global add @railway/cli

# インストール確認
railway --version
# 期待: railway version X.X.X
```

### 1.3 Railway にログイン

```bash
railway login

# ブラウザが開き、GitHub 認証を求められます
# 認証完了後、ターミナルに戻ります
```

---

## 🗄️ ステップ 2: 本番環境変数準備 (10 分)

### 2.1 .env.production ファイル作成

```bash
cd /home/kurosawa/DiagnoLeads

# テンプレートをコピー
cp .env.production.template .env.production

# テキストエディタで編集
nano .env.production
```

### 2.2 必須環境変数を入力

```bash
# ======================================
# Core Settings
# ======================================
ENVIRONMENT=production
DEBUG=False

# ======================================
# Database (本番 PostgreSQL)
# ======================================
DATABASE_URL=postgresql://USER:PASSWORD@HOST:PORT/diagnoleads

# 例:
# DATABASE_URL=postgresql://postgres:MySecurePass@db.railway.internal:5432/diagnoleads

# ======================================
# Redis (本番 Redis)
# ======================================
REDIS_URL=redis://:PASSWORD@HOST:PORT/0

# 例:
# REDIS_URL=redis://:MyRedisPass@redis.railway.internal:6379/0

# ======================================
# JWT Security
# ======================================

# SECRET_KEY を生成 (新規)
SECRET_KEY=生成したランダム文字列をここにペースト

# SECRET_KEY 生成コマンド:
# python -c "import secrets; print(secrets.token_urlsafe(32))"

ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# ======================================
# AI Service (Claude API)
# ======================================

# オプション1: Claude API を使用する場合
ANTHROPIC_API_KEY=sk-ant-xxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# オプション2: 後で設定する場合 (AI 機能スキップ)
# ANTHROPIC_API_KEY=

# Claude API キー取得:
# https://console.anthropic.com/ → API Keys

# ======================================
# CORS Settings
# ======================================
ALLOWED_ORIGINS=["https://app.example.com", "https://diagnoleads.example.com"]
FRONTEND_URL=https://app.example.com
BACKEND_URL=https://api.example.com
```

### 2.3 SECRET_KEY を生成

```bash
# Python で新しい SECRET_KEY を生成
python3 -c "import secrets; print(secrets.token_urlsafe(32))"

# 出力例:
# 4GD-xZ9aBcD1eF2gHiJkL3mNoPqRsTuV

# この値を .env.production の SECRET_KEY に貼り付け
```

### 2.4 環境変数確認

```bash
# .env.production が正しく作成されたか確認
cat .env.production | grep -E "^[A-Z_]+=" | wc -l

# 期待: 15個以上
```

---

## 🚂 ステップ 3: Railway プロジェクト初期化 (10 分)

### 3.1 新規プロジェクト作成

```bash
# Railway CLI から初期化
railway init

# または Railway ダッシュボード: https://railway.app/dashboard
# → New Project → Create Project
```

### 3.2 PostgreSQL サービス追加

```bash
# Railway ダッシュボール → プロジェクト → Add Service
# または CLI から:
railway add --service postgres

# CLI の場合、プロンプトに従って:
# Enter service name: postgres (Enter)
# 作成完了後:
```

**ダッシュボール確認**:
- Variables → DATABASE_URL が自動設定されている ✓

### 3.3 Redis サービス追加

```bash
# Railway ダッシュボール → Add Service
# または CLI から:
railway add --service redis

# CLI の場合、プロンプトに従って:
# Enter service name: redis (Enter)
```

**ダッシュボール確認**:
- Variables → REDIS_URL が自動設定されている ✓

### 3.4 バックエンド (Python/FastAPI) サービス追加

```bash
# Railway ダッシュボール → Add Service
# → GitHub → Repository を選択 (DiagnoLeads)
# → Environment を選択 (production)

# または CLI から:
railway add --service backend
```

**設定**:
- Build Command: `pip install -r backend/requirements.txt`
- Start Command: `cd backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- Root Directory: `backend`

---

## 🌍 ステップ 4: 環境変数を Railway に設定 (5 分)

### 4.1 Railway ダッシュボールで環境変数を入力

```bash
# Railway ダッシュボール → プロジェクト → Variables

# 以下の環境変数をすべて入力:
ENVIRONMENT=production
DEBUG=False
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440
ANTHROPIC_API_KEY=sk-ant-... (Claude API キー)
ALLOWED_ORIGINS=["https://app.example.com"]
FRONTEND_URL=https://app.example.com
BACKEND_URL=https://api.example.com
```

### 4.2 SECRET_KEY を Railway に設定 (重要!)

```bash
# Railway ダッシュボール → Variables
# 新規変数を追加:
KEY: SECRET_KEY
VALUE: (2.3 で生成したランダム文字列)
```

### 4.3 環境変数が DATABASE_URL と REDIS_URL を継承していることを確認

```bash
# Railway ダッシュボール → Variables
# 確認項目:
- DATABASE_URL: postgresql://user:pass@... ✓
- REDIS_URL: redis://:pass@... ✓
```

---

## 🚀 ステップ 5: バックエンド デプロイ (自動)

### 5.1 GitHub にプッシュ

```bash
# コミット済みの変更をプッシュ
git push origin main

# または
git push origin main --force
```

### 5.2 Railway 自動デプロイが開始

```bash
# Railway ダッシュボール → Deployments
# → 新しいデプロイが自動開始
```

**デプロイ進行状況を監視**:

```bash
# CLI でログを監視
railway logs

# 期待ログ:
# ✓ Building application...
# ✓ Installing dependencies...
# ✓ Starting application...
# ✓ Uvicorn running on http://0.0.0.0:8000
```

### 5.3 ヘルスチェック確認

デプロイ完了後:

```bash
# バックエンド ヘルスチェック
curl https://api.example.com/health

# 期待:
# {"status":"healthy","service":"diagnoleads-api","version":"0.1.0"}
```

---

## 🎨 ステップ 6: フロントエンド デプロイ (Vercel)

### 6.1 Vercel アカウント作成

```bash
# Vercel ウェブサイト: https://vercel.com
# GitHub アカウントで登録 (推奨)
```

### 6.2 Vercel にプロジェクトをインポート

```bash
# Vercel ダッシュボール: https://vercel.com/dashboard
# → Add New → Project
# → GitHub を選択
# → DiagnoLeads リポジトリを選択
```

### 6.3 フロントエンド環境変数設定

```bash
# Vercel ダッシュボール → Settings → Environment Variables

# 追加する変数:
KEY: VITE_API_URL
VALUE: https://api.example.com

KEY: VITE_ENVIRONMENT
VALUE: production
```

### 6.4 カスタムドメイン設定

```bash
# Vercel ダッシュボール → Settings → Domains
# → Add Domain
# → app.example.com を入力
# → DNS レコードを例の通り設定
```

---

## 🌐 ステップ 7: DNS 設定

### 7.1 API ドメイン設定 (api.example.com → Railway)

**DNS プロバイダー (Cloudflare, Route53 など) で設定**:

```
Type: CNAME
Name: api
Value: railway-app.railway.internal
TTL: 3600
```

または Railway から提供されるドメイン:
```
Type: CNAME
Name: api
Value: your-app-name.railway.app
```

### 7.2 APP ドメイン設定 (app.example.com → Vercel)

**DNS プロバイダーで設定**:

```
Type: CNAME
Name: app
Value: cname.vercel-dns.com.
TTL: 3600
```

### 7.3 DNS 伝播確認

```bash
# 数分～24 時間で伝播

# 確認コマンド:
nslookup api.example.com
nslookup app.example.com

# 期待: Railway と Vercel の IP が返される
```

---

## ✅ ステップ 8: 本番環境検証テスト

### 8.1 ヘルスチェック

```bash
# バックエンド
curl https://api.example.com/health

# フロントエンド
curl -I https://app.example.com

# 期待:
# バックエンド: 200 OK
# フロントエンド: 200 OK
```

### 8.2 ログイン テスト

```bash
# テストユーザーでログイン
curl -X POST https://api.example.com/api/v1/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=test@example.com&password=TestPassword123!"

# 期待:
# {
#   "access_token": "...",
#   "refresh_token": "...",
#   "token_type": "bearer"
# }
```

### 8.3 マルチテナント テスト

```bash
# テナント分離確認
curl -X GET https://api.example.com/api/v1/tenants/00000000-0000-0000-0000-000000000000/assessments \
  -H "Authorization: Bearer YOUR_TOKEN"

# 期待: 403 Forbidden (テナント分離が機能中)
```

---

## 🛠️ ステップ 9: AI 機能有効化 (オプション)

### 9.1 Claude API キー取得

1. https://console.anthropic.com/ にアクセス
2. API Keys → Create API Key
3. キーをコピー

### 9.2 Railway に Claude API キーを設定

```bash
# Railway ダッシュボール → Variables
# KEY: ANTHROPIC_API_KEY
# VALUE: sk-ant-xxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

### 9.3 バックエンド自動再デプロイ

Railway は環境変数の変更を自動検出:
- 数分以内に再デプロイが開始
- AI 機能が有効化

### 9.4 AI 機能テスト

```bash
# AI Assessment 生成テスト
curl -X POST https://api.example.com/api/v1/tenants/YOUR_TENANT_ID/ai/assessments \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "Digital Transformation",
    "industry": "Manufacturing",
    "num_questions": 3
  }'

# 期待: 200 OK + 生成されたアセスメント JSON
```

---

## 📊 ステップ 10: モニタリング設定

### 10.1 Sentry エラー追跡 (オプション)

```bash
# Sentry アカウント作成: https://sentry.io/
# Python プロジェクトを作成
# DSN を取得

# Railway ダッシュボール → Variables
# KEY: SENTRY_DSN
# VALUE: https://xxxxx@sentry.io/xxxxx
```

### 10.2 Railway ログ監視

```bash
# CLI でログ確認
railway logs --tail 100

# または Railway ダッシュボール → Logs
```

### 10.3 パフォーマンス監視

```bash
# 定期的にヘルスチェック
watch -n 60 'curl -s https://api.example.com/health | jq'

# または Uptime Robot などの監視サービスを使用
```

---

## 🔧 トラブルシューティング

### 問題 1: ログイン 500 エラー

**原因**: DATABASE_URL が正しくない

**解決策**:
```bash
# 1. Railway ダッシュボール → Variables
# 2. DATABASE_URL を確認
# 3. 形式を確認: postgresql://user:pass@host:port/db
# 4. バックエンド再デプロイ
railway redeploy
```

### 問題 2: CORS エラー

**原因**: ALLOWED_ORIGINS が設定されていない

**解決策**:
```bash
# Railway ダッシュボール → Variables
ALLOWED_ORIGINS=["https://app.example.com", "https://diagnoleads.example.com"]

# バックエンド再デプロイ
railway redeploy
```

### 問題 3: AI Assessment 500 エラー

**原因**: ANTHROPIC_API_KEY が無効または設定されていない

**解決策**:
```bash
# オプション1: Claude API キーを再確認
# https://console.anthropic.com/account/billing/overview

# オプション2: AI 機能を一時的にスキップ
# (API キーなしでも他の機能は動作)
```

### 問題 4: デプロイが失敗

**確認手順**:
```bash
# 1. ビルドログを確認
railway logs

# 2. requirements.txt が存在するか確認
ls -la backend/requirements.txt

# 3. Python バージョン確認 (3.11 以上)
python --version

# 4. マニュアル再デプロイ
railway redeploy
```

---

## 📞 ロールバック

何か問題が発生した場合:

### ロールバック方法 1: 前のコミットに戻す

```bash
# 前のコミットを確認
git log --oneline -5

# 前のコミットに戻す
git revert HEAD
git push origin main

# Railway が自動的に前のバージョンをデプロイ
```

### ロールバック方法 2: Railway ダッシュボールから戻す

```bash
# Railway ダッシュボール → Deployments
# → 前の成功したデプロイを選択
# → Redeploy
```

---

## ✨ デプロイ完了！

確認項目:

- [x] ヘルスチェック: 200 OK
- [x] ログイン: 成功
- [x] マルチテナント分離: 403 確認
- [x] ドメイン: 正常に稼働
- [x] ログ: エラーなし

**本番環境は稼働中です。** 🎉

---

## 📚 次のステップ

### 短期 (1 週間)

- [ ] E2E テスト実施 (実ユーザーでテスト)
- [ ] パフォーマンス監視開始
- [ ] バックアップ自動化確認
- [ ] エラー監視 (Sentry) 設定

### 中期 (1 ヶ月)

- [ ] 外部連携実装 (Salesforce/HubSpot)
- [ ] ユーザー オンボーディング実施
- [ ] 営業・マーケティングチームへの展開

### 長期 (3 ヶ月)

- [ ] モバイルアプリ開発検討
- [ ] 高度な分析機能追加
- [ ] スケーリング計画実行

---

## 📝 参考資料

- Railway ドキュメント: https://docs.railway.app/
- Vercel ドキュメント: https://vercel.com/docs
- FastAPI ドキュメント: https://fastapi.tiangolo.com/
- PostgreSQL ドキュメント: https://www.postgresql.org/docs/

---

**作成日**: 2025-11-12  
**対象バージョン**: DiagnoLeads v0.1.0  
**ステータス**: 本番環境対応

