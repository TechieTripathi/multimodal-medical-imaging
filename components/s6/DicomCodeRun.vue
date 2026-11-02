<script setup lang="ts">
import { computed, ref, shallowRef, watch } from 'vue'
import { useStep } from '../../composables/useStep'
import { ANALYSES, type Output, run } from '../../composables/analyses'
import { buffer, pub } from '../../composables/draw'

// Demo E — code that really runs on the real DICOM files, in the slide. The panel shows the exact
// source that the Run button executes. Click 1 runs the first analysis; click 2 switches to the second
// and runs it. Either can be run again at any time. clicks: 2
const props = defineProps<{ tasks: string[] }>()
const { step } = useStep(2)
const task = ref(props.tasks[0])
const out = shallowRef<Output | null>(null)
const busy = ref(false)
const err = ref('')
const ms = ref(0)
// Full code before the first run; once results show, the code shrinks to a scrollable strip
const showCode = ref(false)
async function go(id = task.value) {
  task.value = id
  showCode.value = false
  busy.value = true
  err.value = ''
  out.value = null
  const t = performance.now()
  try { out.value = await run(id, n => pub(`dicom/${n}`)) }
  catch (e) { err.value = String((e as Error).message ?? e) }
  ms.value = Math.round(performance.now() - t)
  busy.value = false
}
watch(step, (s) => {
  if (s === 0) { task.value = props.tasks[0]; out.value = null }
  else go(props.tasks[s - 1] ?? props.tasks.at(-1)!)
}, { immediate: true })

const COLORS = [[255, 196, 0], [0, 229, 255], [255, 90, 200], [120, 255, 120]]
const cv = ref<HTMLCanvasElement>()
watch([out, cv], () => {
  const o = out.value, c = cv.value
  if (!o?.image || !c) return
  const { src, level, width, invert, focus } = o.image
  const W = src.cols, H = src.rows
  const vals = 'frame' in src ? (src.frame(0) as Float32Array) : src.values
  // Crop around the focus mask (padded) so small lesions fill the frame
  let x0 = 0, y0 = 0, x1 = W, y1 = H
  if (focus) {
    let a = W, b = H, cc = 0, d = 0
    for (let i = 0; i < focus.length; i++) if (focus[i]) { const x = i % W, y = (i / W) | 0; a = Math.min(a, x); b = Math.min(b, y); cc = Math.max(cc, x); d = Math.max(d, y) }
    const pad = Math.max(cc - a, d - b) * 1.2 + 10, cx = (a + cc) / 2, cy = (b + d) / 2
    x0 = Math.max(0, Math.round(cx - pad)); y0 = Math.max(0, Math.round(cy - pad)); x1 = Math.min(W, Math.round(cx + pad)); y1 = Math.min(H, Math.round(cy + pad))
  }
  const w = x1 - x0, h = y1 - y0
  const img = buffer(c, w, h)
  const lo = level - width / 2
  for (let y = 0; y < h; y++) for (let x = 0; x < w; x++) {
    const i = (y + y0) * W + x + x0, j = (y * w + x) * 4
    let g = ((vals[i] - lo) / width) * 255
    g = g < 0 ? 0 : g > 255 ? 255 : g
    if (invert) g = 255 - g
    img.data[j] = img.data[j + 1] = img.data[j + 2] = g
    for (const { mask, i: k } of o.outlines) {
      const edge = mask[i] && (!mask[i - 1] || !mask[i + 1] || !mask[i - W] || !mask[i + W])
      if (edge) img.data.set(COLORS[k % 4], j)
    }
  }
  c.getContext('2d')!.putImageData(img, 0, 0)
}, { flush: 'post' })
const maxH = computed(() => Math.max(1, ...(out.value?.hist?.counts.map(v => Math.log1p(v)) ?? [1])))
</script>

