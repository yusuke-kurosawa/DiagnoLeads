# DiagnoLeads Embed Widget

フレームワーク非依存の軽量診断ウィジェット。Web Componentsを使用して、任意のWebサイトに埋め込み可能です。

## 特徴

- 🎯 **フレームワーク非依存**: Vanilla JavaScript、React、Vue、Angular など、どのフレームワークでも使用可能
- 🪶 **軽量**: バンドルサイズ < 50KB (gzip圧縮前)
- 🎨 **カスタマイズ可能**: テーマ、カラー、スタイルを自由にカスタマイズ
- 🔒 **スタイル分離**: Shadow DOM でホストサイトのCSSと干渉しない
- 📊 **GA4統合**: Google Analytics 4 で自動イベントトラッキング
- 📱 **レスポンシブ**: モバイルフレンドリーなデザイン
- ⚡ **高速**: Viteによる最適化ビルド

## インストール

### CDN経由（推奨）

```html
<script src="https://cdn.diagnoleads.com/widget/v1/diagnoleads-widget.umd.js"></script>
```

### npm経由

```bash
npm install @diagnoleads/embed-widget
```

```javascript
import '@diagnoleads/embed-widget';
```

## 使用方法

### 基本的な使い方

HTMLに以下のコードを追加するだけです:

```html
<!DOCTYPE html>
<html>
<head>
  <title>My Website</title>
</head>
<body>
  <!-- DiagnoLeads Widget -->
  <diagnoleads-widget
    tenant-id="your-tenant-id"
    assessment-id="your-assessment-id"
    api-url="https://api.diagnoleads.com"
  ></diagnoleads-widget>

  <!-- Widget Script -->
  <script src="https://cdn.diagnoleads.com/widget/v1/diagnoleads-widget.umd.js"></script>
</body>
</html>
```

### オプション設定

| 属性 | 必須 | 説明 | デフォルト |
|------|------|------|-----------|
| `tenant-id` | ✅ | テナントID | - |
| `assessment-id` | ✅ | 診断ID | - |
| `api-url` | ❌ | APIのベースURL | `http://localhost:8000` |
| `ga4-id` | ❌ | Google Analytics 4 測定ID | - |
| `theme` | ❌ | テーマ (`light` / `dark`) | `light` |
| `primary-color` | ❌ | プライマリカラー (16進数) | `#3b82f6` |

### GA4トラッキングの設定

Google Analytics 4でイベントを追跡する場合:

```html
<diagnoleads-widget
  tenant-id="your-tenant-id"
  assessment-id="your-assessment-id"
  api-url="https://api.diagnoleads.com"
  ga4-id="G-XXXXXXXXXX"
></diagnoleads-widget>
```

**追跡されるイベント**:
- `widget_loaded`: ウィジェット読み込み完了
- `assessment_started`: 診断開始
- `question_answered`: 質問回答
- `assessment_completed`: 診断完了
- `lead_submitted`: リード情報送信（コンバージョン）

### テーマとスタイルのカスタマイズ

#### ダークテーマ

```html
<diagnoleads-widget
  tenant-id="your-tenant-id"
  assessment-id="your-assessment-id"
  theme="dark"
  primary-color="#8b5cf6"
></diagnoleads-widget>
```

#### カスタムカラー

```html
<diagnoleads-widget
  tenant-id="your-tenant-id"
  assessment-id="your-assessment-id"
  primary-color="#10b981"
></diagnoleads-widget>
```

### JavaScriptでの操作

プログラムからウィジェットを制御する場合:

```javascript
// ウィジェット要素を取得
const widget = document.querySelector('diagnoleads-widget');

// 完了イベントのリスナー登録
widget.addEventListener('complete', (event) => {
  console.log('Assessment completed:', event.detail);
  // カスタム処理（例: モーダルを開く、GTMイベント送信など）
});

// プログラムから設定変更（初期化前）
widget.setAttribute('theme', 'dark');
widget.setAttribute('primary-color', '#ff6b6b');
```

### React での使用例

```jsx
import { useEffect, useRef } from 'react';

function AssessmentWidget() {
  const widgetRef = useRef(null);

  useEffect(() => {
    const handleComplete = (event) => {
      console.log('Completed:', event.detail);
    };

    const widget = widgetRef.current;
    widget?.addEventListener('complete', handleComplete);

    return () => {
      widget?.removeEventListener('complete', handleComplete);
    };
  }, []);

  return (
    <diagnoleads-widget
      ref={widgetRef}
      tenant-id="your-tenant-id"
      assessment-id="your-assessment-id"
      api-url="https://api.diagnoleads.com"
    />
  );
}
```

