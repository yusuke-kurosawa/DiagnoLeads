# OpenSpec駆動開発 - DiagnoLeads

DiagnoLeadsは**完全Spec駆動開発**を採用しています。OpenAPI仕様を唯一の信頼できる情報源（Single Source of Truth）として、すべての開発を進めます。

## 🎯 なぜOpenSpec駆動開発？

### 従来の問題

- ❌ コードとドキュメントの乖離
- ❌ フロントエンドとバックエンドの型の不一致
- ❌ API変更時の手動同期の手間
- ❌ テストで発見される型エラー

### OpenSpec駆動開発の利点

- ✅ **Single Source of Truth**: OpenAPI仕様が唯一の真実
- ✅ **型安全性**: 自動生成された型で完全な型安全性
- ✅ **自動同期**: コード変更時に自動で仕様と型を更新
- ✅ **Contract Testing**: 仕様との一致を自動検証
- ✅ **即座のドキュメント**: 仕様がそのままドキュメント

## 🚀 クイックスタート

### 1. OpenAPI仕様の確認

```bash
# 現在のOpenAPI仕様を表示
cat openapi.json | jq

# または、ブラウザで確認
open http://localhost:8000/docs  # Swagger UI
open http://localhost:8000/redoc # ReDoc
```

### 2. バックエンドからOpenAPI仕様を生成

```bash
cd backend
source venv/bin/activate
python scripts/generate_openapi.py
```

出力:
```
✅ OpenAPI specification generated: /path/to/openapi.json
📊 Endpoints: 10
📦 Schemas: 10
✅ Specification validation passed
```

### 3. フロントエンドの型を生成

```bash
cd frontend
npm run generate:types
```

出力:
```
✨ openapi-typescript 7.10.1
🚀 ../openapi.json → src/types/api.generated.ts [105.4ms]
```

### 4. 生成された型を使用

```typescript
// ❌ 従来: 手動で型定義
interface Assessment {
  id: string;
  title: string;
  // ... 手動で全フィールドを定義
}

// ✅ OpenSpec駆動: 自動生成された型を使用
import type { components } from '@/types/api.generated';

type Assessment = components['schemas']['AssessmentResponse'];
```

## 📋 開発ワークフロー

### Phase 1: 仕様設計（Spec First）

新機能を追加する際は、まずOpenAPI仕様を定義します。

```yaml
# openapi.json (または手動編集)
paths:
  /api/v1/tenants/{tenant_id}/leads:
    post:
      operationId: createLead
      summary: Create a new lead
      parameters:
        - name: tenant_id
          in: path
          required: true
          schema:
            type: string
            format: uuid
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/LeadCreate'
      responses:
        '201':
          description: Lead created
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/LeadResponse'
```

### Phase 2: 型生成

```bash
# 仕様から型を生成
cd frontend
npm run generate:types

# 結果を確認
git diff src/types/api.generated.ts
```

### Phase 3: バックエンド実装

```python
from fastapi import APIRouter, Depends
from app.schemas.lead import LeadCreate, LeadResponse

router = APIRouter()

@router.post(
    "/tenants/{tenant_id}/leads",
    response_model=LeadResponse,  # 仕様と一致
    status_code=201,
    summary="Create a new lead",
    operation_id="createLead"  # 仕様のoperationIdと一致
)
async def create_lead(
    tenant_id: UUID,
    lead_data: LeadCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # 実装
    ...
```

### Phase 4: フロントエンド実装

```typescript
// 自動生成された型を使用
import type { components, paths } from '@/types/api.generated';

type LeadCreate = components['schemas']['LeadCreate'];
type LeadResponse = components['schemas']['LeadResponse'];
type CreateLeadOperation = paths['/api/v1/tenants/{tenant_id}/leads']['post'];

// API呼び出し（型安全）
const createLead = async (
  tenantId: string,
  data: LeadCreate
): Promise<LeadResponse> => {
  const response = await fetch(
    `/api/v1/tenants/${tenantId}/leads`,
    {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    }
  );
  return response.json();
};
```

### Phase 5: 検証

```bash
# OpenAPI仕様の再生成
cd backend
python scripts/generate_openapi.py

# 型の再生成
cd ../frontend
npm run generate:types

# 差分確認（意図しない変更がないか）
git diff ../openapi.json
git diff src/types/api.generated.ts

# テスト実行
cd ../backend
pytest tests/

cd ../frontend
npm run build
npm run lint
```

