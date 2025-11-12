# QRコード配信機能 実装キックオフ 🚀

**日付**: 2025-11-11  
**優先度**: High  
**推定工数**: 1-2週間  
**担当**: Backend Dev 1名 + Frontend Dev 1名

---

## 📢 チームへの共有メッセージ

皆さん、

QRコード配信機能の実装を開始します！🎉

この機能により、オフラインマーケティング（展示会、名刺、ポスター等）でDiagnoLeadsの診断を配信し、スキャン数のトラッキングと効果測定が可能になります。

**完全な実装計画書**: `docs/QR_CODE_IMPLEMENTATION_PLAN.md`

---

## 🎯 機能概要（エレベーターピッチ）

「展示会ブースにQRコード付きポスターを設置。来場者がスキャンすると診断ページが開き、完了後リードとして記録。どのQRコードが何回スキャンされたか、どれだけ診断が完了したかをリアルタイムで分析できる。」

**ビジネス価値**:
- オフライン→オンライン誘導
- イベントROIの可視化
- 低コスト（ランニングコスト ~$0/月）

---

## 📅 実装スケジュール

### Week 1: バックエンド実装

| Day | タスク | 担当 | 状態 |
|-----|--------|------|------|
| **Day 1** | データモデル & マイグレーション | Backend | 🟢 開始 |
| **Day 2** | QRコード生成サービス | Backend | ⏳ 待機 |
| **Day 3** | API CRUD実装 | Backend | ⏳ 待機 |
| **Day 4** | リダイレクト & トラッキング | Backend | ⏳ 待機 |
| **Day 5** | 統計分析API | Backend | ⏳ 待機 |

### Week 2: フロントエンド & テスト

| Day | タスク | 担当 | 状態 |
|-----|--------|------|------|
| **Day 6-7** | 管理画面UI | Frontend | ⏳ 待機 |
| **Day 8** | 統計ダッシュボード | Frontend | ⏳ 待機 |
| **Day 9-10** | テスト & バグ修正 | Both | ⏳ 待機 |

---

## 📦 Day 1: データモデル実装（今日の作業）

### 作成するファイル

```
backend/app/models/qr_code.py           ← 新規作成
backend/app/models/qr_code_scan.py      ← 新規作成
backend/app/schemas/qr_code.py          ← 新規作成
backend/alembic/versions/XXXX_add_qr_code_tables.py  ← マイグレーション
```

### データモデル概要

**QRCode** (主テーブル):
- 診断ごとのQRコード
- 短縮URL (`https://dgnl.ds/{code}`)
- UTMパラメータ（トラッキング用）
- スキャン数カウント

**QRCodeScan** (トラッキング):
- 各スキャンの記録
- デバイス、OS、ブラウザ
- 地域（GeoIP）
- ファネル（スキャン→開始→完了→リード）

### 推定時間: 4-6時間

---

## 🛠️ セットアップ

### Backend開発者

**1. 依存関係のインストール**:
```bash
cd backend
source venv/bin/activate  # または venv/bin/python を直接使用

# QRコード生成
pip install qrcode[pil]==7.4.2
pip install pillow==10.1.0

# トラッキング
pip install user-agents==2.2.0
pip install geoip2==4.7.0

# requirements.txt に追加
echo "qrcode[pil]==7.4.2" >> requirements.txt
echo "pillow==10.1.0" >> requirements.txt
echo "user-agents==2.2.0" >> requirements.txt
echo "geoip2==4.7.0" >> requirements.txt
```

**2. GeoIPデータベースのダウンロード**（オプション）:
```bash
# MaxMind GeoLite2 (無料)
# https://dev.maxmind.com/geoip/geolite2-free-geolocation-data
# ダウンロード後: backend/data/GeoLite2-City.mmdb
```

**3. 環境変数**:
```bash
# .env に追加
SHORT_URL_DOMAIN=dgnl.ds
GEOIP_DATABASE_PATH=./data/GeoLite2-City.mmdb  # オプション
```

### Frontend開発者（Day 6から）

**依存関係のインストール**:
```bash
cd frontend
npm install qrcode.react
```

---

## 📋 Day 1 詳細タスク

### Task 1.1: QRCodeモデル作成 ⏱️ 1-2時間

**ファイル**: `backend/app/models/qr_code.py`

**実装内容**:
- SQLAlchemyモデル定義
- 16フィールド（id, tenant_id, assessment_id, short_code, utm_params, etc.）
- リレーション: Tenant, Assessment

**参考**: `docs/QR_CODE_IMPLEMENTATION_PLAN.md` のデータモデル詳細セクション

---

### Task 1.2: QRCodeScanモデル作成 ⏱️ 1時間

**ファイル**: `backend/app/models/qr_code_scan.py`

**実装内容**:
- トラッキングデータのモデル
- 15フィールド（user_agent, device_type, location, etc.）
- リレーション: QRCode, Lead

---

### Task 1.3: Alembicマイグレーション ⏱️ 1時間

