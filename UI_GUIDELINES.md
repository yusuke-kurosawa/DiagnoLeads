# UI/UX ガイドライン - DiagnoLeads

このドキュメントは、DiagnoLeads フロントエンドの一貫性のある UI/UX を実現するためのガイドラインです。すべてのコンポーネント開発時に従ってください。

## 1. デザイン原則

### 1.1 ユーザー体験を最優先
- すべてのインタラクションは、ユーザーの意図を最初から理解する
- シンプルで直感的なデザイン
- 常にアクセシビリティを考慮

### 1.2 一貫性
- 同じ目的を持つコンポーネントは統一されたスタイルを使用
- 色、サイズ、フォント、スペーシングは指定されたシステムに従う

### 1.3 視認性と可視性
- すべてのボタン、テキスト、要素は十分な色コントラストを持つ
- 色のみに頼らずに情報を区別できる（AAA準拠を目指す）
- 最小フォントサイズ: 12px

## 2. カラーシステム

### 2.1 基本色

Tailwind CSS の標準パレットを使用します：

| 名前 | Tailwind Class | 用途 |
|------|----------------|------|
| **Blue** | `blue-600` / `blue-700` | プライマリアクション、リンク、フォーカス |
| **Gray** | `gray-100` ～ `gray-900` | ニュートラル、背景、テキスト |
| **Green** | `green-600` / `green-700` | 成功、完了、肯定的なアクション |
| **Red** | `red-600` / `red-700` | 破壊的アクション、エラー、警告 |
| **Amber** | `amber-500` / `amber-600` | 注意、情報 |

### 2.2 色の使用ルール

**背景:**
- ページ背景: `bg-white` または `bg-gray-50`
- コンテナ背景: `bg-white`
- ホバー状態背景: `bg-gray-50` または `bg-gray-100`

**テキスト:**
- 本文: `text-gray-900`
- 説明テキスト: `text-gray-600`
- 補足テキスト: `text-gray-500`
- 無効テキスト: `text-gray-400`

**必須フィールド:**
- マーク: `text-red-600`

### 2.3 カスタムカラートークンの廃止

⚠️ **重要**: `primary-600`、`success-600` などのカスタムカラートークンは使用しないでください。
代わりに、Tailwind CSS の標準色を直接使用してください：

```tsx
// ❌ 使用禁止
className="bg-primary-600 text-success-600"

// ✅ 推奨
className="bg-blue-600 text-green-600"
```

## 3. ボタンコンポーネント

### 3.1 バリアント

```tsx
<Button variant="primary">プライマリアクション</Button>    // 青
<Button variant="secondary">セカンダリアクション</Button>  // グレー
<Button variant="success">成功</Button>                    // 緑
<Button variant="destructive">削除</Button>                // 赤
<Button variant="outline">アウトライン</Button>            // 枠線
<Button variant="ghost">ゴースト</Button>                  // 透明
<Button variant="link">リンク</Button>                     // テキスト
```

### 3.2 サイズ

```tsx
<Button size="xs">超小</Button>      // h-7
<Button size="sm">小</Button>        // h-9
<Button size="md">中（デフォルト）</Button> // h-10
<Button size="lg">大</Button>        // h-12
<Button size="xl">超大</Button>      // h-14
<Button size="icon">アイコン</Button> // h-10 w-10
```

### 3.3 スタイル定義

| バリアント | 背景色 | テキスト色 | ホバー背景 | 説明 |
|-----------|-------|----------|----------|------|
| primary | `bg-blue-600` | `text-white` | `bg-blue-700` | CTA、主要アクション |
| secondary | `bg-gray-100` | `text-gray-900` | `bg-gray-200` | サブアクション |
| success | `bg-green-600` | `text-white` | `bg-green-700` | 成功、確認 |
| destructive | `bg-red-600` | `text-white` | `bg-red-700` | 削除、キャンセル |
| outline | `bg-white` + `border-2 border-gray-300` | `text-gray-700` | `bg-gray-50` | セカンダリ |
| ghost | `bg-transparent` | `text-gray-700` | `bg-gray-100` | ツールバー |
| link | `bg-transparent` | `text-blue-600` | `text-blue-700` underline | インラインリンク |

### 3.4 アイコン付きボタン

