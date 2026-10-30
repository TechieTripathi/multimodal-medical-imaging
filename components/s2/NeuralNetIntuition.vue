<script setup lang="ts">
import { useStep } from '../../composables/useStep'
import ct from '../../data/imaging/ct/slice_lung.png'
import run from '../../data/runs/cnn_features.json'

// Artifact 21 — a network as a stack of pattern detectors. Real feature maps from ResNet-50 on our
// patient's CT slice: early layers respond to edges and brightness, later layers to larger blobs. clicks: 4
const { step } = useStep(4)
const maps = import.meta.glob('../../data/imaging/cnn/*.png', { eager: true, import: 'default' }) as Record<string, string>
const src = (f: string) => maps[`../../data/imaging/cnn/${f}`]
const labels = ['Early layer: edges, brightness', 'Middle layer: textures, outlines', 'Late layer: large patterns']
</script>

<template>
  <div class="nn">
    <figure class="input">
      <img :src="ct" alt="CT slice given to the network">
      <figcaption>Input: 448 × 448 pixels</figcaption>
    </figure>
    <span class="arrow" aria-hidden="true">→</span>
    <div v-for="(l, i) in run.layers" :key="l.layer" class="layer rv" :class="{ on: step >= i + 1 }">
      <img v-for="f in l.files" :key="f" :src="src(f)" alt="" class="fm">
      <p>{{ labels[i] }}<br><span class="muted">{{ l.grid[0] }} × {{ l.grid[1] }} grid, {{ l.channels }} maps</span></p>
    </div>
    <div class="out rv" :class="{ on: step >= 4 }">
      <strong>A final layer</strong> turns these patterns into an answer, after training on many labelled examples
    </div>
  </div>
</template>

<style scoped>
.nn { display: grid; grid-template-columns: 200px 24px repeat(3, 1fr) 150px; gap: 14px; align-items: center; }
.input { margin: 0; display: flex; flex-direction: column; gap: 6px; }
.input img { width: 200px; height: 200px; border-radius: var(--radius); background: var(--image-mat); }
figcaption, .layer p { font-size: var(--fs-micro); color: var(--ink-2); margin: 0; line-height: 1.3; }
.layer p { font-size: 15px; color: var(--ink); text-align: center; }
.arrow { font-size: 26px; color: var(--ink-3); }
.layer { display: flex; flex-direction: column; gap: 5px; align-items: center; }
.fm { width: 92px; height: 92px; image-rendering: pixelated; border-radius: 3px; background: var(--image-mat); }
.out { border: 2px solid var(--accent); border-radius: var(--radius); padding: 14px; font-size: var(--fs-label); line-height: 1.3; }
.out strong { color: var(--accent); display: block; }
</style>
