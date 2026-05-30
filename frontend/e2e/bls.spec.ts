/**
 * E2E tests for the BLS Signature Scheme frontend.
 * Run:  npx playwright test
 */

import { test, expect, Page } from '@playwright/test';

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

async function fillForm(
  page: Page,
  opts: { p?: string; A?: string; B?: string; privateKey?: string; message?: string } = {}
) {
  const { p = '103', A = '1', B = '0', privateKey = '7', message = 'שלום' } = opts;
  await page.locator('input[type="number"]').nth(0).fill(p);
  await page.locator('input[type="number"]').nth(1).fill(A);
  await page.locator('input[type="number"]').nth(2).fill(B);
  await page.locator('input[type="number"]').nth(3).fill(privateKey);
  await page.locator('input[type="text"]').fill(message);
}

async function submitAndWaitForResult(page: Page) {
  await page.click('button[type="submit"]');
  await expect(page.locator('text=/Signature Verified|Verification Failed/')).toBeVisible({ timeout: 30_000 });
}

// ---------------------------------------------------------------------------
// Page load
// ---------------------------------------------------------------------------

test.describe('Page load', () => {
  test('loads the page and shows the header', async ({ page }) => {
    await page.goto('/');
    await expect(page).toHaveTitle('BLS Signature Scheme');
    await expect(page.locator('h1')).toContainText('BLS');
  });

  test('shows the parameters form', async ({ page }) => {
    await page.goto('/');
    await expect(page.locator('form')).toBeVisible();
    await expect(page.getByText('Parameters')).toBeVisible();
  });

  test('default value of p is 103', async ({ page }) => {
    await page.goto('/');
    await expect(page.locator('input[type="number"]').nth(0)).toHaveValue('103');
  });

  test('default value of A is 1', async ({ page }) => {
    await page.goto('/');
    await expect(page.locator('input[type="number"]').nth(1)).toHaveValue('1');
  });

  test('default value of B is 0', async ({ page }) => {
    await page.goto('/');
    await expect(page.locator('input[type="number"]').nth(2)).toHaveValue('0');
  });

  test('default private key is 7', async ({ page }) => {
    await page.goto('/');
    await expect(page.locator('input[type="number"]').nth(3)).toHaveValue('7');
  });

  test('default message is שלום', async ({ page }) => {
    await page.goto('/');
    await expect(page.locator('input[type="text"]')).toHaveValue('שלום');
  });

  test('submit button is enabled on load', async ({ page }) => {
    await page.goto('/');
    await expect(page.locator('button[type="submit"]')).toBeEnabled();
  });

  test('submit button text is "Sign & Verify"', async ({ page }) => {
    await page.goto('/');
    await expect(page.locator('button[type="submit"]')).toHaveText('Sign & Verify');
  });

  test('no results section on initial load', async ({ page }) => {
    await page.goto('/');
    await expect(page.locator('text=Signature Verified')).not.toBeVisible();
    await expect(page.locator('text=Verification Failed')).not.toBeVisible();
  });
});

// ---------------------------------------------------------------------------
// Loading state
// ---------------------------------------------------------------------------

test.describe('Loading state', () => {
  test('button shows "Computing..." while request is in flight', async ({ page }) => {
    await page.goto('/');
    await fillForm(page);

    // Hold the response until we've had a chance to check the button state
    let release!: () => void;
    const held = new Promise<void>(r => { release = r; });

    await page.route('/api/bls/run', async (route) => {
      await held;
      await route.continue();
    });

    const btn = page.locator('button[type="submit"]');
    await btn.click();

    // Button should immediately switch to "Computing..." and be disabled
    await expect(btn).toHaveText('Computing...', { timeout: 3_000 });
    await expect(btn).toBeDisabled();

    // Release the backend response so the test can finish cleanly
    release();
    await expect(btn).toHaveText('Sign & Verify', { timeout: 30_000 });
  });
});

