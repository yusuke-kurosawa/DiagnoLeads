'use client';

import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Text } from '@/components/ui/metric';
import { useOrganization } from '@/hooks/use-organization';
import { trpc } from '@/lib/trpc/client';
import { Building2, Hash } from 'lucide-react';
import { useLocale, useTranslations } from 'next-intl';
import { useRouter } from 'next/navigation';
import { type FormEvent, useState } from 'react';
import { toast } from 'sonner';

const SLUG_PATTERN = /^[a-z0-9-]+$/;

/** Suggest a slug from an ASCII name; names in other scripts leave it to the user */
export function suggestSlug(name: string): string {
  return name
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-+|-+$/g, '')
    .slice(0, 63);
}

type FieldErrors = { name?: string; slug?: string };

/**
 * Create an organization and make it the current one.
 * The creator becomes the owner (organizations.create adds the membership).
 */
export function CreateOrganizationForm() {
  const t = useTranslations('organizations.create');
  const locale = useLocale();
  const router = useRouter();
  const utils = trpc.useUtils();
  const { setOrganization } = useOrganization();

  const [name, setName] = useState('');
  const [slug, setSlug] = useState('');
  const [slugEdited, setSlugEdited] = useState(false);
  const [fieldErrors, setFieldErrors] = useState<FieldErrors>({});
  const [formError, setFormError] = useState<string | null>(null);

  const createOrganization = trpc.organizations.create.useMutation({
    onSuccess: async (organization) => {
      setOrganization(organization.id, organization);
      await utils.organizations.list.invalidate();
      toast.success(t('success', { name: organization.name }));
      router.push(`/${locale}/leads`);
    },
    onError: (error) => {
      if (error.data?.code === 'CONFLICT') {
        setFieldErrors({ slug: t('slugTaken') });
      } else {
        setFormError(t('error'));
      }
    },
  });

  const handleNameChange = (value: string) => {
    setName(value);
    if (!slugEdited) setSlug(suggestSlug(value));
  };

  const handleSlugChange = (value: string) => {
    setSlugEdited(true);
    setSlug(value.toLowerCase().replace(/[^a-z0-9-]/g, ''));
  };

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();
    setFormError(null);

    const trimmedName = name.trim();
    const errors: FieldErrors = {};
    if (!trimmedName) errors.name = t('nameRequired');
    if (!slug) errors.slug = t('slugRequired');
    else if (!SLUG_PATTERN.test(slug)) errors.slug = t('slugInvalid');
    setFieldErrors(errors);
    if (errors.name || errors.slug) return;

    createOrganization.mutate({ name: trimmedName, slug });
  };

  const pending = createOrganization.isPending;

  return (
    <div className="container mx-auto py-8 px-4">
      <div className="max-w-2xl mx-auto space-y-8">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-gray-100">{t('title')}</h1>
          <Text className="mt-1">{t('description')}</Text>
        </div>

        <Card decoration="top" decorationColor="blue">
          <form onSubmit={handleSubmit} className="p-6 space-y-6" noValidate>
            <div className="space-y-2">
              <Label htmlFor="organization-name" className="flex items-center gap-2">
                <Building2 className="h-4 w-4 text-gray-500" aria-hidden="true" />
                {t('nameLabel')}
              </Label>
              <Input
                id="organization-name"
                value={name}
                onChange={(e) => handleNameChange(e.target.value)}
                placeholder={t('namePlaceholder')}
                maxLength={255}
                aria-invalid={Boolean(fieldErrors.name)}
                aria-describedby={fieldErrors.name ? 'organization-name-error' : undefined}
                disabled={pending}
                autoFocus
              />
              {fieldErrors.name && (
                <p id="organization-name-error" className="text-sm text-red-600">
                  {fieldErrors.name}
                </p>
              )}
            </div>

            <div className="space-y-2">
              <Label htmlFor="organization-slug" className="flex items-center gap-2">
                <Hash className="h-4 w-4 text-gray-500" aria-hidden="true" />
                {t('slugLabel')}
              </Label>
              <Input
                id="organization-slug"
                value={slug}
                onChange={(e) => handleSlugChange(e.target.value)}
                placeholder={t('slugPlaceholder')}
                maxLength={255}
                aria-invalid={Boolean(fieldErrors.slug)}
                aria-describedby={
                  fieldErrors.slug
                    ? 'organization-slug-error organization-slug-help'
                    : 'organization-slug-help'
                }
                disabled={pending}
              />
              <Text id="organization-slug-help" className="text-xs">
                {t('slugHelp')}
              </Text>
              {fieldErrors.slug && (
                <p id="organization-slug-error" className="text-sm text-red-600">
                  {fieldErrors.slug}
                </p>
              )}
            </div>

            {formError && (
              <p role="alert" className="text-sm text-red-600">
                {formError}
              </p>
            )}

            <div className="flex justify-end">
              <Button type="submit" disabled={pending}>
                {pending ? t('submitting') : t('submit')}
              </Button>
            </div>
          </form>
        </Card>
      </div>
    </div>
  );
}
