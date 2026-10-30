<script setup lang="ts">
import run from '../../data/runs/biomedclip_ranking.json'

// Slide 37 — two IU X-rays (unmodified) with BiomedCLIP's top description; one right, one wrong.
const thumbs = import.meta.glob('../../data/imaging/thumbs/rank_*.png', { eager: true, import: 'default' }) as Record<string, string>
const pick = run.images.filter(i => i.mesh && (i.mesh[0].startsWith('Cardiomegaly') || i.mesh[0].startsWith('Pleural Effusion')))
const short = (s: string) => s.replace('a chest X-ray showing ', '').replace(/ \(.*\)/, '')
const EXPECT: Record<string, string> = { 'Cardiomegaly': 'enlarged heart', 'Pleural Effusion': 'pleural effusion' }
const right = (im: typeof pick[number]) => im.ranking[0].includes(EXPECT[im.mesh![0].split('/')[0]])
</script>

<template>
  <div class="cx">
    <figure v-for="im in pick" :key="im.id">
      <img :src="thumbs[`../../data/imaging/${im.thumb}`]" alt="Chest X-ray from the IU collection">
      <figcaption>
        <span class="rep">Report: {{ im.mesh![0].split('/')[0].toLowerCase() }}</span>
        <span class="top" :class="right(im) ? 'ok' : 'bad'">Model’s top match: {{ short(im.ranking[0]) }}</span>
      </figcaption>
    </figure>
  </div>
  <p class="credit">Indiana University chest X-ray collection (Open-i), shown unmodified</p>
</template>

<style scoped>
.cx { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }
figure { margin: 0; display: flex; flex-direction: column; gap: 6px; }
img { width: 100%; aspect-ratio: 1; object-fit: cover; border-radius: var(--radius); background: var(--image-mat); }
figcaption { display: flex; flex-direction: column; gap: 3px; font-size: 15px; line-height: 1.2; }
.rep { color: var(--ink-2); }
.top.ok { color: var(--ok); font-weight: 600; }
.top.bad { color: var(--bad); font-weight: 600; }
.credit { font-size: var(--fs-micro); color: var(--ink-3); margin: 6px 0 0; }
</style>
