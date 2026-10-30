<script setup lang="ts">
import { computed } from 'vue'
import { useStep } from '../../composables/useStep'
import xray from '../../data/imaging/dx/dx1.png'
import x224 from '../../data/imaging/dx/dx1_224.png'
import meta from '../../data/imaging/dx/meta.json'

// Artifact 3 — an image is a grid of numbers. Zoom from the X-ray into a 6×6 block of the real stored
// values, then show how a vision transformer cuts the image into 16×16-pixel patches. clicks: 3
const { step } = useStep(3)
const im = meta.images[0]
const region = im.region
const vals = region.values.slice(0, 6).map(r => r.slice(0, 6))
const [lo, hi] = im.display_window
const grey = (v: number) => Math.round(Math.min(1, Math.max(0, (v - lo) / (hi - lo))) * 255)
const markerStyle = computed(() => ({ left: `${(region.col0 / im.cols) * 100}%`, top: `${(region.row0 / im.rows) * 100}%` }))
const patches = [[3, 4], [3, 5], [5, 3], [5, 10], [7, 7], [9, 4], [11, 9]]
</script>

<template>
  <div class="p2n">
    <div class="xr">
      <img :src="xray" alt="Chest X-ray">
      <span class="marker" :style="markerStyle" />
      <p class="cap">{{ im.rows }} × {{ im.cols }} pixels, values {{ im.stored_min }}–{{ im.stored_max }}</p>
    </div>
    <div class="panel">
      <div v-if="step < 3" class="grid rv" :class="{ on: step >= 1 }">
        <template v-for="(row, r) in vals" :key="r">
          <span v-for="(v, c) in row" :key="c" class="cell" :style="{ background: `rgb(${grey(v)},${grey(v)},${grey(v)})`, color: grey(v) > 140 ? '#111' : '#fff' }">
            <span class="num" :class="{ show: step >= 2 }">{{ v }}</span>
          </span>
        </template>
      </div>
      <div v-else class="vit rv on">
        <div class="cut">
          <img :src="x224" alt="X-ray resized to 224 × 224">
          <svg viewBox="0 0 224 224" class="lines" aria-hidden="true">
            <path v-for="i in 13" :key="`v${i}`" :d="`M${i * 16} 0V224`" /><path v-for="i in 13" :key="`h${i}`" :d="`M0 ${i * 16}H224`" />
          </svg>
        </div>
        <div class="row">
          <span v-for="([r, c], i) in patches" :key="i" class="patch" :style="{ backgroundImage: `url(${x224})`, backgroundPosition: `-${c * 40}px -${r * 40}px` }" />
          <span class="more">… 196 patches</span>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.p2n { display: grid; grid-template-columns: 320px 1fr; gap: 40px; align-items: center; }
.xr { position: relative; }
.xr img { width: 320px; height: 320px; display: block; border-radius: var(--radius); }
.marker { position: absolute; width: 14px; height: 14px; border: 2px solid #ffc400; transform: translate(-3px, -3px); }
.cap { font-size: var(--fs-micro); color: var(--ink-2); margin: 6px 0 0; }
.panel { display: flex; justify-content: center; }
.grid { display: grid; grid-template-columns: repeat(6, 62px); grid-auto-rows: 54px; gap: 2px; background: #ffc400; padding: 2px; border-radius: 3px; }
.cell { display: grid; place-items: center; }
.num { font: 500 18px var(--font-mono); opacity: 0; transition: opacity var(--dur) var(--ease); }
.num.show { opacity: 1; }
.vit { display: flex; flex-direction: column; gap: 20px; align-items: center; }
.cut { position: relative; width: 224px; height: 224px; }
.cut img { width: 224px; height: 224px; display: block; }
.lines { position: absolute; inset: 0; }
.lines path { stroke: #ffc400; stroke-width: 0.6; fill: none; }
.row { display: flex; gap: 8px; align-items: center; }
.patch { width: 40px; height: 40px; background-size: 560px 560px; border: 1px solid var(--rule-strong); }
.more { font-size: var(--fs-label); color: var(--ink-2); margin-left: 6px; }
</style>
