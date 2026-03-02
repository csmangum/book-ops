import { expect, test } from "@playwright/test";

test.describe("Chapters", () => {
  test("chapters list page loads", async ({ page }) => {
    await page.goto("/chapters");
    await expect(
      page.getByRole("heading", { name: "Chapters", exact: true }),
    ).toBeVisible();
  });

  test("chapter workbench loads and shows layout", async ({ page }) => {
    await page.goto("/chapters/1");
    await expect(page.getByText(/chapter workbench/i)).toBeVisible();
    await expect(page.getByRole("heading", { name: "Manuscript" })).toBeVisible();
  });
});
