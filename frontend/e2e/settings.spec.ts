import { expect, test } from "@playwright/test";

test.describe("Settings", () => {
  test("settings page loads with project paths form", async ({ page }) => {
    await page.goto("/settings");
    await expect(page.getByRole("heading", { name: /settings/i })).toBeVisible();
    await expect(page.getByText(/project paths/i)).toBeVisible();
  });
});
