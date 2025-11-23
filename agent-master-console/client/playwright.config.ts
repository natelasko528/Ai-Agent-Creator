import { defineConfig, devices } from '@playwright/test'
import fs from 'fs'
import path from 'path'

const serverDir = path.join(__dirname, '../server')
const uvicornBin = process.env.UVICORN_BIN
  ?? (process.platform === 'win32'
    ? path.join(serverDir, '.venv', 'Scripts', 'uvicorn.exe')
    : path.join(serverDir, '.venv', 'bin', 'uvicorn'))
const uvicornFallback = 'python -m uvicorn main:app --host 0.0.0.0 --port 8000'
const uvicornCommand = fs.existsSync(uvicornBin)
  ? `${uvicornBin} main:app --host 0.0.0.0 --port 8000`
  : uvicornFallback
const mockEnvPrefix = process.platform === 'win32' ? '' : 'MOCK_MODE=1'

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
      command: [mockEnvPrefix, uvicornCommand].filter(Boolean).join(' '),
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
