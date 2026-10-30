<script setup lang="ts">
import { useStep } from '../../composables/useStep'
import run from '../../data/runs/biomedclip_retrieval.json'

// Slide 43 — search by sentence: real top five of the searched IU X-rays, with what each report says. clicks: 2
const { step } = useStep(2)
const thumbs = import.meta.glob('../../data/imaging/thumbs/ret_*.png', { eager: true, import: 'default' }) as Record<string, string>
</script>

<template>
  <div class="rt">
    <p class="q">Search: <span class="mono">“{{ run.query }}”</span> across {{ run.searched }} X-rays</p>
    <div class="row">
      <figure v-for="(r, i) in run.top5" :key="i" class="rv" :class="{ on: step >= 1 }" :style="{ transitionDelay: `${i * 80}ms` }">
        <span class="rank">{{ i + 1 }}</span>
        <img :src="thumbs[`../../data/imaging/${r.thumb}`]" alt="Retrieved chest X-ray">
        <figcaption><span class="mono">{{ r.score.toFixed(3) }}</span><span class="lab rv" :class="[{ on: step >= 2 }, r.label.startsWith('cardio') ? 'ok' : 'bad']">{{ r.label }}</span></figcaption>
      </figure>
    </div>
    <p class="res rv" :class="{ on: step >= 2 }">{{ Math.round(run.precision_at_5 * 5) }} of the top 5 are enlarged-heart cases (precision at 5 = {{ run.precision_at_5.toFixed(1) }})</p>
    <p class="credit">Indiana University chest X-ray collection (Open-i), shown unmodified</p>
  </div>
</template>

<style scoped>
.rt { display: flex; flex-direction: column; gap: 14px; }
.q { font-size: var(--fs-label); margin: 0; }
.q .mono { font-size: 17px; background: var(--accent-tint); padding: 2px 8px; border-radius: 4px; }
.row { display: grid; grid-template-columns: repeat(5, 1fr); gap: 12px; }
figure { margin: 0; position: relative; display: flex; flex-direction: column; gap: 6px; }
.rank { position: absolute; left: 6px; top: 6px; background: var(--accent); color: #fff; width: 26px; height: 26px; border-radius: 50%; display: grid; place-items: center; font-weight: 600; font-size: 15px; }
img { width: 100%; aspect-ratio: 1; object-fit: cover; border-radius: var(--radius); }
figcaption { display: flex; flex-direction: column; gap: 2px; font-size: 15px; }
.lab.ok { color: var(--ok); font-weight: 600; }
.lab.bad { color: var(--bad); font-weight: 600; }
.res { font-size: var(--fs-body); margin: 0; }
.credit { font-size: var(--fs-micro); color: var(--ink-3); margin: 0; }
</style>