```tsx
import { Plus, Trash2 } from 'lucide-react';

<Button leftIcon={<Plus className="w-4 h-4" />}>
  診断を作成
</Button>

<Button rightIcon={<Trash2 className="w-4 h-4" />}>
  削除
</Button>
```

### 3.5 ボタンの可視性チェックリスト

ボタンを実装する際に、以下を必ず確認してください：

- [ ] テキストと背景に十分なコントラストがあるか（AAA準拠）
- [ ] ホバー状態が視覚的に明確か
- [ ] 無効状態が視覚的に区別できるか
- [ ] 背景色がカスタムトークンではなく Tailwind 標準色か
- [ ] アイコンが背景と区別できるか

## 4. タイポグラフィ

### 4.1 フォントサイズ

Tailwind CSS の標準スケールを使用：

```css
text-xs:   0.75rem   (12px)  - キャプション、補足
text-sm:   0.875rem  (14px)  - ラベル、説明
text-base: 1rem      (16px)  - 本文（デフォルト）
text-lg:   1.125rem  (18px)  - サブタイトル
text-xl:   1.25rem   (20px)  - 見出し (H3)
text-2xl:  1.5rem    (24px)  - 見出し (H2)
text-3xl:  1.875rem  (30px)  - 見出し (H1)
```

### 4.2 フォントウェイト

```css
font-normal:   400  - 本文
font-medium:   500  - 強調、ボタン
font-semibold: 600  - 小見出し
font-bold:     700  - 見出し
```

## 5. スペーシング

### 5.1 マージン・パディング

Tailwind CSS の 4px ベースのスケール：

```
p-1 p-2 p-3 p-4 p-6 p-8 p-12 p-16
m-1 m-2 m-3 m-4 m-6 m-8 m-12 m-16
```

### 5.2 一般的なスペーシング

- **コンテナ内側**: `p-6`
- **セクション間**: `mb-8` または `mt-8`
- **要素間**: `gap-4` または `space-y-4`
- **ボタングループ**: `space-x-2` または `space-x-4`

## 6. フォーム要素

### 6.1 入力フィールド

```tsx
<input
  className="w-full px-3 py-2 border border-gray-300 rounded-lg 
             focus:outline-none focus:ring-2 focus:ring-blue-600"
/>
```

### 6.2 必須フィールド表示

```tsx
<label>
  Email <span className="text-red-600">*</span>
</label>
```

## 7. コンポーネント実装のチェックリスト

新しいコンポーネントを実装する際に確認してください：

- [ ] ダークモード対応を考慮しているか（将来的に）
- [ ] レスポンシブデザインか（モバイル優先）
- [ ] アクセシビリティか（ARIA属性、キーボード操作）
- [ ] すべてのカラーが Tailwind 標準パレットか
- [ ] カスタムカラートークンを使用していないか
- [ ] ボタンのコントラストが AAA 準拠か
- [ ] ホバー・フォーカス・アクティブ状態が定義されているか

## 8. よくある落とし穴

### ❌ 白地に白いテキスト
```tsx
// 悪い例
className="bg-white text-white"
className="bg-primary-600"  // primary-600 が定義されていない場合
```

### ✅ 正しい実装
```tsx
// 良い例
className="bg-blue-600 text-white"
className="bg-white text-gray-900"
```

### ❌ カスタムカラートークン
```tsx
className="bg-primary-600 text-success-600"
```

### ✅ Tailwind 標準色
```tsx
className="bg-blue-600 text-green-600"
```

## 9. 品質保証

### 9.1 ビジュアルテスト

各ブラウザ・デバイスで以下を確認：
- Chrome・Firefox・Safari での表示
- iPhone・iPad での表示
- 異なる画面サイズでのレスポンシブ対応

### 9.2 アクセシビリティテスト

- キーボード操作可能か（Tab、Enter）
- スクリーンリーダーで読み込みできるか
- 色のコントラストが十分か

### 9.3 ダークモード対応（将来）

`dark:` プレフィックスを使用：
```tsx
className="bg-white dark:bg-gray-900 text-gray-900 dark:text-white"
```

## 10. 更新履歴

| 日付 | 更新内容 |
|------|---------|
| 2025-11-12 | 初版作成。カスタムカラートークン廃止、Tailwind 標準色へ移行 |
