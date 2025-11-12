# UI/UX Guidelines - DiagnoLeads

**Version**: 2.0  
**Last Updated**: 2025-11-12  
**Status**: Published

---

## 📋 Overview

This document defines the consistent UI/UX standards for DiagnoLeads frontend development. All component development must follow these guidelines.

**Design Philosophy**: User-centric, accessible, consistent, and performant.

---

## 🎨 Design Principles

### 1. User Experience First
- All interactions must understand user intent from the beginning
- Simple and intuitive design
- Always consider accessibility (WCAG AAA compliance target)

### 2. Consistency
- Same-purpose components use unified styles
- Follow specified system for color, size, font, spacing
- Maintain visual hierarchy across all pages

### 3. Visibility and Clarity
- All buttons, text, and elements have sufficient color contrast
- Information distinction doesn't rely on color alone
- Minimum font size: 12px (16px for body text)

### 4. Performance
- Optimize rendering with React.memo, useMemo
- Lazy load heavy components
- Minimize re-renders

### 5. Accessibility
- WCAG AA compliance (target AAA)
- Keyboard navigation support
- Screen reader support
- ARIA labels where needed

---

## 🎨 Color System

### Base Colors

Using Tailwind CSS standard palette:

| Name | Tailwind | Primary Use | Secondary Use |
|------|----------|-------------|---------------|
| **Blue** | `blue-600` / `700` | Primary actions, links, focus | Brand color |
| **Gray** | `gray-100` ~ `900` | Neutral, backgrounds, text | UI structure |
| **Green** | `green-600` / `700` | Success, completion, confirmation | Positive feedback |
| **Red** | `red-600` / `700` | Destructive actions, errors | Error states |
| **Amber** | `amber-500` / `600` | Warnings, information | Alerts |

### Color Usage Rules

**Backgrounds:**
- Page background: `bg-white` or `bg-gray-50`
- Container: `bg-white`
- Hover state: `bg-gray-50` or `bg-gray-100`
- Disabled: `bg-gray-100`

**Text:**
- Primary (body): `text-gray-900`
- Secondary: `text-gray-600`
- Tertiary: `text-gray-500`
- Disabled: `text-gray-400`
- On colored backgrounds: `text-white`

**Borders:**
- Primary: `border-gray-300`
- Light: `border-gray-200`
- Heavy: `border-gray-400`
- Focus: `border-blue-500`

**Required Fields:**
- Mark: `text-red-600` with asterisk (*)

### ⚠️ Custom Color Tokens Deprecated

Do NOT use custom color tokens like `primary-600`, `success-600`. Use Tailwind CSS standard colors directly:

```tsx
// ❌ WRONG
className="bg-primary-600 text-success-600"

// ✅ CORRECT
className="bg-blue-600 text-green-600"
```

---

## 🔘 Button Component

### Variants

```tsx
<Button variant="primary">Primary Action</Button>      // Blue - CTA
<Button variant="secondary">Secondary Action</Button>  // Gray
<Button variant="success">Success</Button>              // Green
<Button variant="destructive">Delete</Button>          // Red
<Button variant="outline">Outline</Button>             // Border only
<Button variant="ghost">Ghost</Button>                 // Transparent
<Button variant="link">Link</Button>                   // Text only
```

### Sizes

```tsx
<Button size="xs">Extra Small</Button>   // h-7
<Button size="sm">Small</Button>         // h-9
<Button size="md">Medium (default)</Button> // h-10
<Button size="lg">Large</Button>         // h-12
<Button size="xl">Extra Large</Button>   // h-14
<Button size="icon">Icon</Button>        // h-10 w-10 (square)
```

### Button Style Definitions

