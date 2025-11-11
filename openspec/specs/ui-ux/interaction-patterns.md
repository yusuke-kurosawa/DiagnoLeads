# Interaction Patterns Specification

## Overview

DiagnoLeadsのインタラクションパターン仕様。アニメーション、トランジション、マイクロインタラクションを定義し、直感的で楽しいユーザー体験を提供します。

---

## Animation Principles

### 1. Purpose-Driven
アニメーションは装飾ではなく、目的を持つ：
- **Feedback**: ユーザーの操作に対する反応
- **Guidance**: ユーザーの注意を引く
- **Context**: 状態の変化を説明
- **Delight**: 楽しい体験を提供

### 2. Subtle & Fast
- 過度なアニメーションは避ける
- デュレーション: 150-300ms（ほとんどの場合）
- 自然なイージング関数を使用

### 3. Respect User Preferences
```tsx
// Respect prefers-reduced-motion
@media (prefers-reduced-motion: reduce) {
  * {
    animation-duration: 0.01ms !important;
    transition-duration: 0.01ms !important;
  }
}
```

---

## Transition System

### Duration Scale

```css
--duration-instant: 0ms;      /* Immediate change */
--duration-fast: 150ms;       /* Quick feedback */
--duration-normal: 200ms;     /* Default */
--duration-moderate: 300ms;   /* Noticeable */
--duration-slow: 500ms;       /* Deliberate */
--duration-slower: 700ms;     /* Page transitions */
```

### Easing Functions

```css
/* Accelerating (ease-in) - Entering */
--ease-in: cubic-bezier(0.4, 0, 1, 1);

/* Decelerating (ease-out) - Exiting */
--ease-out: cubic-bezier(0, 0, 0.2, 1);

/* Smooth (ease-in-out) - Default */
--ease-in-out: cubic-bezier(0.4, 0, 0.2, 1);

/* Spring (bounce) - Playful */
--ease-spring: cubic-bezier(0.68, -0.55, 0.265, 1.55);

/* Sharp - Attention */
--ease-sharp: cubic-bezier(0.4, 0, 0.6, 1);
```

### Usage Guidelines

**Enter**: `ease-out` (Start fast, end slow)
**Exit**: `ease-in` (Start slow, end fast)
**Move**: `ease-in-out` (Smooth throughout)

---

## Button Interactions

### Hover Effects

**Primary Button**
```tsx
<Button className="
  bg-primary-600 
  hover:bg-primary-700 
  hover:shadow-primary
  hover:scale-105
  transition-all duration-200
">
  クリック
</Button>
```

**Ghost Button**
```tsx
<Button variant="ghost" className="
  hover:bg-gray-100
  hover:scale-105
  transition-all duration-150
">
  <IconEdit />
</Button>
```

### Active (Pressed) State

```tsx
<Button className="
  active:scale-95
  active:shadow-inner
  transition-transform duration-100
">
  プレス
</Button>
```

### Loading State

**Spinner Animation**
```tsx
<Button loading className="relative">
  {isLoading && (
    <span className="absolute inset-0 flex items-center justify-center">
      <Spinner className="animate-spin" />
    </span>
  )}
  <span className={isLoading ? 'opacity-0' : 'opacity-100'}>
    送信
  </span>
</Button>
```

**CSS Animation**
```css
@keyframes spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

.animate-spin {
  animation: spin 1s linear infinite;
}
```

---

## Card Interactions

### Hover Elevation

**Standard Card**
```tsx
<Card className="
  shadow-sm
  hover:shadow-md
  hover:-translate-y-1
  transition-all duration-300
  cursor-pointer
">
  {content}
</Card>
```

**Interactive Card**
```tsx
<Card className="
  shadow-md
  hover:shadow-xl
  hover:-translate-y-2
  hover:scale-[1.02]
  transition-all duration-300 ease-out
  cursor-pointer
  group
">
  <CardContent>
    <h3 className="group-hover:text-primary-600 transition-colors">
      タイトル
    </h3>
  </CardContent>
</Card>
```

### Click/Tap Feedback

```tsx
<Card className="
  active:scale-[0.98]
  active:shadow-sm
  transition-all duration-100
">
  {content}
</Card>
```

