<script setup lang="ts">
import { SECTIONS } from '../../data/sections'

// Slide 8 — the seven parts, each with the one question it answers.
const QUESTIONS: Record<number, string> = {
  1: 'Why combine images with words and data?',
  2: 'How does a computer read an X-ray and a report?',
  3: 'How are models trained, tested and compared?',
  4: 'How are medical images stored?',
  5: 'Where is this used today?',
  6: 'What happens when we run real models?',
  7: 'What can go wrong, and who is responsible?',
}
</script>

<template>
  <ol class="road">
    <li v-for="s in SECTIONS" :key="s.no">
      <span class="no">{{ s.no }}</span>
      <span class="q">{{ QUESTIONS[s.no] }}</span>
      <span class="min">{{ s.minutes }} min</span>
    </li>
  </ol>
</template>

<style scoped>
.road { list-style: none; padding: 0; margin: 0; display: flex; flex-direction: column; gap: 4px; }
.road li { display: grid; grid-template-columns: 40px 1fr auto; align-items: baseline; gap: 14px; padding: 5px 0; border-bottom: 1px solid var(--rule); margin: 0; }
.no { font-weight: 600; color: var(--accent); font-size: var(--fs-body); }
.q { font-size: var(--fs-small); }
.min { font-size: var(--fs-label); color: var(--ink-3); font-variant-numeric: tabular-nums; }
</style>
