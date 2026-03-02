import { expect, test } from "@playwright/test";

test.describe("Home / Command Center", () => {
  test("loads command center and shows main sections", async ({ page }) => {
    await page.goto("/");
    await expect(page.getByRole("heading", { name: /command center/i })).toBeVisible();
    await expect(page.getByText(/index status/i)).toBeVisible();
  });

  test("sidebar navigation links work", async ({ page }) => {
    await page.goto("/");
    await page.getByRole("link", { name: "Chapters" }).click();
    await expect(page).toHaveURL(/\/chapters/);
    await page.getByRole("link", { name: "Issues" }).click();
    await expect(page).toHaveURL(/\/issues/);
    await page.getByRole("link", { name: "Settings" }).click();
    await expect(page).toHaveURL(/\/settings/);
  });
});