---

## Modal & Overlay Animations

### Fade In/Out

**Overlay (Backdrop)**
```tsx
// Using Framer Motion
<motion.div
  initial={{ opacity: 0 }}
  animate={{ opacity: 1 }}
  exit={{ opacity: 0 }}
  transition={{ duration: 0.2 }}
  className="fixed inset-0 bg-black/50 backdrop-blur-sm"
/>
```

**Modal Content**
```tsx
<motion.div
  initial={{ opacity: 0, scale: 0.95, y: 20 }}
  animate={{ opacity: 1, scale: 1, y: 0 }}
  exit={{ opacity: 0, scale: 0.95, y: 20 }}
  transition={{ duration: 0.2, ease: 'easeOut' }}
  className="bg-white rounded-lg p-6 max-w-md"
>
  {content}
</motion.div>
```

### Slide In/Out

**Drawer (Side Panel)**
```tsx
// From right
<motion.div
  initial={{ x: '100%' }}
  animate={{ x: 0 }}
  exit={{ x: '100%' }}
  transition={{ duration: 0.3, ease: 'easeInOut' }}
  className="fixed right-0 top-0 h-full w-96 bg-white shadow-2xl"
>
  {content}
</motion.div>

// From bottom
<motion.div
  initial={{ y: '100%' }}
  animate={{ y: 0 }}
  exit={{ y: '100%' }}
  transition={{ duration: 0.3, ease: 'easeInOut' }}
  className="fixed bottom-0 left-0 right-0 bg-white rounded-t-2xl p-6"
>
  {content}
</motion.div>
```

---

## Dropdown & Popover Animations

### Dropdown Menu

```tsx
<motion.div
  initial={{ opacity: 0, y: -10 }}
  animate={{ opacity: 1, y: 0 }}
  exit={{ opacity: 0, y: -10 }}
  transition={{ duration: 0.15 }}
  className="absolute top-full mt-2 right-0 bg-white rounded-lg shadow-lg"
>
  <DropdownMenuItem>項目1</DropdownMenuItem>
  <DropdownMenuItem>項目2</DropdownMenuItem>
</motion.div>
```

### Popover

```tsx
<motion.div
  initial={{ opacity: 0, scale: 0.9 }}
  animate={{ opacity: 1, scale: 1 }}
  exit={{ opacity: 0, scale: 0.9 }}
  transition={{ duration: 0.15 }}
  className="absolute z-50 bg-white rounded-lg shadow-xl p-4"
>
  {content}
</motion.div>
```

---

## Toast Notifications

### Slide In from Top

```tsx
<motion.div
  initial={{ opacity: 0, y: -50 }}
  animate={{ opacity: 1, y: 0 }}
  exit={{ opacity: 0, y: -50 }}
  transition={{ duration: 0.3, ease: 'easeOut' }}
  className="fixed top-4 right-4 bg-white rounded-lg shadow-lg p-4"
>
  <div className="flex items-start gap-3">
    <IconCheck className="text-success-600" />
    <div>
      <h4 className="font-semibold">成功</h4>
      <p className="text-sm text-gray-600">保存しました</p>
    </div>
  </div>
</motion.div>
```

### Slide In from Bottom

```tsx
<motion.div
  initial={{ opacity: 0, y: 50 }}
  animate={{ opacity: 1, y: 0 }}
  exit={{ opacity: 0, y: 50 }}
  transition={{ duration: 0.3, ease: 'easeOut' }}
  className="fixed bottom-4 right-4 bg-white rounded-lg shadow-lg p-4"
>
  {content}
</motion.div>
```

### Auto-dismiss with Progress

```tsx
<motion.div className="relative overflow-hidden">
  <div className="p-4">
    {content}
  </div>
  
  {/* Progress bar */}
  <motion.div
    initial={{ width: '100%' }}
    animate={{ width: '0%' }}
    transition={{ duration: 3, ease: 'linear' }}
    className="absolute bottom-0 left-0 h-1 bg-primary-600"
  />
</motion.div>
```

---

## Loading Animations

### Skeleton Pulse

