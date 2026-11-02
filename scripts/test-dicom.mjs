// Check composables/dicom.ts against pydicom: every teaching copy in public/dicom/ must give the same
// key tags, the same pixel statistics after rescale, and (for PET) the same SUV factor as
// notebook/prepare_deck_assets.py recorded in public/dicom/manifest.json.
// Usage: node --experimental-strip-types scripts/test-dicom.mjs
import { readFileSync } from 'node:fs'
import { loadDicom, suvFactor } from '../composables/dicom.ts'

const { files } = JSON.parse(readFileSync('public/dicom/manifest.json', 'utf8'))
const close = (a, b, tol = 1e-3) => Math.abs(a - b) <= tol * Math.max(1, Math.abs(b))
let bad = 0
for (const f of files) {
  const buf = readFileSync(`public/dicom/${f.file}`)
  const d = await loadDicom(buf.buffer.slice(buf.byteOffset, buf.byteOffset + buf.byteLength))
  const problems = []
  for (const [k, want] of Object.entries(f.tags)) {
    if (Array.isArray(want)) { const got = d.nums(k); if (got.length !== want.length || got.some((g, i) => !close(g, want[i]))) problems.push(`${k}: ${got} vs ${want}`) }
    else if (typeof want === 'number') { const got = d.num(k); if (got === undefined || !close(got, want)) problems.push(`${k}: ${got} vs ${want}`) }
    else if ((d.str(k) ?? '') !== want.trim()) problems.push(`${k}: "${d.str(k)}" vs "${want}"`)
  }
  let min = Infinity, max = -Infinity, sum = 0, n = 0
  for (let i = 0; i < d.frames; i++) for (const v of d.frame(i)) { if (v < min) min = v; if (v > max) max = v; sum += v; n++ }
  const s = f.pixels
  if (!close(min, s.min) || !close(max, s.max) || !close(sum / n, s.mean)) problems.push(`pixels: ${min}/${max}/${(sum / n).toFixed(3)} vs ${s.min}/${s.max}/${s.mean}`)
  if (f.suv) { const got = suvFactor(d); if (!got || !close(got.factor, f.suv.factor, 1e-6)) problems.push(`SUV factor ${got?.factor} vs ${f.suv.factor}`) }
  if (problems.length) bad++
  console.log(`${problems.length ? 'FAIL' : 'ok  '} ${f.file} (${d.str('Modality')}, ${d.rows}x${d.cols}, ${d.frames} frame${d.frames > 1 ? 's' : ''})${problems.length ? `\n     ${problems.join('\n     ')}` : ''}`)
}
console.log(`${files.length - bad}/${files.length} files match pydicom`)
process.exit(bad ? 1 : 0)
