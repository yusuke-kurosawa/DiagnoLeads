#!/usr/bin/env python3
"""
GitHub Actions Job Logs Downloader

GitHub ActionsのジョブログをAPIから直接ダウンロードして表示します。
UIからコピペする必要がなくなります。

Usage:
    # 最新の失敗したrunのログを表示
    python scripts/download-job-logs.py

    # 特定のrun IDのログを表示
    python scripts/download-job-logs.py 19520121110

    # 特定のjob IDのログを表示
    python scripts/download-job-logs.py --job 55881484347

    # ログをファイルに保存
    python scripts/download-job-logs.py --save
"""

import os
import sys
import json
import subprocess
import re
from typing import Optional, Dict, Any, List
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

# カラー出力
class Colors:
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    CYAN = '\033[0;36m'
    MAGENTA = '\033[0;35m'
    NC = '\033[0m'

def print_color(text: str, color: str) -> None:
    """カラーテキストを出力"""
    print(f"{color}{text}{Colors.NC}")

def get_github_token() -> Optional[str]:
    """GitHub Tokenを取得"""
    token = os.environ.get('GITHUB_TOKEN')
    if token:
        return token

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
            check=False
        )
        url = result.stdout.strip()

        # GitHub URLのパターンをチェック
        if 'github.com' in url:
            url = url.replace('.git', '')
            if url.startswith('https://'):
                parts = url.split('github.com/')[-1]
            elif url.startswith('git@'):
                parts = url.split('github.com:')[-1]
            else:
                raise ValueError("Unknown URL format")

            owner, repo = parts.split('/')
            return owner, repo

        # 特殊なURL形式（例: http://local_proxy@127.0.0.1:53269/git/owner/repo）
        elif '/git/' in url:
            # /git/ 以降の部分を抽出
            parts = url.split('/git/')[-1]
            parts = parts.replace('.git', '')
            owner, repo = parts.split('/')
            return owner, repo

        else:
            raise ValueError("Not a GitHub repository")

    except Exception as e:
        print_color(f"Error: Failed to get repository info: {e}", Colors.RED)
        print_color("Tip: Use --owner and --repo flags to specify manually", Colors.YELLOW)
        sys.exit(1)

def github_api_request(endpoint: str, token: Optional[str] = None, accept_header: str = 'application/vnd.github+json') -> Any:
    """GitHub APIリクエスト"""
    url = f"https://api.github.com{endpoint}"

    headers = {
        'Accept': accept_header,
        'X-GitHub-Api-Version': '2022-11-28'
    }

    if token:
        headers['Authorization'] = f'Bearer {token}'

    try:
        req = Request(url, headers=headers)
        with urlopen(req) as response:
            # ログの場合はテキストとして返す
            if 'text/plain' in accept_header:
                return response.read().decode('utf-8')
            # JSONの場合
            return json.loads(response.read().decode())

    except HTTPError as e:
        if e.code == 401:
            print_color("Error: Unauthorized. Please set GITHUB_TOKEN", Colors.RED)
        elif e.code == 404:
            print_color(f"Error: Resource not found (404): {endpoint}", Colors.RED)
        else:
            print_color(f"Error: API request failed: {e.code} {e.reason}", Colors.RED)
        sys.exit(1)

    except URLError as e:
        print_color(f"Error: Network error: {e.reason}", Colors.RED)
        sys.exit(1)

def get_latest_failed_run(owner: str, repo: str, token: Optional[str]) -> Optional[Dict[str, Any]]:
    """最新の失敗したworkflow runを取得"""
    endpoint = f"/repos/{owner}/{repo}/actions/runs?status=failure&per_page=5"
    data = github_api_request(endpoint, token)
    runs = data.get('workflow_runs', [])

    return runs[0] if runs else None

def get_run_details(owner: str, repo: str, run_id: str, token: Optional[str]) -> Dict[str, Any]:
    """Workflow runの詳細を取得"""
    endpoint = f"/repos/{owner}/{repo}/actions/runs/{run_id}"
    return github_api_request(endpoint, token)

def get_run_jobs(owner: str, repo: str, run_id: str, token: Optional[str]) -> List[Dict[str, Any]]:
    """Workflow runのジョブ一覧を取得"""
    endpoint = f"/repos/{owner}/{repo}/actions/runs/{run_id}/jobs"
    data = github_api_request(endpoint, token)
    return data.get('jobs', [])

def get_job_logs(owner: str, repo: str, job_id: str, token: Optional[str]) -> str:
    """ジョブのログを取得"""
    endpoint = f"/repos/{owner}/{repo}/actions/jobs/{job_id}/logs"
    url = f"https://api.github.com{endpoint}"

    headers = {
        'Accept': 'application/vnd.github+json',
        'X-GitHub-Api-Version': '2022-11-28'
    }

    if token:
        headers['Authorization'] = f'Bearer {token}'

    try:
        req = Request(url, headers=headers)
        # GitHub APIはログに対してリダイレクトを返す
        with urlopen(req) as response:
            # リダイレクト先のURLを取得してログをダウンロード
            log_url = response.url
            with urlopen(log_url) as log_response:
                return log_response.read().decode('utf-8')

    except HTTPError as e:
        if e.code == 401:
            print_color(f"Error: Unauthorized for job {job_id}", Colors.RED)
        else:
            print_color(f"Error: Failed to fetch logs for job {job_id}: {e.code} {e.reason}", Colors.RED)
        return f"Error: Could not fetch logs (HTTP {e.code})"

    except Exception as e:
        print_color(f"Error: Failed to fetch logs: {e}", Colors.RED)
        return f"Error: Could not fetch logs ({e})"

