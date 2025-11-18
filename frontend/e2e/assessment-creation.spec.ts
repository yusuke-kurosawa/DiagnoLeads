import { test, expect } from '@playwright/test';

test.describe('診断作成フロー', () => {
  test.beforeEach(async ({ page }) => {
    // ログイン処理（実際のログインエンドポイントに合わせて調整）
    await page.goto('/');
    // TODO: 実際の認証フローを実装
  });

  test('新規診断を作成できる', async ({ page }) => {
    // 診断作成ページに移動
    await page.goto('/assessments/new');

    // 診断名を入力
    await page.fill('input[name="title"]', 'E2Eテスト診断');

    // 説明を入力
    await page.fill('textarea[name="description"]', 'これはE2Eテストで作成された診断です');

    // 保存ボタンをクリック
    await page.click('button:has-text("保存")');

    // 成功メッセージまたはリダイレクトを確認
    await expect(page).toHaveURL(/\/assessments\/[\w-]+/);
    await expect(page.locator('text=E2Eテスト診断')).toBeVisible();
  });

  test('診断に質問を追加できる', async ({ page }) => {
    // 既存の診断ページに移動（実際のIDに置き換え）
    await page.goto('/assessments/test-id/edit');

    // 質問追加ボタンをクリック
    await page.click('button:has-text("質問を追加")');

    // 質問文を入力
    await page.fill('input[placeholder*="質問"]', 'あなたの年齢層は？');

    // 選択肢を追加
    await page.click('button:has-text("選択肢を追加")');
    await page.fill('input[placeholder*="選択肢"]', '20代');

    // 保存
    await page.click('button:has-text("保存")');

    // 質問が追加されたことを確認
    await expect(page.locator('text=あなたの年齢層は？')).toBeVisible();
  });

  test('A/Bテストを作成できる', async ({ page }) => {
    // A/Bテスト管理ページに移動
    await page.goto('/assessments/test-id/ab-tests');

    // 新規テスト作成ボタンをクリック
    await page.click('button:has-text("新規テスト作成")');

    // テスト名を入力
    await page.fill('#test-name', 'CTA文言テスト');

    // 説明を入力
    await page.fill('#test-description', 'CTAボタンの文言を最適化するテスト');

    // テストを作成ボタンをクリック
    await page.click('button:has-text("テストを作成")');

    // テストが作成されたことを確認
    await expect(page.locator('text=CTA文言テスト')).toBeVisible();
  });

  test('SMSキャンペーンを作成できる', async ({ page }) => {
    // SMSキャンペーン管理ページに移動
    await page.goto('/assessments/test-id/sms-campaigns');

    // 新規キャンペーン作成ボタンをクリック
    await page.click('button:has-text("新規キャンペーン作成")');

    // キャンペーン名を入力
    await page.fill('#campaign-name', 'E2Eテストキャンペーン');

    // メッセージテンプレートを確認（デフォルト値があるはず）
    const messageTemplate = await page.locator('#message-template').inputValue();
    expect(messageTemplate).toContain('{url}');

    // テスト電話番号を入力
    await page.fill('input[placeholder*="+819012345678"]:first-child', '+819000000000');

    // キャンセルボタンをクリック（実際の送信はテストしない）
    await page.click('button:has-text("キャンセル")');

    // モーダルが閉じたことを確認
    await expect(page.locator('#campaign-name')).not.toBeVisible();
  });
});

test.describe('診断管理機能', () => {
  test('リフレッシュボタンでデータを再読み込みできる', async ({ page }) => {
    // A/Bテスト管理ページに移動
    await page.goto('/assessments/test-id/ab-tests');

    // 初期データを取得
    const initialTestCount = await page.locator('[class*="grid"]').count();

    // リフレッシュボタンをクリック
    await page.click('button:has-text("更新")');

    // リフレッシュアイコンがアニメーションすることを確認
    await expect(page.locator('button:has-text("更新") svg.animate-spin')).toBeVisible();

    // データが再読み込みされるまで待機
    await page.waitForTimeout(1000);

    // リフレッシュアイコンのアニメーションが終了することを確認
    await expect(page.locator('button:has-text("更新") svg.animate-spin')).not.toBeVisible();
  });
});

test.describe('アクセシビリティ', () => {
  test('フォームラベルが適切に関連付けられている', async ({ page }) => {
    // A/Bテスト作成フォームに移動
    await page.goto('/assessments/test-id/ab-tests');
    await page.click('button:has-text("新規テスト作成")');

    // ラベルをクリックしてフォーカスが移動することを確認
    await page.click('label:has-text("テスト名")');
    await expect(page.locator('#test-name')).toBeFocused();

    await page.click('label:has-text("説明")');
    await expect(page.locator('#test-description')).toBeFocused();

    await page.click('label:has-text("最小サンプルサイズ")');
    await expect(page.locator('#min-sample-size')).toBeFocused();
  });

  test('キーボードナビゲーションが機能する', async ({ page }) => {
    // A/Bテスト作成フォームに移動
    await page.goto('/assessments/test-id/ab-tests');
    await page.click('button:has-text("新規テスト作成")');

    // Tabキーでフォーカスを移動
    await page.keyboard.press('Tab');
    await expect(page.locator('#test-name')).toBeFocused();

    await page.keyboard.press('Tab');
    await expect(page.locator('#test-description')).toBeFocused();

    // Enterキーでボタンをクリックできることを確認
    await page.keyboard.press('Escape');
    await expect(page.locator('#test-name')).not.toBeVisible();
  });
});
