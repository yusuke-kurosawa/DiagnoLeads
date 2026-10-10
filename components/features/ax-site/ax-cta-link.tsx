'use client';

import { trackAxEvent } from '@/components/features/ax-diagnosis/tracking';
import { cn } from '@/lib/utils';
import { ArrowRight } from 'lucide-react';
import type { ReactNode } from 'react';

type CtaVariant = 'diagnosis' | 'consultation';

const VARIANT_CLASS: Record<CtaVariant, string> = {
  // Yellow pill: the diagnosis button of maru2-dx.com (dark text keeps the contrast)
  diagnosis:
    'rounded-full bg-ax-yellow text-ax-ink shadow-[0_6px_16px_rgba(0,0,0,0.18)] hover:bg-ax-yellow-dark',
  consultation:
    'rounded-lg bg-ax-teal-dark text-white shadow-[0_6px_16px_rgba(0,0,0,0.18)] hover:bg-ax-deep',
};

interface AxCtaLinkProps {
  href: string;
  variant?: CtaVariant;
  /** On a dark background the focus outline is white (teal would not stand out) */
  tone?: 'light' | 'dark';
  /** Where the button is, for the analytics event (hero, header, final, floating) */
  location: string;
  external?: boolean;
  className?: string;
  tabIndex?: number;
  children: ReactNode;
}

/** Call-to-action button of the AX migration site */
export function AxCtaLink({
  href,
  variant = 'diagnosis',
  tone = 'light',
  location,
  external = false,
  className,
  tabIndex,
  children,
}: AxCtaLinkProps) {
  return (
    <a
      href={href}
      tabIndex={tabIndex}
      onClick={() => trackAxEvent('ax_lp_cta_click', { cta: variant, location })}
      {...(external ? { target: '_blank', rel: 'noopener noreferrer' } : {})}
      className={cn(
        'inline-flex items-center justify-center gap-2 px-7 py-4 text-base font-bold transition-colors focus-visible:outline focus-visible:outline-3 focus-visible:outline-offset-2',
        tone === 'dark' ? 'focus-visible:outline-white' : 'focus-visible:outline-ax-teal-dark',
        VARIANT_CLASS[variant],
        className
      )}
    >
      {children}
      <ArrowRight className="h-5 w-5 shrink-0" aria-hidden="true" />
    </a>
  );
}
