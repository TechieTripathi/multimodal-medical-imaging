// The DICOM analyses run by the "Run" button on the demo slides. Each analysis is source text that is
// shown on the slide and executed exactly as shown, with the helpers below in scope. All values come
// from the real DICOM files in public/dicom/ (checked against pydicom by scripts/test-dicom.mjs).
import { type Dicom, type Seg, loadDicom, loadSeg, suvFactor } from './dicom.ts'

export interface Grey { values: Float32Array, cols: number, rows: number }
export interface Output {
  image?: { src: Dicom | Grey, level: number, width: number, invert: boolean, focus?: Uint8Array }
  outlines: { mask: Uint8Array, i: number }[]
  hist?: { counts: number[], lo: number, hi: number }
  header?: string[]
  rows: string[][]
  says: string[]
}

/** Count the pixels of `values` whose value falls in each named [low, high) band. */
export function bands(values: Float32Array, ranges: Record<string, [number, number]>) {
  const n: Record<string, number> = Object.fromEntries(Object.keys(ranges).map(k => [k, 0]))
  for (const v of values) for (const [k, [lo, hi]] of Object.entries(ranges)) if (v >= lo && v < hi) n[k]++
  return n
}

/** Max, mean and count of `values` where `mask` is set (all pixels if no mask). */
export function stats(values: ArrayLike<number>, mask?: ArrayLike<number>) {
  let max = -Infinity, sum = 0, n = 0
  for (let i = 0; i < values.length; i++) if (!mask || mask[i]) { const v = values[i]; if (v > max) max = v; sum += v; n++ }
  return { max, mean: n ? sum / n : NaN, n }
}

/** Longest distance (mm) between two set pixels of a 2D mask on `img`'s grid. */
export function longest(mask: Uint8Array, img: Dicom) {
  const [sy, sx] = img.nums('PixelSpacing')
  const pts: [number, number][] = []
  for (let i = 0; i < mask.length; i++) if (mask[i]) pts.push([(i % img.cols) * sx, Math.floor(i / img.cols) * sy])
  let best = 0
  for (let a = 0; a < pts.length; a++) for (let b = a + 1; b < pts.length; b++) {
    const d = (pts[a][0] - pts[b][0]) ** 2 + (pts[a][1] - pts[b][1]) ** 2
    if (d > best) best = d
  }
  return Math.sqrt(best)
}

