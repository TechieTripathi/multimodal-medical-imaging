<script setup lang="ts">
import { useStep } from '../../composables/useStep'
import xray from '../../data/imaging/gallery/xray.png'

// Slide 27 — a vision-language assistant: image encoder feeds a language model, which writes text.
// The output text is a simulated example, not a model run. clicks: 3
const { step } = useStep(3)
</script>

<template>
  <div class="af">
    <div class="ins">
      <img :src="xray" alt="Chest X-ray">
      <span class="q">“Describe this chest X-ray.”</span>
    </div>
    <span class="arr">→</span>
    <div class="stack rv" :class="{ on: step >= 1 }">
      <span class="b enc">Image encoder</span>
      <span class="plus">+</span>
      <span class="b llm">Language model<small>writes one word at a time</small></span>
    </div>
    <span class="arr rv" :class="{ on: step >= 2 }">→</span>
    <div class="out rv" :class="{ on: step >= 2 }">
      <p>“Rounded opacity in the left lower zone.</p>
      <p>Heart size is normal.</p>
      <p :class="{ flag: step >= 3 }">No change from the prior study.”</p>
      <p v-if="step >= 3" class="why">There is no prior study. Fluent text can state things the image cannot support.</p>
    </div>
  </div>
</template>

<style scoped>
.af { display: grid; grid-template-columns: 200px 30px 220px 30px 1fr; gap: 10px; align-items: center; }
.ins { display: flex; flex-direction: column; gap: 10px; }
.ins img { width: 200px; height: 200px; border-radius: var(--radius); }
.q { font-size: var(--fs-label); font-style: italic; }
.arr { font-size: 24px; color: var(--ink-3); text-align: center; }
.stack { display: flex; flex-direction: column; gap: 8px; align-items: stretch; }
.b { border-radius: var(--radius); padding: 14px; font-size: var(--fs-label); font-weight: 600; display: flex; flex-direction: column; gap: 4px; }
.b small { font-weight: 400; font-size: 15px; }
.enc { border: 2px solid var(--accent); color: var(--accent); }
.llm { background: var(--accent); color: #fff; }
.plus { text-align: center; color: var(--ink-3); font-size: 20px; }
.out { background: var(--surface); border: 1px solid var(--rule); border-radius: var(--radius); padding: 16px; }
.out p { margin: 0 0 6px; font-size: var(--fs-label); font-style: italic; }
.flag { background: var(--bad-tint); color: var(--bad); border-radius: 3px; }
.why { font-style: normal !important; color: var(--bad); margin-top: 10px !important; font-size: 16px !important; }
</style>
