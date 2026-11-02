<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { useStep } from '../../composables/useStep'
import { useBinary } from '../../composables/useBinary'
import { rafThrottle } from '../../composables/raf'
import volUrl from '../../data/imaging/ct/volume_u8.bin?url'
import meta from '../../data/imaging/ct/meta.json'
import dmeta from '../../data/imaging/dicom/meta.json'

// Artifact 15 — slices make a volume. Step 0: the stack. Step 1: files must be sorted by position,
// not by name (real file order). Step 2: the same volume cut three ways, linked crosshairs. clicks: 2
const { step } = useStep(2)
const buf = useBinary(volUrl)
const [Z, Y, X] = meta.volume.shape_zyx
const pos = ref<[number, number, number]>([...meta.volume.nodule_zyx] as [number, number, number])
const cA = ref<HTMLCanvasElement>(), cC = ref<HTMLCanvasElement>(), cS = ref<HTMLCanvasElement>()
const stackCv = ref<HTMLCanvasElement[]>([])
const stackZ = [20, 40, 60, 80, 100, 115]
function paint(c: HTMLCanvasElement | undefined, w: number, h: number, get: (r: number, k: number) => number) {
  if (!c) return
  const g = c.getContext('2d')!
  const img = g.createImageData(w, h)
  for (let r = 0; r < h; r++) for (let k = 0; k < w; k++) { const v = get(r, k); const i = (r * w + k) * 4; img.data[i] = img.data[i + 1] = img.data[i + 2] = v; img.data[i + 3] = 255 }
  g.putImageData(img, 0, 0)
}
function draw() {
  if (!buf.value) return
  const v = new Uint8Array(buf.value)
  const at = (z: number, y: number, x: number) => v[(z * Y + y) * X + x]
  const [z, y, x] = pos.value
  paint(cA.value, X, Y, (r, k) => at(z, r, k))
  paint(cC.value, X, Z, (r, k) => at(Z - 1 - r, y, k))
  paint(cS.value, Y, Z, (r, k) => at(Z - 1 - r, k, x))
  stackCv.value.forEach((c, i) => paint(c, X, Y, (r, k) => at(stackZ[i], r, k)))
}
watch([buf, pos, step, cA], rafThrottle(draw), { deep: true, flush: 'post' })
const files = dmeta.ct_file_order.slice(0, 5)
const sorted = [...dmeta.ct_file_order].sort((a, b) => b.z - a.z).slice(0, 5)
const clickAxial = (e: MouseEvent) => { const r = (e.currentTarget as HTMLElement).getBoundingClientRect(); pos.value = [pos.value[0], Math.floor(((e.clientY - r.top) / r.height) * Y), Math.floor(((e.clientX - r.left) / r.width) * X)] }
const pct = (v: number, n: number) => `${(v / n) * 100}%`
</script>

<template>
  <div class="ve">
    <div v-if="step < 2" class="intro">
      <div class="stack">
        <canvas v-for="(z, i) in stackZ" :key="z" :ref="el => { if (el) stackCv[i] = el as HTMLCanvasElement }" :width="X" :height="Y" :style="{ transform: `translate(${i * 22}px, ${-i * 22}px)` }" />
        <p class="cap">{{ meta.slices }} slices, {{ meta.spacing_mm[2] }} mm apart</p>
      </div>
      <div class="order rv" :class="{ on: step >= 1 }">
        <table>
          <thead><tr><th>File name</th><th>Instance</th><th>Height (z, mm)</th></tr></thead>
          <tbody><tr v-for="f in files" :key="f.file"><td class="mono">{{ f.file }}</td><td>{{ f.instance }}</td><td>{{ f.z }}</td></tr></tbody>
        </table>
        <p>File names are not in body order. Sort by the <span class="mono">ImagePositionPatient</span> height instead: {{ sorted[0].z }}, {{ sorted[1].z }}, {{ sorted[2].z }} …</p>
      </div>
    </div>
    <div v-else class="mpr">
      <figure>
        <div class="v" @click="clickAxial"><canvas ref="cA" :width="X" :height="Y" /><span class="h" :style="{ top: pct(pos[1], Y) }" /><span class="vv" :style="{ left: pct(pos[2], X) }" /></div>
        <figcaption>Axial (as scanned)</figcaption>
        <input v-model.number="pos[0]" type="range" :min="0" :max="Z - 1" aria-label="Axial slice" @keydown.stop>
      </figure>
      <figure>
        <div class="v"><canvas ref="cC" :width="X" :height="Z" /><span class="h" :style="{ top: pct(Z - 1 - pos[0], Z) }" /><span class="vv" :style="{ left: pct(pos[2], X) }" /></div>
        <figcaption>Coronal (front view)</figcaption>
        <input v-model.number="pos[1]" type="range" :min="0" :max="Y - 1" aria-label="Coronal slice" @keydown.stop>
      </figure>
      <figure>
        <div class="v"><canvas ref="cS" :width="Y" :height="Z" /><span class="h" :style="{ top: pct(Z - 1 - pos[0], Z) }" /><span class="vv" :style="{ left: pct(pos[1], Y) }" /></div>
        <figcaption>Sagittal (side view)</figcaption>
        <input v-model.number="pos[2]" type="range" :min="0" :max="X - 1" aria-label="Sagittal slice" @keydown.stop>
      </figure>
    </div>
  </div>
</template>

<style scoped>
.intro { display: grid; grid-template-columns: 330px 1fr; gap: 30px; align-items: center; }
.stack { position: relative; height: 330px; }
.stack canvas { position: absolute; left: 0; top: 120px; width: 170px; height: 170px; border: 1px solid #444; border-radius: 3px; box-shadow: 0 0 0 1px var(--paper); }
.cap { position: absolute; left: 0; bottom: -10px; margin: 0; font-size: var(--fs-label); max-width: 320px; }
.order table { font-size: 16px; margin-bottom: 12px; }
.order p { font-size: var(--fs-label); margin: 0; }
.mpr { display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; }
figure { margin: 0; display: flex; flex-direction: column; gap: 6px; align-items: center; }
.v { position: relative; width: 260px; height: 260px; background: var(--image-mat); border-radius: var(--radius); overflow: hidden; display: flex; align-items: center; justify-content: center; cursor: crosshair; }
.v canvas { max-width: 100%; max-height: 100%; width: 100%; height: 100%; object-fit: contain; }
.h, .vv { position: absolute; background: #ffc400; opacity: 0.7; pointer-events: none; }
.h { left: 0; right: 0; height: 1px; }
.vv { top: 0; bottom: 0; width: 1px; }
figcaption { font-size: var(--fs-label); }
figure input { width: 220px; accent-color: var(--accent); }
</style>
