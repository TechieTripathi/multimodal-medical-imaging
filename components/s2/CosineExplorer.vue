<script setup lang="ts">
import { computed, ref } from 'vue'
import { useStep } from '../../composables/useStep'
import run from '../../data/runs/biomedclip_ranking.json'

// Artifact 7 — cosine similarity: do two arrows point the same way? Step 0: drag two arrows.
// Step 1: a three-number worked example. Step 2: the same formula on real 512-number BiomedCLIP
// embeddings of our patient's X-ray and two descriptions, computed live in the page. clicks: 2
const { step } = useStep(2)
const a = ref<[number, number]>([150, -40])
const b = ref<[number, number]>([90, -120])
const deg = (v: [number, number]) => Math.atan2(-v[1], v[0])
const cos2d = computed(() => Math.cos(deg(a.value) - deg(b.value)))
const angle = computed(() => Math.round(Math.abs(deg(a.value) - deg(b.value)) * 180 / Math.PI))
let dragging: 'a' | 'b' | null = null
function move(e: PointerEvent) {
  if (!dragging) return
  const r = (e.currentTarget as SVGElement).getBoundingClientRect()
  const scale = 360 / r.width
  const v: [number, number] = [(e.clientX - r.left) * scale - 180, (e.clientY - r.top) * scale - 180]
  const len = Math.hypot(v[0], v[1]) || 1
  const k = 150 / len;
  (dragging === 'a' ? a : b).value = [v[0] * k, v[1] * k]
}
// Real embeddings: image 0 is our patient's X-ray
const img = run.images[0].embedding
const TEXTS = [run.candidates.indexOf('a chest X-ray showing a mass in the lung'), run.candidates.indexOf('an MRI scan of the brain')]
const dot = (x: number[], y: number[]) => x.reduce((s, v, i) => s + v * y[i], 0)
const norm = (x: number[]) => Math.sqrt(dot(x, x))
const real = TEXTS.map(i => ({ text: run.candidates[i], vec: run.text_embeddings[i], cos: dot(img, run.text_embeddings[i]) / (norm(img) * norm(run.text_embeddings[i])) }))
const f = (v: number) => v.toFixed(2)
</script>

<template>
  <div class="cx">
    <div class="left">
      <svg viewBox="0 0 360 360" class="plane" @pointermove="move" @pointerup="dragging = null" @pointerleave="dragging = null">
        <defs><marker id="ca" viewBox="0 0 8 8" refX="6" refY="4" markerWidth="7" markerHeight="7" orient="auto"><path d="M0 0L8 4L0 8z" fill="context-stroke" /></marker></defs>
        <circle cx="180" cy="180" r="150" class="ring" />
        <line :x2="180 + a[0]" :y2="180 + a[1]" x1="180" y1="180" class="va" marker-end="url(#ca)" />
        <line :x2="180 + b[0]" :y2="180 + b[1]" x1="180" y1="180" class="vb" marker-end="url(#ca)" />
        <circle :cx="180 + a[0]" :cy="180 + a[1]" r="14" class="h" @pointerdown="dragging = 'a'" />
        <circle :cx="180 + b[0]" :cy="180 + b[1]" r="14" class="h" @pointerdown="dragging = 'b'" />
        <text :x="180 + a[0] * 0.6" :y="180 + a[1] * 0.6 - 12" class="lab a">image</text>
        <text :x="180 + b[0] * 0.6" :y="180 + b[1] * 0.6 - 12" class="lab b">words</text>
      </svg>
      <p class="read">angle {{ angle }}° → cosine <strong>{{ f(cos2d) }}</strong></p>
    </div>
    <div class="right">
      <p class="rule"><strong>1</strong> same direction · <strong>0</strong> unrelated · <strong>−1</strong> opposite</p>
      <div v-if="step === 1" class="work rv on">
        <p class="mono">image = [2, 1, 0]<br>words = [1, 1, 1]</p>
        <p>Multiply and add: 2·1 + 1·1 + 0·1 = <strong>3</strong></p>
        <p>Lengths: √5 = 2.24 and √3 = 1.73</p>
        <p>Cosine = 3 ÷ (2.24 × 1.73) = <strong>0.77</strong></p>
      </div>
      <div v-if="step === 2" class="work rv on">
        <p class="mono small">our X-ray = [{{ img.slice(0, 4).map(f).join(', ') }}, … 508 more]</p>
        <div v-for="r in real" :key="r.text" class="pair">
          <span class="txt">“{{ r.text }}”</span>
          <span class="bar"><span :style="{ width: `${Math.max(0, r.cos) * 200}%` }" /></span>
          <strong>{{ r.cos.toFixed(3) }}</strong>
        </div>
        <p class="small muted">Real BiomedCLIP scores sit in a narrow band; only the order matters</p>
      </div>
    </div>
  </div>
</template>

<style scoped>
.cx { display: grid; grid-template-columns: 330px 1fr; gap: 40px; align-items: center; }
.plane { width: 330px; height: 330px; touch-action: none; }
.ring { fill: var(--surface); stroke: var(--rule); stroke-width: 1.5; }
.va { stroke: var(--accent); stroke-width: 4; }
.vb { stroke: var(--warn); stroke-width: 4; }
.h { fill: transparent; cursor: grab; }
.lab { font: 600 16px var(--font-sans); text-anchor: middle; }
.lab.a { fill: var(--accent); }
.lab.b { fill: var(--warn); }
.read { text-align: center; font-size: var(--fs-label); margin: 4px 0 0; }
.rule { font-size: var(--fs-label); color: var(--ink-2); margin: 0 0 18px; }
.work p { margin: 0 0 10px; font-size: var(--fs-body); }
.mono { font-family: var(--font-mono); font-size: var(--fs-label) !important; }
.small { font-size: 15px !important; }
.pair { display: grid; grid-template-columns: 1fr 120px 64px; gap: 12px; align-items: center; margin: 10px 0; font-size: var(--fs-label); }
.bar { height: 14px; background: var(--stage); border-radius: 3px; overflow: hidden; }
.bar span { display: block; height: 100%; background: var(--accent); transition: width var(--dur) var(--ease); }
</style>
