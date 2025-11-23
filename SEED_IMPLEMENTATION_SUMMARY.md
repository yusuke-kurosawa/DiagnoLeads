# Seed実装完了サマリー

## 🎉 実装内容

テスト用の初期データをseedで管理できるシステムを完全に実装しました。

## 📦 構成

```
backend/
├── seed_database.py              # CLIスクリプト
├── app/core/seed.py              # Seedingロジック（拡張済み）
├── seeds/
│   ├── __init__.py
│   ├── development.py            # 開発環境用（完全なデータセット）
│   └── test.py                   # テスト環境用（最小データセット）
└── README.seed.md                # Seedingガイド
```

## ✅ 実装済みエンティティ

### 1. Tenants（テナント）
- 3つのテナント（Admin、User、System）

### 2. Users（ユーザー）
- 各テナントに1ユーザー（計3人）
- ロール：tenant_admin、user、system_admin

### 3. Assessments（診断）
- 2つのサンプル診断
  - 営業力診断（Published）
  - マーケティング成熟度（Draft）

### 4. Questions（質問） ⭐ NEW
- 3つの質問（営業力診断に紐付け）
- 各質問に説明とポイント設定

### 5. Question Options（質問の選択肢） ⭐ NEW
- 9つの選択肢（各質問に3つずつ）
- 各選択肢にポイント設定

### 6. Leads（リード）
- 3つのサンプルリード
- 様々なステータス（new、qualified、contacted）
- スコア、タグ、カスタムフィールド付き

### 7. Topics（トピック） ⭐ NEW マスターデータ
- 5つのトピック（マーケティング、営業、CS、DX、組織・人材）
- カラーコード、アイコン付き
- 診断の分類・フィルタリングに使用

### 8. Industries（業界） ⭐ NEW マスターデータ
- 6つの業界（IT、金融、医療、製造、小売、教育）
- カラーコード、アイコン付き
- 業界特化型診断に使用

## 🚀 使い方

### 基本コマンド

```bash
# 開発データをseed
docker compose exec backend python seed_database.py

# または
make seed

# クリーン & seed（既存データ削除）
make seed-clean

# データベースリセット（migrate + seed）
make db-reset
```

### 環境切り替え

```bash
# テスト環境用データ
docker compose exec backend python seed_database.py --env test

# 本番環境用データ（注意！）
docker compose exec backend python seed_database.py --env production
```

## 📊 Seed結果

```bash
$ make seed

🌱 Starting database seeding...
🏢 Seeding tenants...
  ✅ Created tenant: Demo Tenant - Admin
  ✅ Created tenant: Demo Tenant - User
  ✅ Created tenant: Demo Tenant - System

👤 Seeding users...
  ✅ Created user: 管理者ユーザー (admin@demo.example.com)
  ✅ Created user: 一般ユーザー (user@demo.example.com)
  ✅ Created user: システム管理者 (system@demo.example.com)

📋 Seeding assessments...
  ✅ Created assessment: サンプル診断：営業力診断
  ✅ Created assessment: サンプル診断：マーケティング成熟度

❓ Seeding questions...
  ✅ Created question: あなたの営業チームの規模を教えてください...
  ✅ Created question: 営業プロセスはどの程度標準化されていますか？...
  ✅ Created question: CRMツールを活用していますか？...

📝 Seeding question options...
  ✅ Created option: 1-5名...
  ✅ Created option: 6-20名...
  ✅ Created option: 21名以上...
  （計9つの選択肢）

🎯 Seeding leads...
  ✅ Created lead: 山田 太郎 (yamada@example.com)
  ✅ Created lead: 佐藤 花子 (sato@demo.co.jp)
  ✅ Created lead: 鈴木 一郎 (suzuki@testcorp.jp)

🏷️  Seeding topics...
  ✅ Created topic: マーケティング
  ✅ Created topic: 営業
  ✅ Created topic: カスタマーサクセス
  ✅ Created topic: DX・デジタル化
  ✅ Created topic: 組織・人材

🏭 Seeding industries...
  ✅ Created industry: IT・ソフトウェア
  ✅ Created industry: 金融・銀行
  ✅ Created industry: 医療・ヘルスケア
  ✅ Created industry: 製造業
  ✅ Created industry: 小売・E-コマース
  ✅ Created industry: 教育・研修

✅ Database seeding completed successfully!
```

## 🎯 データ統計

| エンティティ | 件数 | 備考 |
|------------|------|------|
| Tenants | 3 | デモテナント |
| Users | 3 | 各ロール |
| Assessments | 2 | 営業・マーケ |
| Questions | 3 | 営業力診断用 |
| Question Options | 9 | 各質問3つずつ |
| Leads | 3 | サンプルリード |
| **Topics** | **5** | **マスターデータ** |
| **Industries** | **6** | **マスターデータ** |

## 🔧 カスタマイズ方法

### 新しいエンティティの追加

1. `backend/app/core/seed.py`にメソッドを追加:

```python
def seed_new_entity(self, entities: List[Dict[str, Any]]):
    """Seed new entity"""
    logger.info("🆕 Seeding new entities...")

    for entity_data in entities:
        # 既存チェック
        # INSERT処理

    self.db.commit()
```

2. `seed_all()`メソッドに追加:

```python
if "new_entities" in data:
    self.seed_new_entities(data["new_entities"])
```

3. `backend/seeds/development.py`にデータ定義を追加:

```python
SEED_DATA = {
    # ... existing data ...
    "new_entities": [
        {
            "id": str(uuid4()),
            # ... entity data ...
        },
    ],
}
```

### 新しい環境の追加

`backend/seeds/staging.py`を作成:

```python
from uuid import uuid4

SEED_DATA = {
    "tenants": [...],
    "users": [...],
    # ...
}
```

実行:
```bash
docker compose exec backend python seed_database.py --env staging
```

## 🎁 主な機能

✅ **べき等性**: 何度実行しても安全
✅ **環境別管理**: development/test/production
✅ **クリーンモード**: 既存データを削除して再seed
✅ **トランザクション**: すべての操作がトランザクション内
✅ **外部キー順序**: 依存関係を考慮した順序で実行
✅ **詳細ログ**: 各ステップの進行状況を表示

## 📝 技術的な詳細

### べき等性の実装

各seedメソッドは既存データをチェックしてからINSERTを実行：

```python
# 既存チェック
result = self.db.execute(
    text("SELECT id FROM questions WHERE id = :id"),
    {"id": question_data["id"]},
)
existing = result.fetchone()

if existing:
    logger.info(f"  ⏭️  Question already exists")
    continue

# INSERT処理
self.db.execute(...)
```

### 外部キー順序

Seedは以下の順序で実行されます：

1. Tenants
2. Users
3. Assessments
4. Questions
5. Question Options
6. Leads
7. Topics（マスターデータ）
8. Industries（マスターデータ）

### トランザクション

各エンティティタイプのseed後に`self.db.commit()`を実行：

```python
def seed_questions(self, questions: List[Dict[str, Any]]):
    # ... seed logic ...
    self.db.commit()  # Commit after all questions
```

## 🔒 セキュリティ注意事項

- ⚠️ 本番環境では使用しないでください
- パスワードは平文で定義されていますが、DBにはハッシュ化されて保存されます
- 本番環境用のデータ投入は別途マイグレーションで行ってください

## 📚 関連ドキュメント

- `backend/README.seed.md` - 詳細なSeedingガイド
- `Makefile` - プロジェクト全体のコマンド
- `backend/Makefile` - バックエンド専用コマンド

## 🎉 完成！

これでDiagnoLeadsの開発環境に一貫したテストデータを簡単に投入できるようになりました！
