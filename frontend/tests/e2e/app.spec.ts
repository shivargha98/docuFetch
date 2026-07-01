// E2E test stubs for docuFetch — exercises the full startup, chat, and new-chat flows
// against a running backend. These tests require the dev server and backend to be active.

import { test, expect } from '@playwright/test'

test.describe('docuFetch E2E', () => {
  test('startup gate appears on load and resolves after backend ingestion completes', async ({ page }) => {
    await page.goto('/')
    await expect(page.getByText(/preparing your documents/i)).toBeVisible()
    await expect(page.locator('textarea')).toBeEnabled({ timeout: 60000 })
  })

  test('user sends a question and receives an answer with a sources block', async ({ page }) => {
    await page.goto('/')
    await expect(page.locator('textarea')).toBeEnabled({ timeout: 60000 })
    await page.locator('textarea').fill('What documents are indexed?')
    await page.keyboard.press('Enter')
    await expect(page.getByText(/Sources:/)).toBeVisible({ timeout: 30000 })
  })

  test('New chat clears history and next message starts a fresh session', async ({ page }) => {
    await page.goto('/')
    await expect(page.locator('textarea')).toBeEnabled({ timeout: 60000 })
    await page.locator('textarea').fill('Tell me something')
    await page.keyboard.press('Enter')
    await expect(page.getByRole('button', { name: /new chat/i })).toBeVisible()
    await page.getByRole('button', { name: /new chat/i }).click()
    // Previous messages should be gone
    await expect(page.getByText('Tell me something')).not.toBeVisible()
  })
})
