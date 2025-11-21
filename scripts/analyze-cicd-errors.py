#!/usr/bin/env python3
"""
CI/CD Error Analysis Script (Python版)

GitHub CLIなしで動作するバージョン。
GitHub APIを直接使用してエラーログをダウンロード・分析します。

Requirements:
    - Python 3.7+
    - requests (pip install requests)
    - GITHUB_TOKEN環境変数（推奨）またはgit認証情報

Usage:
    # 最新の失敗したrunを解析
    python scripts/analyze-cicd-errors.py

    # 特定のrun IDを解析
    python scripts/analyze-cicd-errors.py 1234567890

    # GitHub Token指定
    GITHUB_TOKEN=your_token python scripts/analyze-cicd-errors.py
"""

import os
import sys
import json
import subprocess
import zipfile
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any, List
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

# カラー出力
class Colors:
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    NC = '\033[0m'  # No Color

def print_color(text: str, color: str) -> None:
    """カラーテキストを出力"""
    print(f"{color}{text}{Colors.NC}")

def get_github_token() -> Optional[str]:
    """GitHub Tokenを取得（環境変数またはgit config）"""
    # 環境変数から取得
    token = os.environ.get('GITHUB_TOKEN')
    if token:
        return token

    # git configから取得を試みる
    try:
        result = subprocess.run(
            ['git', 'config', '--get', 'github.token'],
            capture_output=True,
            text=True,
            check=False
        )
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout.strip()
    except Exception:
        pass

    return None

def get_repo_info() -> tuple[str, str]:
    """リポジトリのowner/nameを取得"""
    try:
        result = subprocess.run(
            ['git', 'config', '--get', 'remote.origin.url'],
            capture_output=True,
            text=True,
            check=True
        )
        url = result.stdout.strip()

        # https://github.com/owner/repo.git または git@github.com:owner/repo.git
        if 'github.com' in url:
            # .git を削除
            url = url.replace('.git', '')
            # owner/repo 部分を抽出
            if url.startswith('https://'):
                parts = url.split('github.com/')[-1]
            elif url.startswith('git@'):
                parts = url.split('github.com:')[-1]
            else:
                raise ValueError("Unknown URL format")

            owner, repo = parts.split('/')
            return owner, repo
        else:
            raise ValueError("Not a GitHub repository")

    except Exception as e:
        print_color(f"Error: Failed to get repository info: {e}", Colors.RED)
        print_color("Make sure you're in a git repository directory", Colors.YELLOW)
        sys.exit(1)

def github_api_request(
    endpoint: str,
    token: Optional[str] = None,
    method: str = 'GET'
) -> Any:
    """GitHub APIリクエストを実行"""
    url = f"https://api.github.com{endpoint}"

    headers = {
        'Accept': 'application/vnd.github+json',
        'X-GitHub-Api-Version': '2022-11-28'
    }

    if token:
        headers['Authorization'] = f'Bearer {token}'

    try:
        req = Request(url, headers=headers, method=method)
        with urlopen(req) as response:
            if response.status == 200:
                return json.loads(response.read().decode())
            else:
                raise HTTPError(url, response.status, 'API request failed', headers, None)

    except HTTPError as e:
        if e.code == 401:
            print_color("Error: Unauthorized. Please set GITHUB_TOKEN environment variable", Colors.RED)
            print_color("Create a token at: https://github.com/settings/tokens", Colors.YELLOW)
        elif e.code == 404:
            print_color(f"Error: Resource not found (404): {endpoint}", Colors.RED)
        else:
            print_color(f"Error: GitHub API request failed: {e.code} {e.reason}", Colors.RED)
        sys.exit(1)

    except URLError as e:
        print_color(f"Error: Network error: {e.reason}", Colors.RED)
        sys.exit(1)

