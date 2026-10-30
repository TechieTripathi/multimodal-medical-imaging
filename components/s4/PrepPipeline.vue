<script setup lang="ts">
import { useStep } from '../../composables/useStep'
import raw from '../../data/imaging/pipeline/raw.png'
import win from '../../data/imaging/pipeline/windowed.png'
import small from '../../data/imaging/pipeline/resized.png'
import meta from '../../data/imaging/pipeline/meta.json'

// Artifact 17 — our X-ray on its way into BiomedCLIP, and what each step keeps and loses. clicks: 3
const { step } = useStep(3)
const STAGES = [
  { name: 'DICOM pixels', img: raw, kept: `${meta.stored_bits}-bit values, ${meta.rows} × ${meta.cols}`, lost: 'Nothing yet' },
  { name: 'Window to 8 bits', img: win, kept: '256 grey levels you can see', lost: `Most of the ${2 ** meta.stored_bits} levels; values outside the window` },
  { name: 'Resize to 224', img: small, kept: `224 × 224 pixels`, lost: `${(100 - meta.pixels_kept_pct).toFixed(1)}% of the pixels; spacing in mm` },
  { name: 'Normalise', img: small, kept: `Values from ${meta.normalised_range[0]} to ${meta.normalised_range[1]}, as the model expects`, lost: 'Patient tags (good for privacy)' },
]
</script>

<template>
  <div class="pp">
    <div v-for="(s, i) in STAGES" :key="s.name" class="st rv" :class="{ on: step >= i }">
      <span class="no">{{ i + 1 }}</span>
      <img :src="s.img" :alt="s.name">
      <strong>{{ s.name }}</strong>
      <p class="k"><span>Kept</span>{{ s.kept }}</p>
      <p class="l"><span>Lost</span>{{ s.lost }}</p>
    </div>
  </div>
</template>

<style scoped>
.pp { display: grid; grid-template-columns: repeat(4, 1fr); gap: 18px; }
.st { display: flex; flex-direction: column; gap: 8px; position: relative; }
.no { position: absolute; left: 6px; top: 6px; background: var(--accent); color: #fff; font-weight: 600; width: 26px; height: 26px; border-radius: 50%; display: grid; place-items: center; font-size: 15px; }
.st img { width: 100%; aspect-ratio: 1; border-radius: var(--radius); }
.st strong { font-size: var(--fs-label); }
.st p { margin: 0; font-size: 15px; line-height: 1.25; }
.st p span { display: block; font-size: 14px; font-weight: 600; }
.k span { color: var(--ok); }
.l span { color: var(--bad); }
</style>
