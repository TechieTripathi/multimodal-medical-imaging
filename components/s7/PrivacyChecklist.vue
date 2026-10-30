<script setup lang="ts">
import { useStep } from '../../composables/useStep'
import Status from '../ui/Status.vue'

// Slide 56 — four duties before AI touches patient images. clicks: 3
const { step } = useStep(3)
const ITEMS = [
  { h: 'De-identify', t: 'Blank the tags, mask burned-in text (we masked letters on our X-ray), beware faces in head scans' },
  { h: 'Protect', t: 'Never upload patient files to public AI tools or online notebooks; keep data inside the hospital' },
  { h: 'Follow the law', t: 'India’s DPDP Act 2023 covers personal data; its Rules were notified in November 2025 and phase in over 18 months' },
  { h: 'Check regulation', t: 'Software meant for diagnosis can be a medical device; CDSCO issued guidance on medical device software in July 2026' },
]
</script>

<template>
  <ol class="pc">
    <li v-for="(it, i) in ITEMS" :key="it.h" class="rv" :class="{ on: step >= i }">
      <Status state="active" compact />
      <strong>{{ it.h }}</strong>
      <span>{{ it.t }}</span>
    </li>
  </ol>
</template>

<style scoped>
.pc { list-style: none; padding: 0; margin: 0; display: flex; flex-direction: column; gap: 14px; }
.pc li { display: grid; grid-template-columns: 22px 180px 1fr; gap: 14px; align-items: baseline; border-bottom: 1px solid var(--rule); padding-bottom: 12px; margin: 0; }
.pc strong { font-size: var(--fs-body); }
.pc span { font-size: var(--fs-label); line-height: 1.3; }
</style>