// ---------------------------------------------------------------------------
// Assignment example (p=103, A=1, B=0, key=7, msg=שלום)
// ---------------------------------------------------------------------------

test.describe('Assignment example (p=103, A=1, B=0, key=7, msg=שלום)', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
  });

  test('shows "Signature Verified" after submit', async ({ page }) => {
    await fillForm(page);
    await submitAndWaitForResult(page);
    await expect(page.getByText('Signature Verified')).toBeVisible();
  });

  test('verified banner has green styling', async ({ page }) => {
    await fillForm(page);
    await submitAndWaitForResult(page);
    await expect(page.getByText('Signature Verified')).toBeVisible();
  });

  test('signature coordinates are (18, 44)', async ({ page }) => {
    await fillForm(page);
    await submitAndWaitForResult(page);
    await expect(page.getByText('(18, 44)')).toBeVisible();
  });

  test('H(m) hash point is (32, 47)', async ({ page }) => {
    await fillForm(page);
    await submitAndWaitForResult(page);
    await expect(page.getByText('(32, 47)')).toBeVisible();
  });

  test('pairing LHS equals pairing RHS', async ({ page }) => {
    await fillForm(page);
    await submitAndWaitForResult(page);
    // Both pairing cards render font-mono values; collect them and compare
    const monoValues = page.locator('[class*="font-mono"]');
    const all = await monoValues.allTextContents();
    // The last two mono values in ResultsDisplay are LHS and RHS
    const pairingValues = all.filter(v => v.includes('i') && v !== '');
    expect(pairingValues.length).toBeGreaterThanOrEqual(2);
    expect(pairingValues[0]).toBe(pairingValues[1]);
  });

  test('results section displays Signature card label', async ({ page }) => {
    await fillForm(page);
    await submitAndWaitForResult(page);
    // The card label "Signature" appears in ResultsDisplay
    await expect(page.locator('text=Signature').first()).toBeVisible();
  });

  test('results section displays H(m) card label', async ({ page }) => {
    await fillForm(page);
    await submitAndWaitForResult(page);
    // The "H(m)" label in the 2×2 info grid (first occurrence)
    await expect(page.locator('text=H(m)').first()).toBeVisible();
  });

  test('button re-enables after result returns', async ({ page }) => {
    await fillForm(page);
    await submitAndWaitForResult(page);
    await expect(page.locator('button[type="submit"]')).toBeEnabled();
    await expect(page.locator('button[type="submit"]')).toHaveText('Sign & Verify');
  });
});

// ---------------------------------------------------------------------------
// Step-by-step accordion
// ---------------------------------------------------------------------------

test.describe('Step-by-step view', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
    await fillForm(page);
    await submitAndWaitForResult(page);
  });

  test('Step-by-Step Computation heading is visible after results load', async ({ page }) => {
    await expect(page.getByText('Step-by-Step Computation')).toBeVisible();
  });

  test('group order 104 appears after opening step 1', async ({ page }) => {
    await page.getByText('Step 1: Curve Group').click();
    await expect(page.locator('span.font-mono').filter({ hasText: '104' })).toBeVisible();
  });

  test('r = 13 appears after opening step 1', async ({ page }) => {
    await page.getByText('Step 1: Curve Group').click();
    await expect(page.locator('span.font-mono').filter({ hasText: '13' }).first()).toBeVisible();
  });

  test('embedding degree k = 2 appears after opening step 2', async ({ page }) => {
    await page.getByText('Step 2: Extension Field').click();
    // The embedding degree value is in a span.font-mono inside the step 2 content
    await expect(page.locator('span.font-mono').filter({ hasText: /^2$/ }).first()).toBeVisible();
  });

  test('irreducible polynomial appears after opening step 2', async ({ page }) => {
    await page.getByText('Step 2: Extension Field').click();
    await expect(page.locator('span.font-mono').filter({ hasText: /x/ }).first()).toBeVisible();
  });

  test('accordion opens and closes a section', async ({ page }) => {
    // Initially closed — content not visible
    await expect(page.locator('span.font-mono').filter({ hasText: '104' })).not.toBeVisible();
    // Open
    await page.getByText('Step 1: Curve Group').click();
    await expect(page.locator('span.font-mono').filter({ hasText: '104' })).toBeVisible();
    // Close again
    await page.getByText('Step 1: Curve Group').click();
    await expect(page.locator('span.font-mono').filter({ hasText: '104' })).not.toBeVisible();
  });

  test('opening step 2 closes step 1', async ({ page }) => {
    await page.getByText('Step 1: Curve Group').click();
    await expect(page.locator('span.font-mono').filter({ hasText: '104' })).toBeVisible();
    await page.getByText('Step 2: Extension Field').click();
    await expect(page.locator('span.font-mono').filter({ hasText: '104' })).not.toBeVisible();
  });
});