def get_latest_failed_run(owner: str, repo: str, token: Optional[str]) -> Optional[Dict[str, Any]]:
    """最新の失敗したworkflow runを取得"""
    endpoint = f"/repos/{owner}/{repo}/actions/runs?status=failure&per_page=1"

    try:
        data = github_api_request(endpoint, token)
        runs = data.get('workflow_runs', [])

        # "CI/CD Pipeline" ワークフローのみフィルタ
        for run in runs:
            if 'CI/CD Pipeline' in run.get('name', ''):
                return run

        # なければ最初のfailed runを返す
        return runs[0] if runs else None

    except Exception as e:
        print_color(f"Error: Failed to get workflow runs: {e}", Colors.RED)
        return None

def get_run_details(owner: str, repo: str, run_id: str, token: Optional[str]) -> Dict[str, Any]:
    """Workflow runの詳細を取得"""
    endpoint = f"/repos/{owner}/{repo}/actions/runs/{run_id}"
    return github_api_request(endpoint, token)

def list_artifacts(owner: str, repo: str, run_id: str, token: Optional[str]) -> List[Dict[str, Any]]:
    """Workflow runのartifactsを取得"""
    endpoint = f"/repos/{owner}/{repo}/actions/runs/{run_id}/artifacts"
    data = github_api_request(endpoint, token)
    return data.get('artifacts', [])

def download_artifact(
    owner: str,
    repo: str,
    artifact_id: str,
    output_path: Path,
    token: Optional[str]
) -> bool:
    """Artifactをダウンロード"""
    endpoint = f"/repos/{owner}/{repo}/actions/artifacts/{artifact_id}/zip"
    url = f"https://api.github.com{endpoint}"

    headers = {
        'Accept': 'application/vnd.github+json',
        'X-GitHub-Api-Version': '2022-11-28'
    }

    if token:
        headers['Authorization'] = f'Bearer {token}'

    try:
        req = Request(url, headers=headers)
        with urlopen(req) as response:
            # ZIPファイルを保存
            zip_path = output_path.with_suffix('.zip')
            zip_path.write_bytes(response.read())

            # ZIPを解凍
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(output_path)

            # ZIPファイルを削除
            zip_path.unlink()

            return True

    except Exception as e:
        print_color(f"Warning: Failed to download artifact {artifact_id}: {e}", Colors.YELLOW)
        return False

