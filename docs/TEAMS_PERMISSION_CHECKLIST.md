# Microsoft Teams API 権限設定チェックリスト

## ⚠️ 現在の状況: すべてのAPIで403エラー

すべてのMicrosoft Graph APIエンドポイントで権限エラーが発生しています。以下のチェックリストを確認してください。

---

## 📋 チェックリスト

### 1. 正しいアプリを選択していますか？

Azure Portal → **Azure Active Directory** → **App registrations** で:

- ✅ アプリ名: **DiagnoLeads Teams Integration localhost**
- ✅ Application (client) ID: `08ac2808-5c23-4f76-a5c1-69b6317d0f68`

**⚠️ 重要**: 同じような名前のアプリが複数ある場合、Client IDで正しいアプリを確認してください。

---

### 2. **Application permissions** を選択していますか？（最重要）

**間違った選択（❌ これではない）:**
- ❌ **Delegated permissions** → これはユーザーの代わりに動作する権限

**正しい選択（✅ これが必要）:**
- ✅ **Application permissions** → アプリ自体が動作する権限

#### 確認方法:
1. App registrations → あなたのアプリ → **API permissions**
2. 各権限の **Type** 列を確認
3. すべて **Application** と表示されている必要があります

---

### 3. 必要な権限を追加していますか？

以下の権限が **Application permissions** として追加されている必要があります:

| 権限名 | タイプ | ステータス |
|---|---|---|
| `Group.Read.All` | Application | ✅ 必須 |
| `Team.ReadBasic.All` | Application | ✅ 必須 |
| `Channel.ReadBasic.All` | Application | ⚠️ 推奨 |
| `User.Read.All` | Application | ⚠️ オプション |

#### 追加手順:
1. **Add a permission** をクリック
2. **Microsoft Graph** を選択
3. **Application permissions** を選択（Delegatedではない！）
4. 検索ボックスで権限名を検索
5. チェックボックスを選択
6. **Add permissions** をクリック

---

### 4. 管理者の同意を付与していますか？（最重要）

**これがない場合、権限が有効になりません！**

#### 確認方法:
1. API permissions画面を開く
2. 各権限の **Status** 列を確認
3. **すべて** に緑のチェックマーク ✅ と **"Granted for [Your Organization]"** が表示されている必要があります

#### まだ付与していない場合:
1. **Grant admin consent for [Your Organization]** ボタンをクリック
2. 確認ダイアログで **Yes** をクリック
3. すべての権限のStatusが緑のチェックマークになることを確認

**⚠️ 注意**: このボタンが表示されない、またはクリックできない場合、Azure AD管理者権限が不足しています。

---

### 5. 権限の反映を待ちましたか？

権限変更後、**5-10分** 待つ必要がある場合があります。

- トークンがキャッシュされている
- Microsoftのシステムで権限が反映されるまで時間がかかる

#### 待機後の確認:
```bash
cd /home/kurosawa/DiagnoLeads/backend
./venv/bin/python test_teams_permissions.py
```

---

## 🖼️ スクリーンショット付きガイド

### ステップ1: API permissions画面を開く

```
Azure Portal
└── Azure Active Directory
    └── App registrations
        └── DiagnoLeads Teams Integration localhost
            └── API permissions  ← ここをクリック
```

### ステップ2: 現在の状態を確認

API permissions画面で以下を確認:

```
Configured permissions:
┌─────────────────────────┬──────────────┬────────────────────────┐
│ API / Permission name   │ Type         │ Status                 │
├─────────────────────────┼──────────────┼────────────────────────┤
│ Group.Read.All          │ Application  │ ✅ Granted for ...     │
│ Team.ReadBasic.All      │ Application  │ ✅ Granted for ...     │
│ Channel.ReadBasic.All   │ Application  │ ✅ Granted for ...     │
└─────────────────────────┴──────────────┴────────────────────────┘
```

