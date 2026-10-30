// Contact sheets of slides at their first and last click state, for visual review.
// Usage: node scripts/contact-sheet.mjs <port> <outDir> <from> <to> [perSheet=6]
import { chromium } from 'playwright-chromium'
import { mkdirSync, readFileSync } from 'node:fs'

const [port, outDir, from, to, perSheetArg] = process.argv.slice(2)
const perSheet = Number(perSheetArg ?? 6)
mkdirSync(outDir, { recursive: true })
const browser = await chromium.launch()
const page = await browser.newPage({ viewport: { width: 980, height: 552 }, deviceScaleFactor: 1 })
const errors = []
page.on('pageerror', e => errors.push(String(e).split('\n')[0]))
const shots = []
for (let n = Number(from); n <= Number(to); n++) {
  for (const c of [0, 99]) {
    await page.goto(`http://localhost:${port}/${n}?clicks=${c}&embedded=true`, { waitUntil: 'networkidle' })
    await page.waitForTimeout(700)
    const file = `${outDir}/s${String(n).padStart(2, '0')}-${c ? 'end' : 'start'}.png`
    await page.screenshot({ path: file })
    shots.push({ n, c, file })
  }
}
// Compose: each row = one slide (start | end)
const sheet = await browser.newPage({ viewport: { width: 1960, height: 100 }, deviceScaleFactor: 1 })
for (let i = 0; i < shots.length; i += perSheet * 2) {
  const group = shots.slice(i, i + perSheet * 2)
  const html = `<body style="margin:0;background:#888;display:grid;grid-template-columns:1fr 1fr;gap:4px;padding:4px">${group.map(s => `<div style="position:relative"><img style="width:100%;display:block" src="data:image/png;base64,${readFileSync(s.file).toString('base64')}"><span style="position:absolute;left:4px;top:4px;background:#000;color:#fff;font:bold 14px sans-serif;padding:2px 6px">${s.n} ${s.c ? 'end' : 'start'}</span></div>`).join('')}</body>`
  await sheet.setContent(html)
  const name = `${outDir}/sheet-${String(group[0].n).padStart(2, '0')}-${String(group.at(-1).n).padStart(2, '0')}.png`
  await sheet.screenshot({ path: name, fullPage: true })
  console.log(name)
}
const real = [...new Set(errors)].filter(e => !/FloatingVue|Wake Lock/.test(e))
if (real.length) console.log('PAGE ERRORS:\n' + real.join('\n'))
await browser.close()
