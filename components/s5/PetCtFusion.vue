<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { useStep } from '../../composables/useStep'
import { useBinary } from '../../composables/useBinary'
import ctUrl from '../../data/imaging/petct/ct_hu.bin?url'
import suvUrl from '../../data/imaging/petct/suv_x100.bin?url'
import lesion from '../../data/imaging/petct/lesion_edge.png'
import mip from '../../data/imaging/petct/mip_coronal.png'
import meta from '../../data/imaging/petct/meta.json'

// Artifact 26 — PET/CT: two kinds of image from one scanner session, one picture. CT shows anatomy,
// PET shows sugar uptake (SUV, computed from the PET file's tags); fused, the hot spot gets an address.
// Step 3 adds the expert lesion outline (DICOM SEG). Opacity and hover work freely. clicks: 3
const { step } = useStep(3)
const ct = useBinary(ctUrl)
const suv = useBinary(suvUrl)
const [H, W] = meta.grid
const alpha = ref(0.6)
watch(step, s => { alpha.value = s === 1 ? 1 : 0.6 }, { immediate: true })
const cv = ref<HTMLCanvasElement>()
function hot(t: number): [number, number, number] {
  return [Math.min(255, t * 3 * 255), Math.min(255, Math.max(0, t * 3 - 1) * 255), Math.min(255, Math.max(0, t * 3 - 2) * 255)]
}
function draw() {
  if (!ct.value || !suv.value || !cv.value) return
  const hu = new Int16Array(ct.value), s = new Uint16Array(suv.value)
  const g = cv.value.getContext('2d')!
  const img = g.createImageData(W, H)
  const showCT = step.value !== 1, showPET = step.value >= 1
  for (let i = 0; i < W * H; i++) {
    const c = showCT ? Math.max(0, Math.min(255, ((hu[i] + 160) / 400) * 255)) : 0
    let rgb: [number, number, number] = [c, c, c]
    if (showPET) {
      // Colour only real uptake: transparent below SUV 1.5, fully coloured from SUV 4
      const v = s[i] / 100, t = Math.min(1, v / meta.mip_suv_max_display)
      const h = hot(t), a = alpha.value * Math.min(1, Math.max(0, (v - 1.5) / 2.5))
      rgb = [rgb[0] * (1 - a) + h[0] * a, rgb[1] * (1 - a) + h[1] * a, rgb[2] * (1 - a) + h[2] * a]
    }
    img.data.set([rgb[0], rgb[1], rgb[2], 255], i * 4)
  }
  g.putImageData(img, 0, 0)
}
watch([ct, suv, cv, alpha, step], draw, { flush: 'post' })
const at = ref<{ x: number, y: number } | null>(null)
const probe = computed(() => {
  if (!ct.value || !suv.value || !at.value) return null
  const i = at.value.y * W + at.value.x
  return { hu: new Int16Array(ct.value)[i], suv: new Uint16Array(suv.value)[i] / 100 }
})
const move = (e: PointerEvent) => { const r = (e.currentTarget as HTMLElement).getBoundingClientRect(); at.value = { x: Math.floor(((e.clientX - r.left) / r.width) * W), y: Math.floor(((e.clientY - r.top) / r.height) * H) } }
const CAP = ['CT: anatomy, in Hounsfield units', 'PET: sugar uptake, in SUV', 'Fused: the hot spot gets an address', 'Expert outline of the tumour (DICOM SEG)']
</script>

<template>
  <div class="pf">
    <div>
      <div class="pic" @pointermove="move" @pointerleave="at = null">
        <canvas ref="cv" :width="W" :height="H" />
        <img v-if="step >= 3" :src="lesion" alt="" class="les">
      </div>
      <p class="read">{{ CAP[step] }}<template v-if="probe"> · {{ probe.hu }} HU, SUV {{ probe.suv.toFixed(1) }}</template></p>
      <label v-if="step >= 2" class="ctl">PET opacity <input v-model.number="alpha" type="range" min="0" max="1" step="0.05" @keydown.stop></label>
    </div>
    <div class="side">
      <figure>
        <img :src="mip" alt="Whole-body PET, front view, darker = more uptake">
        <figcaption>Whole body, front view</figcaption>
      </figure>
      <div class="card rv" :class="{ on: step >= 3 }">
        <p>Tumour SUVmax <strong>{{ meta.lesion.suv_max }}</strong></p>
        <p>Volume <strong>{{ Math.round(meta.lesion.volume_ml) }} ml</strong></p>
      </div>
    </div>
  </div>
</template>

<style scoped>
.pf { display: grid; grid-template-columns: 330px 1fr; gap: 30px; align-items: center; }
.pic { position: relative; width: 330px; height: 330px; border-radius: var(--radius); overflow: hidden; background: var(--image-mat); cursor: crosshair; }
.pic canvas, .les { position: absolute; inset: 0; width: 100%; height: 100%; }
.les { image-rendering: pixelated; }
.read { font-size: 15px; margin: 6px 0 2px; min-height: 20px; }
.ctl { font-size: 15px; }
.side { display: grid; grid-template-columns: 150px 1fr; gap: 18px; align-items: center; }
figure { margin: 0; display: flex; flex-direction: column; gap: 4px; }
figure img { width: 150px; border: 1px solid var(--rule); border-radius: 4px; background: #fff; }
figcaption { font-size: 14px; color: var(--ink-2); }
.card p { margin: 0 0 6px; font-size: var(--fs-label); }
</style>
