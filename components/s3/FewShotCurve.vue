<script setup lang="ts">
import { computed, ref } from 'vue'
import { useStep } from '../../composables/useStep'
import run from '../../data/runs/biomedclip_fewshot_crc.json'

// Slide 21 — a few labelled examples go a long way. Real accuracy of a small classifier on frozen
// BiomedCLIP fingerprints, against the best zero-shot wording. Hover a point for the range. clicks: 2
const { step } = useStep(2)
const W = 560, H = 320, L = 54, B = 56
const xs = run.curve.map(c => c.per_class)
const lx = (v: number) => L + (Math.log(v) / Math.log(xs.at(-1)!)) * (W - L - 20)
const ly = (a: number) => H - B - a * (H - B - 16)
const shown = computed(() => step.value >= 2 ? run.curve : [])
const path = computed(() => shown.value.map((c, i) => `${i ? 'L' : 'M'}${lx(c.per_class)} ${ly(c.accuracy_mean)}`).join(''))
const hover = ref<number | null>(null)
const pct = (v: number) => `${Math.round(v * 100)}%`
</script>

<template>
  <div class="fs">
    <svg :viewBox="`0 0 ${W} ${H}`" class="chart" role="img" aria-label="Accuracy against number of labelled examples">
      <line v-for="a in [0, 0.25, 0.5, 0.75, 1]" :key="a" :x1="L" :x2="W - 10" :y1="ly(a)" :y2="ly(a)" class="grid" />
      <text v-for="a in [0, 0.5, 1]" :key="`t${a}`" :x="L - 8" :y="ly(a) + 5" class="ax end">{{ pct(a) }}</text>
      <text v-for="x in xs" :key="`x${x}`" :x="lx(x)" :y="H - 34" class="ax mid">{{ x }}</text>
      <text :x="(W + L) / 2" :y="H - 6" class="ax mid">labelled tiles per class</text>
      <line :x1="L" :x2="W - 10" :y1="ly(run.chance_accuracy)" :y2="ly(run.chance_accuracy)" class="chance" />
      <text :x="W - 12" :y="ly(run.chance_accuracy) - 6" class="ax end bad">guessing</text>
      <g class="rv" :class="{ on: step >= 1 }">
        <line :x1="L" :x2="W - 10" :y1="ly(run.zero_shot_best.accuracy)" :y2="ly(run.zero_shot_best.accuracy)" class="zs" />
        <text :x="W - 12" :y="ly(run.zero_shot_best.accuracy) - 6" class="ax end zst">zero-shot, best wording {{ pct(run.zero_shot_best.accuracy) }}</text>
      </g>
      <path :d="path" class="curve" />
      <g v-for="(c, i) in shown" :key="c.per_class" @mouseenter="hover = i" @mouseleave="hover = null">
        <line :x1="lx(c.per_class)" :x2="lx(c.per_class)" :y1="ly(c.accuracy_min)" :y2="ly(c.accuracy_max)" class="err" />
        <circle :cx="lx(c.per_class)" :cy="ly(c.accuracy_mean)" r="6" class="dot" />
        <text v-if="i === 0 || i === 3 || hover === i" :x="lx(c.per_class) + 8" :y="ly(c.accuracy_mean) + 20" class="val">{{ pct(c.accuracy_mean) }}</text>
      </g>
    </svg>
    <div class="side">
      <p class="rv" :class="{ on: step >= 2 }"><strong>{{ run.curve[0].total_labelled }} labelled images</strong> (one per class) beat the best prompt.</p>
      <p class="rv" :class="{ on: step >= 2 }"><strong>{{ run.curve[3].total_labelled }}</strong> reach {{ pct(run.curve[3].accuracy_mean) }}.</p>
      <p class="muted small rv" :class="{ on: step >= 2 }">The model itself is unchanged; only a small layer on top learns.</p>
    </div>
  </div>
</template>

<style scoped>
.fs { display: grid; grid-template-columns: 560px 1fr; gap: 30px; align-items: center; }
.chart { width: 560px; height: 320px; }
.grid { stroke: var(--rule); stroke-width: 1; }
.ax { font: 400 14px var(--font-sans); fill: var(--ink-2); }
.end { text-anchor: end; }
.mid { text-anchor: middle; }
.bad { fill: var(--bad); }
.chance { stroke: var(--bad); stroke-width: 1.5; stroke-dasharray: 5 4; }
.zs { stroke: var(--warn); stroke-width: 2; stroke-dasharray: 8 4; }
.zst { fill: var(--warn); font-weight: 600; }
.curve { fill: none; stroke: var(--accent); stroke-width: 2.5; }
.err { stroke: var(--accent); stroke-width: 1.5; opacity: 0.5; }
.dot { fill: var(--accent); }
.val { font: 600 15px var(--font-sans); fill: var(--accent); }
.side p { font-size: var(--fs-label); margin: 0 0 14px; }
.small { font-size: 15px !important; }
</style>