```tsx
<div className="animate-pulse">
  <div className="h-4 bg-gray-200 rounded w-3/4 mb-2"></div>
  <div className="h-4 bg-gray-200 rounded w-1/2"></div>
</div>
```

**CSS Animation**
```css
@keyframes pulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.5;
  }
}

.animate-pulse {
  animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
}
```

### Shimmer Effect

```css
@keyframes shimmer {
  0% {
    background-position: -1000px 0;
  }
  100% {
    background-position: 1000px 0;
  }
}

.animate-shimmer {
  background: linear-gradient(
    90deg,
    #f0f0f0 25%,
    #e0e0e0 50%,
    #f0f0f0 75%
  );
  background-size: 1000px 100%;
  animation: shimmer 2s infinite;
}
```

### Spinner Variants

**Circular Spinner**
```tsx
<svg 
  className="animate-spin h-5 w-5 text-primary-600"
  xmlns="http://www.w3.org/2000/svg"
  fill="none"
  viewBox="0 0 24 24"
>
  <circle 
    className="opacity-25" 
    cx="12" 
    cy="12" 
    r="10" 
    stroke="currentColor" 
    strokeWidth="4"
  />
  <path 
    className="opacity-75" 
    fill="currentColor" 
    d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
  />
</svg>
```

**Dot Pulse**
```tsx
<div className="flex gap-2">
  <div className="w-2 h-2 bg-primary-600 rounded-full animate-pulse" />
  <div className="w-2 h-2 bg-primary-600 rounded-full animate-pulse delay-75" />
  <div className="w-2 h-2 bg-primary-600 rounded-full animate-pulse delay-150" />
</div>
```

---

## List Animations

### Staggered Fade In

```tsx
<motion.ul>
  {items.map((item, index) => (
    <motion.li
      key={item.id}
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ 
        duration: 0.3, 
        delay: index * 0.05,
        ease: 'easeOut'
      }}
    >
      {item.name}
    </motion.li>
  ))}
</motion.ul>
```

### Add/Remove Animation

```tsx
<AnimatePresence>
  {items.map((item) => (
    <motion.div
      key={item.id}
      initial={{ opacity: 0, height: 0 }}
      animate={{ opacity: 1, height: 'auto' }}
      exit={{ opacity: 0, height: 0 }}
      transition={{ duration: 0.2 }}
    >
      {item.content}
    </motion.div>
  ))}
</AnimatePresence>
```

---

## Micro-interactions

### Checkbox

```tsx
<motion.div
  initial={false}
  animate={isChecked ? 'checked' : 'unchecked'}
  variants={{
    checked: { scale: 1, rotate: 0 },
    unchecked: { scale: 0.8, rotate: -90 }
  }}
  transition={{ duration: 0.2 }}
>
  <Checkbox checked={isChecked} onChange={setIsChecked} />
</motion.div>
```

### Toggle Switch

```tsx
<button
  onClick={() => setIsOn(!isOn)}
  className={`
    relative w-14 h-8 rounded-full transition-colors duration-200
    ${isOn ? 'bg-primary-600' : 'bg-gray-300'}
  `}
>
  <motion.span
    className="absolute top-1 left-1 w-6 h-6 bg-white rounded-full shadow"
    animate={{ x: isOn ? 24 : 0 }}
    transition={{ duration: 0.2, ease: 'easeInOut' }}
  />
</button>
```

### Like Button

```tsx
<motion.button
  whileTap={{ scale: 0.9 }}
  onClick={handleLike}
>
  <motion.div
    animate={isLiked ? { scale: [1, 1.3, 1] } : {}}
    transition={{ duration: 0.3 }}
  >
    <IconHeart 
      className={isLiked ? 'text-red-500 fill-current' : 'text-gray-400'} 
    />
  </motion.div>
</motion.button>
```

### Counter Increment

```tsx
<AnimatePresence mode="wait">
  <motion.span
    key={count}
    initial={{ y: -20, opacity: 0 }}
    animate={{ y: 0, opacity: 1 }}
    exit={{ y: 20, opacity: 0 }}
    transition={{ duration: 0.2 }}
  >
    {count}
  </motion.span>
</AnimatePresence>
```

---

## Page Transitions

