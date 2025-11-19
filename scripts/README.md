# Scripts

このディレクトリには、DiagnoLeadsプロジェクトで使用するユーティリティスクリプトが含まれています。

## 利用可能なスクリプト

### 1. GitHub Actionsワークフローキャンセルツール

実行中およびキューイング中のGitHub Actionsワークフローを一括でキャンセルするツールです。

**ファイル:**
- `cancel_workflows.sh` - シェルスクリプト版（推奨）
- `cancel_workflows.py` - Python版
- `CANCEL_WORKFLOWS_README.md` - 詳細なドキュメント

**クイックスタート:**

```bash
# GitHub tokenを設定
export GITHUB_TOKEN=your_github_token_here

# 実行
./scripts/cancel_workflows.sh --all
```

詳細は [CANCEL_WORKFLOWS_README.md](./CANCEL_WORKFLOWS_README.md) を参照してください。

### 2. CI/CDエラー解析ツール

GitHub Actionsの失敗したワークフローからエラーログをダウンロードし、解析レポートを生成します。

**ファイル:**
- `setup-cicd-tools.sh` - セットアップヘルパー（推奨：初回実行）
- `analyze-cicd-errors.sh` - Bash版（GitHub CLI使用）
- `analyze-cicd-errors.py` - Python版（**GitHub CLI不要**）

**クイックスタート:**

```bash
# 1. セットアップ（初回のみ）
./scripts/setup-cicd-tools.sh

# 2. エラー解析
# 方法A: Bash版（GitHub CLI使用）
./scripts/analyze-cicd-errors.sh

# 方法B: Python版（GitHub CLI不要）
python3 scripts/analyze-cicd-errors.py

# 3. Claude Codeで修正
/fix-cicd
```

**特徴:**
- ✅ 2つの実装（Bash版/Python版）から選択可能
- ✅ Python版は**GitHub CLI不要**（標準ライブラリのみ）
- ✅ 自動セットアップガイド
- ✅ Claude Code統合（`/fix-cicd`コマンド）
- ✅ 詳細なMarkdownレポート生成

**Python版の利点:**
- GitHub CLIのインストール不要
- クロスプラットフォーム対応
- CI/CD環境でも使用可能

**必要な環境:**
- Bash版: GitHub CLI (`gh`) + 認証
- Python版: Python 3.7+ + GITHUB_TOKEN（推奨）

詳細は [cicd-error-auto-fix-usage.md](../docs/cicd-error-auto-fix-usage.md) を参照してください。

### 3. ER図生成ツール

データベースのER図を自動生成するツールです。

**ファイル:**
- `generate_er_diagram.py` - ER図生成スクリプト

**使用方法:**

```bash
python3 scripts/generate_er_diagram.py
```

## スクリプトの追加

新しいユーティリティスクリプトを追加する場合:

1. このディレクトリにスクリプトファイルを配置
2. 実行可能な場合は実行権限を付与: `chmod +x script_name.sh`
3. このREADMEに説明を追加
4. 必要に応じて個別のドキュメントを作成

## 注意事項

- すべてのスクリプトはプロジェクトルートから実行することを想定しています
- 環境変数やシークレットは絶対にコミットしないでください
- `.env.example` を参考に必要な環境変数を設定してください
