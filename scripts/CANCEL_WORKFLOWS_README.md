# GitHub Actions ワークフローキャンセルツール

実行中およびキューイング中のGitHub Actionsワークフローを一括でキャンセルするためのツールです。

## 使用方法

### 方法1: シェルスクリプト（推奨）

```bash
# 1. GitHub Personal Access Token (PAT)を作成
# https://github.com/settings/tokens
# 必要な権限: repo, workflow

# 2. 環境変数に設定
export GITHUB_TOKEN=your_github_token_here

# 3. スクリプトを実行
./scripts/cancel_workflows.sh

# または、確認をスキップして全てキャンセル
./scripts/cancel_workflows.sh --all
```

### 方法2: Pythonスクリプト

```bash
# 1. GitHub tokenを環境変数に設定（上記と同じ）
export GITHUB_TOKEN=your_github_token_here

# 2. Pythonスクリプトを実行
python3 scripts/cancel_workflows.py --all
```

### 方法3: GitHub Actions ワークフロー

このブランチをメインブランチにマージした後：

1. GitHubリポジトリの「Actions」タブに移動
2. 「Cancel Old Pipelines」ワークフローを選択
3. 「Run workflow」ボタンをクリック
4. ブランチを選択して実行

### 方法4: 手動でキャンセル（GitHub UI）

1. https://github.com/yusuke-kurosawa/DiagnoLeads/actions にアクセス
2. 実行中のワークフローをクリック
3. 右上の「Cancel workflow」ボタンをクリック
4. 必要に応じて他のワークフローも同様に操作

## 現在実行中のワークフロー

WebFetchの結果によると、以下のワークフローが実行中です：

- **Backend CI #84** - PR #27, Branch: `claude/fix-cicd-pipeline-01E8JuqKPRyuu4fwpsj9kkHf`
- **Frontend CI #89, #88, #87, #86, #84, #83, #82, #81** - PR #27
- **CI/CD Pipeline #160** - PR #27

これらは別のブランチで実行中のため、不要であればキャンセルすることをお勧めします。

## トラブルシューティング

### `GITHUB_TOKEN`が見つからない

```
エラー: GITHUB_TOKEN 環境変数が設定されていません
```

→ 上記の手順に従ってGitHub PATを作成し、環境変数に設定してください。

### `jq`コマンドが見つからない（シェルスクリプト使用時）

```bash
# Ubuntu/Debian
sudo apt-get install jq

# macOS
brew install jq
```

### `yaml`モジュールが見つからない（Pythonスクリプト使用時）

```bash
pip install pyyaml
```

## セキュリティに関する注意

- GitHub tokenは絶対に公開リポジトリにコミットしないでください
- tokenは必要最小限の権限のみを付与してください
- 使用後はtokenを削除または無効化することを推奨します