**❌ 問題のある例:**
```
┌─────────────────────────┬──────────────┬────────────────────────┐
│ Group.Read.All          │ Delegated    │ ❌ Not granted         │  ← Delegated (間違い)
│ Team.ReadBasic.All      │ Application  │ ❌ Not granted         │  ← 同意未付与
└─────────────────────────┴──────────────┴────────────────────────┘
```

### ステップ3: Application permissions を追加

1. **Add a permission** をクリック
2. **Microsoft Graph** を選択
3. **⚠️ Application permissions** を選択（上のタブ）
4. 検索ボックスで `Group.Read.All` を検索
5. チェックボックスを選択
6. **Add permissions** をクリック
7. 同様に `Team.ReadBasic.All`, `Channel.ReadBasic.All` を追加

### ステップ4: 管理者の同意を付与

1. API permissions画面で **Grant admin consent for [Your Organization]** をクリック
2. ダイアログで **Yes** をクリック
3. ページをリフレッシュ
4. すべての権限に緑のチェックマーク ✅ が表示されることを確認

---

## 🔍 トラブルシューティング

### Q1: "Grant admin consent" ボタンが表示されない

**原因**: Azure AD管理者権限がないアカウントでログインしている

**解決策**:
- Azure AD管理者アカウントでログインし直す
- または、IT部門/管理者に依頼する

必要な権限:
- **Application Administrator** または
- **Cloud Application Administrator** または
- **Global Administrator**

---

### Q2: 権限を追加したが、Typeが "Delegated" になっている

**原因**: 権限追加時に "Delegated permissions" タブを選択してしまった

**解決策**:
1. その権限を削除（権限行の右端の `...` → Remove permission）
2. 再度追加時に **Application permissions** タブを選択
3. 管理者の同意を再度付与

---

### Q3: 管理者の同意を付与したが、まだ403エラー

**原因1**: トークンキャッシュ
- 待機時間: 5-10分

**原因2**: 間違ったアプリに権限を設定した
- Client IDを再確認: `08ac2808-5c23-4f76-a5c1-69b6317d0f68`

**原因3**: 権限のTypeが間違っている
- すべて "Application" になっているか確認

---

### Q4: "Error: AADSTS65001: The user or administrator has not consented"

**原因**: 管理者の同意が付与されていない

**解決策**: ステップ4の管理者同意を実行

---

## ✅ 正常動作時の出力

権限が正しく設定されている場合、以下のような出力が表示されます:

```bash
$ ./venv/bin/python test_teams_permissions.py

============================================================
Microsoft Teams API Permissions Test
============================================================

1. Getting Access Token...
✅ Access token acquired successfully

============================================================
Testing: All Groups (for Teams)
Endpoint: https://graph.microsoft.com/v1.0/groups?$top=5
Required Permission: Group.Read.All
============================================================
✅ SUCCESS: Retrieved 8 items
Status: 200

============================================================
TEST SUMMARY
============================================================
✅ PASS: All Groups (for Teams)

Total: 1/1 tests passed

🎉 All tests passed! Teams integration is ready.
```

---

## 📞 サポートが必要な場合

以下の情報を用意してIT部門/管理者に連絡してください:

```
件名: Azure AD App への API権限付与の依頼

アプリ情報:
- アプリ名: DiagnoLeads Teams Integration localhost
- Client ID: 08ac2808-5c23-4f76-a5c1-69b6317d0f68
- Tenant ID: afa5f8a9-ec65-4590-a8b5-f375824a68e7

必要な権限（Microsoft Graph - Application permissions）:
1. Group.Read.All
2. Team.ReadBasic.All
3. Channel.ReadBasic.All

作業:
1. 上記権限を "Application permissions" として追加
2. 管理者の同意を付与 ("Grant admin consent")

目的: Microsoft Teams との統合機能のため
```

---

**最終更新**: 2025-11-11  
**ステータス**: 権限設定の再確認が必要
