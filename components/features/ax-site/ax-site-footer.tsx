import { ExternalLink } from 'lucide-react';
import { getTranslations } from 'next-intl/server';
import { AX_SITE_LINKS, axPrivacyPolicyUrl } from './site-config';

export async function AxSiteFooter({ locale }: { locale: string }) {
  const t = await getTranslations({ locale, namespace: 'axSite.footer' });
  const privacyPolicyUrl = axPrivacyPolicyUrl();
  const links = [
    { href: AX_SITE_LINKS.operator, label: t('company') },
    { href: AX_SITE_LINKS.relatedService, label: t('related') },
    ...(privacyPolicyUrl ? [{ href: privacyPolicyUrl, label: t('privacy') }] : []),
  ];

  return (
    <footer className="bg-ax-deep text-white">
      <div className="mx-auto flex max-w-6xl flex-col gap-6 px-4 py-10 sm:px-6 md:flex-row md:items-center md:justify-between">
        <p className="text-sm font-bold">{t('operator')}</p>
        <ul className="flex flex-wrap gap-x-6 gap-y-3 text-sm">
          {links.map(({ href, label }) => (
            <li key={href}>
              <a
                href={href}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center gap-1 underline-offset-4 hover:underline focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-white"
              >
                {label}
                <ExternalLink className="h-3.5 w-3.5" aria-hidden="true" />
                <span className="sr-only">{t('newTab')}</span>
              </a>
            </li>
          ))}
        </ul>
      </div>
    </footer>
  );
}
