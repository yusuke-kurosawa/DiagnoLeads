# Design System Specification

## Overview

DiagnoLeadsのデザインシステム仕様。一貫性のある、モダンで洗練されたUI/UXを提供するための基盤となるデザイントークンとガイドラインを定義します。

## Design Principles

### 1. プロフェッショナル & モダン
B2B SaaS製品として、信頼性とプロフェッショナリズムを表現しつつ、最新のデザイントレンドを取り入れる。

### 2. 明確な視覚階層
情報の重要度に応じた明確な視覚階層を構築し、ユーザーの認知負荷を軽減する。

### 3. 一貫性
すべてのページ・コンポーネントで一貫したデザイン言語を使用する。

### 4. アクセシビリティ
WCAG 2.1 AAレベルに準拠し、すべてのユーザーが使いやすいUIを提供する。

### 5. パフォーマンス
軽量で高速なUIを実現し、優れたユーザー体験を提供する。

---

## Color System

### Brand Colors

**Primary Color (Brand Identity)**
```css
--primary-50: #eff6ff;   /* 最も明るい（背景用） */
--primary-100: #dbeafe;
--primary-200: #bfdbfe;
--primary-300: #93c5fd;
--primary-400: #60a5fa;
--primary-500: #3b82f6;  /* メインブランドカラー */
--primary-600: #2563eb;  /* ボタン、リンク（デフォルト） */
--primary-700: #1d4ed8;  /* ボタンhover */
--primary-800: #1e40af;
--primary-900: #1e3a8a;  /* 最も暗い */
```

**Accent Color (Secondary Actions)**
```css
--accent-50: #f0f9ff;
--accent-100: #e0f2fe;
--accent-200: #bae6fd;
--accent-300: #7dd3fc;
--accent-400: #38bdf8;
--accent-500: #0ea5e9;  /* アクセントカラー */
--accent-600: #0284c7;
--accent-700: #0369a1;
--accent-800: #075985;
--accent-900: #0c4a6e;
```

### Semantic Colors

**Success (成功状態)**
```css
--success-50: #f0fdf4;
--success-100: #dcfce7;
--success-500: #22c55e;  /* メイン */
--success-600: #16a34a;  /* デフォルト */
--success-700: #15803d;  /* hover */
```

**Warning (警告)**
```css
--warning-50: #fffbeb;
--warning-100: #fef3c7;
--warning-500: #f59e0b;  /* メイン */
--warning-600: #d97706;  /* デフォルト */
--warning-700: #b45309;  /* hover */
```

**Error (エラー)**
```css
--error-50: #fef2f2;
--error-100: #fee2e2;
--error-500: #ef4444;  /* メイン */
--error-600: #dc2626;  /* デフォルト */
--error-700: #b91c1c;  /* hover */
```

**Info (情報)**
```css
--info-50: #f0f9ff;
--info-100: #e0f2fe;
--info-500: #3b82f6;  /* メイン */
--info-600: #2563eb;  /* デフォルト */
--info-700: #1d4ed8;  /* hover */
```

### Neutral Colors (Grayscale)

```css
--gray-50: #f9fafb;   /* 背景（明） */
--gray-100: #f3f4f6;  /* 背景（カード） */
--gray-200: #e5e7eb;  /* ボーダー（明） */
--gray-300: #d1d5db;  /* ボーダー */
--gray-400: #9ca3af;  /* プレースホルダー */
--gray-500: #6b7280;  /* セカンダリテキスト */
--gray-600: #4b5563;  /* プライマリテキスト */
--gray-700: #374151;
--gray-800: #1f2937;  /* 見出し */
--gray-900: #111827;  /* 最も濃いテキスト */
```

### Special Colors

**Gradient Backgrounds**
```css
--gradient-primary: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
--gradient-accent: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
--gradient-success: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
--gradient-subtle: linear-gradient(180deg, #ffffff 0%, #f9fafb 100%);
```

**Glassmorphism**
```css
--glass-background: rgba(255, 255, 255, 0.7);
--glass-border: rgba(255, 255, 255, 0.18);
--glass-backdrop: blur(10px);
```

---

## Typography

### Font Families

**Primary Font (UI Text)**
```css
--font-sans: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', 
             'Helvetica Neue', Arial, sans-serif;
```

**Secondary Font (Headings - Optional)**
```css
--font-display: 'Poppins', 'Inter', sans-serif;
```

