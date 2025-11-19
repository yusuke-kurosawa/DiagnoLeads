# CI/CD エラー自動改修システム - 使い方ガイド

## 概要

このガイドでは、CI/CDパイプラインのエラーを自動的に検出・解析・修正するシステムの使い方を説明します。

## 🎯 3つのアプローチ

### 1. PR自動コメント（最も簡単）

**仕組み**: CI/CDが失敗すると、エラー詳細が自動的にPRにコメントされます。

**使い方**:
1. PRを作成または更新
2. CI/CDが失敗したら、PRのコメント欄を確認
3. エラー詳細がコメントとして投稿される
4. Claude Codeでコメントを読んで修正

**メリット**:
- ✅ 完全自動
- ✅ 手動操作不要
- ✅ チーム全員が見られる

**例**:
```markdown
## 🔴 CI/CD Failed - Error Analysis

**Workflow Run**: #1234567890
**Commit**: abc123
**Branch**: feature/add-new-feature

---

### 🐍 Backend Errors

<details>
<summary>📝 Pytest Errors (click to expand)</summary>

[エラー詳細]
</details>
```

### 2. ローカル解析スクリプト（最も柔軟）

**仕組み**: CLIツールでエラーログをダウンロードし、Claude Codeで解析します。

**セットアップ（2つの方法）**:

#### 方法A: 自動セットアップスクリプト（推奨）
```bash
# セットアップヘルパーを実行
./scripts/setup-cicd-tools.sh

# 環境チェック、インストールガイド、認証を自動実行
```

#### 方法B: GitHub CLIを手動インストール
```bash
# macOS
brew install gh

# Windows
winget install --id GitHub.cli

# Linux
sudo apt install gh

# 認証
gh auth login
```

#### 方法C: Python版を使用（GitHub CLI不要）
```bash
# Python 3.7+があればOK
python3 scripts/analyze-cicd-errors.py

# GitHub Token設定（レート制限回避）
export GITHUB_TOKEN=your_token_here
# トークン作成: https://github.com/settings/tokens
```

**使い方**:

```bash
# 方法1: Bash版（GitHub CLI使用）
./scripts/analyze-cicd-errors.sh              # 最新の失敗したrun
./scripts/analyze-cicd-errors.sh 1234567890   # 特定のrun ID

# 方法2: Python版（GitHub CLI不要）
python3 scripts/analyze-cicd-errors.py        # 最新の失敗したrun
python3 scripts/analyze-cicd-errors.py 1234567890  # 特定のrun ID

# どちらの方法でもレポートが生成される
# cicd-errors/1234567890/ERROR_ANALYSIS_REPORT.md
```

**Claude Codeで修正**:
```bash
# スラッシュコマンドを使用
/fix-cicd

# または、レポートを直接読む
cat cicd-errors/1234567890/ERROR_ANALYSIS_REPORT.md
```

**メリット**:
- ✅ 完全にローカルで制御
- ✅ Claude Codeで柔軟に対応
- ✅ オンデマンド実行
- ✅ **Python版はGitHub CLI不要**（標準ライブラリのみ）
- ✅ クロスプラットフォーム（macOS/Linux/Windows）

### 3. 自動修正（最も自動化）

**仕組み**: CI/CDが失敗すると、既知のエラー（linter）を自動的に修正します。

**対応エラー**:
- ✅ Ruff linter errors (`ruff check --fix`)
- ✅ Ruff formatter errors (`ruff format`)
- ✅ ESLint errors (`eslint --fix`)

**使い方**:
1. PRを作成または更新
2. CI/CDが失敗
3. 自動修正ワークフローが起動
4. 修正可能なエラーがあれば自動的に修正してコミット
5. CI/CDが再実行される

**メリット**:
- ✅ 完全自動
- ✅ 既知のエラーは即座に修正
- ✅ 人間の介入不要

**デメリット**:
- ⚠️ 複雑なエラーには対応不可
- ⚠️ linterエラーのみ対応

## 📋 典型的なワークフロー

### シナリオ1: PRのlinterエラー

1. PRを作成
2. CI/CDが失敗（linterエラー）
3. **自動修正ワークフローが起動** ← 自動
4. エラーが修正されてコミット ← 自動
5. CI/CDが再実行 ← 自動
6. ✅ テスト成功！

**あなたの作業**: なし（完全自動）

### シナリオ2: PRのテスト失敗

1. PRを作成
2. CI/CDが失敗（テスト失敗）
3. **PR自動コメント**にエラー詳細が投稿される ← 自動
4. Claude Codeでコメントを読む
5. テストを修正
6. コミット＆プッシュ
7. ✅ テスト成功！

**あなたの作業**: エラーを読んで修正

### シナリオ3: CI/CDが失敗（ローカルで調査）

1. CI/CDが失敗
2. ローカルで調査したい
3. **エラー解析スクリプトを実行**:
   ```bash
   ./scripts/analyze-cicd-errors.sh
   ```
4. レポートを確認:
   ```bash
   cat cicd-errors/<run-id>/ERROR_ANALYSIS_REPORT.md
   ```
5. Claude Codeで修正:
   ```bash
   /fix-cicd
   ```
6. コミット＆プッシュ
7. ✅ テスト成功！

**あなたの作業**: スクリプト実行 + 修正