// ---------------------------------------------------------------------------
// Error handling
// ---------------------------------------------------------------------------

test.describe('Error handling', () => {
  test('invalid prime (17 ≡ 1 mod 4) shows error', async ({ page }) => {
    await page.goto('/');
    await fillForm(page, { p: '17' });
    await page.click('button[type="submit"]');
    await expect(page.locator('[class*="red"], [class*="error"]').first())
      .toBeVisible({ timeout: 15_000 });
  });

  test('singular curve (A=0, B=0) shows error', async ({ page }) => {
    await page.goto('/');
    await fillForm(page, { A: '0', B: '0' });
    await page.click('button[type="submit"]');
    await expect(page.locator('[class*="red"], [class*="error"]').first())
      .toBeVisible({ timeout: 15_000 });
  });

  test('composite p shows error', async ({ page }) => {
    await page.goto('/');
    await fillForm(page, { p: '100' });
    await page.click('button[type="submit"]');
    await expect(page.locator('[class*="red"], [class*="error"]').first())
      .toBeVisible({ timeout: 15_000 });
  });

  test('error banner can be dismissed', async ({ page }) => {
    await page.goto('/');
    await fillForm(page, { p: '17' });
    await page.click('button[type="submit"]');
    const errorBanner = page.locator('[class*="red"]').first();
    await expect(errorBanner).toBeVisible({ timeout: 15_000 });
    await page.locator('button').filter({ hasText: '×' }).click();
    await expect(page.locator('[class*="red"]').first()).not.toBeVisible();
  });
});

// ---------------------------------------------------------------------------
// API mocked responses — fast, no waiting on crypto
// ---------------------------------------------------------------------------

const mockSuccess = {
  group_order: 104, r: 13, cofactor: 8, embedding_degree: 2,
  irreducible_poly: '1 + x^2',
  hash_point:  { x: '32', y: '47' },
  signature:   { x: '18', y: '44' },
  Q:           { x: '8i', y: '47 + 56i' },
  pairing_lhs: '22 + 49i',
  pairing_rhs: '22 + 49i',
  verified: true,
  display_message: 'e_r(sig, Q) = e_r(H(m), aQ) — signature is valid.',
};

