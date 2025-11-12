# Next Session Quickstart Guide

**次回セッション開始時のクイックスタートガイド**

このドキュメントは、次回のセッション開始時に素早く状況を把握し、作業を開始するためのガイドです。

---

## 📍 現在の状況（一目でわかる）

### ✅ 完了済み
- 革新的機能提案（12機能）
- Phase 1実装計画（12週間）
- GitHub Project Setup（5 Milestones, 12 Issues）
- Teams統合プロトタイプ
- 全ドキュメント作成

### 🎯 次のタスク
**Issue #1**: Azure AD & Bot Framework初期セットアップ
- 所要時間: 1-2時間
- 優先度: Critical

---

## 🚀 3分で状況確認

### 1. 最新コミット確認
```bash
cd /path/to/DiagnoLeads
git log --oneline -5
```

**期待される出力**:
```
8c9a0f5 docs: Add comprehensive session summary
80871e3 feat: Add Phase 1 GitHub project setup and Teams integration prototype
4b9e422 docs: Add Phase 1 implementation plan and Teams setup guide
7b84d24 spec: Add innovative features proposal and detailed specs
...
```

### 2. GitHub Issues確認
```bash
gh issue list --limit 5
```

または: https://github.com/yusuke-kurosawa/DiagnoLeads/issues

**確認ポイント**:
- Issue #1-12 がすべて作成されている ✅
- Issue #1 が "OPEN" 状態

### 3. ドキュメント確認
重要なドキュメント3つ：
1. [SESSION_SUMMARY.md](./SESSION_SUMMARY.md) - 前回セッションの完全な記録
2. [IMPLEMENTATION_PLAN_PHASE1.md](./IMPLEMENTATION_PLAN_PHASE1.md) - 12週間の実装計画
3. [SETUP_GUIDE_TEAMS.md](./SETUP_GUIDE_TEAMS.md) - Teams統合手順

---

## 🎬 今すぐ開始できるタスク

### Option A: Azure AD & Bot Framework Setup（推奨）

**所要時間**: 1-2時間  
**難易度**: Easy  
**必要なもの**: Microsoftアカウント（無料）

#### ステップ
1. **Azure Portalにアクセス**
   - https://portal.azure.com/
   - Microsoftアカウントでログイン（無料アカウント作成可）