## 🛠️ エラータイプ別の対処法

### Linterエラー

**自動修正**: ✅ 対応済み

```bash
# Backend
cd backend
ruff check --fix .
ruff format .

# Frontend
cd frontend
npm run lint -- --fix
```

### 型エラー

**自動修正**: ❌ Claude Code推奨

**修正方法**:
1. PR自動コメントまたはローカル解析でエラー確認
2. Claude Codeで型を追加/修正
3. 検証:
   ```bash
   # Backend
   cd backend
   mypy app/

   # Frontend
   cd frontend
   npx tsc --noEmit
   ```

### テスト失敗

**自動修正**: ❌ Claude Code推奨

**修正方法**:
1. エラーログから失敗したテストを特定
2. Claude Codeでテストまたはコードを修正
3. ローカルで実行:
   ```bash
   # Backend
   cd backend
   pytest tests/test_specific.py -v

   # Frontend
   cd frontend
   npm test
   ```

### ビルドエラー

**自動修正**: ❌ Claude Code推奨

**修正方法**:
1. エラーログからビルドエラーを特定
2. Claude Codeで依存関係やコードを修正
3. ローカルで実行:
   ```bash
   # Backend
   cd backend
   pip install -r requirements.txt

   # Frontend
   cd frontend
   npm install
   npm run build
   ```

## 📊 エラー解析レポートの見方

### レポート構成

```markdown
# CI/CD Error Analysis Report

**Run ID**: 1234567890
**Branch**: feature/xxx
**Commit**: abc123
**Status**: failure

---

## Error Summary

### 🐍 Backend Errors

#### Pytest Errors
[テスト失敗の詳細]

#### Ruff Linter Errors
[linterエラーの詳細]

#### MyPy Type Errors
[型エラーの詳細]

### ⚛️ Frontend Errors

#### ESLint Errors
[linterエラーの詳細]

#### TypeScript Errors
[型エラーの詳細]

#### Build Errors
[ビルドエラーの詳細]

---

## 🤖 Instructions for Claude Code
[Claude Codeへの指示]
```

### 読み方のコツ

1. **Error Summaryから開始**
   - どのステップで失敗したかを確認

2. **エラーログを上から順に読む**
   - 最初のエラーが根本原因のことが多い

3. **ファイルパスと行番号を確認**
   - エラー箇所を特定

4. **Claude Codeに渡す**
   - `/fix-cicd` コマンドまたは直接コピペ

## 🔍 トラブルシューティング

### エラーログがダウンロードできない

**原因1**: GitHub CLIが認証されていない

**解決策**:
```bash
gh auth login
```

**原因2**: GitHub CLIがインストールされていない

**解決策**:
```bash
# セットアップスクリプトを実行
./scripts/setup-cicd-tools.sh

# または、Python版を使用（GitHub CLI不要）
python3 scripts/analyze-cicd-errors.py
```

**原因3**: Python版でGitHub APIレート制限

**解決策**:
```bash
# GitHub Tokenを設定
export GITHUB_TOKEN=your_token_here

# トークン作成: https://github.com/settings/tokens
# 必要な権限: repo, workflow
```

### 自動修正が動かない

**原因1**: mainブランチへのPR
**解決策**: 自動修正はfeatureブランチのみ対応

**原因2**: 権限不足
**解決策**: リポジトリ設定で Actions に write 権限を付与

### PR自動コメントが投稿されない

**原因**: workflow_run権限不足
**解決策**: リポジトリ設定で Actions に pull-requests write 権限を付与

## 📈 ベストプラクティス

### 1. 小さなPRを作る
- エラーが少なく、修正が簡単

### 2. ローカルでテストしてからプッシュ
```bash
# Backend
cd backend
pytest tests/ -v

# Frontend
cd frontend
npm test
```

### 3. エラーログを全部読む
- 最初のエラーだけでなく、関連エラーも確認

### 4. 自動修正を信頼しすぎない
- 自動修正後も必ず確認

### 5. Claude Codeを活用
- `/fix-cicd` コマンドで効率的に修正

## 🎓 よくある質問

### Q: 自動修正が間違った修正をした場合は？

A: `git revert` で修正を取り消し、手動で修正してください:
```bash
git revert HEAD
```

### Q: 複数のエラーがある場合、どの順番で修正すべき？

A: 以下の順番を推奨:
1. Linterエラー（自動修正可能）
2. 型エラー
3. テスト失敗
4. ビルドエラー

### Q: エラーログが大きすぎて読めない

A: レポートは最新200行のみ表示します。全ログはアーティファクトからダウンロードできます。

### Q: ローカルで再現しないエラーがある

A: CI環境固有の問題の可能性があります。以下を確認:
- Python/Nodeバージョン
- 依存関係のバージョン
- 環境変数

## 📚 関連ドキュメント

- [CI/CD Error Auto-fix System Design](./cicd-error-auto-fix-system.md)
- [CICD Error Analysis Investigation](../CICD_ERROR_ANALYSIS_INVESTIGATION.md)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)

## 🤝 サポート

問題が解決しない場合:
1. [GitHub Issues](https://github.com/yusuke-kurosawa/DiagnoLeads/issues) で報告
2. Claude Code に質問
3. チームメンバーに相談