| Variant | Background | Text | Hover | Use Case |
|---------|-----------|------|-------|----------|
| primary | `bg-blue-600` | `text-white` | `bg-blue-700` | Primary CTA, main actions |
| secondary | `bg-gray-100` | `text-gray-900` | `bg-gray-200` | Sub-actions |
| success | `bg-green-600` | `text-white` | `bg-green-700` | Confirmation, success |
| destructive | `bg-red-600` | `text-white` | `bg-red-700` | Delete, cancel |
| outline | `bg-white` `border-2` `border-gray-300` | `text-gray-700` | `bg-gray-50` | Secondary |
| ghost | `bg-transparent` | `text-gray-700` | `bg-gray-100` | Toolbar, navigation |
| link | `bg-transparent` | `text-blue-600` | `underline` | Inline links |

### Button States

```tsx
// Disabled state
<Button disabled>Disabled</Button>           // Opacity 50%, cursor-not-allowed

// Loading state
<Button loading>
  <Spinner className="mr-2" />
  Loading...
</Button>

// Full width
<Button className="w-full">Full Width</Button>

// With icon
<Button>
  <Icon className="mr-2" />
  Action
</Button>
```

---

## 📝 Form Components

### Input Field

```tsx
<Input 
  type="text"
  placeholder="Enter text..."
  label="Field Label"
  required
  error="Error message"
/>
```

**Styling:**
- Border: `border border-gray-300`
- Focus: `border-blue-500 ring-2 ring-blue-200`
- Error: `border-red-500 ring-2 ring-red-200`
- Disabled: `bg-gray-100 cursor-not-allowed`

### Select / Dropdown

```tsx
<Select label="Select option" required>
  <option value="">Choose...</option>
  <option value="1">Option 1</option>
  <option value="2">Option 2</option>
</Select>
```

### Checkbox & Radio

```tsx
<Checkbox label="I agree" />
<Radio label="Option 1" name="group" />
```

### Form Validation

- Show error message below field
- Use `text-red-600` for error text
- Add red border to field
- Icon: ❌ for errors, ✓ for success

---

## 📊 Data Display

### Table

```tsx
<Table>
  <TableHeader>
    <TableRow>
      <TableHead>Header 1</TableHead>
      <TableHead>Header 2</TableHead>
    </TableRow>
  </TableHeader>
  <TableBody>
    <TableRow>
      <TableCell>Data 1</TableCell>
      <TableCell>Data 2</TableCell>
    </TableRow>
  </TableBody>
</Table>
```

**Styling:**
- Header: `bg-gray-100 font-semibold`
- Row hover: `bg-gray-50`
- Borders: `border-gray-200`
- Padding: `px-4 py-3`

### Card

```tsx
<Card>
  <CardHeader>
    <CardTitle>Card Title</CardTitle>
  </CardHeader>
  <CardContent>
    Card content here
  </CardContent>
  <CardFooter>
    Footer content
  </CardFooter>
</Card>
```

**Styling:**
- Background: `bg-white`
- Border: `border border-gray-200`
- Rounded: `rounded-lg`
- Shadow: `shadow-sm` for depth
- Padding: `p-6`

---

## 🔤 Typography

### Font Stack

```css
font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen',
  'Ubuntu', 'Cantarell', 'Fira Sans', 'Droid Sans', 'Helvetica Neue',
  sans-serif;
```

### Font Sizes

| Level | Size | Weight | Use |
|-------|------|--------|-----|
| H1 | 32px (2rem) | Bold (700) | Page title |
| H2 | 24px (1.5rem) | Bold (700) | Section title |
| H3 | 20px (1.25rem) | Semibold (600) | Subsection |
| Body | 16px (1rem) | Regular (400) | Main text |
| Small | 14px (0.875rem) | Regular (400) | Secondary text |
| Tiny | 12px (0.75rem) | Regular (400) | Help text |

### Text Styling

```tsx
// Heading
<h1 className="text-3xl font-bold text-gray-900">Heading</h1>

// Body text
<p className="text-base text-gray-900">Body text</p>

// Secondary text
<p className="text-sm text-gray-600">Secondary text</p>

// Highlighted
<span className="font-semibold">Important text</span>

// Code
<code className="bg-gray-100 px-2 py-1 rounded text-sm">code()</code>
```

