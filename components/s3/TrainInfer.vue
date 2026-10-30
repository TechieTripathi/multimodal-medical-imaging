<script setup lang="ts">
import { useStep } from '../../composables/useStep'

// Slide 19 — training happens once, with many labelled examples; inference happens every time, with one. clicks: 1
const { step } = useStep(1)
</script>

<template>
  <div class="ti">
    <div class="lane">
      <h3>Training</h3>
      <div class="flow">
        <span class="box many">Millions of examples<br><small>BiomedCLIP: 15 million figure–caption pairs</small></span>
        <span class="arr">→</span>
        <span class="box model">Model<br><small>its numbers keep changing</small></span>
      </div>
      <ul><li>Done once, by the developer</li><li>Days on many GPUs</li><li>Needs data, labels, and checks</li></ul>
    </div>
    <div class="lane rv" :class="{ on: step >= 1 }">
      <h3>Inference</h3>
      <div class="flow">
        <span class="box one">One new image</span>
        <span class="arr">→</span>
        <span class="box model frozen">Model<br><small>its numbers are fixed</small></span>
        <span class="arr">→</span>
        <span class="box">An answer</span>
      </div>
      <ul><li>Done every time it is used</li><li>Seconds on one computer</li><li>Can only be as good as its training</li></ul>
    </div>
  </div>
</template>

<style scoped>
.ti { display: grid; grid-template-columns: 1fr 1fr; gap: 40px; }
h3 { font-size: var(--fs-lead) !important; color: var(--accent) !important; margin-bottom: 14px !important; }
.flow { display: flex; align-items: center; gap: 10px; margin-bottom: 18px; }
.box { border: 1.5px solid var(--ink-2); border-radius: var(--radius); padding: 12px; font-size: var(--fs-label); line-height: 1.25; background: var(--surface); }
.box small { font-size: 15px; color: var(--ink-2); }
.many { box-shadow: 4px 4px 0 var(--rule-strong), 8px 8px 0 var(--rule); }
.model { background: var(--accent); color: #fff; border-color: var(--accent); }
.model small { color: #dfe4fb; }
.frozen { background: var(--accent-strong); }
.arr { color: var(--ink-3); font-size: 22px; }
ul { font-size: var(--fs-label); }
li { margin-bottom: 6px !important; }
</style>
