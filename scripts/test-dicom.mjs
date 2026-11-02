// Check composables/dicom.ts against pydicom: every teaching copy in public/dicom/ must give the same
// key tags, the same pixel statistics after rescale, and (for PET) the same SUV factor as
// notebook/prepare_deck_assets.py recorded in public/dicom/manifest.json.
// Usage: node --experimental-strip-types scripts/test-dicom.mjs
import { readFileSync } from 'node:fs'
import { loadDicom, loadSeg, suvFactor } from '../composables/dicom.ts'
import { run } from '../composables/analyses.ts'

const { files, segs } = JSON.parse(readFileSync('public/dicom/manifest.json', 'utf8'))
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

// DICOM SEG files and the four "Run" analyses: the numbers shown on the slides must match pydicom
const open = (name) => { const b = readFileSync(`public/dicom/${name}`); return b.buffer.slice(b.byteOffset, b.byteOffset + b.byteLength) }
let segBad = 0
for (const s of segs) {
  const g = await loadSeg(open(s.file))
  if (s.voxels !== undefined && g.voxels !== s.voxels) { segBad++; console.log(`FAIL ${s.file}: ${g.voxels} voxels vs ${s.voxels}`) }
}
const nod = await run('nodule', open)
nod.rows.forEach((r, i) => {
  const ref = segs.find(s => s.reader === i + 1)
  const ok = r[1] === `${(ref.volume_mm3 / 1000).toFixed(1)} cm³` && r[2] === `${ref.longest_diameter_on_ct_slice_mm.toFixed(0)} mm` && r[3] === ref.mean_hu_on_ct_slice.toFixed(0)
  if (!ok) segBad++
  console.log(`${ok ? 'ok  ' : 'FAIL'} nodule ${r.join(' | ')}  (pydicom: ${(ref.volume_mm3 / 1000).toFixed(1)} cm³, ${ref.longest_diameter_on_ct_slice_mm.toFixed(0)} mm, ${ref.mean_hu_on_ct_slice.toFixed(0)} HU)`)
})
const pet = await run('pet', open)
const pr = segs.find(s => s.suv_max !== undefined)
const want = [['SUVmax', pr.suv_max.toFixed(1)], ['SUVmean', pr.suv_mean.toFixed(1)], ['Area', `${pr.area_cm2.toFixed(1)} cm²`]]
want.forEach(([k, v], i) => { const ok = pet.rows[i][0] === k && pet.rows[i][1] === v; if (!ok) segBad++; console.log(`${ok ? 'ok  ' : 'FAIL'} pet ${pet.rows[i].join(' ')} (pydicom ${v})`) })
const ratio = (pr.suv_mean / pr.background_suv_mean).toFixed(1)
if (!pet.says[0].includes(`ratio ${ratio}`)) { segBad++; console.log(`FAIL pet ratio: ${pet.says[0]} (pydicom ${ratio})`) }
for (const id of ['tissue', 'audit']) { const o = await run(id, open); console.log(`ran ${id}:`, o.rows.map(r => r.join(' ')).join(' / '), '|', o.says.join(' ')) }
console.log(segBad ? `${segBad} SEG/analysis problem(s)` : 'SEG files and analyses match pydicom')
process.exit(bad || segBad ? 1 : 0)
