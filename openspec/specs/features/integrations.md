# Feature: 外部連携（Salesforce/HubSpot/Slack）

Status: Proposed
Created: 2025-11-10

## Overview
既存の CRM/MA 運用を崩さず、確実な同期と通知を実現する。

## User Stories
- 管理者として、HubSpot と双方向同期したい
- IS として、ホットリードを Slack に即時通知してほしい

## Functional Requirements
- FR-INT-001: Salesforce/HubSpot への双方向同期（Lead/Company/Activity）
- FR-INT-002: Slack 通知（ホットリード、しきい値アラート、朝レポート）
- FR-INT-003: レート制限/失敗時の再試行（指数バックオフ、最大3回）
- FR-INT-004: マッピング UI（フィールド対応/変換ルール）

## Acceptance (Example: FR-INT-001)
Given HubSpot 接続済
When リードが更新
Then 30 秒以内に HubSpot 側が更新、失敗時は最大 3 回再試行

## Events
- integration.synced
- integration.failed
- integration.retried

## Non-Functional
- 外部 API のレート制限順守、ジョブ冪等性

## Security / Multi-Tenant
- 資格情報は KMS/Secret 管理、テナントごとに隔離

## Testing Strategy
- Webhook モックによる同期テスト
- 再試行/バックオフの挙動検証
