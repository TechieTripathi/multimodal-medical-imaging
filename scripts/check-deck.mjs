// Static checks on the deck source: slide count, sections, speaker notes, citation keys,
// honesty labels and the per-slide word limit (IDEA.md §4.2, §5).
// Usage: node scripts/check-deck.mjs
import { readFileSync, readdirSync, existsSync } from 'node:fs'
import { resolve } from 'node:path'
import { load } from '@slidev/parser/fs'

const UNNUMBERED = ['institution-cover', 'opener', 'sources']
const TAGS = ['actual', 'real-data', 'illustrative', 'simulated', 'teaching', 'published']
const WORD_LIMIT = 45
const EXPECTED = Number(readFileSync('data/sections.ts', 'utf8').match(/CORE_SLIDES = (\d+)/)[1])

const root = process.cwd()
const data = await load({ roots: [root], userRoot: root }, resolve(root, 'slides.md'))
const slides = data.slides
const core = slides.filter(s => !UNNUMBERED.includes(s.frontmatter?.layout))
const problems = []
const warnings = []

const keys = new Set()
for (const f of readdirSync('data/refs').filter(f => f.endsWith('.ts'))) {
  for (const m of readFileSync(`data/refs/${f}`, 'utf8').matchAll(/key:\s*'([^']+)'/g)) {
    if (keys.has(m[1])) problems.push(`Duplicate ref key ${m[1]} (in ${f})`)
    keys.add(m[1])
  }
}

// Visible words: markdown text outside components, comments, code and frontmatter.
function visibleWords(md) {
  const text = (md ?? '')
    .replace(/<!--[\s\S]*?-->/g, ' ')
    .replace(/```[\s\S]*?```/g, ' ')
    .replace(/<[A-Z][\s\S]*?\/>/g, ' ')
    .replace(/<[^>]+>/g, ' ')
    .replace(/[#*_`>|-]/g, ' ')
  return text.split(/\s+/).filter(w => /[A-Za-z]/.test(w)).length
}

const perSection = {}
core.forEach((s, i) => {
  const no = i + 1
  const fm = s.frontmatter ?? {}
  const sec = fm.section
  if (!sec) problems.push(`Slide ${no}: missing section`)
  perSection[sec] = (perSection[sec] ?? 0) + 1
  const note = (s.note ?? '').trim()
  if (note.length < 120) problems.push(`Slide ${no}: speaker notes missing or very short (${note.length} chars)`)
  if (/PLACEHOLDER|TODO|FIXME|[Ll]orem ipsum/.test(s.content + note)) problems.push(`Slide ${no}: placeholder text`)
  const src = Array.isArray(fm.sources) ? fm.sources : fm.sources ? [fm.sources] : []
  for (const k of src) if (!keys.has(k)) problems.push(`Slide ${no}: unknown source key ${k}`)
  for (const m of (s.content ?? '').matchAll(/<Cite\s+k="([^"]+)"/g))
    if (!src.includes(m[1])) problems.push(`Slide ${no}: <Cite k="${m[1]}"> not listed in frontmatter sources`)
  if (fm.tag && !TAGS.includes(fm.tag)) problems.push(`Slide ${no}: unknown honesty tag ${fm.tag}`)
  if (fm.tag === 'actual') {
    if (!fm.run) problems.push(`Slide ${no}: tag "actual" needs a \`run:\` file in data/runs/`)
    else if (!existsSync(`data/runs/${fm.run}`)) problems.push(`Slide ${no}: run file data/runs/${fm.run} not found`)
  }
  const w = visibleWords(s.content)
  if (w > WORD_LIMIT) warnings.push(`Slide ${no}: ${w} visible words in markdown (limit about 40)`)
})

const openers = slides.filter(s => s.frontmatter?.layout === 'opener').length
if (core.length !== EXPECTED) problems.push(`Core slides: ${core.length}, expected ${EXPECTED} (data/sections.ts)`)
console.log(`Core slides: ${core.length} (expected ${EXPECTED}); openers: ${openers}; appendix: ${slides.filter(s => s.frontmatter?.layout === 'sources').length}; cover: ${slides.filter(s => s.frontmatter?.layout === 'institution-cover').length}`)
console.log('Slides per section:', perSection)
console.log(`Reference keys defined: ${keys.size}`)
if (warnings.length) console.log(`\n${warnings.length} warning(s):\n- ${warnings.join('\n- ')}`)
console.log(problems.length ? `\n${problems.length} problem(s):\n- ${problems.join('\n- ')}` : '\nNo problems found.')
process.exit(problems.length ? 1 : 0)
