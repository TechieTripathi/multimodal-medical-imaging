<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { useStep } from '../../composables/useStep'
import { useBinary } from '../../composables/useBinary'
import huUrl from '../../data/imaging/ct/slice_hu.bin?url'
import meta from '../../data/imaging/dicom/meta.json'
import tagWin from '../../data/imaging/pipeline/tag_window.png'
import good from '../../data/imaging/pipeline/windowed.png'

// Slide 32 — a stored number becomes a real-world unit (Hounsfield) through slope and intercept;
// a display window then turns units into grey. Hover the CT to read real values. clicks: 2
const { step } = useStep(2)
const buf = useBinary(huUrl)
const cv = ref<HTMLCanvasElement>()
const tags = meta.ct_tags['How to read the pixels']
const intercept = Number(tags.find(r => r.keyword === 'RescaleIntercept')!.value)
const slope = Number(tags.find(r => r.keyword === 'RescaleSlope')!.value)
watch([buf, cv], () => {
  if (!buf.value || !cv.value) return
  const hu = new Int16Array(buf.value)
  const g = cv.value.getContext('2d')!
  const img = g.createImageData(512, 512)
  for (let i = 0; i < hu.length; i++) { const v = Math.max(0, Math.min(255, ((hu[i] + 1350) / 1500) * 255)); img.data.set([v, v, v, 255], i * 4) }
  g.putImageData(img, 0, 0)
}, { flush: 'post' })
const at = ref<{ x: number, y: number } | null>({ x: 316, y: 367 })
const probe = computed(() => {
  if (!buf.value || !at.value) return null
  const hu = new Int16Array(buf.value)[at.value.y * 512 + at.value.x]
  return { hu, stored: (hu - intercept) / slope }
})
const move = (e: PointerEvent) => {
  const r = (e.currentTarget as HTMLElement).getBoundingClientRect()
  at.value = { x: Math.min(511, Math.max(0, Math.floor(((e.clientX - r.left) / r.width) * 512))), y: Math.min(511, Math.max(0, Math.floor(((e.clientY - r.top) / r.height) * 512))) }
}
const what = (hu: number) => hu < -900 ? 'air' : hu < -400 ? 'lung' : hu < -50 ? 'fat' : hu < 100 ? 'soft tissue or fluid' : hu < 400 ? 'contrast-filled vessel' : 'bone'
</script>

<template>
  <div class="sd">
    <div class="pic" @pointermove="move">
      <canvas ref="cv" width="512" height="512" />
      <span v-if="at" class="cross" :style="{ left: `${(at.x / 512) * 100}%`, top: `${(at.y / 512) * 100}%` }" />
    </div>
    <div class="side">
      <p v-if="probe" class="readout">
        stored <strong class="mono">{{ probe.stored }}</strong>
        <span class="rv" :class="{ on: step >= 1 }"> → × {{ slope }} {{ intercept < 0 ? '−' : '+' }} {{ Math.abs(intercept) }} → <strong class="mono">{{ probe.hu }} HU</strong> <span class="muted">({{ what(probe.hu) }})</span></span>
      </p>
      <p class="rv" :class="{ on: step >= 1 }">The file says how: <span class="mono">RescaleSlope {{ slope }}</span>, <span class="mono">RescaleIntercept {{ intercept }}</span></p>
      <div v-if="step >= 2" class="wrong rv on">
        <figure>
          <img :src="tagWin" alt="X-ray shown with its own window tags: almost all white">
          <figcaption class="bad">Window from the file’s tags: all white</figcaption>
        </figure>
        <figure>
          <img :src="good" alt="The same X-ray with a sensible window">
          <figcaption>A sensible window</figcaption>
        </figure>
        <p>The X-ray’s own window tags (<span class="mono">{{ meta.dx_window_tags.join(' / ') }}</span>) look copied from a CT. Metadata can be wrong.</p>
      </div>
    </div>
  </div>
</template>

<style scoped>
.sd { display: grid; grid-template-columns: 330px 1fr; gap: 36px; align-items: center; }
.pic { position: relative; width: 330px; height: 330px; cursor: crosshair; }
canvas { width: 100%; height: 100%; display: block; border-radius: var(--radius); }
.cross { position: absolute; width: 18px; height: 18px; border: 2px solid #ffc400; border-radius: 50%; transform: translate(-50%, -50%); pointer-events: none; }
.side p { font-size: var(--fs-label); margin: 0 0 14px; }
.readout { font-size: var(--fs-body) !important; }
.readout strong { color: var(--accent); }
.wrong { display: grid; grid-template-columns: 110px 110px 1fr; gap: 10px; align-items: start; margin-top: 12px; }
.wrong figure { margin: 0; display: flex; flex-direction: column; gap: 4px; }
.wrong img { width: 110px; height: 110px; border-radius: 4px; border: 1px solid var(--rule-strong); }
.wrong figcaption { font-size: 14px; line-height: 1.2; color: var(--ink-2); }
.wrong figcaption.bad { color: var(--bad); font-weight: 600; }
.wrong p { font-size: 16px !important; margin: 0 !important; }
</style>
