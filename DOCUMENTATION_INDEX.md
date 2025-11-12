# 📚 DiagnoLeads ドキュメント索引

**最終更新**: 2025-11-12  
**整理状況**: ✅ **完全整理済み**

---

## 🎯 クイックアクセス

### 🚀 本番環境デプロイ (最優先)

| ドキュメント | 概要 | 場所 |
|-----------|------|------|
| **QUICKSTART_DEPLOYMENT.md** | 25分で本番起動 | `docs/` |
| **PRODUCTION_DEPLOYMENT_GUIDE.md** | 詳細デプロイガイド | `docs/` |

### 💻 開発ガイド

| ドキュメント | 概要 | 場所 |
|-----------|------|------|
| **CLAUDE.md** | 開発ガイドライン・技術スタック | `root` |
| **README.md** | プロジェクト概要 | `root` |
| **README.openspec.md** | OpenSpec ガイド | `root` |
| **UI_GUIDELINES.md** | UI/UX ガイドライン | `root` |
| **SPEC_STRATEGY.md** | 仕様駆動開発戦略 | `docs/` |

### 📊 OpenSpec - データモデル・ER図

| ドキュメント | 概要 | 場所 |
|-----------|------|------|
| **openspec/specs/database/er-diagram-system.md** | ER図システム統合仕様 | `openspec/` |
| **openspec/specs/database/diagnoleads-data-model.md** | DiagnoLeads ER図定義 | `openspec/` |
| **openspec/specs/database/er-diagram-format.md** | ER図フォーマット仕様 | `openspec/` |

### 🔧 セッションレポート (参考)

| ドキュメント | 内容 | 場所 |
|-----------|------|------|
| **docs/SESSION_FINAL_REPORT.md** | セッション最終報告 | `docs/` |
| **docs/RECOMMENDED_IMPROVEMENTS_SUMMARY.md** | 推奨改善 | `docs/` |

---

## 📁 ディレクトリ構造

```
DiagnoLeads/
├── 📄 CLAUDE.md                    # 開発ガイドライン（必読）
├── 📄 README.md                    # プロジェクト概要
├── 📄 README.openspec.md           # OpenSpec ガイド
├── 📄 UI_GUIDELINES.md             # UI/UX ガイド
├── 📄 ER_DIAGRAM_SYSTEM.md         # ER図システム
├── 📄 DOCUMENTATION_INDEX.md       # このファイル
│
├── docs/                           # ドキュメント
│   ├── QUICKSTART_DEPLOYMENT.md    # 25分デプロイ
│   ├── PRODUCTION_DEPLOYMENT_GUIDE.md
│   ├── SPEC_STRATEGY.md
│   ├── OPENSPEC_ER_DIAGRAM_COMPLETE.md
│   ├── OPENSPEC_ER_DIAGRAM_PLAN.md
│   ├── SESSION_FINAL_REPORT.md
│   └── ... (その他セッションレポート)
│
├── openspec/specs/database/
│   ├── er-diagram-format.md        # ER図仕様
│   └── diagnoleads-data-model.md   # DiagnoLeads ER図
│
├── scripts/
│   └── generate_er_diagram.py      # ER図生成ツール
│
├── diagrams/
│   ├── er_diagram.md               # 生成Mermaid図
│   ├── er_diagram.pu               # 生成PlantUML
│   └── er_diagram.json             # メタデータ
│
├── tests/
│   └── test_er_diagram_generator.py # テストスイート
│
├── backend/                        # FastAPI バックエンド
├── frontend/                       # React フロントエンド
├── openspec/                       # OpenSpec 仕様
└── embed/                          # 埋め込みウィジェット
```

---

## 🎯 用途別ガイド

### 1️⃣ 初めての方

```
1. README.md を読む (5分)
2. CLAUDE.md で技術スタック確認 (10分)
3. README.openspec.md で仕様駆動開発を理解 (5分)
└─ 準備完了！開発開始
```

### 2️⃣ 本番環境へデプロイしたい

```
1. docs/QUICKSTART_DEPLOYMENT.md を実行 (25分)
2. ヘルスチェック確認 (5分)
└─ 本番環境稼働！
```