### Vue での使用例

```vue
<template>
  <diagnoleads-widget
    ref="widget"
    tenant-id="your-tenant-id"
    assessment-id="your-assessment-id"
    api-url="https://api.diagnoleads.com"
    @complete="handleComplete"
  />
</template>

<script setup>
import { ref, onMounted } from 'vue';

const widget = ref(null);

const handleComplete = (event) => {
  console.log('Completed:', event.detail);
};

onMounted(() => {
  // ウィジェットが準備できた後の処理
  console.log('Widget mounted:', widget.value);
});
</script>
```

## 開発

### セットアップ

```bash
cd embed
npm install
```

### 開発サーバー起動

```bash
npm run dev
```

ブラウザで http://localhost:3001 を開くとデモページが表示されます。

### ビルド

```bash
npm run build
```

ビルド成果物は `dist/` ディレクトリに生成されます:
- `diagnoleads-widget.es.js` - ES modules
- `diagnoleads-widget.umd.js` - UMD (ブラウザ/CDN用)
- `index.d.ts` - TypeScript型定義

### 型チェック

```bash
npm run type-check
```

## アーキテクチャ

```
embed/
├── src/
│   ├── index.ts                     # エントリポイント
│   ├── components/
│   │   └── DiagnoLeadsWidget.ts     # メインWebComponent
│   ├── api/
│   │   └── client.ts                # APIクライアント
│   ├── tracking/
│   │   └── ga4.ts                   # GA4トラッキング
│   └── utils/
│       └── helpers.ts               # ヘルパー関数
├── public/
│   └── demo.html                    # デモページ
├── package.json
├── tsconfig.json
├── vite.config.ts
└── README.md
```

### 主要クラス

#### DiagnoLeadsWidget

メインのWeb Componentクラス。Shadow DOMを使用してスタイルを分離。

**ライフサイクル**:
1. `connectedCallback()`: 診断データをAPIから取得
2. `render()`: 質問または結果フォームを表示
3. `handleOptionClick()`: 質問回答を処理
4. `handleLeadFormSubmit()`: リード情報を送信

#### DiagnoLeadsAPI

バックエンドAPIとの通信を担当。

**メソッド**:
- `getAssessment(assessmentId)`: 診断データ取得
- `submitLead(assessmentId, leadData)`: リード情報送信

#### GA4Tracker

Google Analytics 4イベントトラッキング。

**メソッド**:
- `trackWidgetLoaded()`: ウィジェット読み込み
- `trackAssessmentStarted()`: 診断開始
- `trackQuestionAnswered()`: 質問回答
- `trackAssessmentCompleted()`: 診断完了
- `trackLeadSubmitted()`: リード送信（コンバージョン）

## セキュリティ

- **CORS**: APIエンドポイントでCORS設定が必要
- **XSS対策**: すべてのユーザー入力をサニタイズ
- **CSP**: Content Security Policyと互換性あり
- **プライバシー**: ユーザーデータはセキュアに送信（HTTPS推奨）

## ブラウザサポート

- Chrome/Edge: 最新2バージョン
- Firefox: 最新2バージョン
- Safari: 最新2バージョン
- iOS Safari: 最新2バージョン
- Android Chrome: 最新2バージョン

Web Componentsをサポートしているブラウザであれば動作します（IE11は非対応）。

## トラブルシューティング

### ウィジェットが表示されない

1. JavaScriptコンソールでエラーを確認
2. `tenant-id`と`assessment-id`が正しいか確認
3. APIエンドポイントが正しいか確認
4. CORSエラーが出ていないか確認

### CORSエラーが発生する

バックエンドで以下のヘッダーを設定してください:

```python
# FastAPI
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 本番環境では特定のドメインのみ許可
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)
```

### GA4イベントが送信されない

1. `ga4-id`が正しいか確認（G-XXXXXXXXXXの形式）
2. ブラウザの開発者ツールのNetworkタブで`google-analytics.com`へのリクエストを確認
3. 広告ブロッカーが有効になっていないか確認

## ライセンス

MIT License

## サポート

問題が発生した場合は、以下にお問い合わせください:
- Email: support@diagnoleads.com
- GitHub Issues: https://github.com/diagnoleads/embed-widget/issues
