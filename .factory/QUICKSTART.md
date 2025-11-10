# Factory Droid クイックスタートガイド

DiagnoLeadsプロジェクトでFactory Droidを使い始めるための5分間クイックガイドです。

## 🚀 クイックスタート

### 1. 環境確認

```bash
# プロジェクトディレクトリに移動
cd /path/to/DiagnoLeads

# Factory Droid設定を確認
ls -la .factory/

# 設定ファイルを表示
cat .factory/config.yml
```

### 2. 開発環境のセットアップ

#### バックエンド

```bash
cd backend

# 仮想環境作成
python3 -m venv venv
source venv/bin/activate

# 依存関係インストール
pip install -r requirements.txt

# データベースマイグレーション
alembic upgrade head
```

#### フロントエンド

```bash
cd frontend

# 依存関係インストール
npm install
```

### 3. 開発チェックの実行

Factory Droidのコマンドを使ってコード品質をチェック：

```bash
# 開発チェック（lint、test、build）
# 注: 実際のコマンドは将来実装されます
# 現在は手動で以下を実行：

# バックエンド
cd backend
source venv/bin/activate
ruff check .
ruff format .
mypy app/
pytest tests/ -v

# フロントエンド
cd frontend
npm run lint
npx tsc --noEmit
npm test
npm run build
```

### 4. マルチテナントチェック

**重要**: 新しいコードを書く前に必ず確認！

```bash
# テナント分離チェック
# 注: 実際のコマンドは将来実装されます
# 現在は以下のポイントを手動確認：

# ✅ チェックポイント
# 1. すべてのDBクエリでtenant_idフィルタ
# 2. APIエンドポイントでテナント検証
# 3. モデルにtenant_idカラム
# 4. テストでテナント分離を検証
```

## 📝 開発ワークフロー例

### 新機能開発

```bash
# 1. 仕様を確認
cat openspec/specs/feature-name/specification.md

# 2. ブランチ作成
git checkout -b feature/new-feature

# 3. テンプレートからファイル生成
cp .factory/templates/api_endpoint.py backend/app/api/v1/new_feature.py
cp .factory/templates/model.py backend/app/models/new_model.py
cp .factory/templates/service.py backend/app/services/new_service.py

# 4. ファイルを編集
# - ResourceNameを実際の名前に置換
# - 必要な機能を実装
# - tenant_idフィルタリングを必ず実装

# 5. テスト作成
# tests/ にテストケースを追加

# 6. コード品質チェック
cd backend
source venv/bin/activate
ruff check .
ruff format .
pytest tests/ -v

# 7. コミット
git add .
git commit -m "feat: Add new feature"

# 8. プッシュ
git push origin feature/new-feature

# 9. PR作成
gh pr create
```

## 🛡️ マルチテナント開発のベストプラクティス

### ✅ 必ず守るべきルール

#### 1. データベースクエリ

```python
# ❌ 絶対にNG
items = db.query(Item).all()

# ✅ 必ずテナントでフィルタ
items = db.query(Item).filter(
    Item.tenant_id == current_tenant.id
).all()
```

#### 2. APIエンドポイント

```python
# ✅ テナントIDをパスに含める
@router.get("/api/v1/tenants/{tenant_id}/items")
async def list_items(
    tenant_id: UUID,
    current_user: User = Depends(get_current_user)
):
    # テナントIDの検証
    if current_user.tenant_id != tenant_id:
        raise HTTPException(status_code=403)
    
    # テナントフィルタ付きクエリ
    return await item_service.list_by_tenant(tenant_id)
```

#### 3. モデル定義

```python
class Item(Base):
    __tablename__ = "items"
    
    id = Column(UUID(as_uuid=True), primary_key=True)
    tenant_id = Column(UUID(as_uuid=True), nullable=False, index=True)  # 必須
    name = Column(String)
    # ...
```

#### 4. テスト

```python
def test_tenant_isolation():
    """テナント分離を検証"""
    # テナントAでデータ作成
    tenant_a_item = create_item(tenant_id=tenant_a.id)
    
    # テナントBでアクセス試行
    response = client.get(
        f"/api/v1/tenants/{tenant_b.id}/items/{tenant_a_item.id}",
        headers=get_auth_headers(tenant_b_user)
    )
    
    # 403 Forbiddenを期待
    assert response.status_code == 403
```

