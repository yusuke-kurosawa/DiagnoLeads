# OpenSpec駆動開発ワークフロー

DiagnoLeadsプロジェクトは**完全Spec駆動開発**を採用しています。
OpenAPI仕様を唯一の信頼できる情報源（Single Source of Truth）として、すべての開発を進めます。

## 🎯 基本原則

1. **Spec First**: コードより先にOpenAPI仕様を定義する
2. **Contract Testing**: 仕様との一致を自動検証する
3. **Code Generation**: 仕様から型とクライアントを生成する
4. **Documentation**: 仕様がそのままドキュメントになる

## 📋 開発フロー

### Phase 1: 仕様設計

```bash
# 1. OpenAPI仕様を更新
vim openapi.json

# 2. 仕様の妥当性を検証
npm run validate:openapi
```

### Phase 2: 型生成

```bash
# バックエンド型の生成（FastAPIから自動生成）
cd backend
python scripts/generate_openapi.py

# フロントエンド型の生成
cd frontend
npm run generate:types
```

### Phase 3: 実装

```bash
# バックエンド実装
# - FastAPIエンドポイントは自動的にOpenAPI仕様を生成
# - response_model、status_code等を明示的に指定

# フロントエンド実装
# - 生成された型を使用
# - 生成されたAPIクライアントを使用
```

### Phase 4: 検証

```bash
# 仕様との一致を検証
npm run test:contract

# E2Eテスト
npm run test:e2e
```

## 🛠️ ツール構成

### OpenAPI生成（バックエンド）

```python
# backend/scripts/generate_openapi.py
from app.main import app
import json

spec = app.openapi()
with open('../openapi.json', 'w') as f:
    json.dump(spec, f, indent=2)
```

### 型生成（フロントエンド）

```json
{
  "scripts": {
    "generate:types": "openapi-typescript ../openapi.json -o src/types/api.ts",
    "generate:client": "openapi-typescript-codegen --input ../openapi.json --output src/api --client axios"
  }
}
```

### 仕様検証

```json
{
  "scripts": {
    "validate:openapi": "swagger-cli validate ../openapi.json",
    "lint:openapi": "spectral lint ../openapi.json"
  }
}
```

## 📂 ファイル構成

```
DiagnoLeads/
├── openapi.json                    # 👑 OpenAPI仕様（信頼できる唯一の情報源）
├── backend/
│   ├── app/
│   │   ├── api/                   # FastAPIエンドポイント
│   │   ├── schemas/               # Pydanticスキーマ
│   │   └── main.py               # OpenAPI自動生成
│   └── scripts/
│       └── generate_openapi.py   # 仕様生成スクリプト
├── frontend/
│   ├── src/
│   │   ├── types/
│   │   │   └── api.ts            # 生成された型定義
│   │   ├── api/                  # 生成されたAPIクライアント
│   │   └── services/             # カスタムサービス層
│   └── package.json              # 生成スクリプト定義
└── .github/
    └── workflows/
        └── openapi-validation.yml # CI/CDでの仕様検証
```

## 🔄 新機能追加の手順

### 例: Lead CRUD機能の追加

#### 1. OpenAPI仕様を更新

```yaml
paths:
  /api/v1/tenants/{tenant_id}/leads:
    get:
      summary: List leads
      operationId: listLeads
      parameters:
        - name: tenant_id
          in: path
          required: true
          schema:
            type: string
            format: uuid
      responses:
        '200':
          description: Successful response
          content:
            application/json:
              schema:
                type: array
                items:
                  $ref: '#/components/schemas/Lead'
```

#### 2. スキーマを定義

```yaml
components:
  schemas:
    Lead:
      type: object
      required:
        - id
        - tenant_id
        - name
        - email
      properties:
        id:
          type: string
          format: uuid
        tenant_id:
          type: string
          format: uuid
        name:
          type: string
        email:
          type: string
          format: email
        status:
          type: string
          enum: [new, contacted, qualified, converted]
```

#### 3. 型を生成

```bash
# フロントエンド型生成
cd frontend
npm run generate:types
npm run generate:client
```

#### 4. バックエンド実装

```python
from app.schemas.lead import LeadResponse

@router.get(
    "/tenants/{tenant_id}/leads",
    response_model=List[LeadResponse],  # 仕様と一致
    status_code=200,
    summary="List leads",
    operation_id="listLeads"  # 仕様のoperationIdと一致
)
async def list_leads(...):
    ...
```

#### 5. フロントエンド実装

```typescript
// 生成された型を使用
import { Lead, LeadResponse } from '@/types/api';
import { LeadsApi } from '@/api';

const leadsApi = new LeadsApi();
const leads: LeadResponse[] = await leadsApi.listLeads(tenantId);
```

#### 6. 検証

```bash
# 仕様の再生成と検証
cd backend
python scripts/generate_openapi.py

# 差分チェック
git diff openapi.json

# テスト実行
npm run test:contract
```

## 🎯 ベストプラクティス

### DO ✅

- **仕様を先に書く**: 実装前にOpenAPI仕様を定義
- **operationId を付ける**: すべてのエンドポイントに一意なoperationIdを設定
- **詳細な説明を書く**: summary、description、examplesを充実させる
- **スキーマを再利用**: `$ref`を使ってDRYに保つ
- **バージョニング**: 破壊的変更時は新しいバージョンを作成
- **自動生成を活用**: 手書きの型定義は避ける

### DON'T ❌

- **仕様なしでコードを書かない**: 必ず仕様から始める
- **手動で型を定義しない**: 生成された型を使用
- **仕様とコードを乖離させない**: CI/CDで検証
- **不完全な仕様を残さない**: description、examplesを省略しない

## 🔧 トラブルシューティング

### 仕様とコードが一致しない

```bash
# 1. バックエンドから仕様を再生成
cd backend
python scripts/generate_openapi.py

# 2. 差分を確認
git diff ../openapi.json

# 3. 必要に応じてコードを修正
```

### フロントエンドの型が古い

```bash
# 型を再生成
cd frontend
npm run generate:types
npm run generate:client

# キャッシュをクリア
rm -rf node_modules/.cache
npm run build
```

## 📚 参考資料

- [OpenAPI Specification](https://spec.openapis.org/oas/v3.1.0)
- [FastAPI - OpenAPI](https://fastapi.tiangolo.com/tutorial/metadata/)
- [openapi-typescript](https://github.com/drwpow/openapi-typescript)
- [Spectral](https://stoplight.io/open-source/spectral)

## 🎓 学習リソース

1. **OpenAPI入門**: https://swagger.io/docs/specification/about/
2. **Contract Testing**: https://pactflow.io/how-pact-works/
3. **API Design Best Practices**: https://swagger.io/resources/articles/best-practices-in-api-design/

---

**Remember**: OpenAPI仕様が真実。コードは仕様に従う。
