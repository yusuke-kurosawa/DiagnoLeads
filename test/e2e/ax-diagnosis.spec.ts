import { expect, test } from '@playwright/test';
import {
  answerAccess,
  answerAcos,
  answerAs400,
  canSubmit,
  fillContact,
  submit,
} from './helpers/ax-diagnosis';

/**
 * E2E Test: AX migration self-diagnosis v2 on its own page (/ax-diagnosis)
 *
 * Requires AX_DIAGNOSIS_ORGANIZATION_ID (or DEFAULT_ORGANIZATION_ID) and a database
 * with the drizzle migrations applied.
 */
test.describe('AX migration diagnosis', () => {
  test('starts with the migration path and is hidden from search engines @smoke', async ({
    page,
  }) => {
    await page.goto('/ja/ax-diagnosis');
    await expect(
      page.getByRole('heading', { name: '今の基幹システムのまま、AI時代の経営判断はできますか？' })
    ).toBeVisible();
    for (const id of ['as400', 'acos', 'access', 'other']) {
      await expect(page.getByTestId(`platform-${id}`)).toBeVisible();
    }
    await expect(page.locator('meta[name="robots"]')).toHaveAttribute('content', /noindex/);
  });

  test('names the unanswered questions before moving on', async ({ page }) => {
    await page.goto('/ja/ax-diagnosis');
    await page.getByTestId('platform-acos').click();
    await page.getByRole('button', { name: /次へ/ }).click();
    await expect(page.locator('#q-maintenance-error')).toHaveText('いずれか1つを選んでください');
    await expect(page.getByRole('heading', { name: /STEP 2 \/ 5/ })).toBeVisible();
  });

  test('goes back a step with the browser back button', async ({ page }) => {
    await page.goto('/ja/ax-diagnosis');
    await page.getByTestId('platform-as400').click();
    await expect(page.getByRole('heading', { name: /STEP 2 \/ 5/ })).toBeVisible();
    await page.goBack();
    await expect(page.getByRole('heading', { name: /STEP 1 \/ 5/ })).toBeVisible();
    await expect(page.getByTestId('platform-as400')).toHaveAttribute('aria-pressed', 'true');
  });

  test('completes the AS/400 path and requests a consultation from the result @smoke', async ({
    page,
  }) => {
    test.skip(!canSubmit, 'AX_DIAGNOSIS_ORGANIZATION_ID is not set');
    await page.goto('/ja/ax-diagnosis?utm_source=google&utm_medium=cpc&utm_campaign=ax-hito');
    await answerAs400(page);
    await page.getByRole('button', { name: /診断結果を見る/ }).click();
    await expect(page.locator('#contact-company-error')).toHaveText('会社名を入力してください');

    await fillContact(page, `e2e-ax-as400-${Date.now()}@example.com`);
    const body = await submit(page);
    expect(body.result).not.toHaveProperty('leadScore');

    await expect(page.getByRole('heading', { name: '診断結果' })).toBeVisible();
    await expect(page.getByText('移行元：AS/400（IBM i）')).toBeVisible();
    await expect(page.getByTestId('ax-result-checkpoints')).toContainText('見つからないソース');
    await expect(page.getByTestId('ax-result-reasons')).toBeVisible();

    await page.getByRole('button', { name: /無料の個別相談を申し込む/ }).first().click();
    await expect(page.getByText('個別相談のお申し込みを受け付けました')).toBeVisible();
  });

  test('completes the NEC ACOS path @smoke', async ({ page }) => {
    test.skip(!canSubmit, 'AX_DIAGNOSIS_ORGANIZATION_ID is not set');
    await page.goto('/ja/ax-diagnosis');
    await answerAcos(page);
    await fillContact(page, `e2e-ax-acos-${Date.now()}@example.com`);
    await submit(page);

    await expect(page.getByText('移行元：NEC ACOS')).toBeVisible();
    await expect(page.getByTestId('ax-result-urgency')).toHaveAttribute('data-level', 'high');
    await expect(page.getByTestId('ax-result-checkpoints')).toContainText('ACOSの文字コード');
  });

  test('completes the Access path and refines it with the follow-up questions @smoke', async ({
    page,
  }) => {
    test.skip(!canSubmit, 'AX_DIAGNOSIS_ORGANIZATION_ID is not set');
    await page.goto('/ja/ax-diagnosis');
    await answerAccess(page);
    await fillContact(page, `e2e-ax-access-${Date.now()}@example.com`);
    await page.getByRole('checkbox', { name: /無料の個別相談を希望する/ }).check();
    await page.getByRole('textbox', { name: /電話番号/ }).fill('03-0000-0000');
    await submit(page);

    await expect(page.getByText('移行元：Microsoft Access')).toBeVisible();
    await expect(page.getByText('個別相談のお申し込みを受け付けました')).toBeVisible();

    const followUp = page.getByTestId('ax-follow-up');
    await followUp.getByRole('button', { name: /追加質問/ }).click();
    await followUp.getByRole('group', { name: /データはどこに置いて/ }).getByLabel(/OneDrive/).check();
    const detailsResponse = page.waitForResponse('**/api/diagnostics/ax-migration/details');
    await followUp.getByRole('button', { name: '回答して結果を更新する' }).click();
    expect((await detailsResponse).status()).toBe(200);
    await expect(page.getByText(/結果を更新しました/)).toBeVisible();
    await expect(page.getByTestId('ax-result-checkpoints')).toContainText('クラウドのフォルダ');
  });
});
