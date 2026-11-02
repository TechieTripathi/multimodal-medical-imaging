<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { useStep } from '../../composables/useStep'
import { useBinary } from '../../composables/useBinary'
import { rafThrottle } from '../../composables/raf'
import huUrl from '../../data/imaging/ct/slice_hu.bin?url'

// Artifact 14 — CT windowing on the real Hounsfield values of our patient's slice. The window
// (level = centre, width = range) decides which HU become black-to-white; everything else is clipped.
// Clicks step through presets; the sliders and preset buttons work freely. clicks: 3
const { step } = useStep(3)
const buf = useBinary(huUrl)
const PRESETS = [
  { name: 'Everything', level: 1000, width: 4000 },
  { name: 'Lung', level: -600, width: 1500 },
  { name: 'Soft tissue', level: 40, width: 400 },
  { name: 'Bone', level: 400, width: 1800 },
]
const level = ref(PRESETS[0].level)
const width = ref(PRESETS[0].width)
const set = (p: typeof PRESETS[number]) => { level.value = p.level; width.value = p.width }
watch(step, s => set(PRESETS[s]), { immediate: true })
const cv = ref<HTMLCanvasElement>()
const LO = -1100, HI = 1700, BIN = 25
const hist = computed(() => {
  if (!buf.value) return []
  const hu = new Int16Array(buf.value)
  const h = new Array(Math.ceil((HI - LO) / BIN)).fill(0)
  for (const v of hu) { const b = Math.floor((v - LO) / BIN); if (b >= 0 && b < h.length) h[b]++ }
  return h.map(c => Math.log1p(c))
})
const maxH = computed(() => Math.max(...hist.value, 1))
function draw() {
  if (!buf.value || !cv.value) return
  const hu = new Int16Array(buf.value)
  const g = cv.value.getContext('2d')!
  const img = g.createImageData(512, 512)
  const lo = level.value - width.value / 2
  for (let i = 0; i < hu.length; i++) {
    const v = Math.max(0, Math.min(255, ((hu[i] - lo) / width.value) * 255))
    img.data[i * 4] = img.data[i * 4 + 1] = img.data[i * 4 + 2] = v
    img.data[i * 4 + 3] = 255
  }
  g.putImageData(img, 0, 0)
}
watch([buf, cv, level, width], rafThrottle(draw), { flush: 'post' })
const HW = 420
const hx = (hu: number) => ((hu - LO) / (HI - LO)) * HW
</script>

<template>
  <div class="ws">
    <canvas ref="cv" width="512" height="512" class="ct" />
    <div class="side">
      <div class="presets">
        <button v-for="p in PRESETS" :key="p.name" class="chip" :aria-pressed="level === p.level && width === p.width" @click="set(p)">{{ p.name }}</button>
      </div>
      <svg :viewBox="`0 0 ${HW} 150`" class="hist" role="img" aria-label="Histogram of Hounsfield units with the current window">
        <defs><linearGradient id="ramp"><stop offset="0" stop-color="#000" /><stop offset="1" stop-color="#fff" /></linearGradient></defs>
        <rect :x="Math.max(0, hx(level - width / 2))" y="0" :width="Math.max(2, Math.min(HW, hx(level + width / 2)) - Math.max(0, hx(level - width / 2)))" height="112" class="win" />
        <rect v-for="(c, i) in hist" :key="i" :x="(i / hist.length) * HW" :y="112 - (c / maxH) * 100" :width="HW / hist.length - 1" :height="(c / maxH) * 100" class="bar" />
        <rect :x="Math.max(0, hx(level - width / 2))" y="116" :width="Math.max(2, Math.min(HW, hx(level + width / 2)) - Math.max(0, hx(level - width / 2)))" height="10" fill="url(#ramp)" stroke="var(--ink-3)" />
        <g v-for="t in [-1000, -500, 0, 500, 1000, 1500]" :key="t"><text :x="hx(t)" y="146" class="ax">{{ t }}</text></g>
        <text v-for="[t, l] in [[-1000, 'air'], [-700, 'lung'], [40, 'soft tissue'], [700, 'bone']]" :key="l" :x="hx(Number(t))" y="12" class="lbl">{{ l }}</text>
      </svg>
      <label class="ctl">Level (centre) <input v-model.number="level" type="range" min="-1000" max="1200" step="10" @keydown.stop><span class="mono">{{ level }}</span></label>
      <label class="ctl">Width (range) <input v-model.number="width" type="range" min="50" max="4000" step="10" @keydown.stop><span class="mono">{{ width }}</span></label>
    </div>
  </div>
</template>

<style scoped>
.ws { display: grid; grid-template-columns: 350px 1fr; gap: 32px; align-items: center; }
.ct { width: 350px; height: 350px; border-radius: var(--radius); display: block; }
.side { display: flex; flex-direction: column; gap: 12px; }
.presets { display: flex; gap: 6px; flex-wrap: wrap; }
.presets .chip { padding: 6px 12px; }
.hist { width: 100%; height: 150px; }
.bar { fill: var(--ink-3); }
.win { fill: var(--accent-tint); stroke: var(--accent); stroke-width: 1.5; }
.ax { font: 400 13px var(--font-sans); fill: var(--ink-2); text-anchor: middle; }
.lbl { font: 600 13px var(--font-sans); fill: var(--accent); text-anchor: middle; }
.ctl input[type='range'] { width: 220px; }
.ctl .mono { font-size: 16px; color: var(--ink); min-width: 48px; }
</style>