---

## 🎯 Spacing System

Using 4px base unit (Tailwind scale):

```
xs: 2px (0.5rem)    → p-0.5
sm: 4px (1rem)      → p-1
md: 8px (2rem)      → p-2
lg: 16px (4rem)     → p-4
xl: 24px (6rem)     → p-6
2xl: 32px (8rem)    → p-8
3xl: 48px (12rem)   → p-12
```

**Common patterns:**
- Component padding: 16px (p-4)
- Section padding: 24px (p-6)
- Page padding: 32px (p-8)
- Between sections: 32px (mb-8)
- Between items: 8px (gap-2)

---

## 🔄 Interaction Patterns

### Hover States
- Buttons: Background color change + cursor pointer
- Links: Underline + color change
- Cards: Shadow increase + subtle scale
- Rows: Background color change

### Focus States
- Focus ring: `ring-2 ring-blue-500 outline-none`
- All interactive elements must have focus state
- Tab order must be logical

### Loading States
- Show spinner or skeleton
- Disable user input
- Show loading message

### Error States
- Show error message
- Highlight affected field
- Use red color (`text-red-600`)
- Icon: ❌

### Success States
- Show confirmation message
- Use green color (`text-green-600`)
- Icon: ✓
- Optional toast notification

---

## 📱 Responsive Design

Using Tailwind CSS breakpoints:

```
sm: 640px   (mobile)
md: 768px   (tablet)
lg: 1024px  (desktop)
xl: 1280px  (wide)
2xl: 1536px (ultra-wide)
```

**Examples:**

```tsx
// Mobile: 1 column, Tablet: 2 columns, Desktop: 3 columns
<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">

// Mobile: text-sm, Desktop: text-base
<p className="text-sm lg:text-base">Responsive text</p>

// Hide on mobile, show on tablet+
<div className="hidden md:block">Desktop only</div>
```

---

## ♿ Accessibility Checklist

- [ ] Semantic HTML (`<button>`, `<a>`, `<form>`, etc.)
- [ ] ARIA labels for icon-only buttons
- [ ] Keyboard navigation (Tab, Enter, Escape)
- [ ] Color contrast ratio ≥ 4.5:1 for text
- [ ] Focus visible for all interactive elements
- [ ] Form labels associated with inputs (`htmlFor`)
- [ ] Alt text for all images
- [ ] Screen reader support for dynamic content
- [ ] Error messages linked to form fields
- [ ] No keyboard trap

---

## 🚀 Performance Guidelines

- Lazy load heavy components (`React.lazy`, `Suspense`)
- Memoize expensive computations (`useMemo`)
- Memoize components (`React.memo`) when parent re-renders
- Virtualize long lists
- Optimize images (use WebP, lazy loading)
- Minimize bundle size (code split by route)

---

## 📖 Component Library

DiagnoLeads uses **shadcn/ui** with Tailwind CSS.

Available components:
- Button, Input, Select, Checkbox, Radio
- Card, Table, Dialog, Dropdown Menu
- Toast, Badge, Progress Bar, Spinner
- Tabs, Accordion, Collapsible
- etc.

**Documentation**: https://ui.shadcn.com/

---

## ✅ Checklist for Component Development

Before submitting a PR:

- [ ] Follows design system
- [ ] Responsive on mobile, tablet, desktop
- [ ] Keyboard accessible
- [ ] Color contrast AAA (target)
- [ ] Error states handled
- [ ] Loading states handled
- [ ] Dark mode compatible (if applicable)
- [ ] Storybook story created
- [ ] Unit tested
- [ ] No console warnings/errors

---

## 📞 Design Feedback

For design questions or suggestions:
1. Create an issue in GitHub
2. Reference this guidelines document
3. Include screenshot/Figma link if applicable
4. Tag @designers and @frontend-leads

---

**Last Updated**: 2025-11-12  
**Maintained by**: Design & Frontend Teams  
**Related**: `openspec/specs/ui-ux/components.md` (Component Specifications)