## 🎯 コードテンプレート使用方法

### 1. APIエンドポイント作成

```bash
# テンプレートをコピー
cp .factory/templates/api_endpoint.py backend/app/api/v1/assessments.py

# 置換作業
# ResourceName → Assessment
# resources → assessments
# resource_id → assessment_id

# 実装
# - エンドポイントロジックを追加
# - tenant_id検証を確認
# - エラーハンドリングを追加
```

### 2. モデル作成

```bash
# テンプレートをコピー
cp .factory/templates/model.py backend/app/models/assessment.py

# 置換作業
# ResourceName → Assessment
# resource_names → assessments

# 実装
# - カラムを追加
# - リレーションを定義
# - tenant_idは必須（削除しない）
```

### 3. サービス作成

```bash
# テンプレートをコピー
cp .factory/templates/service.py backend/app/services/assessment_service.py

# 置換作業
# ResourceName → Assessment

# 実装
# - ビジネスロジックを追加
# - すべてのメソッドでtenant_idフィルタ
# - AI機能統合（必要に応じて）
```

### 4. Reactコンポーネント作成

```bash
# テンプレートをコピー
cp .factory/templates/component.tsx frontend/src/features/assessments/AssessmentList.tsx

# 置換作業
# ResourceName → Assessment
# resources → assessments

# 実装
# - UIロジックを追加
# - TanStack Queryでデータ取得
# - エラーハンドリングを追加
```

## 🔍 トラブルシューティング

### よくある問題

#### 1. Lintエラー

```bash
# 自動修正
cd backend
source venv/bin/activate
ruff check . --fix
ruff format .

cd frontend
npm run lint --fix
```

#### 2. 型エラー

```bash
# バックエンド
cd backend
source venv/bin/activate
mypy app/

# フロントエンド
cd frontend
npx tsc --noEmit
```

#### 3. テスト失敗

```bash
# バックエンド
cd backend
source venv/bin/activate
pytest tests/ -v -x  # 最初の失敗で停止

# フロントエンド
cd frontend
npm test -- --verbose
```

#### 4. マルチテナント違反

```bash
# コードレビュー
grep -rn "\.query(" backend/app/ | grep -v "tenant_id"

# テナントフィルタが欠けているクエリを検出
grep -rn "\.all()" backend/app/ | grep -v "tenant_id"
```

## 📚 参考リソース

### ドキュメント

- [README.md](.factory/README.md) - 詳細ガイド
- [context.md](.factory/context.md) - プロジェクトコンテキスト
- [config.yml](.factory/config.yml) - 設定ファイル

### Droid定義

- [dev-workflow.yml](.factory/droids/dev-workflow.yml) - 開発ワークフロー
- [multi-tenant-guard.yml](.factory/droids/multi-tenant-guard.yml) - テナント検証
- [openspec-sync.yml](.factory/droids/openspec-sync.yml) - OpenSpec統合

### コードテンプレート

- [api_endpoint.py](.factory/templates/api_endpoint.py) - FastAPI
- [model.py](.factory/templates/model.py) - SQLAlchemy
- [service.py](.factory/templates/service.py) - ビジネスロジック
- [component.tsx](.factory/templates/component.tsx) - React

## 💡 Tips

### 1. 開発前に必ず実行

```bash
# 仕様を確認
cat openspec/specs/{feature}/specification.md

# 既存コードを確認
grep -rn "similar_feature" backend/app/
```

### 2. コミット前に必ず実行

```bash
# コード品質チェック
cd backend && ruff check . && pytest tests/
cd frontend && npm run lint && npm test && npm run build
```

### 3. PR作成前に必ず実行

```bash
# テナント分離チェック
grep -rn "\.query(" backend/app/api backend/app/services | grep -v "tenant_id"

# .envが含まれていないか確認
git diff --cached --name-only | grep "\.env$"
```

## 🎉 まとめ

Factory Droidを使用することで：

✅ **自動化**: コード品質チェックが自動化  
✅ **セキュリティ**: マルチテナント分離を強制  
✅ **一貫性**: テンプレートで一貫したコード  
✅ **効率**: 仕様駆動開発でムダを削減  

**Happy Coding! 🚀**
