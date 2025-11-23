# Database Seeding Guide

DiagnoLeadsでは、開発・テスト用の初期データを簡単に投入できるseedシステムを提供しています。

## 📁 構成

```
backend/
├── seed_database.py          # Seed実行スクリプト
├── app/core/seed.py          # Seedingロジック
└── seeds/                    # Seed定義ファイル
    ├── development.py        # 開発環境用データ
    ├── test.py               # テスト環境用データ
    └── __init__.py
```

## 🚀 使い方

### 基本的な使い方

```bash
# 開発データをseed（Docker内）
docker compose exec backend python seed_database.py

# または、Makefileを使用
make seed
```

### オプション

```bash
# 環境を指定
docker compose exec backend python seed_database.py --env test

# 既存データをクリーンしてから再seed
docker compose exec backend python seed_database.py --clean

# 組み合わせ
docker compose exec backend python seed_database.py --env development --clean
```

### Makefileコマンド

```bash
# 開発データをseed
make seed

# クリーン & seed
make seed-clean

# データベースをリセット（migrate + seed）
make db-reset
```

## 📋 Seedデータの内容

### Development環境

**テナント:**
- Demo Tenant - Admin (Enterprise)
- Demo Tenant - User (Pro)
- Demo Tenant - System (Enterprise)

**ユーザー:**

| 名前 | Email | Password | Role |
|------|-------|----------|------|
| 管理者ユーザー | admin@demo.example.com | Admin@Demo123 | tenant_admin |
| 一般ユーザー | user@demo.example.com | User@Demo123 | user |
| システム管理者 | system@demo.example.com | System@Demo123 | system_admin |

**診断:**
- サンプル診断：営業力診断 (Published)
  - 3つの質問
  - 各質問に3つの選択肢
- サンプル診断：マーケティング成熟度 (Draft)

**リード:**
- 山田 太郎 (qualified, スコア: 85)
- 佐藤 花子 (new, スコア: 65)
- 鈴木 一郎 (contacted, スコア: 75)

### Test環境

最小限のテストデータ（1テナント、1ユーザー）

## 🔧 Seedデータの追加・カスタマイズ

### 新しいSeed環境の追加

1. `backend/seeds/`に新しいファイルを作成:

```python
# backend/seeds/staging.py
from uuid import uuid4

TENANT_ID = str(uuid4())
USER_ID = str(uuid4())

SEED_DATA = {
    "tenants": [
        {
            "id": TENANT_ID,
            "name": "Staging Tenant",
            "slug": "staging",
            "plan": "enterprise",
            "settings": "{}",
        },
    ],
    "users": [
        {
            "id": USER_ID,
            "tenant_id": TENANT_ID,
            "email": "staging@example.com",
            "password": "Staging@123",
            "name": "Staging User",
            "role": "tenant_admin",
        },
    ],
    "assessments": [],
}
```

2. 実行:

```bash
docker compose exec backend python seed_database.py --env staging
```

### 既存Seedデータの編集

`backend/seeds/development.py`を直接編集してください。

```python
# ユーザーを追加
{
    "id": str(uuid4()),
    "tenant_id": TENANT_ADMIN_ID,
    "email": "newuser@demo.example.com",
    "password": "NewUser@123",
    "name": "新しいユーザー",
    "role": "user",
},
```

## ⚙️ 内部動作

1. **べき等性**: 同じデータを複数回実行しても安全（既存データはスキップ）
2. **トランザクション**: すべての操作はトランザクション内で実行
3. **外部キー順序**: 依存関係を考慮した順序でseed（tenants → users → assessments）
4. **パスワードハッシュ**: パスワードは自動的にハッシュ化

## 🧹 データのクリーン

既存データを削除してから再seedする場合：

```bash
make seed-clean
```

**警告**: これは**すべての**データを削除します！本番環境では絶対に実行しないでください。

## 💡 Tips

### 開発開始時

```bash
# データベースを初期化
make db-reset
```

### テスト前

```bash
# テスト用データをseed
docker compose exec backend python seed_database.py --env test --clean
```

### デバッグ時

```bash
# 既存データを保持したままseed（重複はスキップ）
make seed
```

## 🔒 セキュリティ注意事項

- **本番環境では使用しないでください**: Seedデータは開発・テスト用です
- パスワードは平文で定義されていますが、データベースにはハッシュ化されて保存されます
- 本番環境用のデータ投入は別途マイグレーションまたは専用スクリプトで行ってください
