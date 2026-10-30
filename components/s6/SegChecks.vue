<script setup lang="ts">
import { useStep } from '../../composables/useStep'
import meta from '../../data/imaging/ct/meta.json'
import seg from '../../data/runs/segmentation.json'

// Slide 52 — checking segmentations against people: radiologists against each other (3D Dice),
// MedSAM against each radiologist, and whether TotalSegmentator marks the nodule at all. clicks: 2
const { step } = useStep(2)
const D = meta.readers.dice_3d
const shade = (v: number) => `color-mix(in srgb, var(--accent) ${Math.round(Math.max(0, (v - 0.7) / 0.3) * 100)}%, var(--surface))`
const between = seg.medsam.dice_between_readers_on_slice.flatMap((r, i) => r.filter((_, j) => j > i))
</script>

<template>
  <div class="sc">
    <div>
      <p class="lbl">Radiologist vs radiologist, whole nodule (3D Dice)</p>
      <div class="grid">
        <span /><span v-for="j in 4" :key="`h${j}`" class="h">R{{ j }}</span>
        <template v-for="(row, i) in D" :key="i">
          <span class="h">R{{ i + 1 }}</span>
          <span v-for="(v, j) in row" :key="j" class="c" :style="{ background: i === j ? 'var(--stage)' : shade(v), color: v > 0.85 && i !== j ? '#fff' : 'var(--ink)' }">{{ i === j ? '' : v.toFixed(2) }}</span>
        </template>
      </div>
    </div>
    <div class="rv" :class="{ on: step >= 1 }">
      <p class="lbl">MedSAM vs each radiologist, nodule slice</p>
      <div v-for="(v, i) in seg.medsam.dice_vs_readers" :key="i" class="bar"><span>R{{ i + 1 }}</span><span class="t"><span class="f" :style="{ width: `${v * 100}%` }" /></span><strong>{{ v.toFixed(2) }}</strong></div>
      <p class="small">Readers among themselves on this slice: {{ Math.min(...between).toFixed(2) }}–{{ Math.max(...between).toFixed(2) }}</p>
    </div>
    <div class="card rv last" :class="{ on: step >= 2 }">
      <strong>TotalSegmentator</strong> puts {{ (seg.nodule_vs_lung_label.fraction_inside_lung_label * 100).toFixed(1) }}% of the nodule inside “lung”. It was never asked to find disease, and it does not.
    </div>
  </div>
</template>

<style scoped>
.sc { display: grid; grid-template-columns: 1fr 1fr; gap: 20px 36px; align-items: start; }
.lbl { font-size: var(--fs-label); color: var(--ink-2); margin: 0 0 10px; }
.grid { display: grid; grid-template-columns: 40px repeat(4, 64px); gap: 3px; }
.h { font-size: 15px; color: var(--ink-2); display: grid; place-items: center; }
.c { height: 44px; display: grid; place-items: center; font: 600 16px var(--font-mono); border-radius: 3px; }
.bar { display: grid; grid-template-columns: 30px 1fr 50px; gap: 10px; align-items: center; margin-bottom: 8px; font-size: 16px; }
.t { height: 16px; background: var(--stage); border-radius: 3px; overflow: hidden; }
.f { display: block; height: 100%; background: rgb(40, 200, 120); }
.bar strong { font-family: var(--font-mono); }
.small { font-size: 15px; color: var(--ink-2); margin: 6px 0 0; }
.last { grid-column: 1 / -1; font-size: var(--fs-label); }
</style>
