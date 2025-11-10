# Feature: 公開・バージョン管理

Status: Proposed
Created: 2025-11-10

## Overview
下書き/公開の状態管理と、公開バージョンのロールバックを提供し、安全な運用を実現する。

## Functional Requirements
- FR-BLD-005: 下書き/公開の状態管理、公開バージョンのロールバック
- FR-BLD-006: プレビュー（デスクトップ/モバイル）を 2 秒以内で反映
- FR-BLD-007: ブランド設定（色/ロゴ/トーン）をテーマとして保存/適用

## Acceptance (Example: FR-BLD-005)
Given 下書き版が存在
When 公開する
Then 新しい公開バージョンが作成され、任意の過去版へ 1 クリックでロールバック可能

## API (Draft)
- POST /api/v1/tenants/{tenant_id}/assessments/{id}/publish
- POST /api/v1/tenants/{tenant_id}/assessments/{id}/rollback

## Events
- assessment.published
- assessment.rolled_back