2. **App Registration作成**
   - [詳細手順](./SETUP_GUIDE_TEAMS.md#part-1-azure-ad-app-registration)に従う
   - Client ID/Secretを取得
   - 権限設定（4つ）

3. **Bot Framework App作成**
   - [詳細手順](./SETUP_GUIDE_TEAMS.md#part-2-bot-framework-app-registration)
   - Bot App ID/Passwordを取得
   - Messaging endpoint設定

4. **環境変数設定**
   ```bash
   cd backend
   cp .env.example .env
   # .envに以下を追加:
   # MICROSOFT_CLIENT_ID=<your-client-id>
   # MICROSOFT_CLIENT_SECRET=<your-client-secret>
   # MICROSOFT_TENANT_ID=<your-tenant-id>
   # BOT_APP_ID=<your-bot-app-id>
   # BOT_APP_PASSWORD=<your-bot-password>
   ```

5. **Issue #1をクローズ**
   ```bash
   gh issue close 1 --comment "Azure AD & Bot Framework setup completed"
   ```

---

### Option B: Issue #2実装開始

**前提条件**: Azure AD登録完了（Option A）  
**所要時間**: 1週間  
**難易度**: Medium

#### ステップ
1. **依存関係インストール**
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

2. **`teams_client.py`本実装**
   - プロトタイプのコメント解除
   - msal、msgraph-sdk統合
   - 認証フロー実装

3. **データベーススキーマ作成**
   ```bash
   # Alembicマイグレーション作成
   alembic revision --autogenerate -m "Add teams_integrations table"
   alembic upgrade head
   ```

4. **API endpoints実装**
   - POST /api/v1/integrations/teams/install
   - GET /api/v1/integrations/teams
   - DELETE /api/v1/integrations/teams/{id}

5. **ユニットテスト作成**
   ```bash
   pytest backend/tests/test_teams_integration.py -v --cov
   ```

---

### Option C: プロトタイプテスト

**所要時間**: 10分  
**難易度**: Easy  
**用途**: 現在の実装を理解する

```bash
cd backend
python3 app/integrations/microsoft/teams_client.py
```

**期待される出力**:
```
============================================================
Microsoft Teams Integration - Technical Spike Prototype
============================================================
✅ Authentication successful
✅ Found 2 teams
✅ Found 2 channels
✅ Notification sent
🎉 Prototype Test Completed Successfully!
```

---

## 📋 チェックリスト（次回セッション開始時）

### 環境確認（5分）
- [ ] gitリポジトリが最新（`git pull`）
- [ ] 依存関係が最新（`pip install -r requirements.txt`）
- [ ] Dockerが起動している（`docker-compose ps`）
- [ ] GitHub CLIが認証済み（`gh auth status`）

### ドキュメント確認（5分）
- [ ] [SESSION_SUMMARY.md](./SESSION_SUMMARY.md)を読む
- [ ] [GitHub Issues](https://github.com/yusuke-kurosawa/DiagnoLeads/issues)を確認
- [ ] 現在のMilestone進捗を確認

### タスク選択（1分）
- [ ] Option A, B, Cから選択
- [ ] Issue を "In Progress" にする

---

## 🆘 トラブルシューティング

### Azure AD登録でエラー
**問題**: "Insufficient privileges"  
**解決**: 管理者アカウントでログイン、または管理者に権限リクエスト

### Bot Webhookが動作しない
**問題**: Bot がメッセージを受信しない  
**解決**: 
1. ngrokが起動しているか確認
2. Messaging endpointが正しいか確認（`https://xxxx.ngrok.io/api/v1/integrations/teams/bot/webhook`）

### 依存関係インストールエラー
**問題**: `pip install`でエラー  
**解決**:
```bash
# 仮想環境を再作成
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

---

## 📞 重要な連絡先・リンク

### GitHub
- **Repository**: https://github.com/yusuke-kurosawa/DiagnoLeads
- **Issues**: https://github.com/yusuke-kurosawa/DiagnoLeads/issues
- **Milestones**: https://github.com/yusuke-kurosawa/DiagnoLeads/milestones

### Azure
- **Portal**: https://portal.azure.com/
- **Bot Framework Portal**: https://dev.botframework.com/

### Documentation
- **Microsoft Graph**: https://learn.microsoft.com/graph/
- **Bot Framework**: https://dev.botframework.com/
- **Adaptive Cards**: https://adaptivecards.io/

---

## 💡 開発のヒント

### VS Code推奨拡張機能
- Python
- Pylance
- GitLens
- GitHub Pull Requests
- Azure Account
- REST Client

### デバッグ時の便利コマンド
```bash
# ログ確認
docker-compose logs -f backend

# データベース接続確認
docker-compose exec postgres psql -U postgres

# Redis接続確認
docker-compose exec redis redis-cli ping

# APIテスト
curl -X GET http://localhost:8000/api/v1/health
```

---

## 🎯 Phase 1 進捗確認

現在の進捗を確認:
```bash
gh issue list --milestone "Milestone 1: Teams統合基盤 (Week 1-3)"
```

または: https://github.com/yusuke-kurosawa/DiagnoLeads/milestone/1

---

## 📅 次回セッションの推奨フロー

### 最初の10分
1. このドキュメントを読む
2. 環境確認チェックリストを実行
3. GitHub Issuesを確認

### 次の30分
4. Option A（Azure AD Setup）を開始

### 残りの時間
5. Issue #2実装開始
6. または他のMilestoneタスクを選択

---

**Ready to start? Let's build something amazing! 🚀**

---

**Document Version**: 1.0  
**Created**: 2025-11-11  
**For**: Phase 1 Implementation
