// Read real DICOM files in the browser (and in Node for tests) with dicom-parser.
// Supports uncompressed little-endian files: 8- or 16-bit greyscale (signed or not), RGB, multi-frame.
// The deck's teaching copies in public/dicom/ are written that way; other files get a clear error.
import dicomParser from 'dicom-parser'

/** DICOM keyword → tag, for the attributes the slides read. */
export const TAGS: Record<string, string> = {
  TransferSyntaxUID: 'x00020010', SOPClassUID: 'x00080016', StudyDate: 'x00080020', SeriesTime: 'x00080031',
  Modality: 'x00080060', Manufacturer: 'x00080070', SeriesDescription: 'x0008103e', ManufacturerModelName: 'x00081090',
  DerivationDescription: 'x00082111', PatientName: 'x00100010', PatientID: 'x00100020', PatientBirthDate: 'x00100030', AccessionNumber: 'x00080050', PatientAge: 'x00101010',
  PatientWeight: 'x00101030', PatientIdentityRemoved: 'x00120062', BodyPartExamined: 'x00180015',
  Radiopharmaceutical: 'x00180031', SliceThickness: 'x00180050', KVP: 'x00180060', FrameTime: 'x00181063',
  RadiopharmaceuticalStartTime: 'x00181072', RadionuclideTotalDose: 'x00181074', RadionuclideHalfLife: 'x00181075',
  ImagerPixelSpacing: 'x00181164', ViewPosition: 'x00185101', ImagePositionPatient: 'x00200032', ImageOrientationPatient: 'x00200037',
  ImageLaterality: 'x00200062', SamplesPerPixel: 'x00280002', PhotometricInterpretation: 'x00280004',
  PlanarConfiguration: 'x00280006', NumberOfFrames: 'x00280008', Rows: 'x00280010', Columns: 'x00280011',
  PixelSpacing: 'x00280030', BitsAllocated: 'x00280100', BitsStored: 'x00280101', PixelRepresentation: 'x00280103',
  WindowCenter: 'x00281050', WindowWidth: 'x00281051', RescaleIntercept: 'x00281052', RescaleSlope: 'x00281053',
  RadiopharmaceuticalInformationSequence: 'x00540016', Units: 'x00541001', DecayCorrection: 'x00541102',
  PixelData: 'x7fe00010',
}
const UNCOMPRESSED = ['1.2.840.10008.1.2', '1.2.840.10008.1.2.1']

export interface Dicom {
  /** Text value of a keyword (all values, backslash-separated), or undefined if absent. */
  str: (kw: string) => string | undefined
  /** First numeric value of a keyword, or undefined. */
  num: (kw: string) => number | undefined
  /** All numeric values of a multi-valued keyword. */
  nums: (kw: string) => number[]
  /** Same helpers inside the first item of a sequence. */
  item: (seq: string) => Pick<Dicom, 'str' | 'num'> | undefined
  rows: number
  cols: number
  frames: number
  rgb: boolean
  monochrome1: boolean
  /** Frame i: greyscale values after rescale slope/intercept (Float32Array), or RGB bytes (Uint8Array). Decoded once, then cached. */
  frame: (i: number) => Float32Array | Uint8Array
  bytes: number
}

function helpers(ds: any) {
  const str = (kw: string) => {
    const t = TAGS[kw]
    if (!t || !ds.elements[t]) return undefined
    const v = ds.string(t)
    return v === undefined ? undefined : v.trim()
  }
  const nums = (kw: string) => (str(kw) ?? '').split('\\').filter(Boolean).map(Number).filter(n => !Number.isNaN(n))
  const num = (kw: string) => {
    const t = TAGS[kw]
    if (!t || !ds.elements[t]) return undefined
    const el = ds.elements[t]
    // US (unsigned short) attributes are binary; text-encoded numbers (DS, IS) are strings
    if (['Rows', 'Columns', 'BitsAllocated', 'BitsStored', 'PixelRepresentation', 'SamplesPerPixel', 'PlanarConfiguration'].includes(kw) || el.vr === 'US')
      return ds.uint16(t)
    return nums(kw)[0]
  }
  return { str, num, nums }
}

export async function loadDicom(src: string | ArrayBuffer | Blob): Promise<Dicom> {
  const buf = typeof src === 'string' ? await (await fetch(src)).arrayBuffer() : src instanceof ArrayBuffer ? src : await src.arrayBuffer()
  const bytes = new Uint8Array(buf)
  const ds = dicomParser.parseDicom(bytes)
  const { str, num, nums } = helpers(ds)
  const ts = str('TransferSyntaxUID') ?? '1.2.840.10008.1.2.1'
  if (!UNCOMPRESSED.includes(ts))
    throw new Error(`Compressed DICOM (transfer syntax ${ts}) is not supported by this viewer`)
  const rows = num('Rows')!, cols = num('Columns')!
  const frames = num('NumberOfFrames') ?? 1
  const spp = num('SamplesPerPixel') ?? 1
  const bitsA = num('BitsAllocated') ?? 16
  const signed = (num('PixelRepresentation') ?? 0) === 1
  const slope = num('RescaleSlope') ?? 1, intercept = num('RescaleIntercept') ?? 0
  const px = ds.elements[TAGS.PixelData]
  if (!px) throw new Error('No pixel data in this file')
  const perFrame = rows * cols * spp * (bitsA / 8)
  const cache = new Map<number, Float32Array | Uint8Array>()
  const frame = (i: number) => {
    const hit = cache.get(i)
    if (hit) return hit
    const f = decode(i)
    cache.set(i, f)
    return f
  }
  const decode = (i: number) => {
    const start = px.dataOffset + i * perFrame
    const slice = buf.slice(start, start + perFrame)
    if (spp === 3) return new Uint8Array(slice)
    const raw = bitsA === 8 ? new Uint8Array(slice) : signed ? new Int16Array(slice) : new Uint16Array(slice)
    const out = new Float32Array(raw.length)
    for (let k = 0; k < raw.length; k++) out[k] = raw[k] * slope + intercept
    return out
  }
  const item = (seq: string) => {
    const el = ds.elements[TAGS[seq]]
    const it = el?.items?.[0]?.dataSet
    if (!it) return undefined
    const h = helpers(it)
    return { str: h.str, num: h.num }
  }
  return { str, num, nums, item, rows, cols, frames, rgb: spp === 3, monochrome1: str('PhotometricInterpretation') === 'MONOCHROME1', frame, bytes: bytes.length }
}

const secs = (tm: string) => Number(tm.slice(0, 2)) * 3600 + Number(tm.slice(2, 4)) * 60 + Number(tm.slice(4) || 0)

/** Body-weight SUV factor for a PET file in Bq/ml (decay-corrected to series start), from its own tags. */
export function suvFactor(d: Dicom) {
  const r = d.item('RadiopharmaceuticalInformationSequence')
  const weight = d.num('PatientWeight'), series = d.str('SeriesTime')
  const dose = r?.num('RadionuclideTotalDose'), half = r?.num('RadionuclideHalfLife'), start = r?.str('RadiopharmaceuticalStartTime')
  if (d.str('Units') !== 'BQML' || !weight || !series || !dose || !half || !start) return null
  const dt = secs(series) - secs(start)
  const doseNow = dose * 2 ** (-dt / half)
  return { factor: (weight * 1000) / doseNow, minutes: dt / 60, doseNowMBq: doseNow / 1e6, weight, doseMBq: dose / 1e6, halfLifeMin: half / 60, start, series }
}