def create_analysis_report(
    output_dir: Path,
    run_info: Dict[str, Any],
    backend_dir: Optional[Path],
    frontend_dir: Optional[Path]
) -> Path:
    """解析レポートを生成"""
    report_file = output_dir / "ERROR_ANALYSIS_REPORT.md"

    with open(report_file, 'w', encoding='utf-8') as f:
        # ヘッダー
        f.write("# CI/CD Error Analysis Report\n\n")
        f.write(f"**Run ID**: {run_info['id']}\n")
        f.write(f"**Branch**: {run_info['head_branch']}\n")
        f.write(f"**Commit**: {run_info['head_sha'][:8]}\n")
        f.write(f"**Status**: {run_info['conclusion']}\n")
        f.write(f"**Created**: {run_info['created_at']}\n")
        f.write(f"**URL**: [{run_info['html_url']}]({run_info['html_url']})\n\n")
        f.write("---\n\n")
        f.write("## Error Summary\n\n")

        # Backend errors
        if backend_dir and backend_dir.exists():
            f.write("## 🐍 Backend Errors\n\n")

            # Pytest errors
            pytest_log = backend_dir / "pytest-errors.log"
            if pytest_log.exists():
                f.write("### Pytest Errors\n\n")
                f.write("```python\n")
                content = pytest_log.read_text(encoding='utf-8', errors='ignore')
                # 最新200行のみ
                lines = content.splitlines()
                f.write('\n'.join(lines[-200:]))
                f.write("\n```\n\n")

            # Ruff errors
            ruff_log = backend_dir / "ruff-errors.log"
            if ruff_log.exists():
                f.write("### Ruff Linter Errors\n\n")
                f.write("```\n")
                f.write(ruff_log.read_text(encoding='utf-8', errors='ignore'))
                f.write("```\n\n")

            # MyPy errors
            mypy_log = backend_dir / "mypy-errors.log"
            if mypy_log.exists():
                f.write("### MyPy Type Errors\n\n")
                f.write("```\n")
                f.write(mypy_log.read_text(encoding='utf-8', errors='ignore'))
                f.write("```\n\n")

            # Metadata
            metadata = backend_dir / "metadata.txt"
            if metadata.exists():
                f.write("### Metadata\n\n")
                f.write("```\n")
                f.write(metadata.read_text(encoding='utf-8', errors='ignore'))
                f.write("```\n\n")

        # Frontend errors
        if frontend_dir and frontend_dir.exists():
            f.write("## ⚛️ Frontend Errors\n\n")

            # ESLint errors
            lint_log = frontend_dir / "lint-errors.log"
            if lint_log.exists():
                f.write("### ESLint Errors\n\n")
                f.write("```javascript\n")
                f.write(lint_log.read_text(encoding='utf-8', errors='ignore'))
                f.write("```\n\n")

            # TypeScript errors
            ts_log = frontend_dir / "typescript-errors.log"
            if ts_log.exists():
                f.write("### TypeScript Errors\n\n")
                f.write("```typescript\n")
                content = ts_log.read_text(encoding='utf-8', errors='ignore')
                lines = content.splitlines()
                f.write('\n'.join(lines[-200:]))
                f.write("\n```\n\n")

            # Build errors
            build_log = frontend_dir / "build-errors.log"
            if build_log.exists():
                f.write("### Build Errors\n\n")
                f.write("```\n")
                content = build_log.read_text(encoding='utf-8', errors='ignore')
                lines = content.splitlines()
                f.write('\n'.join(lines[-200:]))
                f.write("\n```\n\n")

            # Metadata
            metadata = frontend_dir / "metadata.txt"
            if metadata.exists():
                f.write("### Metadata\n\n")
                f.write("```\n")
                f.write(metadata.read_text(encoding='utf-8', errors='ignore'))
                f.write("```\n\n")

        # Claude Code instructions
        f.write("""
---

## 🤖 Instructions for Claude Code

### Analysis Steps

1. **Identify Error Type**
   - Syntax errors
   - Type errors
   - Test failures
   - Linter violations
   - Build errors

2. **Locate Error Source**
   - File path
   - Line number
   - Function/class name

3. **Determine Root Cause**
   - Missing imports
   - Type mismatches
   - Logic errors
   - Configuration issues

4. **Propose Fix**
   - Specific code changes
   - Configuration updates
   - Dependency additions

### Quick Fix Commands

```bash
# Backend fixes
cd backend
ruff check --fix .
ruff format .
mypy app/
pytest tests/ -v

# Frontend fixes
cd frontend
npm run lint -- --fix
npx tsc --noEmit
npm run build
npm test
```

### After Fixing

1. Run tests locally
2. Commit changes
3. Push to trigger CI/CD
4. Monitor workflow run

---

""")

        # Timestamp
        timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
        f.write(f"**Generated**: {timestamp}\n")
        f.write("**Tool**: analyze-cicd-errors.py (Python版)\n")

    return report_file

