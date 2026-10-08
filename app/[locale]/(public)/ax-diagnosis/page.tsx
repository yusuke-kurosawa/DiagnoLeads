import { AxDiagnosisFlow } from '@/components/features/ax-diagnosis/ax-diagnosis-flow';
import { AX_MIGRATION_CONFIG } from '@/lib/features/diagnostics/ax-migration/config';
import type { Metadata } from 'next';
import { getTranslations } from 'next-intl/server';

interface AxDiagnosisPageProps {
  params: Promise<{ locale: string }>;
}

export async function generateMetadata({ params }: AxDiagnosisPageProps): Promise<Metadata> {
  const { locale } = await params;
  const t = await getTranslations({ locale, namespace: 'axDiagnosis.meta' });
  return {
    title: { absolute: t('title') },
    description: t('description'),
    // Keep out of search engines until external publication is approved (広報部門の確認)
    robots: { index: false, follow: false },
  };
}

/**
 * AX migration self-diagnosis (public)
 * Answers are evaluated on the server: POST /api/diagnostics/ax-migration
 */
export default async function AxDiagnosisPage({ params }: AxDiagnosisPageProps) {
  const { locale } = await params;
  return (
    <main className="min-h-screen bg-gray-50">
      <AxDiagnosisFlow
        locale={locale === 'en' ? 'en' : 'ja'}
        consultationDays={AX_MIGRATION_CONFIG.consultationResponseBusinessDays}
        privacyPolicyUrl={process.env.NEXT_PUBLIC_AX_PRIVACY_POLICY_URL || undefined}
      />
    </main>
  );
}
