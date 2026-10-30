<script setup lang="ts">
import { computed } from 'vue'
import { useStep } from '../../composables/useStep'
import cells from '../../data/notebook/cells.json'
import run from '../../data/runs/notebook.json'

// Artifact 24 — a cell of the companion notebook, exactly as it ran. Only the chosen lines are shown
// (gaps marked "…"); each click highlights the next group of lines; the last click shows the cell's
// real output or figure. clicks: steps.length
const props = defineProps<{ cell: keyof typeof cells, lines: number[], steps: number[][], outLines?: number, figure?: boolean }>()
const { step } = useStep(props.steps.length)
const figs = import.meta.glob('../../data/notebook/*.png', { eager: true, import: 'default' }) as Record<string, string>
const c = cells[props.cell]
const src = c.code.split('\n')
const shown = computed(() => {
  const out: { n: number, text: string, gap?: boolean }[] = []
  props.lines.forEach((n, i) => {
    if (i > 0 && n !== props.lines[i - 1] + 1) out.push({ n: -i, text: '…', gap: true })
    out.push({ n, text: src[n - 1] })
  })
  return out
})
const hot = computed(() => step.value >= 1 && step.value <= props.steps.length ? props.steps[step.value - 1] : [])
const showOut = computed(() => step.value >= props.steps.length)
// Long outputs keep their first lines and their last line
const outAll = c.output.split('\n')
const n = props.outLines ?? 6
const output = outAll.length > n ? [...outAll.slice(0, n - 1), '…', outAll.at(-1)].join('\n') : c.output
const fig = c.figures[0] ? figs[`../../data/notebook/${c.figures[0]}`] : null
</script>

<template>
  <div class="nc" :class="{ withfig: figure && fig }">
    <div class="code">
      <p class="hd">notebook cell {{ props.cell }}</p>
      <div class="pre"><span v-for="l in shown" :key="l.n" class="ln" :class="{ hot: hot.includes(l.n), gap: l.gap, dim: hot.length && !hot.includes(l.n) && !l.gap }"><span class="no">{{ l.gap ? '' : l.n }}</span>{{ l.text }}</span></div>
    </div>
    <div class="out rv" :class="{ on: showOut }">
      <p class="hd">output · run {{ run.run_date }} on {{ run.device }}</p>
      <img v-if="figure && fig" :src="fig" alt="Figure produced by this notebook cell" class="fig">
      <pre v-else class="txt">{{ output }}</pre>
    </div>
  </div>
</template>

<style scoped>
.nc { display: flex; flex-direction: column; gap: 12px; }
.nc.withfig { display: grid; grid-template-columns: 1.15fr 1fr; align-items: start; }
.hd { font-size: 14px; color: var(--ink-3); margin: 0 0 4px; }
pre, .pre { margin: 0; font: 400 17px/1.45 var(--font-mono); background: var(--surface); border: 1px solid var(--rule); border-radius: var(--radius); padding: 10px 12px; white-space: pre-wrap; word-break: break-word; }
.ln { display: block; white-space: pre-wrap; padding-left: 2.6em; text-indent: -2.6em; border-radius: 3px; transition: background var(--dur) var(--ease), opacity var(--dur) var(--ease); }
.no { display: inline-block; width: 2.2em; text-indent: 0; color: var(--ink-3); font-size: 14px; }
.hot { background: #fff3c4; }
.dim { opacity: 0.45; }
.gap { color: var(--ink-3); }
.txt { background: var(--night); color: #e8eaed; font-size: 16px; }
.fig { width: 100%; border: 1px solid var(--rule); border-radius: var(--radius); background: #fff; }
</style>
