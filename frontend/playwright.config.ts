import path from "node:path";
import { defineConfig, devices } from "@playwright/test";

const projectRoot = path.resolve(process.cwd(), "..");

export default defineConfig({
  testDir: "./e2e",
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: "html",
  use: {
    baseURL: "http://localhost:3000",
    trace: "on-first-retry",
  },
  projects: [{ name: "chromium", use: { ...devices["Desktop Chrome"] } }],
  webServer: [
    {
      command: "python3 -m uvicorn bookops.api:app --host 0.0.0.0 --port 8000",
      cwd: projectRoot,
      env: {
        ...process.env,
        BOOKOPS_PROJECT: process.env.BOOKOPS_PROJECT || projectRoot,
        BOOKOPS_OUTPUT_DIR: "reports",
      },
      port: 8000,
      reuseExistingServer: !process.env.CI,
    },
    {
      command: "npm run dev",
      cwd: process.cwd(),
      env: {
        ...process.env,
        NEXT_PUBLIC_API_URL: "http://localhost:8000",
      },
      port: 3000,
      reuseExistingServer: !process.env.CI,
    },
  ],
});
