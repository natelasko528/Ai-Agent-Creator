import { test, expect, Page } from '@playwright/test'

const APP_URL = '/'

async function openApp(page: Page) {
  await page.goto(APP_URL)
  await expect(page.getByTestId('new-agent-button')).toBeVisible()
}

test('user can create an agent and exchange a message', async ({ page }) => {
  const agentName = `Weekly Tester ${Date.now()}`
  const systemPrompt = 'Respond cheerfully with mock data.'
  const userMessage = 'Hello from Playwright'

  await openApp(page)

  await page.getByTestId('new-agent-button').click()
  await page.getByTestId('agent-name-input').fill(agentName)
  await page.getByTestId('agent-prompt-input').fill(systemPrompt)
  await page.getByTestId('create-agent-button').click()

  await expect(page.getByText(agentName)).toBeVisible()
  await page.getByText(agentName).click()

  await page.getByTestId('chat-input').fill(userMessage)
  await page.getByTestId('send-message-button').click()

  await expect(page.locator('.text-blue-300', { hasText: userMessage })).toBeVisible()
  await expect(page.locator('.text-gray-200', { hasText: 'You said:' })).toBeVisible()
})
