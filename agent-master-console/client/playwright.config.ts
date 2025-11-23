import { defineConfig, devices } from '@playwright/test'
import path from 'path'

export default defineConfig({
  testDir: './tests',
  timeout: 30_000,
  expect: {
    timeout: 10_000,
  },
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 1 : 0,
  reporter: 'html',
  use: {
    baseURL: 'http://localhost:5173',
    trace: 'on-first-retry',
    headless: true,
  },
  globalSetup: path.join(__dirname, 'playwright.global-setup.ts'),
  webServer: [
    {
      command: 'MOCK_MODE=1 uvicorn main:app --host 0.0.0.0 --port 8000',
      cwd: path.join(__dirname, '../server'),
      env: {
        ...process.env,
        MOCK_MODE: '1',
      },
      port: 8000,
      timeout: 120_000,
      reuseExistingServer: !process.env.CI,
    },
    {
      command: 'npm run dev -- --host --port 5173',
      cwd: __dirname,
      port: 5173,
      timeout: 120_000,
      reuseExistingServer: !process.env.CI,
    },
  ],
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
  ],
})
