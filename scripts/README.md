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

### 2. ER図生成ツール

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