def main():
    """メイン処理"""
    print_color("━" * 60, Colors.GREEN)
    print_color("CI/CD Error Analysis (Python版)", Colors.GREEN)
    print_color("━" * 60, Colors.GREEN)
    print()

    # GitHub Token取得
    token = get_github_token()
    if not token:
        print_color("Warning: GITHUB_TOKEN not found. Using unauthenticated requests.", Colors.YELLOW)
        print_color("For higher rate limits, set GITHUB_TOKEN environment variable:", Colors.YELLOW)
        print_color("  export GITHUB_TOKEN=your_token", Colors.YELLOW)
        print_color("  Create token at: https://github.com/settings/tokens", Colors.YELLOW)
        print()

    # リポジトリ情報取得
    owner, repo = get_repo_info()
    print_color(f"Repository: {owner}/{repo}", Colors.BLUE)
    print()

    # Run ID取得
    if len(sys.argv) > 1:
        run_id = sys.argv[1]
        print_color(f"Using specified run: {run_id}", Colors.GREEN)
    else:
        print_color("No run ID provided. Fetching latest failed run...", Colors.YELLOW)
        run = get_latest_failed_run(owner, repo, token)

        if not run:
            print_color("Error: No failed runs found", Colors.RED)
            sys.exit(1)

        run_id = str(run['id'])
        print_color(f"Using latest failed run: {run_id}", Colors.GREEN)

    print()

    # Run詳細取得
    print_color("Fetching run details...", Colors.BLUE)
    run_info = get_run_details(owner, repo, run_id, token)

    print_color(f"Branch: {run_info['head_branch']}", Colors.BLUE)
    print_color(f"Commit: {run_info['head_sha'][:8]}", Colors.BLUE)
    print_color(f"Status: {run_info['conclusion']}", Colors.RED)
    print_color(f"Created: {run_info['created_at']}", Colors.BLUE)
    print_color(f"URL: {run_info['html_url']}", Colors.BLUE)
    print()

    # 出力ディレクトリ作成
    output_dir = Path("cicd-errors") / run_id
    output_dir.mkdir(parents=True, exist_ok=True)

    # Artifacts取得
    print_color("Downloading error logs...", Colors.YELLOW)
    artifacts = list_artifacts(owner, repo, run_id, token)

    backend_dir = None
    frontend_dir = None

    for artifact in artifacts:
        artifact_name = artifact['name']
        artifact_id = str(artifact['id'])

        # Backend error logs
        if 'backend-error-logs' in artifact_name:
            backend_dir = output_dir / "backend"
            if download_artifact(owner, repo, artifact_id, backend_dir, token):
                print_color("✓ Downloaded backend error logs", Colors.GREEN)
            else:
                print_color("⚠ Failed to download backend error logs", Colors.YELLOW)

        # Frontend error logs
        elif 'frontend-error-logs' in artifact_name:
            frontend_dir = output_dir / "frontend"
            if download_artifact(owner, repo, artifact_id, frontend_dir, token):
                print_color("✓ Downloaded frontend error logs", Colors.GREEN)
            else:
                print_color("⚠ Failed to download frontend error logs", Colors.YELLOW)

    if not backend_dir and not frontend_dir:
        print_color("⚠ No error log artifacts found", Colors.YELLOW)

    print()

    # レポート生成
    report_file = create_analysis_report(output_dir, run_info, backend_dir, frontend_dir)

    # サマリー出力
    print_color("━" * 60, Colors.GREEN)
    print_color("✓ Error analysis complete!", Colors.GREEN)
    print_color("━" * 60, Colors.GREEN)
    print()
    print_color(f"Report saved to: {report_file}", Colors.BLUE)
    print()

    # エラーログ数カウント
    backend_count = len(list((backend_dir or Path()).glob("*.log"))) if backend_dir else 0
    frontend_count = len(list((frontend_dir or Path()).glob("*.log"))) if frontend_dir else 0

    print_color("Error log files found:", Colors.BLUE)
    print(f"  Backend:  {Colors.RED}{backend_count}{Colors.NC}")
    print(f"  Frontend: {Colors.RED}{frontend_count}{Colors.NC}")
    print()

    # プレビュー
    print_color("Quick Preview:", Colors.YELLOW)
    print()
    with open(report_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()[:50]
        print(''.join(lines))
    print()
    print_color(f"... (see full report in {report_file})", Colors.YELLOW)
    print()

    # 次のステップ
    print_color("Next Steps:", Colors.BLUE)
    print(f"  1. {Colors.GREEN}cat {report_file}{Colors.NC} - View full report")
    print(f"  2. {Colors.GREEN}code {report_file}{Colors.NC} - Open in VS Code")
    print(f"  3. Use Claude Code to analyze and fix errors")
    print(f"  4. {Colors.GREEN}/fix-cicd{Colors.NC} - Claude Code slash command")
    print()

if __name__ == "__main__":
    main()