### Fade Transition

```tsx
<AnimatePresence mode="wait">
  <motion.div
    key={location.pathname}
    initial={{ opacity: 0 }}
    animate={{ opacity: 1 }}
    exit={{ opacity: 0 }}
    transition={{ duration: 0.3 }}
  >
    <Routes location={location}>
      {/* Routes */}
    </Routes>
  </motion.div>
</AnimatePresence>
```

### Slide Transition

```tsx
<AnimatePresence mode="wait">
  <motion.div
    key={location.pathname}
    initial={{ x: 300, opacity: 0 }}
    animate={{ x: 0, opacity: 1 }}
    exit={{ x: -300, opacity: 0 }}
    transition={{ duration: 0.3, ease: 'easeInOut' }}
  >
    <Routes location={location}>
      {/* Routes */}
    </Routes>
  </motion.div>
</AnimatePresence>
```

---

## Scroll Animations

### Fade In on Scroll

```tsx
import { useInView } from 'framer-motion';

const FadeInSection = ({ children }) => {
  const ref = useRef(null);
  const isInView = useInView(ref, { once: true, margin: '-100px' });
  
  return (
    <motion.div
      ref={ref}
      initial={{ opacity: 0, y: 50 }}
      animate={isInView ? { opacity: 1, y: 0 } : { opacity: 0, y: 50 }}
      transition={{ duration: 0.5 }}
    >
      {children}
    </motion.div>
  );
};
```

### Parallax Effect

```tsx
const ParallaxSection = ({ children }) => {
  const { scrollY } = useScroll();
  const y = useTransform(scrollY, [0, 1000], [0, 300]);
  
  return (
    <motion.div style={{ y }}>
      {children}
    </motion.div>
  );
};
```

### Progress Indicator

```tsx
const ScrollProgress = () => {
  const { scrollYProgress } = useScroll();
  
  return (
    <motion.div
      style={{ scaleX: scrollYProgress }}
      className="fixed top-0 left-0 right-0 h-1 bg-primary-600 origin-left z-50"
    />
  );
};
```

---

## Form Interactions

### Input Focus

```tsx
<div className="relative">
  <Input
    onFocus={() => setIsFocused(true)}
    onBlur={() => setIsFocused(false)}
    className="peer"
  />
  <motion.div
    className="absolute inset-0 border-2 border-primary-600 rounded-lg pointer-events-none"
    initial={{ opacity: 0, scale: 0.95 }}
    animate={isFocused ? { opacity: 1, scale: 1 } : { opacity: 0, scale: 0.95 }}
    transition={{ duration: 0.2 }}
  />
</div>
```

### Label Float

```tsx
<div className="relative">
  <input
    id="email"
    type="text"
    className="peer w-full pt-6 pb-2 px-3 border rounded"
    placeholder=" "
  />
  <label
    htmlFor="email"
    className="
      absolute left-3 top-1/2 -translate-y-1/2
      text-gray-500 transition-all duration-200
      peer-placeholder-shown:top-1/2
      peer-placeholder-shown:text-base
      peer-focus:top-2
      peer-focus:text-xs
      peer-focus:text-primary-600
    "
  >
    メールアドレス
  </label>
</div>
```

### Submit Button

```tsx
<motion.button
  whileHover={{ scale: 1.05 }}
  whileTap={{ scale: 0.95 }}
  className="
    bg-primary-600 text-white px-6 py-3 rounded-lg
    transition-colors duration-200
    hover:bg-primary-700
  "
>
  送信
</motion.button>
```

---

## Drag & Drop

### Draggable Item

```tsx
<motion.div
  drag
  dragConstraints={{ left: 0, right: 300, top: 0, bottom: 300 }}
  dragElastic={0.1}
  whileDrag={{ scale: 1.05, cursor: 'grabbing' }}
  className="cursor-grab"
>
  ドラッグ可能
</motion.div>
```

### Sortable List

