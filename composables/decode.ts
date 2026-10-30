// Decoders for the compact arrays written by notebook/prepare_deck_assets.py and run_segmentation.py.

function bytes(b64: string): Uint8Array {
  const s = atob(b64)
  const out = new Uint8Array(s.length)
  for (let i = 0; i < s.length; i++) out[i] = s.charCodeAt(i)
  return out
}

/** numpy.packbits(mask.ravel()) as base64 → 0/1 array of length n. */
export function unpackBits(b64: string, n: number): Uint8Array {
  const b = bytes(b64)
  const out = new Uint8Array(n)
  for (let i = 0; i < n; i++) out[i] = (b[i >> 3] >> (7 - (i & 7))) & 1
  return out
}

/** Little-endian int16 array as base64. */
export function int16(b64: string): Int16Array {
  const b = bytes(b64)
  return new Int16Array(b.buffer, b.byteOffset, b.byteLength / 2)
}

/** Dice and IoU between two 0/1 masks. */
export function overlap(a: ArrayLike<number>, b: ArrayLike<number>) {
  let inter = 0, sa = 0, sb = 0
  for (let i = 0; i < a.length; i++) { sa += a[i]; sb += b[i]; inter += a[i] & b[i] }
  return { dice: sa + sb ? (2 * inter) / (sa + sb) : 1, iou: sa + sb - inter ? inter / (sa + sb - inter) : 1, inter, sa, sb }
}
