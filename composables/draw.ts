// Draw DICOM pixel data on a canvas: greyscale through a window (level, width), optionally inverted,
// or RGB bytes as they are.

export function percentileWindow(v: Float32Array, lo = 0.01, hi = 0.995) {
  const s = Float32Array.from(v).sort()
  const a = s[Math.floor(lo * (s.length - 1))], b = s[Math.floor(hi * (s.length - 1))]
  return { level: (a + b) / 2, width: Math.max(1e-6, b - a) }
}

export function drawGrey(c: HTMLCanvasElement, v: Float32Array, w: number, h: number, level: number, width: number, invert = false) {
  c.width = w
  c.height = h
  const g = c.getContext('2d')!
  const img = g.createImageData(w, h)
  const lo = level - width / 2
  for (let i = 0; i < w * h; i++) {
    let x = Math.max(0, Math.min(255, ((v[i] - lo) / width) * 255))
    if (invert) x = 255 - x
    img.data[i * 4] = img.data[i * 4 + 1] = img.data[i * 4 + 2] = x
    img.data[i * 4 + 3] = 255
  }
  g.putImageData(img, 0, 0)
}

export function drawRGB(c: HTMLCanvasElement, v: Uint8Array, w: number, h: number) {
  c.width = w
  c.height = h
  const g = c.getContext('2d')!
  const img = g.createImageData(w, h)
  for (let i = 0; i < w * h; i++) img.data.set([v[i * 3], v[i * 3 + 1], v[i * 3 + 2], 255], i * 4)
  g.putImageData(img, 0, 0)
}

/** Base URL of a file in public/ (works under the GitHub Pages sub-path). */
export const pub = (p: string) => `${import.meta.env.BASE_URL}${p}`
