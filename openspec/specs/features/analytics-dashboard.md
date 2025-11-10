# Feature: 分析ダッシュボード（完了率/離脱/ファネル）

Status: Proposed
Created: 2025-11-10

## Overview
診断体験の「完了率・離脱・CV ファネル」をリアルタイムに可視化し、改善サイクルを加速する。

## User Stories
- マーケとして、直近 30 日の完了率と離脱ポイントを把握したい
- 事業責任者として、チャネル別の CV ファネルを追いたい

## Functional Requirements
- FR-ANL-001: 完了率、離脱ポイント、平均回答時間を可視化
- FR-ANL-002: ファネル（閲覧→開始→中間→完了→CV）の時系列
- FR-ANL-003: 設問別貢献度と改善提案（AI）
- FR-ANL-004: セグメント比較（流入チャネル、業界、企業規模）
- FR-ANL-005: エクスポート（CSV/Slack サマリー）

## Acceptance (Example: FR-ANL-001)
Given 直近 30 日の回答
When ダッシュボード表示
Then p95 200ms 以内で KPI を表示、ドリルダウンで個別回答へ到達

## API (Draft)
- GET /api/v1/tenants/{tenant_id}/analytics/overview?range=30d
- GET /api/v1/tenants/{tenant_id}/analytics/funnel?range=30d

## Events
- analytics.snapshot_generated

## Non-Functional
- 集計はバッチ + インクリメンタル、UI 応答 p95 < 200ms

## Security / Multi-Tenant
- すべての集計は tenant_id で分離、匿名化済みイベントのみ利用

## Testing Strategy
- 指標の定義テスト（分母/分子の一貫性）
- 性能テスト（N=10万回答で <200ms 応答）
