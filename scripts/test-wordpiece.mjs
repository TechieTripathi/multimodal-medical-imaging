// Check composables/wordpiece.ts against reference tokenizations from the Hugging Face tokenizer.
// Usage: node --experimental-strip-types scripts/test-wordpiece.mjs
import { readFileSync } from 'node:fs'
import { loadVocab, tokenize } from '../composables/wordpiece.ts'

const vocab = loadVocab(readFileSync('data/biomedclip/vocab.txt', 'utf8'))
const { cases } = JSON.parse(readFileSync('data/biomedclip/tokenizer_cases.json', 'utf8'))
let bad = 0
for (const c of cases) {
  const got = tokenize(c.text, vocab)
  const ok = JSON.stringify(got.map(t => t.text)) === JSON.stringify(c.tokens) && JSON.stringify(got.map(t => t.id)) === JSON.stringify(c.ids)
  if (!ok) { bad++; console.log('MISMATCH', c.text, '\n got', got.map(t => t.text).join(' '), '\n want', c.tokens.join(' ')) }
}
console.log(`${cases.length - bad}/${cases.length} cases match`)
process.exit(bad ? 1 : 0)
