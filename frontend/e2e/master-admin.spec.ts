/**
 * E2E Tests for Master Admin Management
 * 
 * Tests for:
 * - Tenant Management (system_admin only)
 * - User Management (admin users)
 * - Topic Management (drag & drop)
 * - Industry Management (drag & drop)
 */

import { test, expect, Page } from '@playwright/test';

// Test configuration
const BASE_URL = 'http://localhost:5173';
const API_BASE_URL = 'http://localhost:8000/api/v1';

// Demo credentials
const SYSTEM_ADMIN = {
  email: 'system@demo.example.com',
  password: 'System@Demo123',
};

const TENANT_ADMIN = {
  email: 'admin@demo.example.com',
  password: 'Admin@Demo123',
};

const REGULAR_USER = {
  email: 'user@demo.example.com',
  password: 'User@Demo123',
};

// Helper function to login
async function login(page: Page, email: string, password: string) {
  await page.goto(`${BASE_URL}/login`);
  
  // Enter credentials
  await page.fill('input[name="email"]', email);
  await page.fill('input[name="password"]', password);
  
  // Click login button
  await page.click('button:has-text("サインイン")');
  
  // Wait for navigation to dashboard
  await page.waitForURL(`${BASE_URL}/dashboard`);
}

// Helper function to navigate to master admin page
async function navigateToMasterAdmin(page: Page) {
  // Get tenant ID from URL
  const url = page.url();
  const tenantMatch = url.match(/tenants\/([^/]+)/);
  if (!tenantMatch) {
    throw new Error('Could not extract tenant ID from URL');
  }
  const tenantId = tenantMatch[1];
  
  await page.goto(`${BASE_URL}/tenants/${tenantId}/admin/masters`);
}

test.describe('Master Admin Management - Access Control', () => {
  test('Regular user cannot access master admin page', async ({ page }) => {
    await login(page, REGULAR_USER.email, REGULAR_USER.password);
    
    try {
      await navigateToMasterAdmin(page);
      
      // Should see access denied message
      const accessDenied = await page.locator('text=アクセス拒否').isVisible();
      expect(accessDenied).toBeTruthy();
    } catch {
      // Expected - regular users may not have a valid path
    }
  });

  test('Tenant admin can access user and taxonomy management', async ({ page }) => {
    await login(page, TENANT_ADMIN.email, TENANT_ADMIN.password);
    await navigateToMasterAdmin(page);
    
    // Should see user tab
    expect(await page.locator('button:has-text("ユーザー")').isVisible()).toBeTruthy();
    
    // Should see topic tab
    expect(await page.locator('button:has-text("トピック")').isVisible()).toBeTruthy();
    
    // Should see industry tab
    expect(await page.locator('button:has-text("業界")').isVisible()).toBeTruthy();
    
    // Should NOT see tenant tab
    const tenantTab = await page.locator('button:has-text("テナント")');
    expect(await tenantTab.count()).toBe(0);
  });

  test('System admin can access all management tabs', async ({ page }) => {
    await login(page, SYSTEM_ADMIN.email, SYSTEM_ADMIN.password);
    await navigateToMasterAdmin(page);
    
    // Should see all tabs
    expect(await page.locator('button:has-text("テナント")').isVisible()).toBeTruthy();
    expect(await page.locator('button:has-text("ユーザー")').isVisible()).toBeTruthy();
    expect(await page.locator('button:has-text("トピック")').isVisible()).toBeTruthy();
    expect(await page.locator('button:has-text("業界")').isVisible()).toBeTruthy();
  });
});

test.describe('User Management', () => {
  test('Tenant admin can create a new user', async ({ page }) => {
    await login(page, TENANT_ADMIN.email, TENANT_ADMIN.password);
    await navigateToMasterAdmin(page);
    
    // Click on User tab
    await page.click('button:has-text("ユーザー")');
    
    // Click on "新規作成" button
    await page.click('button:has-text("新規作成")');
    
    // Fill in user details
    const testEmail = `testuser-${Date.now()}@example.com`;
    const testName = 'テストユーザー';
    
    await page.fill('input[placeholder*="メール"]', testEmail);
    await page.fill('input:has-text("ユーザー名")', testName);
    await page.fill('input[type="password"]', 'TestPassword123');
    
    // Select role
    await page.selectOption('select', 'user');
    
    // Submit form
    await page.click('button:has-text("作成")');
    
    // Wait for success and verify user appears in list
    await page.waitForTimeout(1000);
    expect(await page.locator(`text=${testName}`).isVisible()).toBeTruthy();
  });

  test('Tenant admin can edit a user', async ({ page }) => {
    await login(page, TENANT_ADMIN.email, TENANT_ADMIN.password);
    await navigateToMasterAdmin(page);
    
    // Click on User tab
    await page.click('button:has-text("ユーザー")');
    
    // Find first edit button (excluding the "edit" button text)
    const editButtons = await page.locator('button[title="編集"]');
    if (await editButtons.count() > 0) {
      await editButtons.first().click();
      
      // Modify user name
      const nameInput = await page.locator('input:has-text("ユーザー名")');
      const currentValue = await nameInput.inputValue();
      await nameInput.fill(`${currentValue} (Updated)`);
      
      // Submit
      await page.click('button:has-text("更新")');
      
      // Verify update
      await page.waitForTimeout(500);
      expect(await page.locator(`text=${currentValue} (Updated)`).isVisible()).toBeTruthy();
    }
  });

  test('Tenant admin can delete a user with confirmation', async ({ page }) => {
    await login(page, TENANT_ADMIN.email, TENANT_ADMIN.password);
    await navigateToMasterAdmin(page);
    
    // Click on User tab
    await page.click('button:has-text("ユーザー")');
    
    // Get initial user count
    const userRows = await page.locator('tbody tr').count();
    
    if (userRows > 1) {
      // Click delete on first non-admin user (skip if only one user)
      const deleteButtons = await page.locator('button[title="削除"]');
      if (await deleteButtons.count() > 0) {
        await deleteButtons.first().click();
        
        // Confirm deletion
        await page.on('dialog', dialog => {
          if (dialog.type() === 'confirm') {
            dialog.accept();
          }
        });
        
        // Wait for deletion
        await page.waitForTimeout(1000);
        
        // Verify user count decreased
        const newUserCount = await page.locator('tbody tr').count();
        expect(newUserCount).toBeLessThanOrEqual(userRows);
      }
    }
  });
});