**Monospace (Code)**
```css
--font-mono: 'JetBrains Mono', 'Fira Code', 'Consolas', monospace;
```

### Font Sizes

**Scale (Tailwind-based)**
```css
--text-xs: 0.75rem;     /* 12px - 補足情報 */
--text-sm: 0.875rem;    /* 14px - セカンダリテキスト */
--text-base: 1rem;      /* 16px - ベーステキスト */
--text-lg: 1.125rem;    /* 18px - 強調テキスト */
--text-xl: 1.25rem;     /* 20px - 小見出し */
--text-2xl: 1.5rem;     /* 24px - セクション見出し */
--text-3xl: 1.875rem;   /* 30px - ページ見出し */
--text-4xl: 2.25rem;    /* 36px - メインヘッダー */
--text-5xl: 3rem;       /* 48px - ヒーローテキスト */
```

### Font Weights

```css
--font-light: 300;
--font-normal: 400;
--font-medium: 500;
--font-semibold: 600;
--font-bold: 700;
--font-extrabold: 800;
```

### Line Heights

```css
--leading-none: 1;
--leading-tight: 1.25;
--leading-snug: 1.375;
--leading-normal: 1.5;
--leading-relaxed: 1.625;
--leading-loose: 2;
```

### Typography Usage

**Headings**
- H1: `text-4xl font-bold text-gray-900` - ページタイトル
- H2: `text-3xl font-semibold text-gray-800` - セクションタイトル
- H3: `text-2xl font-semibold text-gray-800` - サブセクション
- H4: `text-xl font-medium text-gray-700` - カードタイトル
- H5: `text-lg font-medium text-gray-700` - 小見出し

**Body Text**
- Primary: `text-base text-gray-700` - メイン本文
- Secondary: `text-sm text-gray-600` - 補足説明
- Caption: `text-xs text-gray-500` - キャプション、タイムスタンプ

**Special**
- Lead: `text-lg text-gray-600 leading-relaxed` - リードテキスト
- Label: `text-sm font-medium text-gray-700` - フォームラベル

---

## Spacing System

### Scale (8px Base Unit)

```css
--space-0: 0;
--space-1: 0.25rem;   /* 4px */
--space-2: 0.5rem;    /* 8px */
--space-3: 0.75rem;   /* 12px */
--space-4: 1rem;      /* 16px */
--space-5: 1.25rem;   /* 20px */
--space-6: 1.5rem;    /* 24px */
--space-8: 2rem;      /* 32px */
--space-10: 2.5rem;   /* 40px */
--space-12: 3rem;     /* 48px */
--space-16: 4rem;     /* 64px */
--space-20: 5rem;     /* 80px */
--space-24: 6rem;     /* 96px */
```

### Usage Guidelines

**Component Padding**
- Small: `p-3` (12px) - Compact buttons, badges
- Medium: `p-4` (16px) - Default buttons, form inputs
- Large: `p-6` (24px) - Cards, modals

**Section Spacing**
- Tight: `space-y-4` (16px) - Related items
- Normal: `space-y-6` (24px) - Section elements
- Loose: `space-y-8` (32px) - Major sections

**Container Padding**
- Mobile: `px-4 py-6` (16px / 24px)
- Tablet: `px-6 py-8` (24px / 32px)
- Desktop: `px-8 py-10` (32px / 40px)

---

## Shadow System (Elevation)

### Levels

```css
/* Subtle - ほとんど見えない影 */
--shadow-xs: 0 1px 2px 0 rgba(0, 0, 0, 0.05);

/* Small - カード、入力フィールド */
--shadow-sm: 0 1px 3px 0 rgba(0, 0, 0, 0.1), 
             0 1px 2px -1px rgba(0, 0, 0, 0.1);

/* Medium - ボタン、ドロップダウン */
--shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 
             0 2px 4px -2px rgba(0, 0, 0, 0.1);

/* Large - モーダル、ポップアップ */
--shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 
             0 4px 6px -4px rgba(0, 0, 0, 0.1);

/* XLarge - ドロワー */
--shadow-xl: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 
             0 8px 10px -6px rgba(0, 0, 0, 0.1);

/* 2XLarge - 最大強調 */
--shadow-2xl: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
```

### Colored Shadows (Accent)

```css
/* Primary action buttons */
--shadow-primary: 0 4px 14px 0 rgba(59, 130, 246, 0.39);

/* Success states */
--shadow-success: 0 4px 14px 0 rgba(34, 197, 94, 0.39);

/* Warning states */
--shadow-warning: 0 4px 14px 0 rgba(245, 158, 11, 0.39);
```