```tsx
// Using Framer Motion with Reorder
import { Reorder } from 'framer-motion';

const SortableList = ({ items, setItems }) => {
  return (
    <Reorder.Group values={items} onReorder={setItems}>
      {items.map((item) => (
        <Reorder.Item 
          key={item.id} 
          value={item}
          className="
            bg-white p-4 mb-2 rounded-lg shadow
            cursor-grab active:cursor-grabbing
          "
          whileDrag={{ scale: 1.05, boxShadow: '0 10px 25px rgba(0,0,0,0.2)' }}
        >
          {item.content}
        </Reorder.Item>
      ))}
    </Reorder.Group>
  );
};
```

---

## Hover Effects Library

### Glow Effect

```tsx
<Button className="
  relative overflow-hidden
  before:absolute before:inset-0
  before:bg-gradient-to-r before:from-transparent before:via-white/20 before:to-transparent
  before:translate-x-[-200%]
  hover:before:translate-x-[200%]
  before:transition-transform before:duration-700
">
  ホバーで光る
</Button>
```

### Border Gradient

```tsx
<Card className="
  relative p-[2px] bg-gradient-to-r from-primary-600 to-accent-600
  hover:from-accent-600 hover:to-primary-600
  transition-all duration-500
  rounded-lg
">
  <div className="bg-white rounded-lg p-6">
    {content}
  </div>
</Card>
```

### Tilt Effect

```tsx
// Using vanilla-tilt or CSS transform
<motion.div
  whileHover={{ rotateX: 5, rotateY: 5 }}
  transition={{ duration: 0.2 }}
  style={{ transformStyle: 'preserve-3d' }}
  className="perspective-1000"
>
  <Card>{content}</Card>
</motion.div>
```

---

## Performance Optimization

### Use CSS Transforms

```tsx
// ✅ Good: GPU-accelerated
transform: translate3d(0, 0, 0);
transform: scale(1.05);
opacity: 0.5;

// ❌ Bad: CPU-intensive
left: 100px;
top: 50px;
width: 200px;
height: 150px;
```

### Will-Change Hint

```css
/* Hint browser for upcoming animations */
.card:hover {
  will-change: transform, opacity;
}

.card {
  transition: transform 0.3s, opacity 0.3s;
}

/* Reset after animation */
.card:not(:hover) {
  will-change: auto;
}
```

### Layout Thrashing Prevention

```tsx
// ❌ Bad: Causes layout thrashing
elements.forEach(el => {
  const height = el.offsetHeight; // Read
  el.style.height = height + 10 + 'px'; // Write
});

// ✅ Good: Batch reads and writes
const heights = elements.map(el => el.offsetHeight); // Read phase
elements.forEach((el, i) => {
  el.style.height = heights[i] + 10 + 'px'; // Write phase
});
```

---

## Implementation Guide

### 1. Install Framer Motion

```bash
npm install framer-motion
```

### 2. Create Animation Hooks

```tsx
// hooks/useAnimationConfig.ts
export const useAnimationConfig = () => {
  const prefersReducedMotion = window.matchMedia(
    '(prefers-reduced-motion: reduce)'
  ).matches;
  
  return {
    duration: prefersReducedMotion ? 0 : 0.2,
    ease: 'easeOut',
  };
};
```

### 3. Create Reusable Motion Components

```tsx
// components/motion/FadeIn.tsx
export const FadeIn = ({ children, delay = 0 }) => {
  const config = useAnimationConfig();
  
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ ...config, delay }}
    >
      {children}
    </motion.div>
  );
};
```

---

## Testing Animations

### Visual Regression Testing

```tsx
// Storybook story with animation states
export const ButtonStates = {
  render: () => (
    <div className="flex gap-4">
      <Button>Default</Button>
      <Button className="hover">Hover</Button>
      <Button className="active">Active</Button>
      <Button disabled>Disabled</Button>
    </div>
  ),
};
```

### Performance Testing

```tsx
// Monitor animation performance
import { measure } from 'web-vitals';

measure((metric) => {
  if (metric.name === 'FCP') {
    console.log('First Contentful Paint:', metric.value);
  }
});
```

---

## Related Specifications

- [Design System](./design-system.md) - Animation tokens
- [Component Library](./component-library.md) - Component implementations
- [Usability Guidelines](./usability-guidelines.md) - Accessibility considerations

---

## Changelog

- 2025-11-11: Initial interaction patterns specification
