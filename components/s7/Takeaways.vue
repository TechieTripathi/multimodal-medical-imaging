<script setup lang="ts">
import { useStep } from '../../composables/useStep'

// Slide 58 — what to remember, and where research is needed. clicks: 1
const { step } = useStep(1)
</script>

<template>
  <div class="tk">
    <div>
      <h3>Remember</h3>
      <ol>
        <li>Multimodal AI turns images and words into comparable numbers</li>
        <li>DICOM details (units, order, windows) change results</li>
        <li>Wording, preparation and data shift move the scores</li>
        <li>A score is not a diagnosis; validate locally, keep a clinician in charge</li>
      </ol>
    </div>
    <div class="rv" :class="{ on: step >= 1 }">
      <h3>Open research questions</h3>
      <ol>
        <li>Models trained and tested on Indian patients and scanners</li>
        <li>Handling missing sequences and missing records</li>
        <li>Calibrated scores that mean what they say</li>
        <li>Checking generated reports, sentence by sentence</li>
      </ol>
    </div>
  </div>
</template>

<style scoped>
.tk { display: grid; grid-template-columns: 1fr 1fr; gap: 40px; }
h3 { font-size: var(--fs-lead) !important; color: var(--accent) !important; margin-bottom: 14px !important; }
ol { font-size: var(--fs-label); padding-left: 1.2em; }
li { margin-bottom: 10px !important; line-height: 1.3; }
</style>
