<script setup lang="ts">
import { useStep } from '../../composables/useStep'
import xray from '../../data/imaging/gallery/xray.png'

// Slide 6 — multimodal = more than one kind of input, learned together. clicks: 3
const { step } = useStep(3)
</script>

<template>
  <div class="mi">
    <div class="ins">
      <div class="in">
        <img :src="xray" alt="">
        <span><strong>Images</strong><br><span class="muted">X-ray, CT, MRI, slides</span></span>
      </div>
      <div class="in rv" :class="{ on: step >= 1 }">
        <span class="chip-txt">“solid nodule, spiculated”</span>
        <span><strong>Text</strong><br><span class="muted">Reports, notes</span></span>
      </div>
      <div class="in rv" :class="{ on: step >= 2 }">
        <span class="chip-num">age 65<br>BP 130/80</span>
        <span><strong>Numbers</strong><br><span class="muted">Labs, vitals, history</span></span>
      </div>
    </div>
    <svg class="join rv" :class="{ on: step >= 3 }" viewBox="0 0 120 320" aria-hidden="true">
      <path v-for="y in [50, 160, 270]" :key="y" :d="`M0 ${y} C 70 ${y}, 50 160, 116 160`" />
    </svg>
    <div class="model rv" :class="{ on: step >= 3 }">
      <strong>One model</strong>
      <span>learns how they relate</span>
      <span class="arrow" aria-hidden="true">↓</span>
      <span class="outp">An answer, a score, or an outline</span>
    </div>
  </div>
</template>

<style scoped>
.mi { display: grid; grid-template-columns: 1.25fr 120px 1fr; align-items: center; }
.ins { display: flex; flex-direction: column; gap: 22px; }
.in { display: flex; align-items: center; gap: 16px; font-size: var(--fs-label); line-height: 1.3; }
.in strong { font-size: var(--fs-body); }
.in img, .chip-txt, .chip-num { width: 120px; height: 84px; flex: none; border-radius: var(--radius); }
.in img { object-fit: cover; background: var(--image-mat); }
.chip-txt, .chip-num { display: grid; place-items: center; text-align: center; padding: 8px; font-size: var(--fs-micro); line-height: 1.3; border: 1px solid var(--rule-strong); background: var(--surface); }
.chip-txt { font-style: italic; }
.chip-num { font-family: var(--font-mono); }
.join { width: 120px; height: 320px; }
.join path { fill: none; stroke: var(--accent); stroke-width: 1.5; }
.model { border: 2px solid var(--accent); border-radius: var(--radius); padding: 22px; display: flex; flex-direction: column; gap: 6px; align-items: flex-start; font-size: var(--fs-label); }
.model strong { font-size: var(--fs-lead); color: var(--accent); }
.arrow { color: var(--ink-3); font-size: 26px; line-height: 1; margin: 4px 0; }
.outp { font-weight: 600; }
</style>