### 3️⃣ ER 図について知りたい

```
1. ER_DIAGRAM_SYSTEM.md を読む (5分)
2. openspec/specs/database/er-diagram-format.md で仕様確認 (10分)
3. python scripts/generate_er_diagram.py で ER図生成 (2分)
└─ ER図完成！
```

### 4️⃣ UI/UX ガイドライン確認

```
UI_GUIDELINES.md を参照
└─ 統一的な UI/UX 実装
```

### 5️⃣ OpenSpec について学びたい

```
1. README.openspec.md を読む (5分)
2. docs/SPEC_STRATEGY.md で戦略確認 (10分)
3. openspec/specs/ で仕様ファイル確認
└─ OpenSpec マスター！
```

---

## ✅ チェックリスト

### 開発環境セットアップ

- [ ] CLAUDE.md で技術スタック確認
- [ ] backend の README を確認
- [ ] frontend の README を確認
- [ ] Docker Compose で起動 (`docker-compose up`)

### 本番デプロイ

- [ ] docs/QUICKSTART_DEPLOYMENT.md を実行
- [ ] ヘルスチェック: `curl https://api.example.com/health`
- [ ] ログイン確認
- [ ] ER図動作確認

### ER 図システム利用

- [ ] scripts/generate_er_diagram.py で ER図生成
- [ ] diagrams/ に出力確認
- [ ] tests/test_er_diagram_generator.py でテスト実行

---

## 📊 ドキュメント統計

```
ルートドキュメント:    5個
  ├─ CLAUDE.md (開発ガイド)
  ├─ README.md (概要)
  ├─ README.openspec.md (OpenSpec)
  ├─ UI_GUIDELINES.md (UI/UX)
  ├─ ER_DIAGRAM_SYSTEM.md (ER図)
  └─ DOCUMENTATION_INDEX.md (このファイル)

docs/ ドキュメント:    30個以上
  ├─ デプロイガイド (2個)
  ├─ 仕様・戦略 (1個)
  ├─ ER図システム (2個)
  └─ セッションレポート (25個+)

実装コード:
  ├─ OpenSpec 仕様 (2個)
  ├─ Python ツール (1個)
  ├─ テストスイート (1個)
  └─ 生成ER図 (3個)

総ドキュメント数: 45個以上 ✅
```

---

## 🚀 推奨読む順序

### エンジニア向け

1. **CLAUDE.md** (必読 - 全体理解)
2. **README.md** (プロジェクト概要)
3. **README.openspec.md** (仕様駆動)
4. **docs/SPEC_STRATEGY.md** (戦略理解)
5. **backend/README.md** (実装開始)

### マネージャー向け

1. **README.md** (プロジェクト概要)
2. **docs/QUICKSTART_DEPLOYMENT.md** (デプロイ可能性)
3. **ER_DIAGRAM_SYSTEM.md** (データモデル理解)
4. **docs/SESSION_FINAL_REPORT.md** (進捗確認)

### デザイナー向け

1. **UI_GUIDELINES.md** (UI/UX ガイド)
2. **README.md** (プロジェクト概要)
3. **frontend/README.md** (フロントエンド実装)

---

## 🎯 クイックコマンド

```bash
# ドキュメント確認
cat README.md
cat CLAUDE.md
cat UI_GUIDELINES.md

# 本番デプロイ
cat docs/QUICKSTART_DEPLOYMENT.md

# ER図生成
python3 scripts/generate_er_diagram.py \
  openspec/specs/database/diagnoleads-data-model.md \
  --format all \
  --output diagrams/er_diagram

# テスト実行
python3 tests/test_er_diagram_generator.py
```

---

## ℹ️ 整理済みの内容

- ✅ 重複ファイルを削除 (15個削除)
- ✅ 重要ドキュメントを docs へ移動
- ✅ ルートは最小限に (5個のコアファイル)
- ✅ ナビゲーション整備
- ✅ インデックス作成

---

**📚 DiagnoLeads ドキュメント - 完全整理済み！** ✅

*最終更新: 2025-11-12*  
*整理状況: 完全整理済み*
