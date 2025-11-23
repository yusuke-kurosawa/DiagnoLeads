# GitHub ブランチ保護ルール設定ガイド

mainブランチへの直接pushを防止し、PRベースの開発フローを強制するため、ブランチ保護ルールを設定してください。

## 設定手順

### 1. リポジトリ設定にアクセス

https://github.com/yusuke-kurosawa/DiagnoLeads/settings/branches

### 2. ブランチ保護ルールを追加

**"Add branch protection rule"** をクリック

### 3. 設定内容

#### Branch name pattern
```
main
```

#### 必須設定（チェックを入れる）

##### ✅ Require a pull request before merging
- **Require approvals**: 1
- **Dismiss stale pull request approvals when new commits are pushed**: チェック
- **Require review from Code Owners**: チェック（オプション）

##### ✅ Require status checks to pass before merging
- **Require branches to be up to date before merging**: チェック

必須ステータスチェック（以下を検索して追加）:
- `validate-schema` (Database Integrity Check)
- `backend-test` (Backend CI)
- `frontend-test` (Frontend CI)
- `lint` (Backend Lint)
- `lint` (Frontend Lint)

##### ✅ Require conversation resolution before merging
すべてのコメントが解決されていることを必須にする

##### ✅ Require linear history
マージコミットを防止し、Squash and Mergeを推奨

##### ✅ Do not allow bypassing the above settings
管理者も含めてルールを適用

#### オプション設定

##### 🔒 Restrict who can push to matching branches
特定のユーザー/チームのみpush可能にする（小規模チームでは不要）

##### 🔄 Require deployments to succeed before merging
デプロイ環境がある場合に設定

### 4. ルールを保存

**"Create"** または **"Save changes"** をクリック

---

## 設定後の動作

### ✅ 許可される操作
- フィーチャーブランチの作成と push
- PRの作成
- レビュー承認後のマージ（Squash and Merge推奨）

### ❌ 禁止される操作
- mainブランチへの直接 push
- PRなしでのマージ
- CI/CDチェック失敗時のマージ
- レビュー承認なしのマージ
- コメント未解決でのマージ

---

## 推奨: CODEOWNERS ファイルの作成

特定のファイルやディレクトリの変更に対して、自動的にレビュワーを指定できます。

### `.github/CODEOWNERS` ファイルを作成

```bash
# データベース関連
backend/app/models/** @yusuke-kurosawa
backend/alembic/versions/** @yusuke-kurosawa
openspec/specs/database/** @yusuke-kurosawa

# CI/CD
.github/workflows/** @yusuke-kurosawa

# OpenSpec仕様
openspec/specs/** @yusuke-kurosawa

# セキュリティ関連
backend/app/core/security.py @yusuke-kurosawa
backend/app/core/auth.py @yusuke-kurosawa

# 設定ファイル
*.yml @yusuke-kurosawa
*.yaml @yusuke-kurosawa
docker-compose*.yml @yusuke-kurosawa
```

---

## トラブルシューティング

### CI/CDチェックが表示されない場合

1. PRを作成してGitHub Actionsが実行されるのを待つ
2. 実行後、ブランチ保護ルールの設定画面で検索可能になる
3. 再度ステータスチェックを追加

### 緊急時のバイパス

本番障害などの緊急時は、管理者が一時的にルールを無効化できます：
1. Settings > Branches
2. 該当ルールの **Edit** をクリック
3. 一時的に **"Do not allow bypassing"** のチェックを外す
4. 対応完了後、再度チェックを入れる

---

## 参考資料

- [GitHub Branch Protection Rules](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/managing-a-branch-protection-rule)
- [About CODEOWNERS](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-code-owners)
