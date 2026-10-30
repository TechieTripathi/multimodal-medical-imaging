<script setup lang="ts">
import { useStep } from '../../composables/useStep'
import run from '../../data/runs/biomedclip_shift.json'

// Artifact 20 — the same X-rays, changed slightly as a different scanner or setting might; the real
// zero-shot AUROC for cardiomegaly falls. Then the published hospital-identification finding. clicks: 2
const { step } = useStep(2)
const thumbs = import.meta.glob('../../data/imaging/thumbs/shift_*.png', { eager: true, import: 'default' }) as Record<string, string>
const names = Object.keys(run.auroc)
const lo = 0.5
</script>

<template>
  <div class="sh">
    <div class="row">
      <figure v-for="(n, i) in names" :key="n" class="rv" :class="{ on: step >= 1 || i === 0 }">
        <img :src="thumbs[`../../data/imaging/${(run.examples as any)[n]}`]" :alt="n">
        <figcaption>{{ n }}</figcaption>
        <span class="bar"><span :style="{ height: `${((run.auroc[n] - lo) / (1 - lo)) * 100}%` }" /></span>
        <strong>AUROC {{ run.auroc[n].toFixed(2) }}</strong>
      </figure>
    </div>
    <div class="card rv" :class="{ on: step >= 2 }">
      In a published study, networks identified <strong>which hospital</strong> a chest X-ray came from for <strong>99.95%</strong> of one hospital’s images, and pneumonia models did worse at hospitals they had not seen.
    </div>
  </div>
</template>

<style scoped>
.sh { display: flex; flex-direction: column; gap: 18px; }
.row { display: grid; grid-template-columns: repeat(5, 1fr); gap: 14px; }
figure { margin: 0; display: flex; flex-direction: column; gap: 6px; align-items: center; }
img { width: 100%; aspect-ratio: 1; border-radius: var(--radius); }
figcaption { font-size: 15px; text-align: center; line-height: 1.2; height: 36px; }
.bar { width: 40px; height: 70px; background: var(--stage); border-radius: 3px; display: flex; align-items: flex-end; overflow: hidden; }
.bar span { width: 100%; background: var(--accent); transition: height 0.6s var(--ease); }
figure strong { font: 600 16px var(--font-mono); }
.card { font-size: var(--fs-label); }
</style>