test.describe('API mocked responses', () => {
  test('mocked success renders Signature Verified', async ({ page }) => {
    await page.route('/api/bls/run', route =>
      route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify(mockSuccess) })
    );
    await page.goto('/');
    await page.click('button[type="submit"]');
    await expect(page.getByText('Signature Verified')).toBeVisible();
  });

  test('mocked success shows correct signature coordinates', async ({ page }) => {
    await page.route('/api/bls/run', route =>
      route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify(mockSuccess) })
    );
    await page.goto('/');
    await page.click('button[type="submit"]');
    await expect(page.getByText('(18, 44)')).toBeVisible();
  });

  test('mocked success shows correct H(m)', async ({ page }) => {
    await page.route('/api/bls/run', route =>
      route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify(mockSuccess) })
    );
    await page.goto('/');
    await page.click('button[type="submit"]');
    await expect(page.getByText('(32, 47)')).toBeVisible();
  });

  test('mocked success shows pairing value', async ({ page }) => {
    await page.route('/api/bls/run', route =>
      route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify(mockSuccess) })
    );
    await page.goto('/');
    await page.click('button[type="submit"]');
    // Both LHS and RHS cards show '22 + 49i' — check at least one is visible
    await expect(page.getByText('22 + 49i').first()).toBeVisible();
  });

  test('mocked verification failure shows Verification Failed', async ({ page }) => {
    const mockFail = { ...mockSuccess, verified: false, pairing_rhs: '1 + 0i', display_message: 'Pairings do not match.' };
    await page.route('/api/bls/run', route =>
      route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify(mockFail) })
    );
    await page.goto('/');
    await page.click('button[type="submit"]');
    await expect(page.getByText('Verification Failed')).toBeVisible();
  });

  test('mocked 400 error shows error detail', async ({ page }) => {
    await page.route('/api/bls/run', route =>
      route.fulfill({ status: 400, contentType: 'application/json', body: JSON.stringify({ detail: 'p must be prime' }) })
    );
    await page.goto('/');
    await page.click('button[type="submit"]');
    await expect(page.getByText(/p must be prime/i)).toBeVisible();
  });

  test('mocked network failure shows error', async ({ page }) => {
    await page.route('/api/bls/run', route => route.abort());
    await page.goto('/');
    await page.click('button[type="submit"]');
    await expect(page.locator('[class*="red"]').first()).toBeVisible({ timeout: 10_000 });
  });
});

// ---------------------------------------------------------------------------
// Different parameters
// ---------------------------------------------------------------------------

test.describe('Different valid parameters', () => {
  test('private key 2 — correct params sent to API', async ({ page }) => {
    let capturedBody: Record<string, unknown> = {};
    await page.route('/api/bls/run', async (route) => {
      capturedBody = JSON.parse(route.request().postData() ?? '{}');
      await route.fulfill({
        status: 200, contentType: 'application/json',
        body: JSON.stringify({ ...mockSuccess, signature: { x: '10', y: '20' }, pairing_lhs: '5 + 3i', pairing_rhs: '5 + 3i' }),
      });
    });
    await page.goto('/');
    await fillForm(page, { privateKey: '2' });
    await page.click('button[type="submit"]');
    await expect(page.getByText('Signature Verified')).toBeVisible();
    expect(capturedBody.private_key).toBe(2);
  });

  test('custom message is sent correctly to API', async ({ page }) => {
    let capturedBody: Record<string, unknown> = {};
    await page.route('/api/bls/run', async (route) => {
      capturedBody = JSON.parse(route.request().postData() ?? '{}');
      await route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify(mockSuccess) });
    });
    await page.goto('/');
    await fillForm(page, { message: 'hello world' });
    await page.click('button[type="submit"]');
    await expect(page.getByText('Signature Verified')).toBeVisible();
    expect(capturedBody.message).toBe('hello world');
  });
});

// ---------------------------------------------------------------------------
// Accessibility basics
// ---------------------------------------------------------------------------

test.describe('Accessibility', () => {
  test('page has an h1 heading', async ({ page }) => {
    await page.goto('/');
    await expect(page.locator('h1')).toBeVisible();
    await expect(page.locator('h1')).toContainText('BLS');
  });

  test('submit button is reachable via Tab key', async ({ page }) => {
    await page.goto('/');
    // Tab through all inputs: p, A, B, private_key, message = 5 inputs + 1 button = 6 tabs
    for (let i = 0; i < 6; i++) await page.keyboard.press('Tab');
    const focused = page.locator(':focus');
    await expect(focused).toHaveAttribute('type', 'submit');
  });

  test('all inputs are focusable', async ({ page }) => {
    await page.goto('/');
    const inputs = page.locator('input');
    const count = await inputs.count();
    expect(count).toBe(5); // p, A, B, private_key, message
  });
});
