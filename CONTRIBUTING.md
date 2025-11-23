# Contributing to DiagnoLeads

DiagnoLeadsプロジェクトへのコントリビューションに興味を持っていただきありがとうございます！

このガイドでは、プロジェクトに貢献する方法を説明します。

---

## 目次

1. [行動規範](#行動規範)
2. [はじめに](#はじめに)
3. [開発環境のセットアップ](#開発環境のセットアップ)
4. [コントリビューションの種類](#コントリビューションの種類)
5. [ブランチ戦略](#ブランチ戦略)
6. [コミット規約](#コミット規約)
7. [プルリクエストのガイドライン](#プルリクエストのガイドライン)
8. [コーディング規約](#コーディング規約)
9. [テストの書き方](#テストの書き方)
10. [ドキュメントの更新](#ドキュメントの更新)

---

## 行動規範

DiagnoLeadsプロジェクトでは、すべての参加者に対して敬意を持った建設的なコミュニケーションを期待しています。

**基本原則**:
- 他の貢献者を尊重する
- 建設的なフィードバックを提供する
- 多様な意見を歓迎する
- 初心者に対して親切である

---

## はじめに

### 必要な知識

DiagnoLeadsに貢献するには、以下の知識があると役立ちます：

**バックエンド**:
- Python 3.11+ (FastAPI, SQLAlchemy)
- PostgreSQL
- REST API設計

**フロントエンド**:
- TypeScript
- React 18+ (Hooks)
- TanStack Query, Zustand

**その他**:
- Git / GitHub
- Docker (オプション)
- マルチテナントアーキテクチャ（学習可）

### 最初の一歩

1. **このリポジトリをフォーク**
2. **開発者ガイドを読む**: [docs/DEVELOPER_GUIDE.md](./docs/DEVELOPER_GUIDE.md)
3. **セキュリティガイドラインを読む**: [docs/SECURITY.md](./docs/SECURITY.md) 🔒
4. **Good First Issueを探す**: ラベル `good first issue` がついたIssueから始めるのがおすすめ

---

## 開発環境のセットアップ

### クイックスタート

```bash
# 1. リポジトリをクローン
git clone https://github.com/<your-username>/DiagnoLeads.git
cd DiagnoLeads

# 2. テスト環境をセットアップ（自動）
./scripts/setup-test-env.sh

# 3. バックエンドの起動
cd backend
source venv/bin/activate
uvicorn app.main:app --reload

# 4. フロントエンドの起動（別のターミナル）
cd frontend
npm run dev
```

詳細な手順は [docs/DEVELOPER_GUIDE.md](./docs/DEVELOPER_GUIDE.md) を参照してください。

### Dockerを使用する場合

```bash
# 開発環境を起動
docker-compose up -d

# ログを確認
docker-compose logs -f backend
```

---

## コントリビューションの種類

### 1. バグ報告

バグを見つけた場合は、GitHubのIssueを作成してください。

**必要な情報**:
- 問題の詳細な説明
- 再現手順
- 期待される動作
- 実際の動作
- 環境情報（OS, Pythonバージョンなど）
- スクリーンショット（あれば）

**テンプレート**:
```markdown
## 問題の説明
[バグの概要を記載]

## 再現手順
1. [手順1]
2. [手順2]
3. [手順3]

## 期待される動作
[期待される動作を記載]

## 実際の動作
[実際の動作を記載]

## 環境
- OS: [例: Ubuntu 22.04]
- Python: [例: 3.11.5]
- Node.js: [例: 18.17.0]
```

### 2. 機能要求

新機能の提案は大歓迎です。

**提案する前に**:
1. 既存のIssueで似た提案がないか確認
2. [openspec/specs/](./openspec/specs/) で既存の仕様を確認
3. プロジェクトのスコープに合っているか検討

**提案フォーマット**:
```markdown
## 提案する機能
[機能の概要]

## 動機・ユースケース
[なぜこの機能が必要か]

## 実装案（あれば）
[実装のアイデア]

## 代替案（あれば）
[他の解決方法]
```

### 3. コード貢献

コードの貢献は以下のプロセスで行います：

1. **Issueを確認/作成** - 既存のIssueを選ぶか、新しいIssueを作成
2. **フォーク & ブランチ作成** - `feature/feature-name` または `fix/bug-name`
3. **実装** - コーディング規約に従って実装
4. **テスト** - 新しいテストを追加、既存のテストが通ることを確認
5. **コミット** - コミット規約に従ってコミット
6. **プルリクエスト** - 詳細な説明とともにPRを作成

### 4. ドキュメント改善

ドキュメントの改善も重要なコントリビューションです：

- タイポの修正
- 説明の明確化
- 翻訳（将来的に英語版を追加予定）
- コード例の追加

---

## ブランチ戦略

### ブランチ命名規則

```
main                  # 本番環境（安定版）
├── develop          # 開発環境（最新の統合版）
├── feature/xxx      # 新機能開発
├── fix/xxx          # バグ修正
├── refactor/xxx     # リファクタリング
└── docs/xxx         # ドキュメント更新
```

### ブランチの作成

```bash
# developブランチから分岐
git checkout develop
git pull origin develop

# 新しいブランチを作成
git checkout -b feature/add-email-notification
```

---

## コミット規約

### Conventional Commits

DiagnoLeadsでは [Conventional Commits](https://www.conventionalcommits.org/) を採用しています。

**フォーマット**:
```
<type>(<scope>): <subject>

<body>

<footer>
```

### Type（必須）

| Type | 説明 | 例 |
|------|------|-----|
| `feat` | 新機能 | `feat(lead): リードエクスポート機能を追加` |
| `fix` | バグ修正 | `fix(auth): ログイン時の認証エラーを修正` |
| `docs` | ドキュメント | `docs(readme): セットアップ手順を更新` |
| `style` | コードスタイル | `style(backend): ruffでフォーマット` |
| `refactor` | リファクタリング | `refactor(service): lead_serviceを分割` |
| `test` | テスト追加 | `test(lead): マルチテナント分離テストを追加` |
| `chore` | その他の変更 | `chore(deps): 依存関係を更新` |

### Scope（オプション）

主要なスコープ：
- `auth` - 認証・認可
- `lead` - リード管理
- `assessment` - 診断管理
- `analytics` - 分析
- `api` - APIエンドポイント
- `ui` - UI/UXコンポーネント
- `docs` - ドキュメント
- `ci` - CI/CD

### 例

**良い例**:
```bash
git commit -m "feat(lead): CSV エクスポート機能を追加

リード一覧をCSV形式でエクスポートできるようになりました。
- LeadExportServiceを実装
- /api/v1/leads/export エンドポイントを追加
- テストを追加

Closes #123"
```

**悪い例**:
```bash
git commit -m "update"  # ❌ 説明が不十分
git commit -m "Fix bug" # ❌ どのバグか不明
```

---

## プルリクエストのガイドライン

### PRを作成する前に

✅ **必須チェックリスト**:
- [ ] すべてのテストが通る（`pytest`, `npm test`）
- [ ] コードがフォーマットされている（`ruff format`, `npm run format`）
- [ ] 新しい機能にテストを追加した
- [ ] ドキュメントを更新した（必要な場合）
- [ ] マルチテナント分離を確認した（リード、診断などのデータ）
- [ ] セキュリティガイドラインを遵守した

### PRのタイトル

コミットメッセージと同じConventional Commits形式を使用：

```
feat(lead): CSV エクスポート機能を追加
```

### PRの説明テンプレート

```markdown
## 概要
[変更の概要を記載]

## 変更内容
- [変更1]
- [変更2]
- [変更3]

## 関連Issue
Closes #123

## テスト方法
1. [テスト手順1]
2. [テスト手順2]

## スクリーンショット（UIの変更の場合）
[スクリーンショットを貼り付け]

## チェックリスト
- [ ] テストが通る
- [ ] ドキュメントを更新した
- [ ] マルチテナント分離を確認した
- [ ] セキュリティガイドラインを遵守した
```

### レビュープロセス

1. **自動チェック** - CI/CDが自動的にテスト・リントを実行
2. **コードレビュー** - メンテナーがコードをレビュー
3. **フィードバック** - 必要に応じて修正
4. **承認** - メンテナーが承認
5. **マージ** - メンテナーがマージ

---

## コーディング規約

### Python（バックエンド）

#### 1. コードフォーマット

```bash
# 自動フォーマット
ruff format .

# リント
ruff check .

# 型チェック
mypy app/
```

#### 2. 命名規則

```python
# クラス: PascalCase
class LeadService:
    pass

# 関数・変数: snake_case
def get_lead_by_id(lead_id: UUID):
    user_name = "John"

# 定数: UPPER_SNAKE_CASE
MAX_LEADS_PER_PAGE = 100

# プライベート: _prefix
def _internal_helper():
    pass
```

#### 3. 型ヒント（必須）

```python
from typing import List, Optional
from uuid import UUID

def get_leads(
    tenant_id: UUID,
    skip: int = 0,
    limit: int = 100
) -> List[Lead]:
    """リード一覧取得"""
    pass
```

#### 4. マルチテナント分離（最重要）

**必ず** `tenant_id` でフィルタリング:

```python
# ❌ 悪い例
leads = db.query(Lead).all()

# ✅ 良い例
leads = db.query(Lead).filter(Lead.tenant_id == tenant_id).all()
```

詳細: [docs/SECURITY.md](./docs/SECURITY.md)

### TypeScript（フロントエンド）

#### 1. コードフォーマット

```bash
# 自動フォーマット
npm run format

# リント
npm run lint

# 型チェック
npm run type-check
```

#### 2. 命名規則

```typescript
// コンポーネント: PascalCase
const LeadCard: React.FC<LeadCardProps> = ({ lead }) => {
  return <div>{lead.name}</div>;
};

// 関数・変数: camelCase
const fetchLeads = async () => {
  const leadData = await api.get('/leads');
};

// 型・インターフェース: PascalCase
interface LeadCardProps {
  lead: Lead;
  onEdit: (id: string) => void;
}

// 定数: UPPER_SNAKE_CASE
const MAX_RETRY_COUNT = 3;
```

#### 3. 型定義（必須）

```typescript
// ❌ 悪い例
const fetchLead = (id) => {
  return api.get(`/leads/${id}`);
};

// ✅ 良い例
const fetchLead = async (id: string): Promise<Lead> => {
  const response = await api.get<Lead>(`/leads/${id}`);
  return response.data;
};
```

---

## テストの書き方

### バックエンド（pytest）

```python
# tests/test_lead.py
import pytest
from app.services.lead_service import LeadService

def test_get_lead_by_id_enforces_tenant_isolation(db_session, tenant_a, tenant_b, lead_a):
    """テナント分離が正しく機能することを確認"""
    service = LeadService(db_session)

    # テナントBがテナントAのリードを取得しようとする
    result = service.get_by_id(lead_a.id, tenant_b.id)

    # None が返されることを確認（データ漏洩なし）
    assert result is None
```

テンプレート: [backend/tests/integration/test_multi_tenant_isolation.py](./backend/tests/integration/test_multi_tenant_isolation.py)

### フロントエンド（Vitest）

```typescript
// src/components/__tests__/LeadCard.test.tsx
import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { LeadCard } from '../LeadCard';

describe('LeadCard', () => {
  it('リード情報が正しく表示される', () => {
    const mockLead = {
      id: '123',
      name: '山田太郎',
      email: 'yamada@example.com',
    };

    render(<LeadCard lead={mockLead} />);

    expect(screen.getByText('山田太郎')).toBeInTheDocument();
    expect(screen.getByText('yamada@example.com')).toBeInTheDocument();
  });
});
```

テンプレート: [frontend/src/components/__tests__/](./frontend/src/components/__tests__/)

---

## OpenAPI仕様のベストプラクティス

DiagnoLeadsでは**Spectral**による厳格なOpenAPI検証を実施しています。

### 必須ルール（エラーレベル）

#### 1. Multi-tenant対応
すべてのエンドポイントは `/api/v1/tenants/{tenant_id}/` を含む必要があります。

**✅ 良い例**:
```yaml
/api/v1/tenants/{tenant_id}/leads:
  get:
    operationId: listLeads
```

**❌ 悪い例**:
```yaml
/api/v1/leads:  # tenant_id が含まれていない
  get:
    operationId: listLeads
```

**例外**: `/api/v1/health`, `/api/v1/auth`, `/api/v1/docs` は除外

#### 2. operationId命名規則
operationIdは **camelCase** で記述する必要があります。

**✅ 良い例**:
```yaml
operationId: createLead
operationId: getLeadById
operationId: updateLeadStatus
```

**❌ 悪い例**:
```yaml
operationId: Create_Lead      # スネークケース
operationId: CreateLead       # PascalCase
operationId: create-lead      # ケバブケース
```

#### 3. レスポンススキーマ必須
すべての成功レスポンス（2xx）にはスキーマ定義が必要です。

**✅ 良い例**:
```yaml
responses:
  200:
    description: Success
    content:
      application/json:
        schema:
          $ref: '#/components/schemas/Lead'
```

**❌ 悪い例**:
```yaml
responses:
  200:
    description: Success
    # スキーマがない！
```

#### 4. セキュリティ要件必須
すべての操作にセキュリティ定義が必要です（認証不要のエンドポイント以外）。

**✅ 良い例**:
```yaml
/api/v1/tenants/{tenant_id}/leads:
  get:
    security:
      - BearerAuth: []
```

### 推奨ルール（警告レベル）

#### 1. エラーレスポンス形式
エラーレスポンスは `ErrorResponse` スキーマを使用してください。

**✅ 良い例**:
```yaml
responses:
  400:
    description: Bad Request
    content:
      application/json:
        schema:
          $ref: '#/components/schemas/ErrorResponse'
```

#### 2. パラメータ説明
パスパラメータには説明を記載してください。

**✅ 良い例**:
```yaml
parameters:
  - name: tenant_id
    in: path
    required: true
    description: テナントの一意識別子
    schema:
      type: string
      format: uuid
```

#### 3. UUID フォーマット
ID系パラメータは `format: uuid` を指定してください。

**✅ 良い例**:
```yaml
parameters:
  - name: lead_id
    schema:
      type: string
      format: uuid
```

### 検証コマンド

```bash
cd frontend

# Spectral厳格検証
npm run validate:openapi:strict

# Breaking Change検出
npm run openapi:diff

# 包括的検証
npm run validate
```

### Breaking Changeポリシー

以下の変更は**Breaking Change**とみなされます：
- ✗ エンドポイントの削除
- ✗ パスの変更
- ✗ HTTPメソッドの変更
- ✗ 必須パラメータの追加
- ✗ レスポンス型の変更（string → number等）
- ✗ Enumの値削除

**Breaking Changeを含むPRの要件**:
1. APIバージョンのメジャーバンプ
2. 最低3ヶ月の非推奨期間
3. クライアント移行ガイドの作成
4. Tech Leadの承認

詳細: [OpenAPI Validation Enhancement](./openspec/changes/openapi-validation-enhancement/proposal.md)

---

## ドキュメントの更新

コードを変更した場合、関連するドキュメントも更新してください：

### 更新が必要な場合

- 新しいAPIエンドポイントを追加した → `openspec/specs/api/` を更新
- 新しい機能を追加した → `README.md` を更新
- 設定を変更した → `docs/DEVELOPER_GUIDE.md` を更新
- セキュリティに関する変更 → `docs/SECURITY.md` を確認

---

## よくある質問

### Q: どのIssueから始めるべきですか？

A: ラベル `good first issue` がついたIssueから始めるのがおすすめです。これらは比較的簡単で、初心者に適しています。

### Q: レビューにどれくらい時間がかかりますか？

A: 通常、2-3営業日以内にレビューを行います。ただし、大きな変更の場合はより時間がかかることがあります。

### Q: PRがリジェクトされた場合はどうすればいいですか？

A: フィードバックを確認し、必要な修正を行ってください。質問がある場合は、PRのコメントで質問してください。

### Q: マルチテナント分離のテストは必須ですか？

A: はい、特にデータに関連する機能（リード、診断など）を扱う場合は必須です。詳細は [docs/SECURITY.md](./docs/SECURITY.md) を参照してください。

---

## サポート

質問や不明点がある場合：

1. **ドキュメントを確認** - [docs/DEVELOPER_GUIDE.md](./docs/DEVELOPER_GUIDE.md)
2. **Issueを検索** - 既存のIssueで解決策が見つかるかもしれません
3. **新しいIssueを作成** - 質問や提案がある場合
4. **ディスカッション** - GitHub Discussionsで議論（将来的に有効化予定）

---

## ライセンス

このプロジェクトにコントリビューションすることにより、あなたの貢献が [MIT License](./LICENSE) の下でライセンスされることに同意したものとみなされます。

---

## 謝辞

DiagnoLeadsプロジェクトへのコントリビューションに感謝します！

あなたの貢献が、より良いプロダクトを作る手助けとなります。🎉
