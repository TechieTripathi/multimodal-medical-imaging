// BERT "uncased" tokenizer (basic tokenizer + WordPiece), as used by BiomedCLIP's text encoder
// (BiomedBERT vocabulary). Checked against the Hugging Face tokenizer by scripts/test-wordpiece.mjs.

export interface Token { text: string, id: number }

export function loadVocab(raw: string): Map<string, number> {
  const m = new Map<string, number>()
  raw.split('\n').forEach((t, i) => { if (t) m.set(t.replace(/\r$/, ''), i) })
  return m
}

const isPunct = (ch: string) => {
  const c = ch.codePointAt(0)!
  if ((c >= 33 && c <= 47) || (c >= 58 && c <= 64) || (c >= 91 && c <= 96) || (c >= 123 && c <= 126))
    return true
  return /\p{P}/u.test(ch)
}

function basic(text: string): string[] {
  const cleaned = [...text].filter(ch => !/[\p{Cc}\p{Cf}]/u.test(ch) || /\s/.test(ch)).join('')
  const lowered = cleaned.toLowerCase().normalize('NFD').replace(/\p{Mn}/gu, '')
  const words: string[] = []
  for (const w of lowered.split(/\s+/).filter(Boolean)) {
    let cur = ''
    for (const ch of w) {
      if (isPunct(ch)) {
        if (cur) words.push(cur)
        words.push(ch)
        cur = ''
      }
      else { cur += ch }
    }
    if (cur) words.push(cur)
  }
  return words
}

function wordpiece(word: string, vocab: Map<string, number>): string[] {
  const chars = [...word]
  if (chars.length > 100)
    return ['[UNK]']
  const out: string[] = []
  let start = 0
  while (start < chars.length) {
    let end = chars.length
    let piece: string | null = null
    while (start < end) {
      let sub = chars.slice(start, end).join('')
      if (start > 0)
        sub = `##${sub}`
      if (vocab.has(sub)) { piece = sub; break }
      end--
    }
    if (!piece)
      return ['[UNK]']
    out.push(piece)
    start = end
  }
  return out
}

/** Tokens including [CLS] and [SEP], with their vocabulary ids. */
export function tokenize(text: string, vocab: Map<string, number>): Token[] {
  const pieces = ['[CLS]', ...basic(text).flatMap(w => wordpiece(w, vocab)), '[SEP]']
  return pieces.map(t => ({ text: t, id: vocab.get(t) ?? vocab.get('[UNK]')! }))
}
