import { type Page, expect, test } from '@playwright/test';

/**
 * E2E Test: AX migration self-diagnosis (/ax-diagnosis)
 *
 * Requires AX_DIAGNOSIS_ORGANIZATION_ID (or DEFAULT_ORGANIZATION_ID) and a database
 * with the drizzle migrations applied.
 */

const answerTypicalAs400 = async (page: Page) => {
  // Step 1: company
  await page.getByLabel('製造業').check();
  await page.getByLabel('100億〜300億円').check();
  await page.getByRole('button', { name: '次へ' }).click();

  // Step 2: core system
  await page.getByLabel('AS/400（IBM i）').check();
  await page.getByLabel('RPG').check();
  await page.getByLabel('CL', { exact: true }).check();
  await page.getByLabel('20年以上').check();
  await page.getByLabel('500〜2,000本').check();
  await page.getByLabel('3〜5').check();
  await page.getByRole('button', { name: '次へ' }).click();

  // Step 3: operations and challenges
  await page.getByLabel('社内の1〜2名に頼っている').check();
  await page.getByLabel('一部が古い・足りない').check();
  await page.getByLabel('扱える技術者が減り、仕様がブラックボックス化している').check();
  await page.getByLabel('保守・延命の費用がかさみ、新しい投資に回せない').check();
  await page.getByRole('button', { name: '次へ' }).click();

  // Step 4: plans
  await page.getByLabel('1〜2年以内').check();
  await page.getByLabel('情報システム部門の責任者').check();
  await page.getByRole('button', { name: '次へ' }).click();
};

const fillContact = async (page: Page, email: string) => {
  await page.getByLabel(/会社名/).fill('E2E製作所');
  await page.getByLabel(/お名前/).fill('E2E 太郎');
  await page.getByLabel(/メールアドレス/).fill(email);
  await page.getByLabel('個人情報の取り扱いに同意する').check();
};

test.describe('AX migration diagnosis', () => {
  test('shows the intro and is hidden from search engines @smoke', async ({ page }) => {
    await page.goto('/ja/ax-diagnosis');
    await expect(
      page.getByRole('heading', { name: '今の基幹システムのまま、AI時代の経営判断はできますか？' })
    ).toBeVisible();
    await expect(page.locator('meta[name="robots"]')).toHaveAttribute('content', /noindex/);
  });

  test('requires an answer before moving on', async ({ page }) => {
    await page.goto('/ja/ax-diagnosis');
    await page.getByRole('button', { name: '診断をはじめる' }).click();
    await page.getByRole('button', { name: '次へ' }).click();
    await expect(page.getByText('回答を選んでください').first()).toBeVisible();
    await expect(page.getByText('ステップ 1 / 5')).toBeVisible();
  });

  test('keeps "I don\'t know" exclusive in multiple-choice questions', async ({ page }) => {
    await page.goto('/ja/ax-diagnosis');
    await page.getByRole('button', { name: '診断をはじめる' }).click();
    await page.getByLabel('製造業').check();
    await page.getByLabel('100億〜300億円').check();
    await page.getByRole('button', { name: '次へ' }).click();

    const languages = page.getByRole('group', { name: /主な開発言語/ });
    await languages.getByLabel('RPG').check();
    await languages.getByLabel('わからない').check();
    await expect(languages.getByLabel('RPG')).not.toBeChecked();
    await languages.getByLabel('COBOL').check();
    await expect(languages.getByLabel('わからない')).not.toBeChecked();
  });

  test('completes the diagnosis and requests a consultation from the result', async ({ page }) => {
    await page.goto('/ja/ax-diagnosis?utm_source=google&utm_medium=cpc&utm_campaign=ax-hito');
    await page.getByRole('button', { name: '診断をはじめる' }).click();
    await answerTypicalAs400(page);

    await expect(page.getByText('ステップ 5 / 5')).toBeVisible();
    await page.getByRole('button', { name: '診断結果を見る' }).click();
    await expect(page.getByText('個人情報の取り扱いへの同意が必要です')).toBeVisible();

    await fillContact(page, `e2e-ax-${Date.now()}@example.com`);
    const responsePromise = page.waitForResponse('**/api/diagnostics/ax-migration');
    await page.getByRole('button', { name: '診断結果を見る' }).click();
    const response = await responsePromise;
    expect(response.status()).toBe(200);
    const body = await response.json();
    expect(body.result).not.toHaveProperty('leadScore');

    await expect(page.getByRole('heading', { name: '診断結果' })).toBeVisible();
    await expect(page.getByTestId('ax-result-difficulty')).toContainText('中');
    await expect(page.getByTestId('ax-result-challenge')).toContainText(
      'ヒト：人に依存した基幹システム'
    );
    await expect(page.getByText('E2E製作所 様の回答にもとづく目安です')).toBeVisible();

    await page.getByRole('button', { name: '無料の個別相談を申し込む' }).click();
    await expect(page.getByText('個別相談のお申し込みを受け付けました')).toBeVisible();
    await expect(page.getByText('2営業日以内に担当者からご連絡します。')).toBeVisible();
  });

  test('shows the accepted message right away when consultation is checked in the form', async ({
    page,
  }) => {
    await page.goto('/ja/ax-diagnosis');
    await page.getByRole('button', { name: '診断をはじめる' }).click();
    await answerTypicalAs400(page);
    await fillContact(page, `e2e-ax-consult-${Date.now()}@example.com`);
    await page.getByLabel('結果をもとに、無料の個別相談を希望する').check();
    await page.getByRole('button', { name: '診断結果を見る' }).click();

    await expect(page.getByText('個別相談のお申し込みを受け付けました')).toBeVisible();
    await expect(page.getByRole('button', { name: '無料の個別相談を申し込む' })).toHaveCount(0);
  });
});
