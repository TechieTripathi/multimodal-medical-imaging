<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { useStep } from '../../composables/useStep'
import { int16, overlap, unpackBits } from '../../composables/decode'
import crops from '../../data/imaging/ct/reader_crops.json'
import seg from '../../data/runs/segmentation.json'
import con from '../../data/runs/biomedclip_contrastive.json'

// Artifact 11 — Dice and IoU on real outlines of our patient's nodule: radiologist vs radiologist,
// then MedSAM vs a radiologist. Drag the image to slide the second outline and watch Dice fall. clicks: 3
const { step } = useStep(3)
const N = crops.box.size
const sl = crops.slices[2]
const hu = int16(sl.hu)
const r1 = unpackBits(sl.readers[0], N * N)
const r2 = unpackBits(sl.readers[1], N * N)
const ms = unpackBits(seg.medsam.mask_crop, N * N)
const dx = ref(0), dy = ref(0)
watch(step, () => { dx.value = 0; dy.value = 0 })
const other = computed(() => step.value >= 2 ? ms : r2)
const shifted = computed(() => {
  const o = other.value, out = new Uint8Array(N * N)
  for (let y = 0; y < N; y++) for (let x = 0; x < N; x++) {
    const sx = x - dx.value, sy = y - dy.value
    if (sx >= 0 && sy >= 0 && sx < N && sy < N) out[y * N + x] = o[sy * N + sx]
  }
  return out
})
const ov = computed(() => overlap(r1, shifted.value))
const cv = ref<HTMLCanvasElement>()
function draw() {
  const c = cv.value; if (!c) return
  const g = c.getContext('2d')!
  const img = g.createImageData(N, N)
  const b = shifted.value
  for (let i = 0; i < N * N; i++) {
    const v = Math.max(0, Math.min(255, ((hu[i] + 160) / 400) * 255))
    let [r, gg, bl] = [v, v, v]
    const edge = (m: Uint8Array) => m[i] && (!m[i - 1] || !m[i + 1] || !m[i - N] || !m[i + N])
    if (step.value >= 1 && r1[i] && b[i]) { r = r * 0.5 + 255 * 0.5; gg = gg * 0.5 + 196 * 0.5; bl = bl * 0.5 }
    if (edge(r1)) [r, gg, bl] = [70, 110, 255]
    if (step.value >= 1 && edge(b)) [r, gg, bl] = step.value >= 2 ? [40, 200, 120] : [255, 150, 40]
    img.data.set([r, gg, bl, 255], i * 4)
  }
  g.putImageData(img, 0, 0)
}
onMounted(draw)
watch([shifted, step], draw)
let drag: { x: number, y: number, dx: number, dy: number } | null = null
const down = (e: PointerEvent) => { drag = { x: e.clientX, y: e.clientY, dx: dx.value, dy: dy.value } }
const move = (e: PointerEvent) => { if (!drag) return; const k = N / (e.currentTarget as HTMLElement).getBoundingClientRect().width; dx.value = Math.round(drag.dx + (e.clientX - drag.x) * k); dy.value = Math.round(drag.dy + (e.clientY - drag.y) * k) }
const f2 = (v: number) => v.toFixed(2)
const recall1 = con.diagonal_is_max_in_row.filter(Boolean).length
</script>

<template>
  <div class="ox">
    <div class="pic">
      <canvas ref="cv" :width="N" :height="N" class="cv" @pointerdown="down" @pointermove="move" @pointerup="drag = null" @pointerleave="drag = null" />
      <p class="key"><span class="sw a" />Radiologist 1 <template v-if="step >= 1"><span class="sw" :class="step >= 2 ? 'm' : 'b'" />{{ step >= 2 ? 'MedSAM' : 'Radiologist 2' }}</template></p>
    </div>
    <div class="side">
      <p class="formula"><strong>Dice</strong> = 2 × overlap ÷ (area A + area B)</p>
      <p class="formula"><strong>IoU</strong> = overlap ÷ everything covered</p>
      <div v-if="step >= 1 && step < 3" class="score">
        <span><strong>{{ f2(ov.dice) }}</strong> Dice</span><span><strong>{{ f2(ov.iou) }}</strong> IoU</span>
      </div>
      <p v-if="step === 1" class="note">Two experts outlining the same nodule do not agree perfectly.</p>
      <p v-if="step === 2" class="note">MedSAM’s outline is smaller than the readers’ ({{ seg.medsam.area_mm2.medsam }} vs about {{ Math.round(seg.medsam.area_mm2.readers[0]) }} mm²).</p>
      <div v-if="step >= 3" class="card ret">
        <h3>For retrieval: Recall@1</h3>
        <p>How often is the right report ranked first? In our six-pair batch: <strong>{{ recall1 }} of {{ con.pairs.length }}</strong>.</p>
      </div>
    </div>
  </div>
</template>

<style scoped>
.ox { display: grid; grid-template-columns: 330px 1fr; gap: 40px; align-items: center; }
.cv { width: 330px; height: 330px; image-rendering: pixelated; border-radius: var(--radius); cursor: grab; touch-action: none; display: block; }
.key { font-size: 15px; margin: 6px 0 0; display: flex; align-items: center; gap: 6px; }
.sw { width: 14px; height: 4px; display: inline-block; border-radius: 2px; margin-left: 8px; }
.sw.a { background: rgb(70, 110, 255); margin-left: 0; }
.sw.b { background: rgb(255, 150, 40); }
.sw.m { background: rgb(40, 200, 120); }
.formula { margin: 0 0 8px; font-size: var(--fs-label); }
.score { display: flex; gap: 28px; margin: 18px 0 10px; font-size: var(--fs-label); color: var(--ink-2); }
.score strong { font-size: 40px; color: var(--accent); display: block; line-height: 1; }
.note { font-size: var(--fs-label); margin: 0; }
.ret { margin-top: 18px; }
.ret p { margin: 0; font-size: var(--fs-label); }
</style>
