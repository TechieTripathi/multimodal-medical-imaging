// Check that every source URL in data/refs/*.ts resolves. Usage: node scripts/check-urls.mjs
import { readFileSync, readdirSync } from 'node:fs'

const entries = []
for (const f of readdirSync('data/refs').filter(f => f.endsWith('.ts'))) {
  const text = readFileSync(`data/refs/${f}`, 'utf8')
  for (const m of text.matchAll(/key:\s*'([^']+)'[\s\S]*?url:\s*'([^']+)'/g)) entries.push({ file: f, key: m[1], url: m[2] })
}

const UA = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130 Safari/537.36'
async function check(url) {
  for (const method of ['HEAD', 'GET']) {
    try {
      const res = await fetch(url, { method, redirect: 'follow', headers: { 'user-agent': UA }, signal: AbortSignal.timeout(20000) })
      if (res.ok || method === 'GET') return res.status
    }
    catch (e) { if (method === 'GET') return `ERR ${e.cause?.code ?? e.name}` }
  }
}

let bad = 0
const results = await Promise.all(entries.map(async e => ({ ...e, status: await check(e.url) })))
for (const r of results) {
  const ok = r.status === 200
  // 403/429 often mean bot protection rather than a dead link; flag for manual check.
  if (!ok) { bad++; console.log(`${String(r.status).padEnd(10)} ${r.key.padEnd(28)} ${r.url}  (${r.file})`) }
}
console.log(`\n${results.length} URLs checked, ${bad} need attention (403/429 usually = bot protection; verify manually).`)