export const ANALYSES: Record<string, { title: string, code: string }> = {
  tissue: {
    title: 'CT: what tissue is on this slice?',
    code: `const ct = await load('ct-lidc-0001.dcm')              // one slice of our patient's CT
const hu = ct.frame(0)                                  // pixel values in Hounsfield units
const cm2 = ct.nums('PixelSpacing')[0] ** 2 / 100       // area of one pixel in cm²
const n = bands(hu, { lung: [-950, -500], fat: [-150, -30], 'soft tissue': [-30, 100], bone: [300, 3000] })
out.image(ct, -600, 1500)
out.histogram(hu, -1100, 1500)
for (const [k, v] of Object.entries(n)) out.row(k, \`\${(v * cm2).toFixed(0)} cm²\`)
const body = Object.values(n).reduce((a, b) => a + b)
out.say(\`Lung is \${Math.round(100 * n.lung / body)}% of the tissue on this slice\`)`,
  },
  nodule: {
    title: 'CT: measure the nodule four radiologists outlined',
    code: `const ct = await load('ct-lidc-0001.dcm')
const readers = await Promise.all([1, 2, 3, 4].map(r => seg(\`seg-lidc-0001-reader\${r}.dcm\`)))
out.header('Reader', 'Volume', 'Longest', 'Mean HU')
readers.forEach((s, i) => {
  const m = s.on(ct)                                    // this reader's outline on the CT slice
  out.outline(m, i)
  out.row(\`R\${i + 1}\`, \`\${(s.volumeMM3 / 1000).toFixed(1)} cm³\`, \`\${longest(m, ct).toFixed(0)} mm\`, stats(ct.frame(0), m).mean.toFixed(0))
})
out.image(ct, 40, 400, { focus: readers[0].on(ct) })
const v = readers.map(s => s.volumeMM3)
out.say(\`Same nodule, same images: volumes differ by \${Math.round(100 * (Math.max(...v) / Math.min(...v) - 1))}%\`)`,
  },
  pet: {
    title: 'PET: how hot is the tumour?',
    code: `const pet = await load('pet-fdg-lung.dcm')
const lesion = (await seg('seg-fdg-lung-slice.dcm')).on(pet)     // expert outline on this slice
const suv = pet.frame(0).map(v => v * suvFactor(pet).factor)    // Bq/ml → SUV, from the file's tags
const t = stats(suv, lesion), bg = stats(suv, suv.map((v, i) => (v > 0.3 && !lesion[i] ? 1 : 0)))
out.image({ values: suv, cols: pet.cols, rows: pet.rows }, 4, 8, { invert: true, focus: lesion })
out.outline(lesion, 0)
out.row('SUVmax', t.max.toFixed(1)); out.row('SUVmean', t.mean.toFixed(1))
out.row('Area', \`\${(t.n * pet.nums('PixelSpacing')[0] ** 2 / 100).toFixed(1)} cm²\`)
out.say(\`Tumour-to-background ratio \${(t.mean / bg.mean).toFixed(1)}: the tumour takes up \${(t.mean / bg.mean).toFixed(0)}× more sugar\`)`,
  },
  audit: {
    title: 'Audit the metadata of every file',
    code: `const files = ['ct-lidc-0001.dcm', 'xray-lidc-0001.dcm', 'mri-flair-upenn-00001.dcm',
  'mammo-cmmd-d2-0333.dcm', 'us-liver-ceus.dcm', 'pet-fdg-lung.dcm']
out.header('Modality', 'Identity removed', 'Birth date', 'Pixel size (mm)')
let noSize = 0
for (const f of files) {
  const d = await load(f)
  const size = d.str('PixelSpacing') ?? d.str('ImagerPixelSpacing')
  if (!size) noSize++
  out.row(d.str('Modality'), d.str('PatientIdentityRemoved') ?? 'not stated', d.str('PatientBirthDate') || 'empty', size?.split('\\\\')[0] ?? 'not recorded')
}
out.say(\`\${noSize} of \${files.length} files have no pixel size: nothing in them can be measured in mm\`)`,
  },
}

const AsyncFunction = Object.getPrototypeOf(async () => {}).constructor

/** Run one analysis. `open` turns a file name into a URL or an ArrayBuffer (browser or Node). */
export async function run(id: string, open: (name: string) => string | ArrayBuffer | Promise<ArrayBuffer>): Promise<Output> {
  const o: Output = { outlines: [], rows: [], says: [] }
  const out = {
    image: (src: Dicom | Grey, level: number, width: number, opt: { invert?: boolean, focus?: Uint8Array } = {}) => { o.image = { src, level, width, invert: !!opt.invert, focus: opt.focus } },
    outline: (mask: Uint8Array | null, i: number) => { if (mask) o.outlines.push({ mask, i }) },
    histogram: (values: Float32Array, lo: number, hi: number, nb = 52) => {
      const counts = Array.from<number>({ length: nb }).fill(0)
      for (const v of values) { const b = Math.floor(((v - lo) / (hi - lo)) * nb); if (b >= 0 && b < nb) counts[b]++ }
      o.hist = { counts, lo, hi }
    },
    header: (...c: string[]) => { o.header = c },
    row: (...c: (string | undefined)[]) => { o.rows.push(c.map(x => x ?? '—')) },
    say: (s: string) => { o.says.push(s) },
  }
  const load = async (name: string): Promise<Dicom> => loadDicom(await open(name))
  const seg = async (name: string): Promise<Seg> => loadSeg(await open(name))
  await new AsyncFunction('load', 'seg', 'suvFactor', 'bands', 'stats', 'longest', 'out', ANALYSES[id].code)(load, seg, suvFactor, bands, stats, longest, out)
  return o
}
