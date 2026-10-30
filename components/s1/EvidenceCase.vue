<script setup lang="ts">
import { useStep } from '../../composables/useStep'
import xray from '../../data/imaging/dx/dx1.png'
import ct from '../../data/imaging/ct/slice_lung.png'
import meta from '../../data/imaging/ct/meta.json'
import reports from '../../data/imaging/ct/reports.json'
import ImageMat from '../ui/ImageMat.vue'

// Slide 2: one real patient, the evidence arriving piece by piece. clicks: 3
const { step } = useStep(3)
const r = reports.readers[0].items
const [cy, cx] = meta.nodule_center_yx
const short = (s: string) => s.split(' (')[0]
</script>

<template>
  <div class="ev">
    <div class="col">
      <ImageMat :src="xray" alt="Frontal chest X-ray" :h="230" caption="Chest X-ray" />
    </div>
    <div class="col rv" :class="{ on: step >= 1 }">
      <ImageMat :src="ct" alt="Axial CT slice through the nodule" :h="230" caption="CT, one slice of 133">
        <span class="ring" :style="{ left: `${cx / 5.12}%`, top: `${cy / 5.12}%` }" />
      </ImageMat>
    </div>
    <div class="col rv" :class="{ on: step >= 2 }">
      <div class="card report">
        <h3>A radiologist’s assessment</h3>
        <p>Solid nodule, about {{ r.Diameter }}</p>
        <p>Spiculated edge: {{ short(r.Spiculation) }}</p>
        <p>Malignancy: <strong>{{ short(r.Malignancy) }}</strong></p>
      </div>
      <p class="cap">Structured report, one of four readers</p>
    </div>
    <div class="col rv" :class="{ on: step >= 3 }">
      <div class="card dashed history">
        <h3>Clinical history</h3>
        <p>Symptoms, smoking, earlier scans, blood tests…</p>
        <p class="missing">Not in the public data</p>
      </div>
      <p class="cap">What a clinician would also ask for</p>
    </div>
  </div>
</template>

<style scoped>
.ev { display: grid; grid-template-columns: 1fr 1fr 1.05fr 1fr; gap: 20px; align-items: start; }
.col { min-width: 0; display: flex; flex-direction: column; gap: 6px; }
.ring { position: absolute; width: 22%; aspect-ratio: 1; border: 2px solid #ffc400; border-radius: 50%; transform: translate(-50%, -50%); }
.report, .history { height: 230px; display: flex; flex-direction: column; gap: 6px; }
.report p, .history p { margin: 0; font-size: var(--fs-label); line-height: 1.3; }
.missing { margin-top: auto !important; color: var(--warn); font-weight: 600; }
.cap { margin: 0; font-size: var(--fs-label); color: var(--ink); font-weight: 500; }
</style>
