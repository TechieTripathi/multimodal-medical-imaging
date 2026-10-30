<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { useStep } from '../../composables/useStep'
import run from '../../data/runs/biomedclip_cxr_roc.json'

// Artifact 10 — real zero-shot scores for cardiomegaly vs normal on IU chest X-rays. Drag the threshold:
// the confusion counts, sensitivity, specificity, precision and the point on the ROC curve move together. clicks: 3
const { step } = useStep(3)
const S = run.scores, Y = run.labels
const lo = Math.min(...S), hi = Math.max(...S)
const thr = ref(lo + (hi - lo) * 0.5)
const preset = (p: 'screen' | 'confirm') => {
  // screening: the lowest threshold that still catches 95% of positives; confirmation: specificity 95%
  const pos = S.filter((_, i) => Y[i] === 1).sort((a, b) => a - b)
  const neg = S.filter((_, i) => Y[i] === 0).sort((a, b) => a - b)
  thr.value = p === 'screen' ? pos[Math.floor(pos.length * 0.05)] : neg[Math.floor(neg.length * 0.95)]
}
const m = computed(() => {
  let tp = 0, fp = 0, tn = 0, fn = 0
  S.forEach((s, i) => { const p = s >= thr.value; if (Y[i]) p ? tp++ : fn++; else p ? fp++ : tn++ })
  return { tp, fp, tn, fn, sens: tp / (tp + fn), spec: tn / (tn + fp), prec: tp + fp ? tp / (tp + fp) : 0 }
})
const roc = (() => {
  const ts = [...new Set(S)].sort((a, b) => b - a)
  const P = Y.filter(y => y).length, N = Y.length - P
  return [[0, 0], ...ts.map(t => { let tp = 0, fp = 0; S.forEach((s, i) => { if (s >= t) Y[i] ? tp++ : fp++ }); return [fp / N, tp / P] })]
})()
const W = 860, X = (s: number) => 10 + ((s - lo) / (hi - lo)) * (W - 20)
// Deterministic jitter so dots do not overlap
const jit = (i: number) => ((i * 37) % 23) / 23
const pct = (v: number) => `${Math.round(v * 100)}%`
watch(step, (s) => { if (s === 1) thr.value = lo + (hi - lo) * 0.5 })
</script>

<template>
  <div class="te">
    <svg :viewBox="`0 0 ${W} 120`" class="strip">
      <text x="10" y="14" class="k">Enlarged heart (from the report) · {{ run.n_positive }}</text>
      <text x="10" y="116" class="k">Normal · {{ run.n_negative }}</text>
      <circle v-for="(s, i) in S" :key="i" :cx="X(s)" :cy="Y[i] ? 24 + jit(i) * 34 : 68 + jit(i) * 34" r="4" :class="Y[i] ? 'pos' : 'neg'" :opacity="step >= 1 && (s >= thr) ? 1 : step >= 1 ? 0.35 : 0.9" />
      <g v-if="step >= 1"><line :x1="X(thr)" :x2="X(thr)" y1="18" y2="104" class="thr" /><text :x="X(thr) + 6" y="112" class="k thrk">called “enlarged” →</text></g>
    </svg>
    <div v-if="step >= 1" class="ctl-row">
      <label class="ctl">Threshold <input v-model.number="thr" type="range" :min="lo" :max="hi" :step="(hi - lo) / 200" @keydown.stop></label>
      <button class="chip" @click="preset('screen')">Screening</button>
      <button class="chip" @click="preset('confirm')">Confirmation</button>
    </div>
    <div class="bottom">
      <div class="cm rv" :class="{ on: step >= 1 }">
        <span /><span class="h">Called enlarged</span><span class="h">Called normal</span>
        <span class="h r">Enlarged</span><span class="c ok">{{ m.tp }}</span><span class="c bad">{{ m.fn }}<small>missed</small></span>
        <span class="h r">Normal</span><span class="c bad">{{ m.fp }}<small>false alarm</small></span><span class="c ok">{{ m.tn }}</span>
      </div>
      <div class="mets rv" :class="{ on: step >= 2 }">
        <p><strong>{{ pct(m.sens) }}</strong> sensitivity <span>of enlarged hearts, found</span></p>
        <p><strong>{{ pct(m.spec) }}</strong> specificity <span>of normal hearts, cleared</span></p>
        <p><strong>{{ pct(m.prec) }}</strong> precision <span>of alarms, correct</span></p>
      </div>
      <div class="roc rv" :class="{ on: step >= 3 }">
        <svg viewBox="0 0 150 150">
          <rect x="0" y="0" width="150" height="150" class="rb" />
          <line x1="0" y1="150" x2="150" y2="0" class="diag" />
          <polyline :points="roc.map(([x, y]) => `${x * 150},${150 - y * 150}`).join(' ')" class="rc" />
          <circle :cx="(1 - m.spec) * 150" :cy="150 - m.sens * 150" r="6" class="rp" />
        </svg>
        <p>ROC curve · AUROC <strong>{{ run.auroc.toFixed(2) }}</strong></p>
      </div>
    </div>
  </div>
</template>

<style scoped>
.te { display: flex; flex-direction: column; gap: 8px; }
.strip { width: 100%; height: 118px; }
.k { font: 400 14px var(--font-sans); fill: var(--ink-2); }
.thrk { fill: var(--ink); font-weight: 600; }
.pos { fill: var(--warn); }
.neg { fill: var(--neutral); }
.thr { stroke: var(--ink); stroke-width: 2; }
.ctl-row { display: flex; gap: 10px; align-items: center; }
.ctl-row .chip { padding: 6px 12px; }
.bottom { display: grid; grid-template-columns: 1.1fr 1fr 190px; gap: 22px; align-items: center; }
.cm { display: grid; grid-template-columns: 90px 1fr 1fr; gap: 4px; font-size: 15px; }
.h { color: var(--ink-2); text-align: center; }
.h.r { text-align: right; padding-right: 6px; align-self: center; }
.c { font: 600 var(--fs-body) var(--font-sans); text-align: center; padding: 6px; border-radius: 4px; display: flex; flex-direction: column; line-height: 1.1; }
.c small { font-size: 13px; font-weight: 400; }
.c.ok { background: var(--ok-tint); color: var(--ok); }
.c.bad { background: var(--bad-tint); color: var(--bad); }
.mets p { margin: 0 0 6px; font-size: var(--fs-label); }
.mets strong { font-size: var(--fs-body); color: var(--accent); display: inline-block; min-width: 54px; }
.mets span { color: var(--ink-2); font-size: 15px; display: block; margin-left: 58px; margin-top: -4px; }
.roc svg { width: 150px; height: 150px; }
.rb { fill: var(--surface); stroke: var(--rule); }
.diag { stroke: var(--rule-strong); stroke-dasharray: 4 3; }
.rc { fill: none; stroke: var(--accent); stroke-width: 2; }
.rp { fill: #ffc400; stroke: var(--ink); }
.roc p { margin: 2px 0 0; font-size: 15px; }
</style>
