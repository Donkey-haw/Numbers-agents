import { expect, test } from '@playwright/test';

const CHROME_PATH = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';

test.use({
  launchOptions: {
    executablePath: CHROME_PATH,
    headless: true,
  },
});

test('manual page selection toggles textbook pages by thumbnail click', async ({ page }) => {
  await page.goto('http://localhost:5172');

  await page.getByRole('button', { name: /새 Run/i }).click();
  await expect(page).toHaveURL(/\/runs\/new$/);
  await expect(page.getByRole('heading', { name: '수동 페이지 선택' })).toBeVisible();
  await expect(page.getByText(/레거시 진도표 위저드/)).toHaveCount(0);
  await page.getByRole('button', { name: '사회' }).click();
  await page.getByRole('button', { name: /\[사회\]6_1_교과서\.pdf/ }).click();

  await expect(page.getByText(/전체 \d+페이지/)).toBeVisible();
  await page.getByPlaceholder('차시 메모 (선택)').fill('테스트 차시');

  await page.getByTitle('110페이지').click();
  await page.getByTitle('111페이지').click();

  await expect(page.getByText('110-111')).toBeVisible();
  await expect(page.getByRole('button', { name: /▶ 실행/ })).toBeEnabled();
});
