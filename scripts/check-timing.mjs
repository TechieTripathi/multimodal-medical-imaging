// Sum the "**Time:** ~N min" lines in speaker notes per section (openers included), against the budget.
import { resolve } from 'node:path'
import { load } from '@slidev/parser/fs'
import { SECTIONS } from '../data/sections.ts'
const root = process.cwd()
const { slides } = await load({ roots: [root], userRoot: root }, resolve(root, 'slides.md'))
const per = {}
const missing = []
slides.filter(s => !['sources', 'institution-cover'].includes(s.frontmatter?.layout)).forEach((s, i) => {
  const m = (s.note ?? '').match(/\*\*Time:\*\*\s*~?\s*([\d.]+)\s*min/)
  if (!m) missing.push(`${i + 1}${s.frontmatter?.layout === 'opener' ? ' (opener)' : ''}`)
  per[s.frontmatter.section] = (per[s.frontmatter.section] ?? 0) + (m ? Number(m[1]) : 0)
})
let total = 0
for (const sec of SECTIONS) {
  const t = Math.round((per[sec.no] ?? 0) * 10) / 10
  total += t
  console.log(`${sec.no}. ${sec.name.padEnd(34)} ${String(t).padStart(5)} min  (budget ${sec.minutes})${t !== sec.minutes ? '  <-- mismatch' : ''}`)
}
console.log(`Total ${Math.round(total * 10) / 10} min (budget 120)`)
if (missing.length) console.log('Slides without a Time line (position among non-cover slides):', missing.join(', '))