<template>
  <div class="cr">
    <div class="bar">
      <button v-for="id in tasks" :key="id" class="chip" :aria-pressed="task === id" @click="task = id; out = null">{{ ANALYSES[id].title }}</button>
      <button class="run" :disabled="busy" @click="go()">{{ busy ? 'Running…' : '▶ Run' }}</button>
    </div>
    <pre class="code" :class="{ small: (out || busy) && !showCode }">{{ ANALYSES[task].code }}</pre>
    <button v-if="out && !showCode" class="more" @click="showCode = true">Show all code</button>
    <div class="out">
      <p v-if="!out && !busy && !err" class="wait">Press Run: this code reads the real DICOM files now</p>
      <p v-if="err" class="err">{{ err }}</p>
      <template v-if="out">
        <canvas v-if="out.image" ref="cv" class="img" />
        <svg v-if="out.hist" viewBox="0 0 260 110" class="hist">
          <rect v-for="(v, i) in out.hist.counts" :key="i" :x="i * 5" :y="96 - (Math.log1p(v) / maxH) * 90" width="4" :height="(Math.log1p(v) / maxH) * 90" class="hb" />
          <text x="0" y="108" class="ax">{{ out.hist.lo }}</text><text x="130" y="108" class="ax mid">HU</text><text x="260" y="108" class="ax end">{{ out.hist.hi }}</text>
        </svg>
        <table class="res">
          <thead v-if="out.header"><tr><th v-for="h in out.header" :key="h">{{ h }}</th></tr></thead>
          <tbody><tr v-for="(r, i) in out.rows" :key="i"><td v-for="(c, j) in r" :key="j"><span v-if="j === 0 && task === 'nodule'" class="sw" :style="{ background: `rgb(${COLORS[i % 4].join(',')})` }" />{{ c }}</td></tr></tbody>
        </table>
        <p v-for="s in out.says" :key="s" class="say">{{ s }} <span class="ms">({{ ms }} ms)</span></p>
      </template>
    </div>
  </div>
</template>

<style scoped>
.cr { display: flex; flex-direction: column; gap: 8px; }
.bar { display: flex; gap: 8px; align-items: center; }
.bar .chip { padding: 5px 12px; font-size: 15px; }
.run { margin-left: auto; font: 600 16px var(--font-sans); background: var(--ok); color: #fff; border: 0; border-radius: 999px; padding: 7px 18px; cursor: pointer; }
.run:disabled { opacity: 0.6; cursor: wait; }
.code { margin: 0; font: 400 13.5px/1.45 var(--font-mono); background: var(--surface); border: 1px solid var(--rule); border-radius: var(--radius); padding: 8px 12px; white-space: pre-wrap; max-height: 230px; overflow: auto; transition: max-height var(--dur) var(--ease); }
.code.small { max-height: 62px; -webkit-mask-image: linear-gradient(#000 55%, transparent); mask-image: linear-gradient(#000 55%, transparent); }
.more { align-self: flex-start; margin-top: -6px; font: 500 13px var(--font-sans); color: var(--accent); background: none; border: 0; padding: 0; cursor: pointer; text-decoration: underline; }
.out { display: flex; gap: 16px; align-items: flex-start; flex-wrap: wrap; min-height: 150px; }
.wait { color: var(--ink-3); font-size: 16px; margin: 20px 0 0; }
.err { color: var(--bad); font-size: 15px; }
.img { width: 170px; height: 170px; border-radius: var(--radius); background: var(--image-mat); image-rendering: auto; }
.hist { width: 230px; height: 110px; }
.hb { fill: var(--accent); }
.ax { font: 400 11px var(--font-sans); fill: var(--ink-2); }
.mid { text-anchor: middle; }
.end { text-anchor: end; }
.res { width: auto; font-size: 15px; }
.res td, .res th { padding: 3px 10px; }
.res tbody tr:nth-child(n) td { line-height: 1.2; }
.sw { display: inline-block; width: 10px; height: 10px; border-radius: 2px; margin-right: 6px; }
.say { flex-basis: 100%; margin: 0; font-size: 17px; font-weight: 600; color: var(--accent); }
.ms { font-weight: 400; font-size: 13px; color: var(--ink-3); }
</style>
