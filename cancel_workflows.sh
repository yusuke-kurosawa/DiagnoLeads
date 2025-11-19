#!/bin/bash
# GitHub Actionsで実行中の不要なワークフローを停止するスクリプト

set -e

REPO_OWNER="yusuke-kurosawa"
REPO_NAME="DiagnoLeads"

# GitHub tokenの確認
if [ -z "$GITHUB_TOKEN" ]; then
    echo "エラー: GITHUB_TOKEN 環境変数が設定されていません"
    echo ""
    echo "以下のコマンドでtokenを設定してから再実行してください:"
    echo "  export GITHUB_TOKEN=your_github_token"
    echo ""
    echo "GitHub Personal Access Token (PAT)は以下から作成できます:"
    echo "  https://github.com/settings/tokens"
    echo "  必要な権限: repo, workflow"
    exit 1
fi

echo "実行中のGitHub Actionsワークフローを確認中..."
echo ""

# 実行中のワークフローを取得
RUNNING_WORKFLOWS=$(curl -s \
    -H "Authorization: token $GITHUB_TOKEN" \
    -H "Accept: application/vnd.github.v3+json" \
    "https://api.github.com/repos/$REPO_OWNER/$REPO_NAME/actions/runs?status=in_progress&per_page=100")

# キューイング中のワークフローを取得
QUEUED_WORKFLOWS=$(curl -s \
    -H "Authorization: token $GITHUB_TOKEN" \
    -H "Accept: application/vnd.github.v3+json" \
    "https://api.github.com/repos/$REPO_OWNER/$REPO_NAME/actions/runs?status=queued&per_page=100")

# 結果をマージしてjqで処理
ALL_WORKFLOWS=$(echo "$RUNNING_WORKFLOWS" "$QUEUED_WORKFLOWS" | jq -s '.[0].workflow_runs + .[1].workflow_runs')

# ワークフロー数を確認
WORKFLOW_COUNT=$(echo "$ALL_WORKFLOWS" | jq 'length')

if [ "$WORKFLOW_COUNT" -eq 0 ]; then
    echo "実行中またはキューイング中のワークフローはありません"
    exit 0
fi

echo "${WORKFLOW_COUNT}個のワークフローが見つかりました:"
echo ""

# ワークフローのリストを表示
echo "$ALL_WORKFLOWS" | jq -r '.[] | "  - \(.name) (ID: \(.id))\n    ブランチ: \(.head_branch)\n    ステータス: \(.status)\n    開始時刻: \(.created_at)\n"'

# 確認（--allフラグで自動承認）
if [ "$1" != "--all" ]; then
    read -p "これら${WORKFLOW_COUNT}個のワークフローをすべてキャンセルしますか？ [y/N]: " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "キャンセルを中止しました"
        exit 0
    fi
fi

echo ""
echo "ワークフローをキャンセル中..."
echo ""

# 各ワークフローをキャンセル
SUCCESS_COUNT=0
FAIL_COUNT=0

for RUN_ID in $(echo "$ALL_WORKFLOWS" | jq -r '.[].id'); do
    WORKFLOW_NAME=$(echo "$ALL_WORKFLOWS" | jq -r ".[] | select(.id == $RUN_ID) | .name")

    RESPONSE=$(curl -s -w "\n%{http_code}" \
        -X POST \
        -H "Authorization: token $GITHUB_TOKEN" \
        -H "Accept: application/vnd.github.v3+json" \
        "https://api.github.com/repos/$REPO_OWNER/$REPO_NAME/actions/runs/$RUN_ID/cancel")

    HTTP_CODE=$(echo "$RESPONSE" | tail -n 1)

    if [ "$HTTP_CODE" -eq 202 ]; then
        echo "✓ キャンセル完了: $WORKFLOW_NAME (ID: $RUN_ID)"
        ((SUCCESS_COUNT++))
    else
        echo "✗ キャンセル失敗: $WORKFLOW_NAME (ID: $RUN_ID) - HTTP $HTTP_CODE"
        ((FAIL_COUNT++))
    fi
done

echo ""
echo "完了: ${SUCCESS_COUNT}/${WORKFLOW_COUNT}個のワークフローをキャンセルしました"

if [ $FAIL_COUNT -gt 0 ]; then
    echo "警告: ${FAIL_COUNT}個のワークフローのキャンセルに失敗しました"
    exit 1
fi
