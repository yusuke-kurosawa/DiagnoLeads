# Feature: AI支援（生成/洞察/改善提案）

Status: Proposed
Created: 2025-11-10

## Overview
ブランク状態から 5 分で「提案→編集→公開」へ到達するための AI 機能群。診断の自動生成、回答データからの洞察抽出、設問改善提案を提供する。

## User Stories
- テナント管理者として、トピックを入力するだけで診断案がほしい
- マーケ担当として、離脱が多い設問の改善提案がほしい
- インサイドセールスとして、回答から推奨アクションを得たい

## Functional Requirements
- FR-AI-001: トピック/業界/目的から質問・選択肢・スコア案を生成
- FR-AI-002: 回答データから課題仮説と推奨アクションを生成
- FR-AI-003: 設問の難易度・離脱率を分析し改善提案を提示
- FR-AI-004: 文面を自然言語で修正（トーン/長さ/専門度）

## Acceptance (Example: FR-AI-001)
Given トピック『B2B SaaS のオンボーディング改善』
When 自動生成を実行
Then 10〜15問の質問案、選択肢、スコアリング案、結果セクション案が 20 秒以内で返る

## API (Draft)
- POST /api/v1/tenants/{tenant_id}/ai/assessments {topic, industry, goal}
- POST /api/v1/tenants/{tenant_id}/ai/insights {assessment_id, filters}
- POST /api/v1/tenants/{tenant_id}/ai/rephrase {text, tone, length, expertise}

## Events
- ai.assessment_proposed
- ai.insight_generated
- ai.copy_rephrased

## Non-Functional
- p95 応答 < 20s（生成系）/ < 500ms（洞察取得）
- コスト上限: 1生成あたり $0.3 以内（目安）

## Security / Multi-Tenant
- すべて tenant_id スコープで実行、出力に他テナントデータを混在させない

## Testing Strategy
- 生成リクエストのスキーマ検証
- 出力最小要素の存在検証（質問数、スコア構造）
- テナント越境が起きないことの検証
