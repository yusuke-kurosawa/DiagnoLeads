# Feature: リード管理（スコアリング/ホットリード/セグメント）

Status: Proposed
Created: 2025-11-10

## Overview
回答完了時にリードを自動生成し、スコアと意思表示からホットリードを検出。セグメント保存と重複解決を提供する。

## User Stories
- IS として、今日優先すべき 20 件が自動でほしい
- マーケとして、条件でセグメントを保存し継続モニタリングしたい

## Functional Requirements
- FR-LEAD-001: 回答完了時の自動リード作成（氏名/会社/メール/スコア/タグ）
- FR-LEAD-002: ホットリード判定（しきい値、AI 補正、最新回答重み）
- FR-LEAD-003: ステータス管理（New/Qualified/Working/Won/Lost）
- FR-LEAD-004: セグメント（条件保存、動的更新）
- FR-LEAD-005: 重複解決（メールキー、マージポリシー）

## Acceptance (Example: FR-LEAD-002)
Given スコア >= 80 かつ 時期=今期
When リード作成
Then hot=true を付与し Slack 通知を送る

## API (Draft)
- GET    /api/v1/tenants/{tenant_id}/leads?segment=hot&page=1
- PATCH  /api/v1/tenants/{tenant_id}/leads/{id}
- POST   /api/v1/tenants/{tenant_id}/segments

## Events
- lead.created
- lead.updated
- lead.merged
- lead.hot_marked

## Non-Functional
- 一覧取得 p95 < 150ms、ページネーション必須
- 競合時は楽観ロックで再試行

## Security / Multi-Tenant
- すべてのリード操作は tenant_id でフィルタ
- PII はトークン化/暗号化保管

## Testing Strategy
- 重複マージ/セグメント更新のユニットテスト
- クロステナントアクセス禁止の統合テスト