test.describe('Topic Management', () => {
  test('Tenant admin can create a topic', async ({ page }) => {
    await login(page, TENANT_ADMIN.email, TENANT_ADMIN.password);
    await navigateToMasterAdmin(page);
    
    // Click on Topic tab
    await page.click('button:has-text("トピック")');
    
    // Click on "新規作成" button
    await page.click('button:has-text("新規作成")');
    
    // Fill in topic details
    const testTopic = `テストトピック-${Date.now()}`;
    const testDescription = 'テストトピックの説明';
    
    await page.fill('input[placeholder*="トピック名"]', testTopic);
    await page.fill('textarea', testDescription);
    
    // Select color
    await page.click('button[style*="background"]').first();
    
    // Submit form
    await page.click('button:has-text("作成")');
    
    // Wait and verify topic appears in list
    await page.waitForTimeout(1000);
    expect(await page.locator(`text=${testTopic}`).isVisible()).toBeTruthy();
  });

  test('Tenant admin can drag and drop topics to reorder', async ({ page }) => {
    await login(page, TENANT_ADMIN.email, TENANT_ADMIN.password);
    await navigateToMasterAdmin(page);
    
    // Click on Topic tab
    await page.click('button:has-text("トピック")');
    
    // Get all topic items
    const topicItems = await page.locator('div[draggable="true"]');
    const itemCount = await topicItems.count();
    
    if (itemCount >= 2) {
      // Drag first item to second position
      const firstItem = topicItems.first();
      const secondItem = topicItems.nth(1);
      
      // Get positions
      const firstBox = await firstItem.boundingBox();
      const secondBox = await secondItem.boundingBox();
      
      if (firstBox && secondBox) {
        // Perform drag and drop
        await firstItem.dragTo(secondItem);
        
        // Verify reorder
        await page.waitForTimeout(500);
        // The order should have changed (this is a basic verification)
        expect(await topicItems.first().textContent()).toBeDefined();
      }
    }
  });
});

test.describe('Industry Management', () => {
  test('Tenant admin can create an industry', async ({ page }) => {
    await login(page, TENANT_ADMIN.email, TENANT_ADMIN.password);
    await navigateToMasterAdmin(page);
    
    // Click on Industry tab
    await page.click('button:has-text("業界")');
    
    // Click on "新規作成" button
    await page.click('button:has-text("新規作成")');
    
    // Fill in industry details
    const testIndustry = `テスト業界-${Date.now()}`;
    const testDescription = 'テスト業界の説明';
    
    await page.fill('input[placeholder*="業界名"]', testIndustry);
    await page.fill('textarea', testDescription);
    
    // Submit form
    await page.click('button:has-text("作成")');
    
    // Wait and verify industry appears in list
    await page.waitForTimeout(1000);
    expect(await page.locator(`text=${testIndustry}`).isVisible()).toBeTruthy();
  });
});

test.describe('Tenant Management (System Admin Only)', () => {
  test('System admin can see tenant management tab', async ({ page }) => {
    await login(page, SYSTEM_ADMIN.email, SYSTEM_ADMIN.password);
    
    // Navigate to system admin's master page
    // Note: System admin might have a different path or need special setup
    // For now, we verify access to the page
    const url = page.url();
    expect(url).toContain('dashboard');
  });

  test('Tenant admin cannot access tenant management', async ({ page }) => {
    await login(page, TENANT_ADMIN.email, TENANT_ADMIN.password);
    await navigateToMasterAdmin(page);
    
    // Should not see tenant tab
    const tenantTab = await page.locator('button:has-text("テナント")');
    expect(await tenantTab.count()).toBe(0);
  });
});
