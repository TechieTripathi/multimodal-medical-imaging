<script setup lang="ts">
import { useSlideContext } from '@slidev/client'
import xray from '../../data/imaging/gallery/xray.png'
import ModelCard from '../ui/ModelCard.vue'

// Slide 25 — CheXzero as a model card, beside the kind of input it takes. Rows reveal with the clicker. clicks: 4
const { $clicks } = useSlideContext()
const rows: [string, string][] = [
  ['Problem', 'Labelling X-rays by hand is slow and expensive'],
  ['Input → output', 'Chest X-ray + a pair of prompts (“pneumonia” / “no pneumonia”) → a score'],
  ['How', 'CLIP-style training on X-rays and the reports already written about them'],
  ['Reported', 'Accuracy comparable to radiologists; beat a fully supervised model on 3 of 8 findings on external data'],
  ['Limits', 'Chest X-ray only; accuracy varies by finding; research model'],
]
</script>

<template>
  <div class="cz">
    <figure>
      <img :src="xray" alt="A chest X-ray, the kind of input CheXzero takes">
      <figcaption>Input: one chest X-ray</figcaption>
    </figure>
    <ModelCard :rows="rows" :reveal="$clicks" />
  </div>
</template>

<style scoped>
.cz { display: grid; grid-template-columns: 220px 1fr; gap: 36px; align-items: center; }
figure { margin: 0; display: flex; flex-direction: column; gap: 6px; }
figure img { width: 220px; height: 220px; border-radius: var(--radius); }
figcaption { font-size: var(--fs-micro); color: var(--ink-2); }
</style>
