<script setup lang="ts">
import { computed, ref } from 'vue'
import { useStep } from '../../composables/useStep'
import run from '../../data/runs/biomedclip_ranking.json'

// Artifact 18 — real BiomedCLIP ranking of candidate descriptions for real X-rays. Scores are
// recomputed in the page from the saved 512-number fingerprints, so switching descriptions on and off
// re-ranks live. Step 1: scores appear; step 2: sorted into a ranking. clicks: 2
const { step } = useStep(2)
const thumbs = import.meta.glob('../../data/imaging/thumbs/rank_*.png', { eager: true, import: 'default' }) as Record<string, string>
const LABEL: Record<string, string> = { 'lidc-dx': 'Our patient' }
const name = (im: typeof run.images[number]) => LABEL[im.id] ?? `IU: ${im.mesh?.[0].split('/')[0].toLowerCase()}`
const which = ref(0)
const on = ref(run.candidates.map(() => true))
const dot = (a: number[], b: number[]) => a.reduce((s, v, i) => s + v * b[i], 0)
const rows = computed(() => {
  const img = run.images[which.value].embedding
  const r = run.candidates.map((c, i) => ({ c, i, s: dot(img, run.text_embeddings[i]) / Math.sqrt(dot(img, img) * dot(run.text_embeddings[i], run.text_embeddings[i])) }))
    .filter(x => on.value[x.i])
  return step.value >= 2 ? [...r].sort((a, b) => b.s - a.s) : r
})
const lo = 0.05, hi = 0.5
const short = (s: string) => s.replace('a chest X-ray showing ', '…').replace(/ \(.*\)/, '')
</script>

<template>
  <div class="rv2">
    <div class="left">
      <img :src="thumbs[`../../data/imaging/${run.images[which].thumb}`]" alt="X-ray being ranked">
      <div class="pick">
        <button v-for="(im, i) in run.images" :key="im.id" class="chip" :aria-pressed="which === i" @click="which = i">{{ name(im) }}</button>
      </div>
      <p class="truth">{{ run.images[which].truth }}</p>
    </div>
    <TransitionGroup tag="div" name="rk" class="bars">
      <div v-for="(r, k) in rows" :key="r.c" class="row" :class="{ top: step >= 2 && k === 0 }">
        <button class="tog" :aria-pressed="on[r.i]" :aria-label="`Remove ${r.c}`" @click="on[r.i] = false">×</button>
        <span class="c">{{ short(r.c) }}</span>
        <span class="track"><span class="fill" :style="{ width: step >= 1 ? `${Math.min(100, Math.max(2, ((r.s - lo) / (hi - lo)) * 100))}%` : '0%' }" /></span>
        <strong class="s">{{ step >= 1 ? r.s.toFixed(3) : '' }}</strong>
      </div>
    </TransitionGroup>
    <button v-if="on.some(x => !x)" class="chip reset" @click="on = run.candidates.map(() => true)">Show all descriptions</button>
  </div>
</template>

<style scoped>
.rv2 { display: grid; grid-template-columns: 230px 1fr; gap: 28px; align-items: start; position: relative; }
.left img { width: 230px; height: 200px; object-fit: cover; border-radius: var(--radius); background: var(--image-mat); }
.pick { display: flex; flex-wrap: wrap; gap: 4px; margin-top: 8px; }
.pick .chip { padding: 4px 9px; font-size: 14px; }
.truth { font-size: 14px; color: var(--ink-2); margin: 6px 0 0; line-height: 1.25; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; }
.bars { display: flex; flex-direction: column; gap: 8px; }
.row { display: grid; grid-template-columns: 26px 1fr 170px 62px; gap: 10px; align-items: center; padding: 3px 6px; border-radius: 4px; }
.row.top { background: var(--accent-tint); }
.c { font-size: 17px; }
.track { height: 16px; background: var(--stage); border-radius: 3px; overflow: hidden; }
.fill { display: block; height: 100%; background: var(--accent); transition: width 0.6s var(--ease); }
.s { font: 600 16px var(--font-mono); text-align: right; }
.tog { width: 24px; height: 24px; border-radius: 50%; border: 1px solid var(--rule-strong); background: var(--surface); cursor: pointer; color: var(--ink-3); }
.rk-move { transition: transform 0.6s var(--ease); }
.reset { position: absolute; right: 0; bottom: -40px; padding: 4px 10px; font-size: 14px; }
</style>
