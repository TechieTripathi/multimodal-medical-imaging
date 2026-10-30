// Screenshot slides from a running Slidev dev server.
// Usage: node scripts/shot.mjs <port> <outDir> <slide[:clicks]> [...more]
//   e.g. node scripts/shot.mjs 3031 /tmp/shots 7 8 12:0 12:3 12:6
// Captures at 1960x1104 (2x the 980x552 canvas). Prints console errors from the page.
import { chromium } from 'playwright-chromium'
import { mkdirSync } from 'node:fs'

const [port, outDir, ...specs] = process.argv.slice(2)
if (!port || !outDir || !specs.length) {
  console.error('Usage: node scripts/shot.mjs <port> <outDir> <slide[:clicks]> ...')
  process.exit(1)
}
mkdirSync(outDir, { recursive: true })
const browser = await chromium.launch()
const page = await browser.newPage({ viewport: { width: 980, height: 552 }, deviceScaleFactor: 2 })
const errors = []
page.on('console', m => { if (m.type() === 'error') errors.push(m.text()) })
page.on('pageerror', e => errors.push(String(e)))
for (const spec of specs) {
  const [no, clicks = '0'] = spec.split(':')
  await page.goto(`http://localhost:${port}/${no}?clicks=${clicks}&embedded=true`, { waitUntil: 'networkidle' })
  await page.waitForTimeout(900)
  const file = `${outDir}/slide-${String(no).padStart(2, '0')}-c${clicks}.png`
  await page.screenshot({ path: file })
  console.log(file)
}
if (errors.length) console.log('PAGE ERRORS:\n' + [...new Set(errors)].join('\n'))
await browser.close()
