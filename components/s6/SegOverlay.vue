<script setup lang="ts">
import { ref, watch } from 'vue'
import { useStep } from '../../composables/useStep'
import { useBinary } from '../../composables/useBinary'
import { rafThrottle } from '../../composables/raf'
import volUrl from '../../data/imaging/ct/volume_u8.bin?url'
import labUrl from '../../data/imaging/ct/labels_u8.bin?url'
import meta from '../../data/imaging/ct/meta.json'
import seg from '../../data/runs/segmentation.json'

// Artifact 19 — TotalSegmentator's real output on our patient's CT. Clicks add structure groups;
// toggles, opacity and the slice slider work freely. Volumes come from the full-resolution labels. clicks: 3
const { step } = useStep(3)
const vol = useBinary(volUrl)
const lab = useBinary(labUrl)
const [Z, Y, X] = meta.volume.shape_zyx
const groups = seg.totalsegmentator.groups
const COL: Record<string, [number, number, number]> = { Lungs: [90, 140, 255], Heart: [230, 70, 70], Aorta: [255, 160, 40], Airway: [120, 220, 220], Spine: [240, 240, 120], Ribs: [220, 220, 220], Liver: [170, 110, 60] }
const STEPS = [[], ['Lungs'], ['Lungs', 'Heart', 'Aorta', 'Airway'], groups.map(g => g.name)]
const shown = ref<string[]>([])
watch(step, s => { shown.value = [...STEPS[s]] }, { immediate: true })
const toggle = (n: string) => { shown.value = shown.value.includes(n) ? shown.value.filter(x => x !== n) : [...shown.value, n] }
const z = ref(meta.volume.nodule_zyx[0])
const alpha = ref(0.5)
const cv = ref<HTMLCanvasElement>()
function draw() {
  if (!vol.value || !lab.value || !cv.value) return
  const v = new Uint8Array(vol.value), l = new Uint8Array(lab.value)
  const g = cv.value.getContext('2d')!
  const img = g.createImageData(X, Y)
  const on = new Set(groups.filter(gr => shown.value.includes(gr.name)).map(gr => gr.id))
  const byId = Object.fromEntries(groups.map(gr => [gr.id, COL[gr.name]]))
  for (let i = 0; i < X * Y; i++) {
    const o = z.value * X * Y + i
    let r = v[o], gg = v[o], b = v[o]
    const id = l[o]
    if (id && on.has(id)) { const c = byId[id]; r = r * (1 - alpha.value) + c[0] * alpha.value; gg = gg * (1 - alpha.value) + c[1] * alpha.value; b = b * (1 - alpha.value) + c[2] * alpha.value }
    img.data.set([r, gg, b, 255], i * 4)
  }
  g.putImageData(img, 0, 0)
}
watch([vol, lab, cv, shown, z, alpha], rafThrottle(draw), { flush: 'post' })
</script>

<template>
  <div class="so">
    <div class="pic">
      <canvas ref="cv" :width="X" :height="Y" />
      <label class="ctl">Slice <input v-model.number="z" type="range" min="0" :max="Z - 1" @keydown.stop></label>
      <label class="ctl">Opacity <input v-model.number="alpha" type="range" min="0" max="1" step="0.05" @keydown.stop></label>
    </div>
    <div class="side">
      <button v-for="g in groups" :key="g.name" class="item" :class="{ off: !shown.includes(g.name) }" @click="toggle(g.name)">
        <span class="sw" :style="{ background: `rgb(${COL[g.name].join(',')})` }" />
        <span class="n">{{ g.name }}</span>
        <span class="v">{{ g.volume_ml >= 1000 ? `${(g.volume_ml / 1000).toFixed(1)} L` : `${Math.round(g.volume_ml)} ml` }}</span>
      </button>
      <p class="note">117 structures found automatically; grouped here into seven</p>
    </div>
  </div>
</template>

<style scoped>
.so { display: grid; grid-template-columns: 340px 1fr; gap: 36px; align-items: center; }
.pic canvas { width: 340px; height: 340px; border-radius: var(--radius); display: block; background: var(--image-mat); }
.pic .ctl { margin-top: 6px; font-size: 16px; }
.pic .ctl input { width: 230px; }
.side { display: flex; flex-direction: column; gap: 6px; }
.item { display: grid; grid-template-columns: 20px 1fr auto; gap: 12px; align-items: center; background: none; border: 0; border-bottom: 1px solid var(--rule); padding: 6px 4px; font: inherit; color: inherit; cursor: pointer; text-align: left; transition: opacity var(--dur) var(--ease); }
.item.off { opacity: 0.35; }
.sw { width: 18px; height: 18px; border-radius: 4px; }
.n { font-size: var(--fs-label); }
.v { font: 500 var(--fs-label) var(--font-mono); }
.note { font-size: 15px; color: var(--ink-2); margin: 8px 0 0; }
</style>