**実行**:
```bash
cd backend
alembic revision -m "add_qr_code_tables"
# 生成されたファイルを編集
alembic upgrade head
```

**マイグレーション内容**:
- qr_codes テーブル作成
- qr_code_scans テーブル作成
- インデックス作成（short_code unique, qr_code_id, etc.）

---

### Task 1.4: Pydanticスキーマ ⏱️ 1-2時間

**ファイル**: `backend/app/schemas/qr_code.py`

**実装内容**:
- QRCodeCreate
- QRCodeUpdate
- QRCodeResponse
- QRCodeScanResponse

---

## ✅ Day 1 完了の定義

以下がすべて完了すれば、Day 1完了：

- [ ] QRCodeモデル作成完了
- [ ] QRCodeScanモデル作成完了
- [ ] マイグレーション実行成功
- [ ] Pydanticスキーマ作成完了
- [ ] データベースにテーブルが存在
- [ ] モデルの基本的なCRUD動作確認

**確認コマンド**:
```bash
# データベース確認
psql $DATABASE_URL -c "\dt qr_codes"
psql $DATABASE_URL -c "\d qr_codes"
```

---

## 📞 コミュニケーション

### Daily Standup報告フォーマット

**昨日やったこと**:
- Task 1.1: QRCodeモデル作成完了

**今日やること**:
- Task 1.2: QRCodeScanモデル作成
- Task 1.3: マイグレーション

**ブロッカー**:
- なし / または具体的な問題

### 質問・相談

- Slack: #diagnoleads-dev
- 緊急: @tech-lead

---

## 🔗 リソース

### 必読ドキュメント

1. **完全実装計画**: `docs/QR_CODE_IMPLEMENTATION_PLAN.md`
   - 全タスクの詳細
   - コード例
   - テスト戦略

2. **データモデル詳細**: 実装計画書の「データモデル詳細」セクション
   - 全フィールド定義
   - インデックス戦略
   - リレーション

3. **API設計**: 実装計画書の「API設計詳細」セクション
   - エンドポイント定義
   - リクエスト/レスポンス例

### 参考コード

既存のモデルを参考に：
- `backend/app/models/assessment.py`
- `backend/app/models/lead.py`
- `backend/app/schemas/assessment.py`

---

## 🎯 成功の指標

### Day 1
- データモデル完成
- マイグレーション成功

### Week 1 (Day 5)
- バックエンドAPI完成
- Swagger UIで動作確認

### Week 2 (Day 10)
- フロントエンド完成
- E2Eテスト成功
- ステージング環境デプロイ

### 最終目標
- QRコード生成・ダウンロード機能
- スキャントラッキング
- 統計ダッシュボード
- 診断完了CVR 20%以上

---

## 🚨 注意事項

### セキュリティ

- [ ] 短縮コードは衝突しないように生成（7文字英数字）
- [ ] IPアドレスはハッシュ化推奨
- [ ] QRコード作成にレート制限（10/hour）

### テナント分離

- [ ] **必須**: すべてのクエリで `tenant_id` フィルタリング
- [ ] QRCodeモデルに `tenant_id` 必須
- [ ] リダイレクト時もテナント検証

### パフォーマンス

- [ ] short_code に unique インデックス
- [ ] qr_code_id, scanned_at にインデックス
- [ ] リダイレクトは500ms以内を目標

---

## 📝 進捗トラッキング

### Gitコミット規約

```bash
# Day 1 完了時
git commit -m "feat(qr): Add QRCode and QRCodeScan models

- Add QRCode model with 16 fields
- Add QRCodeScan model for tracking
- Create Alembic migration
- Add Pydantic schemas

Related: QR_CODE_IMPLEMENTATION_PLAN.md Day 1"

# 各タスク完了時
git commit -m "feat(qr): Add QRCode model"
git commit -m "feat(qr): Add QRCodeScan model"
git commit -m "chore(qr): Add database migration"
git commit -m "feat(qr): Add Pydantic schemas"
```

### 日次レポート

毎日EOD（End of Day）にSlackへ：

```
📊 QRコード実装 - Day X 進捗

✅ 完了:
- Task 1.1: QRCodeモデル
- Task 1.2: QRCodeScanモデル

🚧 進行中:
- Task 1.3: マイグレーション

⏰ 明日:
- Task 1.4: Pydanticスキーマ
- Task 2.1: QRCodeService

⚠️ ブロッカー:
- なし
```

---

## 🎉 Let's Start!

Day 1を開始しましょう！

**最初の一歩**:
```bash
cd backend
source venv/bin/activate
touch app/models/qr_code.py
code app/models/qr_code.py  # または vim/nano
```

実装計画書（`docs/QR_CODE_IMPLEMENTATION_PLAN.md`）を開いて、データモデル定義をコピー＆ペーストから始めるのもOKです。

質問があれば、いつでもSlackで！

頑張りましょう！💪

---

**作成日**: 2025-11-11  
**更新日**: 2025-11-11  
**次回更新**: Day 1完了時
