<script setup lang="ts">
import { useStep } from '../../composables/useStep'
import xray from '../../data/imaging/gallery/xray.png'

// Slide 4 — a clinician joins three kinds of evidence before deciding. clicks: 3
const { step } = useStep(3)
const lanes = [
  { title: 'The images', body: 'What is there, where, how big' },
  { title: 'The words', body: 'Reports, referral letter, notes' },
  { title: 'The patient', body: 'History, symptoms, tests, earlier scans' },
]
</script>

<template>
  <div class="flow">
    <div class="lanes">
      <div v-for="(l, i) in lanes" :key="l.title" class="lane rv" :class="{ on: step >= i }">
        <img v-if="i === 0" :src="xray" alt="" class="thumb">
        <span v-else class="thumb glyph" aria-hidden="true">{{ i === 1 ? '¶' : '♥' }}</span>
        <span><strong>{{ l.title }}</strong><br><span class="muted">{{ l.body }}</span></span>
      </div>
    </div>
    <svg class="arrows" viewBox="0 0 120 300" aria-hidden="true">
      <path v-for="(y, i) in [50, 150, 250]" :key="y" class="rv" :class="{ on: step >= 3 }" :d="`M0 ${y} C 70 ${y}, 50 150, 116 150`" />
    </svg>
    <div class="decide rv" :class="{ on: step >= 3 }">
      <strong>One judgement</strong>
      <span class="muted">Follow-up scan, biopsy, or surgery?</span>
    </div>
  </div>
</template>

<style scoped>
.flow { display: grid; grid-template-columns: 1.3fr 120px 1fr; align-items: center; }
.lanes { display: flex; flex-direction: column; gap: 20px; }
.lane { display: flex; gap: 16px; align-items: center; font-size: var(--fs-label); line-height: 1.3; }
.lane strong { font-size: var(--fs-body); }
.thumb { width: 80px; height: 80px; border-radius: var(--radius); object-fit: cover; flex: none; background: var(--image-mat); }
.glyph { display: grid; place-items: center; color: #fff; font-size: 34px; background: var(--accent); }
.arrows { width: 120px; height: 300px; }
.arrows path { fill: none; stroke: var(--accent); stroke-width: 1.5; }
.decide { border: 2px solid var(--accent); border-radius: var(--radius); padding: 22px; display: flex; flex-direction: column; gap: 8px; font-size: var(--fs-label); }
.decide strong { font-size: var(--fs-lead); color: var(--accent); }
</style>