## 🛠️ 利用可能なコマンド

### バックエンド

```bash
# OpenAPI仕様を生成
python scripts/generate_openapi.py

# 仕様を表示
python -c "from app.main import app; import json; print(json.dumps(app.openapi(), indent=2))"
```

### フロントエンド

```bash
# TypeScript型を生成
npm run generate:types

# OpenAPI仕様を検証
npm run validate:openapi

# OpenAPI仕様をバンドル
npm run openapi:bundle
```

### Factory Droid

```bash
# 完全同期（バックエンド→OpenAPI→フロントエンド→テスト）
# ※Droidが自動実行

# または手動で
cd backend && python scripts/generate_openapi.py
cd ../frontend && npm run generate:types
```

## 📂 ファイル構成

```
DiagnoLeads/
├── openapi.json                          # 👑 OpenAPI仕様（信頼できる唯一の情報源）
│
├── backend/
│   ├── scripts/
│   │   └── generate_openapi.py          # OpenAPI仕様生成スクリプト
│   ├── app/
│   │   ├── api/                         # FastAPIエンドポイント
│   │   ├── schemas/                     # Pydanticスキーマ
│   │   └── main.py                      # FastAPI app（OpenAPI自動生成）
│
├── frontend/
│   ├── src/
│   │   ├── types/
│   │   │   └── api.generated.ts         # 🤖 自動生成された型定義
│   │   ├── services/
│   │   │   └── assessmentService.ts     # APIクライアント
│   │   └── components/
│   └── package.json                      # 型生成スクリプト定義
│
├── .factory/
│   ├── droids/
│   │   └── openspec-driven-dev.yml      # OpenSpec駆動開発Droid
│   └── workflows/
│       └── openspec-driven-dev.md       # 詳細ワークフロー
│
├── .github/
│   └── workflows/
│       └── ci.yml                        # CI/CDでOpenAPI検証
│
└── .redocly.yaml                         # OpenAPI lint設定
```

## 🎯 ベストプラクティス

### DO ✅

1. **Spec First**: 実装前にOpenAPI仕様を定義
2. **operationId を付ける**: すべてのエンドポイントに一意なoperationIdを設定
3. **自動生成を活用**: 手書きの型定義は避ける
4. **仕様の更新**: API変更時は必ずOpenAPI仕様を再生成
5. **差分確認**: コミット前に`git diff openapi.json`で変更を確認
6. **CI/CD統合**: 自動テストでOpenAPI仕様の検証

### DON'T ❌

1. **仕様なしでコードを書かない**: 必ず仕様から始める
2. **手動で型を定義しない**: 生成された型を使用
3. **仕様とコードを乖離させない**: 変更時は必ず同期
4. **operationIdを省略しない**: 必須フィールド
5. **生成ファイルを手動編集しない**: `api.generated.ts`は自動生成専用

## 🔧 トラブルシューティング

### 問題: 仕様とコードが一致しない

```bash
# 1. バックエンドから仕様を再生成
cd backend
python scripts/generate_openapi.py

# 2. 差分を確認
git diff ../openapi.json

# 3. 必要に応じてコードを修正
# FastAPIのresponse_model、status_code等を確認
```

### 問題: フロントエンドの型が古い

```bash
# 1. 型を再生成
cd frontend
npm run generate:types

# 2. キャッシュをクリア
rm -rf node_modules/.cache

# 3. ビルド
npm run build
```

### 問題: OpenAPI検証エラー

```bash
# 警告を確認
cd frontend
npm run validate:openapi

# 一般的な問題:
# - operationIdの重複
# - security定義の欠如
# - レスポンススキーマの不一致

# 修正後、再生成
cd ../backend
python scripts/generate_openapi.py
```

## 📚 参考資料

- [OpenAPI Specification 3.1.0](https://spec.openapis.org/oas/v3.1.0)
- [FastAPI - OpenAPI](https://fastapi.tiangolo.com/tutorial/metadata/)
- [openapi-typescript](https://github.com/drwpow/openapi-typescript)
- [Redocly CLI](https://redocly.com/docs/cli/)

## 🎓 詳細ドキュメント

- [完全ワークフロー](./.factory/workflows/openspec-driven-dev.md)
- [Droid設定](./.factory/droids/openspec-driven-dev.yml)
- [CI/CD設定](./.github/workflows/ci.yml)

---

**Remember**: OpenAPI仕様が真実。コードは仕様に従う。🎯
