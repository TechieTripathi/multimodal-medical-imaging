<script setup lang="ts">
import { computed, onMounted, ref, shallowRef, watch } from 'vue'
import { useStep } from '../../composables/useStep'
import { type Dicom, loadDicom, suvFactor } from '../../composables/dicom'
import { drawGrey, pub } from '../../composables/draw'
import meta from '../../data/imaging/petct/meta.json'

// Slide — PET pixels are radioactivity (Bq/ml); the file's own tags turn them into SUV, the number
// clinicians compare. Every value below is read from the real PET file. Hover the image. clicks: 3
const { step } = useStep(3)
const d = shallowRef<Dicom | null>(null)
const cv = ref<HTMLCanvasElement>()
onMounted(async () => { d.value = await loadDicom(pub('dicom/pet-fdg-lung.dcm')) })
const s = computed(() => d.value ? suvFactor(d.value) : null)
watch([d, cv], () => {
  if (!d.value || !cv.value) return
  const v = d.value.frame(0) as Float32Array
  drawGrey(cv.value, v, d.value.cols, d.value.rows, 4 / s.value!.factor, 8 / s.value!.factor, true)
}, { flush: 'post' })
const at = ref<{ x: number, y: number } | null>(null)
const probe = computed(() => {
  if (!d.value || !at.value || !s.value) return null
  const bq = (d.value.frame(0) as Float32Array)[at.value.y * d.value.cols + at.value.x]
  return { bq, suv: bq * s.value.factor }
})
const move = (e: PointerEvent) => {
  if (!d.value) return
  const r = (e.currentTarget as HTMLElement).getBoundingClientRect()
  at.value = { x: Math.floor(((e.clientX - r.left) / r.width) * d.value.cols), y: Math.floor(((e.clientY - r.top) / r.height) * d.value.rows) }
}
const f1 = (v: number) => v.toFixed(1)
const hhmm = (t: string) => `${t.slice(0, 2)}:${t.slice(2, 4)}`
</script>

<template>
  <div class="sv">
    <div>
      <div class="zoom"><canvas ref="cv" class="pet" @pointermove="move" @pointerleave="at = null" /></div>
      <p class="read">{{ probe ? `${Math.round(probe.bq).toLocaleString()} Bq/ml${step >= 3 ? ` → SUV ${f1(probe.suv)}` : ''}` : 'Point at the image' }}</p>
    </div>
    <div v-if="s" class="side">
      <p class="lbl">Read from the PET file’s tags</p>
      <dl class="tags rv" :class="{ on: step >= 1 }">
        <dt>Units</dt><dd class="mono">{{ d!.str('Units') }} (becquerels per ml)</dd>
        <dt>Tracer</dt><dd>{{ d!.item('RadiopharmaceuticalInformationSequence')?.str('Radiopharmaceutical') }}, {{ f1(s.doseMBq) }} MBq at {{ hhmm(s.start) }}</dd>
        <dt>Scan started</dt><dd>{{ hhmm(d!.str('SeriesTime')!) }}, {{ f1(s.minutes) }} min later</dd>
        <dt>Patient weight</dt><dd>{{ s.weight }} kg</dd>
      </dl>
      <p class="step rv" :class="{ on: step >= 2 }">Decay: half-life {{ f1(s.halfLifeMin) }} min, so {{ f1(s.doseNowMBq) }} MBq were left at the scan</p>
      <p class="step rv" :class="{ on: step >= 3 }"><strong>SUV</strong> = Bq/ml × {{ s.weight * 1000 }} g ÷ {{ f1(s.doseNowMBq) }} MBq · tumour SUVmax <strong>{{ meta.lesion.suv_max }}</strong> (whole tumour, 3D)</p>
    </div>
  </div>
</template>

<style scoped>
.sv { display: grid; grid-template-columns: 320px 1fr; gap: 32px; align-items: center; }
/* The PET field of view is 81 cm wide; show the middle 45% so the chest fills the frame */
.zoom { width: 320px; height: 320px; overflow: hidden; border-radius: var(--radius); border: 1px solid var(--rule); background: #fff; }
.pet { width: 711px; height: 711px; display: block; margin: -195px 0 0 -195px; cursor: crosshair; }
.read { font: 500 16px var(--font-mono); margin: 6px 0 0; color: var(--accent); min-height: 22px; }
.lbl { font-size: var(--fs-label); color: var(--ink-2); margin: 0 0 8px; }
.tags { display: grid; grid-template-columns: 130px 1fr; gap: 6px 12px; margin: 0 0 12px; font-size: 16px; }
.tags dt { color: var(--ink-2); }
.tags dd { margin: 0; }
.step { font-size: var(--fs-label); margin: 0 0 10px; }
</style>
