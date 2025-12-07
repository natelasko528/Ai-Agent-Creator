import type { FullConfig } from '@playwright/test'
import fs from 'fs'
import path from 'path'

async function globalSetup(_config: FullConfig) {
  const templatesDir = path.resolve(__dirname, '../server/agent_core/templates')
  if (!fs.existsSync(templatesDir)) return

  for (const entry of fs.readdirSync(templatesDir)) {
    if (entry.endsWith('.json')) {
      fs.unlinkSync(path.join(templatesDir, entry))
    }
  }
}

export default globalSetup
