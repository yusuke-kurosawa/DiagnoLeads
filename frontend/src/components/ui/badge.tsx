/**
 * Badge Component - Enhanced with design system
 * Based on: openspec/specs/ui-ux/component-library.md
 */

import * as React from "react"
import { cva, type VariantProps } from "class-variance-authority"
import { cn } from "@/lib/utils"

const badgeVariants = cva(
  "inline-flex items-center gap-1 rounded-full border font-semibold transition-all duration-200",
  {
    variants: {
      variant: {
        default: "border-gray-200 bg-gray-100 text-gray-900",
        primary: "border-primary-200 bg-primary-600 text-white",
        success: "border-success-200 bg-success-600 text-white",
        warning: "border-warning-200 bg-warning-600 text-white",
        error: "border-error-200 bg-error-600 text-white",
        info: "border-info-200 bg-info-600 text-white",
        outline: "border-gray-300 bg-transparent text-gray-700",
      },
      size: {
        sm: "px-2 py-0.5 text-xs",
        md: "px-2.5 py-1 text-sm",
        lg: "px-3 py-1.5 text-base",
      },
    },
    defaultVariants: {
      variant: "default",
      size: "sm",
    },
  }
)

interface BadgeProps
  extends React.HTMLAttributes<HTMLDivElement>,
    VariantProps<typeof badgeVariants> {
  leftIcon?: React.ReactNode
  rightIcon?: React.ReactNode
  dot?: boolean
}

function Badge({ 
  className, 
  variant, 
  size, 
  leftIcon, 
  rightIcon, 
  dot,
  children,
  ...props 
}: BadgeProps) {
  return (
    <div className={cn(badgeVariants({ variant, size }), className)} {...props}>
      {dot && (
        <span className="w-1.5 h-1.5 rounded-full bg-current animate-pulse" />
      )}
      {leftIcon && (
        <span className="inline-flex shrink-0">{leftIcon}</span>
      )}
      {children}
      {rightIcon && (
        <span className="inline-flex shrink-0">{rightIcon}</span>
      )}
    </div>
  )
}

export { Badge, badgeVariants }
export type { BadgeProps }