---

## Border Radius

```css
--radius-none: 0;
--radius-sm: 0.25rem;   /* 4px - Tags, badges */
--radius-md: 0.375rem;  /* 6px - Buttons, inputs */
--radius-lg: 0.5rem;    /* 8px - Cards */
--radius-xl: 0.75rem;   /* 12px - Modals */
--radius-2xl: 1rem;     /* 16px - Large containers */
--radius-full: 9999px;  /* Circle - Avatars */
```

---

## Animation & Transition

### Duration

```css
--duration-fast: 150ms;
--duration-normal: 200ms;
--duration-slow: 300ms;
--duration-slower: 500ms;
```

### Easing Functions

```css
--ease-in: cubic-bezier(0.4, 0, 1, 1);
--ease-out: cubic-bezier(0, 0, 0.2, 1);
--ease-in-out: cubic-bezier(0.4, 0, 0.2, 1);
--ease-spring: cubic-bezier(0.68, -0.55, 0.265, 1.55);
```

### Common Transitions

```css
--transition-all: all 200ms cubic-bezier(0.4, 0, 0.2, 1);
--transition-colors: color, background-color, border-color 200ms;
--transition-transform: transform 200ms cubic-bezier(0.4, 0, 0.2, 1);
--transition-opacity: opacity 200ms cubic-bezier(0.4, 0, 0.2, 1);
```

---

## Z-Index System

```css
--z-base: 0;
--z-dropdown: 1000;
--z-sticky: 1020;
--z-fixed: 1030;
--z-modal-backdrop: 1040;
--z-modal: 1050;
--z-popover: 1060;
--z-tooltip: 1070;
--z-notification: 1080;
```

---

## Breakpoints (Responsive Design)

```css
--breakpoint-sm: 640px;   /* Mobile landscape */
--breakpoint-md: 768px;   /* Tablet */
--breakpoint-lg: 1024px;  /* Desktop */
--breakpoint-xl: 1280px;  /* Large desktop */
--breakpoint-2xl: 1536px; /* Extra large */
```

### Usage in Tailwind

```html
<!-- Mobile first approach -->
<div class="w-full md:w-1/2 lg:w-1/3">
  <!-- Full width on mobile, half on tablet, third on desktop -->
</div>
```

---

## Implementation Guide

### 1. CSS Variables Setup

Create `/frontend/src/styles/design-tokens.css`:

```css
:root {
  /* Colors */
  --primary-600: #2563eb;
  --primary-700: #1d4ed8;
  
  /* Typography */
  --font-sans: 'Inter', sans-serif;
  
  /* Spacing */
  --space-4: 1rem;
  
  /* Shadows */
  --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
  
  /* ... all tokens */
}
```

### 2. Tailwind Config Extension

Update `/frontend/tailwind.config.js`:

```js
export default {
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#eff6ff',
          600: '#2563eb',
          700: '#1d4ed8',
          // ...
        },
      },
      fontFamily: {
        sans: ['Inter', 'sans-serif'],
      },
      boxShadow: {
        'primary': '0 4px 14px 0 rgba(59, 130, 246, 0.39)',
      },
    },
  },
}
```

### 3. Global Styles Import

In `/frontend/src/index.css`:

```css
@import './styles/design-tokens.css';

@tailwind base;
@tailwind components;
@tailwind utilities;

/* Custom utility classes */
@layer utilities {
  .glass {
    background: rgba(255, 255, 255, 0.7);
    backdrop-filter: blur(10px);
    border: 1px solid rgba(255, 255, 255, 0.18);
  }
}
```

---

## Design Token Documentation

### For Designers
- Use Figma Variables to mirror these tokens
- Export designs with consistent naming
- Reference: [Figma Design Tokens Plugin](https://www.figma.com/community/plugin/888356646278934516/Design-Tokens)

### For Developers
- Always use design tokens, never hardcode values
- Use Tailwind utility classes when possible
- For custom CSS, reference CSS variables

---

## Related Specifications

- [Component Library](./component-library.md) - UI components implementation
- [Usability Guidelines](./usability-guidelines.md) - Accessibility & best practices
- [Interaction Patterns](./interaction-patterns.md) - Animations & micro-interactions

---

## Changelog

- 2025-11-11: Initial design system specification
