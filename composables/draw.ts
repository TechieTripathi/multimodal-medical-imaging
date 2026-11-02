// Draw DICOM pixel data on a canvas: greyscale through a window (level, width), optionally inverted,
// or RGB bytes as they are.

export function percentileWindow(v: Float32Array, lo = 0.01, hi = 0.995) {
  const s = Float32Array.from(v).sort()
  const a = s[Math.floor(lo * (s.length - 1))], b = s[Math.floor(hi * (s.length - 1))]
  return { level: (a + b) / 2, width: Math.max(1e-6, b - a) }
}

// One pixel buffer per canvas, reused between draws; the canvas is only resized when the image size changes.
const buffers = new WeakMap<HTMLCanvasElement, ImageData>()
export function buffer(c: HTMLCanvasElement, w: number, h: number) {
  if (c.width !== w || c.height !== h) { c.width = w; c.height = h }
  let img = buffers.get(c)
  if (!img || img.width !== w || img.height !== h) {
    img = c.getContext('2d')!.createImageData(w, h)
    img.data.fill(255)
    buffers.set(c, img)
  }
  return img
}

export function drawGrey(c: HTMLCanvasElement, v: Float32Array, w: number, h: number, level: number, width: number, invert = false) {
  const img = buffer(c, w, h)
  const d = img.data
  const lo = level - width / 2, k = 255 / width
  for (let i = 0, j = 0; i < w * h; i++, j += 4) {
    let x = (v[i] - lo) * k
    x = x < 0 ? 0 : x > 255 ? 255 : x
    if (invert) x = 255 - x
    d[j] = d[j + 1] = d[j + 2] = x
  }
  c.getContext('2d')!.putImageData(img, 0, 0)
}

export function drawRGB(c: HTMLCanvasElement, v: Uint8Array, w: number, h: number) {
  const img = buffer(c, w, h)
  const d = img.data
  for (let i = 0, j = 0, k = 0; i < w * h; i++, j += 4, k += 3) { d[j] = v[k]; d[j + 1] = v[k + 1]; d[j + 2] = v[k + 2] }
  c.getContext('2d')!.putImageData(img, 0, 0)
}

/** Base URL of a file in public/ (works under the GitHub Pages sub-path). */
export const pub = (p: string) => `${import.meta.env.BASE_URL}${p}`
