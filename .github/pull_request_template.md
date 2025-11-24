## 📝 変更内容の説明

<!-- このPRで何を変更したか、なぜ変更したかを説明してください -->

### 関連Issue/Spec
<!-- 関連するIssue番号や OpenSpec 仕様へのリンクを記載 -->
- Related OpenSpec: `openspec/specs/features/xxx.md`
- Fixes #(issue番号)

### 変更の種類
<!-- 該当するものにチェックを入れてください -->
- [ ] 🎨 UI/UX改善
- [ ] ✨ 新機能追加
- [ ] 🐛 バグ修正
- [ ] 📚 ドキュメント更新
- [ ] ♻️ リファクタリング
- [ ] 🗄️ データベース変更（マイグレーション）
- [ ] 🔧 設定変更
- [ ] ✅ テスト追加・修正
- [ ] 🚀 パフォーマンス改善
- [ ] 🔒 セキュリティ対応

---

## ✅ チェックリスト

### 基本
- [ ] コードレビューの準備ができている
- [ ] 自分でコードレビューを実施した
- [ ] 関連するドキュメントを更新した
- [ ] ローカル環境で動作確認した

### テスト
- [ ] 新しいテストを追加した（機能追加の場合）
- [ ] 既存のテストがすべてパスすることを確認した
- [ ] エッジケースを考慮したテストを追加した

### コード品質
- [ ] Linterのエラーがない（`npm run lint` / `ruff check`）
- [ ] 型チェックがパスする（`npm run type-check` / `mypy`）
- [ ] コミットメッセージが[Conventional Commits](https://www.conventionalcommits.org/)に従っている

---

## 🗄️ データベース変更（該当する場合のみ）

### マイグレーション
- [ ] マイグレーションファイルを作成した
- [ ] ローカル環境でマイグレーションを適用して動作確認した
- [ ] ロールバックが正常に動作することを確認した
- [ ] 既存データへの影響を確認した

### 外部キー制約
- [ ] 外部キー制約に適切な `ondelete` を設定した
  - [ ] `CASCADE`: 親削除時に子も削除すべき場合
  - [ ] `SET NULL`: 親削除時に子は保持すべき場合（NULL許容）
  - [ ] `RESTRICT`: 子が存在する場合は親を削除できない
- [ ] 制約の選択理由を `openspec/specs/database/schema-constraints.yml` に記載した

### リレーションシップ
- [ ] SQLAlchemyモデルに `relationship()` を追加した
- [ ] `back_populates` で双方向のリレーションを設定した
- [ ] 必要に応じて `lazy` loading戦略を設定した

### データ整合性
- [ ] 一意制約が必要な場合は設定した
- [ ] チェック制約が必要な場合は設定した（例: スコアの範囲）
- [ ] インデックスを追加した（パフォーマンス考慮）
- [ ] `backend/scripts/validate_database_integrity.py` を実行して整合性を確認した

### ER図
- [ ] ER図を更新した（`python backend/scripts/generate_er_diagram.py`）
- [ ] 変更内容が `diagrams/er_diagram.md` に反映されている

---

## 🔌 OpenAPI変更（該当する場合のみ）

### API仕様
- [ ] 新しいエンドポイントに `operationId` を設定した（camelCase）
- [ ] すべてのパスに `tenant_id` パラメータを含めた（Multi-tenant対応）
- [ ] リクエスト/レスポンススキーマを定義した
- [ ] エラーレスポンス（4xx, 5xx）を定義した
- [ ] API仕様書（Swagger UI）で動作を確認した

### 型生成
- [ ] バックエンドから OpenAPI仕様を生成した（`python backend/scripts/generate_openapi.py`）
- [ ] フロントエンドの型を生成した（`npm run generate:types`）
- [ ] 生成された型をGitにコミットした
- [ ] Breaking Changeがないことを確認した（oasdiff）

### Spectral検証
- [ ] `npm run validate:openapi` がパスすることを確認した
- [ ] Multi-tenant対応の検証をパスした
- [ ] operationId命名規則に準拠している

---

## 🎨 フロントエンド変更（該当する場合のみ）

### 型安全性
- [ ] OpenAPI生成型を使用している（`import type { components } from '@/types/api.generated'`）
- [ ] 手動での型定義を避けた
- [ ] Zodスキーマでランタイムバリデーションを追加した（フォーム等）

### UI/UX
- [ ] レスポンシブデザインを確認した（モバイル・タブレット・デスクトップ）
- [ ] アクセシビリティを考慮した（キーボード操作、スクリーンリーダー）
- [ ] ローディング状態を適切に表示している
- [ ] エラーハンドリングを実装した

### Google Analytics
- [ ] 必要に応じてGA4イベントトラッキングを追加した
- [ ] イベント名が命名規則に従っている

---

## 🔒 セキュリティ（該当する場合のみ）

- [ ] 認証・認可が適切に実装されている
- [ ] テナント分離が正しく機能している（データ漏洩防止）
- [ ] SQL Injection対策が施されている（パラメータ化クエリ）
- [ ] XSS対策が施されている（入力のサニタイズ）
- [ ] 機密情報をログに出力していない
- [ ] 環境変数から秘密情報を取得している

---

## 📸 スクリーンショット（UI変更の場合）

### Before
<!-- 変更前のスクリーンショット -->

### After
<!-- 変更後のスクリーンショット -->

---

## 🧪 テスト手順

<!-- レビュワーがこのPRをテストするための手順を記載 -->

1. ブランチをチェックアウト
   ```bash
   git fetch origin
   git checkout feature/xxx
   ```

2. 依存関係をインストール
   ```bash
   # Backend
   cd backend && pip install -r requirements.txt
   
   # Frontend
   cd frontend && npm install
   ```

3. データベースマイグレーション（該当する場合）
   ```bash
   cd backend
   alembic upgrade head
   ```

4. 開発サーバーを起動
   ```bash
   # Backend
   cd backend && uvicorn app.main:app --reload
   
   # Frontend
   cd frontend && npm run dev
   ```

5. テストケース
   - [ ] ケース1: xxx
   - [ ] ケース2: xxx

---

## 📝 レビュワーへの注意事項

<!-- レビュー時に特に注意してほしい点や、設計判断の理由などを記載 -->

---

## 🚀 デプロイ前の確認（マージ前）

- [ ] CI/CDのすべてのチェックがパスしている
- [ ] 少なくとも1人のレビュワーから承認を得た
- [ ] Breaking Changeがある場合、チームに周知した
- [ ] 本番環境への影響を評価した
- [ ] ロールバック手順を確認した

---

## 📚 参考資料

<!-- 参考にしたドキュメントやIssueへのリンク -->
- [OpenSpec Workflow](./openspec/README.md)
- [Database Schema Constraints](./openspec/specs/database/schema-constraints.yml)
- [API Design Guidelines](./docs/DEVELOPER_GUIDE.md)
