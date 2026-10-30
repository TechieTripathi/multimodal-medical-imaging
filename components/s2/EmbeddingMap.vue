<script setup lang="ts">
import { computed, ref } from 'vue'
import { useStep } from '../../composables/useStep'
import run from '../../data/runs/biomedclip_embedding_map.json'

// Artifact 5 — every image becomes 512 numbers (its fingerprint). Squashed to 2 numbers for display,
// images of the same kind land together. Real BiomedCLIP embeddings, PCA to 2D. clicks: 2
const { step } = useStep(2)
const thumbs = import.meta.glob('../../data/imaging/thumbs/map_*.png', { eager: true, import: 'default' }) as Record<string, string>
const src = (p: string) => thumbs[`../../data/imaging/${p}`]
const W = 560
const H = 330
const xs = run.points.map(p => p.x)
const ys = run.points.map(p => p.y)
const [x0, x1, y0, y1] = [Math.min(...xs), Math.max(...xs), Math.min(...ys), Math.max(...ys)]
const px = (x: number) => 30 + ((x - x0) / (x1 - x0)) * (W - 60)
const py = (y: number) => 26 + ((y1 - y) / (y1 - y0)) * (H - 52)
const groups = [...new Set(run.points.map(p => p.group))]
// Group labels at each group's centre, nudged apart vertically where two would overlap
const labelPos = (() => {
  const pos = groups.map((g) => {
    const ps = run.points.filter(p => p.group === g)
    return { g, x: px(ps.reduce((s, p) => s + p.x, 0) / ps.length), y: py(ps.reduce((s, p) => s + p.y, 0) / ps.length) }
  }).sort((a, b) => a.y - b.y)
  for (let i = 1; i < pos.length; i++) {
    for (let j = 0; j < i; j++) {
      if (Math.abs(pos[i].x - pos[j].x) < 120 && pos[i].y - pos[j].y < 30)
        pos[i].y = pos[j].y + 30
    }
  }
  return Object.fromEntries(pos.map(p => [p.g, p]))
})()
const centre = (g: string) => labelPos[g]
const hover = ref<number | null>(null)
const hp = computed(() => hover.value === null ? null : run.points[hover.value])
</script>

<template>
  <div class="em">
    <div class="plot" :style="{ width: `${W}px`, height: `${H}px` }">
      <img
        v-for="(p, i) in run.points" :key="i" :src="src(p.thumb)" alt="" class="pt"
        :style="{ left: `${px(p.x)}px`, top: `${py(p.y)}px` }" @mouseenter="hover = i" @mouseleave="hover = null"
      >
      <span v-for="g in groups" :key="g" class="glabel rv" :class="{ on: step >= 1 }" :style="{ left: `${centre(g).x}px`, top: `${centre(g).y}px` }">{{ g }}</span>
    </div>
    <div class="side">
      <p class="big">512</p>
      <p>numbers per image: its <strong>fingerprint</strong></p>
      <p class="rv muted" :class="{ on: step >= 2 }">Shown here squashed to 2 numbers. Nobody told the model which image is which kind; similar images simply get similar fingerprints.</p>
      <div v-if="hp" class="card hov"><img :src="src(hp.thumb)" alt=""><span>{{ hp.group }}</span></div>
    </div>
  </div>
</template>

<style scoped>
.em { display: grid; grid-template-columns: auto 1fr; gap: 32px; align-items: center; }
.plot { position: relative; background: var(--surface); border: 1px solid var(--rule); border-radius: var(--radius); }
.pt { position: absolute; width: 38px; height: 38px; object-fit: cover; border-radius: 3px; transform: translate(-50%, -50%); border: 1px solid var(--rule-strong); background: var(--image-mat); transition: transform 0.2s var(--ease); }
.pt:hover { transform: translate(-50%, -50%) scale(2.2); z-index: 5; }
.glabel { position: absolute; transform: translate(-50%, -50%); background: rgba(255, 255, 255, 0.92); border: 1.5px solid var(--accent); color: var(--accent); font-weight: 600; font-size: 15px; padding: 2px 8px; border-radius: 999px; white-space: nowrap; pointer-events: none; z-index: 3; }
.side p { margin: 0 0 10px; font-size: var(--fs-label); }
.big { font-size: 56px !important; font-weight: 600; color: var(--accent); line-height: 1; }
.hov { display: flex; flex-direction: column; gap: 6px; padding: 10px; width: 140px; }
.hov img { width: 118px; height: 118px; object-fit: cover; }
</style>