def extract_error_lines(log_text: str, context_lines: int = 5) -> List[str]:
    """ログからエラー行を抽出"""
    lines = log_text.split('\n')
    error_lines = []
    error_patterns = [
        r'error:',
        r'Error:',
        r'ERROR:',
        r'FAILED',
        r'failed',
        r'✗',
        r'Exception',
        r'Traceback',
    ]

    for i, line in enumerate(lines):
        if any(re.search(pattern, line, re.IGNORECASE) for pattern in error_patterns):
            # エラー行の前後のコンテキストを含める
            start = max(0, i - context_lines)
            end = min(len(lines), i + context_lines + 1)
            error_lines.extend(lines[start:end])
            error_lines.append('-' * 80)

    return error_lines

def format_job_output(job: Dict[str, Any], log_text: str, show_full_log: bool = False) -> str:
    """ジョブの出力を整形"""
    output = []
    output.append("=" * 80)
    output.append(f"Job: {job['name']}")
    output.append(f"Status: {job['status']} | Conclusion: {job.get('conclusion', 'N/A')}")
    output.append(f"Started: {job.get('started_at', 'N/A')}")
    output.append(f"Completed: {job.get('completed_at', 'N/A')}")
    output.append(f"URL: {job['html_url']}")
    output.append("=" * 80)

    if show_full_log:
        output.append("\nFull Log:")
        output.append(log_text)
    else:
        output.append("\nError Highlights:")
        error_lines = extract_error_lines(log_text)
        if error_lines:
            output.extend(error_lines)
        else:
            output.append("(No obvious errors found in log)")

    output.append("\n")
    return '\n'.join(output)

def main():
    import argparse

    parser = argparse.ArgumentParser(description='Download GitHub Actions job logs')
    parser.add_argument('run_id', nargs='?', help='Workflow run ID')
    parser.add_argument('--job', help='Specific job ID to download')
    parser.add_argument('--save', action='store_true', help='Save logs to files')
    parser.add_argument('--full', action='store_true', help='Show full logs (not just errors)')
    parser.add_argument('--branch', help='Filter runs by branch')

    args = parser.parse_args()

    print_color("━" * 60, Colors.CYAN)
    print_color("GitHub Actions Job Logs Downloader", Colors.CYAN)
    print_color("━" * 60, Colors.CYAN)
    print()

    # GitHub Token取得
    token = get_github_token()
    if not token:
        print_color("Warning: GITHUB_TOKEN not found. Using unauthenticated requests.", Colors.YELLOW)
        print_color("For higher rate limits, set GITHUB_TOKEN environment variable", Colors.YELLOW)
        print()

    # リポジトリ情報取得
    owner, repo = get_repo_info()
    print_color(f"Repository: {owner}/{repo}", Colors.BLUE)
    print()

    # 特定のJob IDが指定された場合
    if args.job:
        print_color(f"Fetching logs for job {args.job}...", Colors.BLUE)
        log_text = get_job_logs(owner, repo, args.job, token)

        job_endpoint = f"/repos/{owner}/{repo}/actions/jobs/{args.job}"
        job = github_api_request(job_endpoint, token)

        output = format_job_output(job, log_text, args.full)
        print(output)

        if args.save:
            filename = f"job-{args.job}.log"
            with open(filename, 'w') as f:
                f.write(output)
            print_color(f"\n✓ Saved to {filename}", Colors.GREEN)

        return

    # Run ID取得
    if args.run_id:
        run_id = args.run_id
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

    print_color(f"Workflow: {run_info['name']}", Colors.BLUE)
    print_color(f"Branch: {run_info['head_branch']}", Colors.BLUE)
    print_color(f"Commit: {run_info['head_sha'][:8]}", Colors.BLUE)
    print_color(f"Status: {run_info['conclusion']}", Colors.RED if run_info['conclusion'] == 'failure' else Colors.GREEN)
    print_color(f"URL: {run_info['html_url']}", Colors.BLUE)
    print()

    # ジョブ一覧取得
    print_color("Fetching jobs...", Colors.BLUE)
    jobs = get_run_jobs(owner, repo, run_id, token)

    print_color(f"Found {len(jobs)} jobs", Colors.BLUE)
    print()

    # 失敗したジョブのログを取得
    failed_jobs = [job for job in jobs if job['conclusion'] == 'failure']

    if not failed_jobs:
        print_color("No failed jobs found", Colors.YELLOW)
        return

    print_color(f"Downloading logs for {len(failed_jobs)} failed jobs...", Colors.YELLOW)
    print()

    all_output = []

    for job in failed_jobs:
        print_color(f"Fetching logs for: {job['name']}", Colors.CYAN)

        try:
            log_text = get_job_logs(owner, repo, str(job['id']), token)
            output = format_job_output(job, log_text, args.full)

            print(output)
            all_output.append(output)

            if args.save:
                filename = f"job-{job['id']}-{job['name'].replace(' ', '-')}.log"
                with open(filename, 'w') as f:
                    f.write(output)
                print_color(f"✓ Saved to {filename}", Colors.GREEN)

        except Exception as e:
            print_color(f"Failed to fetch logs for job {job['id']}: {e}", Colors.RED)

    # すべてのログを1つのファイルに保存
    if args.save and all_output:
        combined_filename = f"run-{run_id}-all-failed-jobs.log"
        with open(combined_filename, 'w') as f:
            f.write('\n\n'.join(all_output))
        print()
        print_color(f"✓ All logs saved to {combined_filename}", Colors.GREEN)

    print()
    print_color("━" * 60, Colors.CYAN)
    print_color("✓ Download complete", Colors.GREEN)
    print_color("━" * 60, Colors.CYAN)

if __name__ == "__main__":
    main()
