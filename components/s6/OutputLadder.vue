<script setup lang="ts">
import { useStep } from '../../composables/useStep'
import nb from '../../data/runs/notebook.json'

// Slide 53 — from a score to a diagnosis, and what each rung needs. Values from our notebook run. clicks: 3
const { step } = useStep(3)
const top = Object.entries(nb.patient_xray_ranking)[0]
const RUNGS = [
  { what: 'A similarity score', ex: `${top[1].toFixed(3)} for “mass in the lung”`, needs: 'Only ranks options for this one image' },
  { what: 'A “probability”', ex: `${nb.softmax_top2[0].toFixed(2)} after softmax`, needs: 'Looks confident; is not calibrated' },
  { what: 'A finding', ex: '“Suspicious lung mass: yes”', needs: 'A threshold tested on local data, with known sensitivity' },
  { what: 'A diagnosis', ex: '“Lung cancer”', needs: 'A clinician, all the evidence, often a biopsy' },
]
</script>

<template>
  <ol class="ld">
    <li v-for="(r, i) in RUNGS" :key="r.what" class="rv" :class="{ on: step >= i }" :style="{ marginLeft: `${i * 46}px` }">
      <span class="w">{{ r.what }}</span>
      <span class="ex mono">{{ r.ex }}</span>
      <span class="n">{{ r.needs }}</span>
    </li>
  </ol>
</template>

<style scoped>
.ld { list-style: none; padding: 0; margin: 0; display: flex; flex-direction: column; gap: 8px; }
.ld li { display: grid; grid-template-columns: 190px 290px 1fr; gap: 16px; align-items: center; line-height: 1.25; border-left: 4px solid var(--accent); background: var(--surface); padding: 10px 14px; border-radius: 0 var(--radius) var(--radius) 0; margin-bottom: 0; }
.w { font-size: var(--fs-label); font-weight: 600; }
.ex { font-size: 16px; color: var(--ink-2); }
.n { font-size: 16px; }
</style>
