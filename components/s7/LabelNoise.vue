<script setup lang="ts">
import { useStep } from '../../composables/useStep'
import reports from '../../data/imaging/ct/reports.json'
import meta from '../../data/imaging/ct/meta.json'
import rank from '../../data/runs/biomedclip_ranking.json'

// Slide 54 — three real data problems from this session's own data. clicks: 2
const { step } = useStep(2)
const r = reports.readers.map(x => x.items)
const num = (s: string) => s.split(' ')[0]
const cm = rank.images.find(i => i.mesh?.[0].startsWith('Cardiomegaly'))!
const vols = meta.readers.volume_mm3.map(v => (v / 1000).toFixed(1))
</script>

<template>
  <div class="ln">
    <div class="card">
      <h3>Experts disagree</h3>
      <p>Four radiologists, one nodule:</p>
      <p class="mono">malignancy {{ r.map(x => num(x.Malignancy)).join(', ') }} of 5<br>spiculation {{ r.map(x => num(x.Spiculation)).join(', ') }} of 5<br>volume {{ vols.join(', ') }} cm³</p>
      <p class="why">Which one is the “true” label?</p>
    </div>
    <div class="card rv" :class="{ on: step >= 1 }">
      <h3>Labels from text are noisy</h3>
      <p>Labelled <strong>cardiomegaly</strong> from report keywords; the report itself says:</p>
      <p class="quote">“{{ cm.truth.replace('Report impression: ', '') }}”</p>
      <p class="why">Keyword labels inherit every hedge</p>
    </div>
    <div class="card rv" :class="{ on: step >= 2 }">
      <h3>Who is in the data?</h3>
      <p>Our X-ray, CT and MRI data all come from hospitals in the United States.</p>
      <p>How well do they represent the patients you see?</p>
      <p class="why">A model learns the population it saw</p>
    </div>
  </div>
</template>

<style scoped>
.ln { display: grid; grid-template-columns: repeat(3, 1fr); gap: 18px; align-items: stretch; }
.card { display: flex; flex-direction: column; gap: 8px; }
.card h3 { font-size: var(--fs-label) !important; color: var(--ink) !important; font-weight: 600 !important; }
.card p { margin: 0; font-size: 16px; line-height: 1.3; }
.mono { font-size: 15px !important; line-height: 1.6 !important; }
.quote { font-style: italic; }
.why { margin-top: auto !important; padding-top: 10px; color: var(--bad); font-weight: 600; font-size: var(--fs-label) !important; }
</style>
