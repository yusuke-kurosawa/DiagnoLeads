#!/usr/bin/env python3
"""
GitHub Actionsで実行中の不要なワークフローを停止するスクリプト
"""
import os
import subprocess
import json
import sys

def get_github_token():
    """GitHub tokenを取得（環境変数、gh CLI設定、またはgit configから）"""
    # 環境変数から取得を試みる
    token = os.environ.get('GITHUB_TOKEN') or os.environ.get('GH_TOKEN')
    if token:
        return token

    # gh CLIの設定ファイルから取得を試みる
    try:
        gh_config_path = os.path.expanduser('~/.config/gh/hosts.yml')
        if os.path.exists(gh_config_path):
            import yaml
            with open(gh_config_path, 'r') as f:
                config = yaml.safe_load(f)
                if config and 'github.com' in config:
                    token = config['github.com'].get('oauth_token')
                    if token:
                        return token
    except Exception:
        pass

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

def get_running_workflows(token):
    """実行中またはキューイング中のワークフローを取得"""
    workflows = []

    # in_progress と queued の両方を取得
    for status in ['in_progress', 'queued']:
        try:
            result = subprocess.run(
                ['curl', '-s', '-H', f'Authorization: Bearer {token}',
                 '-H', 'Accept: application/vnd.github+json',
                 '-H', 'X-GitHub-Api-Version: 2022-11-28',
                 f'https://api.github.com/repos/yusuke-kurosawa/DiagnoLeads/actions/runs?status={status}&per_page=100'],
                capture_output=True,
                text=True,
                check=True
            )

            data = json.loads(result.stdout)
            workflows.extend(data.get('workflow_runs', []))
        except Exception as e:
            print(f"エラー: {status}ワークフロー取得に失敗しました: {e}")

    return workflows

def cancel_workflow(run_id, workflow_name, token):
    """指定されたワークフローをキャンセル"""
    try:
        result = subprocess.run(
            ['curl', '-s', '-X', 'POST', '-w', '\n%{http_code}',
             '-H', f'Authorization: Bearer {token}',
             '-H', 'Accept: application/vnd.github+json',
             '-H', 'X-GitHub-Api-Version: 2022-11-28',
             f'https://api.github.com/repos/yusuke-kurosawa/DiagnoLeads/actions/runs/{run_id}/cancel'],
            capture_output=True,
            text=True,
            check=False
        )

        # HTTPステータスコードを確認
        lines = result.stdout.strip().split('\n')
        http_code = lines[-1] if lines else ''

        if http_code in ['202', '200']:
            print(f"✓ キャンセル完了: {workflow_name} (ID: {run_id})")
            return True
        else:
            print(f"✗ キャンセル失敗: {workflow_name} (ID: {run_id}) - HTTP {http_code}")
            return False
    except Exception as e:
        print(f"✗ キャンセル失敗: {workflow_name} (ID: {run_id}) - {e}")
        return False

def main():
    print("実行中のGitHub Actionsワークフローを確認中...")

    # GitHub tokenを取得
    token = get_github_token()
    if not token:
        print("\nエラー: GitHub tokenが見つかりません。")
        print("以下のいずれかの方法でtokenを設定してください:")
        print("  1. 環境変数: export GITHUB_TOKEN=your_token")
        print("  2. 環境変数: export GH_TOKEN=your_token")
        print("  3. Git config: git config --global github.token your_token")
        sys.exit(1)

    workflows = get_running_workflows(token)

    if not workflows:
        print("実行中またはキューイング中のワークフローはありません。")
        return

    print(f"\n{len(workflows)}個のワークフローが見つかりました:\n")

    for i, wf in enumerate(workflows, 1):
        print(f"{i}. {wf['name']} (ID: {wf['id']})")
        print(f"   ブランチ: {wf['head_branch']}")
        print(f"   ステータス: {wf['status']}")
        print(f"   開始時刻: {wf['created_at']}")
        print()

    # すべてキャンセルするか確認
    if len(sys.argv) > 1 and sys.argv[1] == '--all':
        confirm = 'y'
    else:
        confirm = input(f"これら{len(workflows)}個のワークフローをすべてキャンセルしますか？ [y/N]: ")

    if confirm.lower() == 'y':
        print("\nワークフローをキャンセル中...")
        success_count = 0
        for wf in workflows:
            if cancel_workflow(wf['id'], wf['name'], token):
                success_count += 1

        print(f"\n完了: {success_count}/{len(workflows)}個のワークフローをキャンセルしました。")
    else:
        print("キャンセルを中止しました。")

if __name__ == '__main__':
    main()
