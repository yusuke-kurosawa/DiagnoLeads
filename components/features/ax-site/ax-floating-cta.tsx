'use client';

import { cn } from '@/lib/utils';
import { useEffect, useState } from 'react';
import { AxCtaLink } from './ax-cta-link';
import { AX_SECTIONS } from './site-config';

/** Hidden while another diagnosis button (hero, final call to action) or the diagnosis is on screen */
const DEFAULT_HIDE_WHEN_VISIBLE = ['ax-hero-heading', AX_SECTIONS.diagnosis, 'ax-final-heading'];

interface AxFloatingCtaProps {
  label: string;
  hideWhenVisible?: string[];
}

/** Bottom bar on phones so the diagnosis is one tap away while reading the page */
export function AxFloatingCta({
  label,
  hideWhenVisible = DEFAULT_HIDE_WHEN_VISIBLE,
}: AxFloatingCtaProps) {
  const [visible, setVisible] = useState(false);

  useEffect(() => {
    const targets = hideWhenVisible
      .map((id) => document.getElementById(id))
      .filter((el): el is HTMLElement => el !== null);
    if (targets.length === 0 || typeof IntersectionObserver === 'undefined') return;

    const onScreen = new Set<Element>();
    const observer = new IntersectionObserver((entries) => {
      for (const entry of entries) {
        if (entry.isIntersecting) onScreen.add(entry.target);
        else onScreen.delete(entry.target);
      }
      setVisible(onScreen.size === 0);
    });
    for (const target of targets) observer.observe(target);
    return () => observer.disconnect();
  }, [hideWhenVisible]);

  return (
    <div
      className={cn(
        'fixed inset-x-0 bottom-0 z-30 border-t border-gray-200 bg-white/95 p-3 backdrop-blur motion-safe:transition-transform motion-safe:duration-300 sm:hidden',
        visible ? 'translate-y-0' : 'pointer-events-none translate-y-full'
      )}
      aria-hidden={!visible}
      data-testid="ax-floating-cta"
    >
      <AxCtaLink
        href={`#${AX_SECTIONS.diagnosis}`}
        location="floating"
        className="w-full py-3"
        tabIndex={visible ? undefined : -1}
      >
        {label}
      </AxCtaLink>
    </div>
  );
}
