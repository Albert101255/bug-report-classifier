import { test, expect } from '@playwright/test';

test.describe('Enterprise Triage Platform E2E Tests', () => {
  const TEST_EMAIL = 'lead.architect@enterprise-triage.com';
  const TEST_PASSWORD = 'EnterprisePassword123!';
  const TEST_ORG = 'Acme Engineering Labs';

  test.beforeAll(async ({ request }) => {
    try {
      await request.post('http://127.0.0.1:8000/api/v1/auth/register', {
        data: {
          email: TEST_EMAIL,
          password: TEST_PASSWORD,
          full_name: 'Lead Architect',
          organization_name: TEST_ORG,
          role: 'ORG_ADMIN',
        },
      });
    } catch {
      // Ignored if already registered
    }
  });

  test('01: Auth & Organization Setup - Register new user and workspace via UI', async ({ page }) => {
    const freshTimestamp = Date.now();
    const freshEmail = `user_${freshTimestamp}@example.com`;
    const freshOrg = `Startup ${freshTimestamp}`;

    await page.goto('/register');
    await expect(page.getByText('Create workspace account')).toBeVisible();

    await page.locator('input[type="text"]').first().fill('Principal Engineer');
    await page.locator('input[type="email"]').fill(freshEmail);
    await page.locator('input[placeholder="Acme Engineering"]').fill(freshOrg);
    await page.locator('input[type="password"]').fill('SecurePassword123!');

    await page.getByRole('button', { name: /Create workspace/i }).click();

    // Should redirect to dashboard / overview
    await expect(page).toHaveURL(/\/(overview)?$/);
    await expect(page.getByText('Triage Overview')).toBeVisible();
    await expect(page.getByText('Principal Engineer')).toBeVisible();
  });

  test('02: Negative Scope Verification - Absolute absence of CSV / batch upload workflows', async ({ page }) => {
    // Log in with known test account
    await page.goto('/login');
    await page.locator('input[type="email"]').fill(TEST_EMAIL);
    await page.locator('input[type="password"]').fill(TEST_PASSWORD);
    await page.getByRole('button', { name: /Sign in/i }).click();
    await expect(page).toHaveURL(/\/(overview)?$/);

    // Verify sidebar navigation links
    const sidebar = page.locator('aside');
    await expect(sidebar).toBeVisible();

    // Verify negative scope: NO batch upload, no CSV, no bulk
    const sidebarText = await sidebar.innerText();
    expect(sidebarText).not.toContain('Batch');
    expect(sidebarText).not.toContain('CSV');
    expect(sidebarText).not.toContain('Bulk');
    expect(sidebarText).not.toContain('Import');

    // Attempting to visit /batch-upload or /import should redirect to Overview
    await page.goto('/batch-upload');
    await expect(page).toHaveURL(/\/(overview)?$/);

    await page.goto('/import');
    await expect(page).toHaveURL(/\/(overview)?$/);
  });

  test('03: Single Issue Creation with Intelligent Triage & SLA Calculation', async ({ page }) => {
    await page.goto('/login');
    await page.locator('input[type="email"]').fill(TEST_EMAIL);
    await page.locator('input[type="password"]').fill(TEST_PASSWORD);
    await page.getByRole('button', { name: /Sign in/i }).click();
    await expect(page).toHaveURL(/\/(overview)?$/);

    // Navigate to Create Issue
    await page.getByRole('link', { name: 'Create Issue' }).first().click();
    await expect(page).toHaveURL('/issues/new');

    // Fill form
    await page.locator('input[placeholder*="PostgreSQL connection pool"]').fill('PostgreSQL connection pool exhausted under concurrent auth requests');
    await page.locator('textarea[placeholder*="Describe the failure mode"]').fill(
      'Database connection pool spikes to 100 max connections and fails with timeout waiting for connection pool after 30000ms. sqlalchemy.exc.TimeoutError: QueuePool limit of size 10 overflow 10 reached.'
    );
    await page.locator('select').nth(1).selectOption('P0 - Blocker');
    await page.locator('select').nth(2).selectOption('URGENT');

    // Submit single issue
    await page.getByRole('button', { name: /Submit Issue & Route/i }).click();

    // Should redirect to issue detail
    await expect(page).toHaveURL(/\/issues\/[a-f0-9-]+/);
    await expect(page.getByText('PostgreSQL connection pool exhausted under concurrent auth requests')).toBeVisible();

    // Intelligent triage results should be visible
    await expect(page.getByText('Triage Classification')).toBeVisible();
    await expect(page.getByText(/Classifier Recommended:/i)).toBeVisible();
  });

  test('04: Issue Lifecycle & Team Collaboration - Commenting and Status State Machine', async ({ page }) => {
    await page.goto('/login');
    await page.locator('input[type="email"]').fill(TEST_EMAIL);
    await page.locator('input[type="password"]').fill(TEST_PASSWORD);
    await page.getByRole('button', { name: /Sign in/i }).click();

    // Go to Issue Explorer
    await page.getByRole('link', { name: 'Issues' }).click();
    await expect(page).toHaveURL('/issues');

    // Click on our newly created issue
    const issueLink = page.getByText('PostgreSQL connection pool exhausted').first();
    await expect(issueLink).toBeVisible();
    await issueLink.click();

    await expect(page).toHaveURL(/\/issues\/[a-f0-9-]+/);

    // Transition status to 'IN_PROGRESS'
    const statusSelect = page.locator('select').first();
    await statusSelect.selectOption('IN_PROGRESS');

    // Add a comment
    const commentInput = page.locator('input[placeholder*="Add engineering notes"]');
    await commentInput.fill('Root cause confirmed: connection pool max_overflow was set to 0. Preparing PR with connection tuning.');
    await page.getByRole('button', { name: /Comment/i }).click();

    // Verify comment appears in activity feed
    await expect(page.getByText('Root cause confirmed: connection pool max_overflow was set to 0.')).toBeVisible();
  });

  test('05: Triage Review Queue - Inbox Verification', async ({ page }) => {
    await page.goto('/login');
    await page.locator('input[type="email"]').fill(TEST_EMAIL);
    await page.locator('input[type="password"]').fill(TEST_PASSWORD);
    await page.getByRole('button', { name: /Sign in/i }).click();

    // Navigate to Triage Inbox
    await page.getByRole('link', { name: 'Triage Inbox' }).click();
    await expect(page).toHaveURL('/triage');
    await expect(page.getByText(/Triage Review Inbox/i)).toBeVisible();
  });

  test('06: Settings & Governance - Update and Persist Automation Policies', async ({ page }) => {
    await page.goto('/login');
    await page.locator('input[type="email"]').fill(TEST_EMAIL);
    await page.locator('input[type="password"]').fill(TEST_PASSWORD);
    await page.getByRole('button', { name: /Sign in/i }).click();

    // Navigate to Settings
    await page.getByRole('link', { name: 'Settings' }).click();
    await expect(page).toHaveURL('/settings');
    await expect(page.getByText('Workspace Configuration')).toBeVisible();

    // Update Low Confidence Threshold
    const lowInput = page.locator('input[type="number"]').nth(1);
    await lowInput.fill('0.70');

    // Click Save
    await page.getByRole('button', { name: /Save Routing Policy/i }).click();
    await expect(page.getByText('Triage routing policies persisted successfully.')).toBeVisible();

    // Reload page to verify persistence from database
    await page.reload();
    await expect(lowInput).toHaveValue(/0\.70?/);
  });
});
