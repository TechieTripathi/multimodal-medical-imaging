<script setup lang="ts">
import { useStep } from '../../composables/useStep'

// Slide 18 — numbers from the record become a short list of scaled values, with "missing" made explicit,
// then join the image fingerprint. Illustrative values. clicks: 3
const { step } = useStep(3)
const FIELDS = [
  { k: 'Age', v: '67 years', n: '0.67', missing: false },
  { k: 'Smoking', v: '40 pack-years', n: '0.80', missing: false },
  { k: 'CRP (blood test)', v: 'not measured', n: '0', missing: true },
  { k: 'Earlier CT', v: 'unknown', n: '0', missing: true },
]
</script>

<template>
  <div class="sd">
    <div class="card rec">
      <h3>From the patient record</h3>
      <p v-for="f in FIELDS" :key="f.k" class="f"><span>{{ f.k }}</span><strong :class="{ miss: f.missing }">{{ f.v }}</strong></p>
    </div>
    <span class="arrow rv" :class="{ on: step >= 1 }" aria-hidden="true">→</span>
    <div class="vec rv" :class="{ on: step >= 1 }">
      <p class="lbl">Scaled to 0–1</p>
      <div v-for="f in FIELDS" :key="f.k" class="cellrow">
        <span class="cell" :class="{ miss: f.missing && step >= 2 }">{{ f.n }}</span>
        <span class="flag rv" :class="{ on: step >= 2 }">{{ f.missing ? 'missing = 1' : 'missing = 0' }}</span>
      </div>
    </div>
    <span class="arrow rv" :class="{ on: step >= 3 }" aria-hidden="true">→</span>
    <div class="join rv" :class="{ on: step >= 3 }">
      <p class="lbl">Joined with the image fingerprint</p>
      <div class="bars"><span class="img" /><span class="num" /></div>
      <p class="small muted">512 numbers from the image + 8 from the record</p>
    </div>
  </div>
</template>

<style scoped>
.sd { display: grid; grid-template-columns: 1.15fr 30px 1fr 30px 1fr; gap: 12px; align-items: center; }
.rec .f { display: flex; justify-content: space-between; gap: 12px; margin: 0 0 10px; font-size: var(--fs-label); }
.rec .f span { color: var(--ink-2); }
.miss { color: var(--warn); }
.arrow { font-size: 26px; color: var(--ink-3); text-align: center; }
.lbl { font-size: var(--fs-label); color: var(--ink-2); margin: 0 0 10px; }
.cellrow { display: flex; align-items: center; gap: 10px; margin-bottom: 10px; }
.cell { font: 500 var(--fs-label) var(--font-mono); width: 64px; text-align: center; padding: 6px 0; border: 1px solid var(--rule-strong); border-radius: 3px; background: var(--surface); }
.cell.miss { border-color: var(--warn); background: var(--warn-tint); }
.flag { font: 400 15px var(--font-mono); color: var(--ink-2); }
.bars { display: flex; height: 34px; border-radius: 3px; overflow: hidden; border: 1px solid var(--rule-strong); }
.bars .img { flex: 512; background: repeating-linear-gradient(90deg, var(--accent) 0 3px, var(--accent-tint-2) 3px 6px); }
.bars .num { flex: 40; background: var(--warn); }
.small { font-size: 15px; margin-top: 8px; }
</style>
