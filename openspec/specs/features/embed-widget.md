# Feature: 埋め込みウィジェット

Status: Proposed
Created: 2025-11-10

## Overview
1 行スニペットで LP/サイトへ診断を設置。モーダル/インライン/フローティング表示に対応し、計測・同意・イベントフックを提供する。

## User Stories
- 実装エンジニアとして、10 分で安全に設置したい
- マーケ担当として、コード改修なしで見た目と文言を更新したい

## Functional Requirements
- FR-EMB-001: 1 行スニペットで設置、テナント/診断を自動解決
- FR-EMB-002: 表示モード（modal/inline/floating）を選択
- FR-EMB-003: i18n（ja/en）切替
- FR-EMB-004: p95 First Interaction < 1.0s、初期 < 35KB gzip
- FR-EMB-005: イベントフック（onStart/onComplete/onLeadCaptured）
- FR-EMB-006: 同意管理（Cookie 同意、プライバシーリンク）

## Acceptance (Example: FR-EMB-005)
Given onComplete にコールバックを渡す
When 回答が完了
Then 結果と lead_id を引数に 1 回だけ呼び出される

## API (Draft)
- GET  /embed/assessments/{public_id}.js
- POST /api/v1/public/assessments/{public_id}/responses

## Events
- widget.loaded
- response.completed
- lead.captured

## Non-Functional
- p95 バンドル取得 < 200ms（CDN）
- SameSite/Lax, CSP 推奨ヘッダ

## Security / Multi-Tenant
- public_id はテナント固有、署名付き
- PII は最小収集、送信時 TLS 必須

## Testing Strategy
- e2e: 各モード表示、フック呼び出し、同意表示
- perf: バンドルサイズ/初回対話時間の測定
