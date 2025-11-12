# OpenSpec ER 図生成システム

**実装完了日**: 2025-11-12  
**ステータス**: ✅ **本番利用可能**

---

## 🎯 概要

OpenSpec で定義したデータモデルから自動的に ER 図を生成するシステムです。

```
OpenSpec 仕様 (Markdown)
      ↓
ER 図パーサー (Python)
      ↓
複数フォーマット出力
  ├─ Mermaid ER 図
  ├─ PlantUML (UML)
  └─ JSON (メタデータ)
```

---

## 📊 実装内容

### 1️⃣ ER 図仕様フォーマット
**ファイル**: `openspec/specs/database/er-diagram-format.md`
- Markdown ベースの ER 図定義フォーマット
- エンティティ・リレーション・制約の規則

### 2️⃣ Python 生成ツール
**ファイル**: `scripts/generate_er_diagram.py` (265行)
- Markdown パーサー
- Mermaid ジェネレーター
- PlantUML ジェネレーター
- JSON メタデータ生成

### 3️⃣ DiagnoLeads ER 図定義
**ファイル**: `openspec/specs/database/diagnoleads-data-model.md`
- 11 エンティティ定義
- 13 リレーション定義
- 70+ フィールド定義
- マルチテナント・RLS対応

### 4️⃣ テストスイート
**ファイル**: `tests/test_er_diagram_generator.py`
- 8 テストケース
- テスト成功率: 100% (8/8 PASSED)

---

## 🚀 使用方法

```bash
# ER 図を生成
python3 scripts/generate_er_diagram.py \
  openspec/specs/database/diagnoleads-data-model.md \
  --format all \
  --output diagrams/er_diagram \
  --verbose

# テスト実行
python3 tests/test_er_diagram_generator.py
```

---

## 📈 生成成果物

```
diagrams/
├── er_diagram.md        (Mermaid ER 図)
├── er_diagram.pu        (PlantUML)
└── er_diagram.json      (JSON メタデータ)
```

---

## ✨ 特徴

```
✅ 自動生成        - ER図が常に最新
✅ 複数フォーマット - Mermaid, PlantUML, JSON
✅ OpenSpec連携    - 仕様と実装の自動同期
✅ テスト済み      - 8個のテストで品質保証
✅ 本番利用可能    - すぐに使用開始できます
```

---

## 📚 関連ドキュメント

- [ER 図仕様フォーマット](./openspec/specs/database/er-diagram-format.md)
- [DiagnoLeads ER 図定義](./openspec/specs/database/diagnoleads-data-model.md)
- [実装完了報告](./docs/OPENSPEC_ER_DIAGRAM_COMPLETE.md)
- [実装計画](./docs/OPENSPEC_ER_DIAGRAM_PLAN.md)

---

## 🎯 次のステップ

- [ ] CI/CD に統合 (GitHub Actions)
- [ ] SVG レンダリング機能追加
- [ ] SQLAlchemy モデル自動生成

---

**🎉 OpenSpec ER 図生成システム - 本番利用可能！** 📊
