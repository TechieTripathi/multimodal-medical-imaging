<script setup lang="ts">
import { useStep } from '../../composables/useStep'
import nb from '../../data/runs/notebook.json'
import rank from '../../data/runs/biomedclip_ranking.json'

// Slide 50 — three real ways a score can mislead, all from our own runs. clicks: 2
const { step } = useStep(2)
const top = Object.entries(nb.patient_xray_ranking).slice(0, 2)
const eff = rank.images.find(i => i.mesh?.[0].startsWith('Pleural Effusion'))!
const effTop = eff.ranking[0]
const deck = rank.images[0].scores[rank.candidates.indexOf('a chest X-ray showing a mass in the lung')]
const notebook = nb.patient_xray_ranking['a chest X-ray showing a mass in the lung']
const short = (s: string) => s.replace('a chest X-ray showing ', '').replace(/ \(.*\)/, '')
</script>

<template>
  <div class="fc">
    <div class="card">
      <h3>Too close to call</h3>
      <p>Our patient, top two:</p>
      <p v-for="[c, s] in top" :key="c" class="mono">{{ s.toFixed(3) }} · {{ short(c) }}</p>
      <p class="why">A gap of {{ (top[0][1] - top[1][1]).toFixed(3) }}: a coin toss, not a finding</p>
    </div>
    <div class="card rv" :class="{ on: step >= 1 }">
      <h3>Confidently wrong</h3>
      <p>Report: pleural effusions</p>
      <p class="mono">top match: {{ short(effTop) }}</p>
      <p class="why">Fluid at the lung bases is subtle at 224 × 224 pixels</p>
    </div>
    <div class="card rv" :class="{ on: step >= 2 }">
      <h3>Same image, different preparation</h3>
      <p>“mass in the lung”, our patient:</p>
      <p class="mono">{{ deck.toFixed(3) }} · from a PNG (slides)<br>{{ notebook.toFixed(3) }} · from DICOM (notebook)</p>
      <p class="why">Windowing and masking changed the score</p>
    </div>
  </div>
</template>

<style scoped>
.fc { display: grid; grid-template-columns: repeat(3, 1fr); gap: 18px; align-items: stretch; }
.card { display: flex; flex-direction: column; gap: 6px; }
.card h3 { font-size: var(--fs-label) !important; color: var(--ink) !important; font-weight: 600 !important; }
.card p { margin: 0; font-size: 16px; line-height: 1.3; }
.mono { font-size: 15px !important; }
.why { margin-top: auto !important; padding-top: 10px; color: var(--bad); font-weight: 600; font-size: var(--fs-label) !important; }
</style>
