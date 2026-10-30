<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { useStep } from '../../composables/useStep'
import { unpackBits } from '../../composables/decode'
import soft from '../../data/imaging/ct/slice_soft.png'
import crops from '../../data/imaging/ct/reader_crops.json'
import seg from '../../data/runs/segmentation.json'

// Slide 26 — MedSAM in one picture: draw a box, get an outline. Real MedSAM output on our patient. clicks: 2
const { step } = useStep(2)
const [x0, y0, x1, y1] = seg.medsam.box_xyxy
const box = computed(() => ({ left: `${x0 / 5.12}%`, top: `${y0 / 5.12}%`, width: `${(x1 - x0) / 5.12}%`, height: `${(y1 - y0) / 5.12}%` }))
const N = crops.box.size
const cv = ref<HTMLCanvasElement>()
onMounted(() => {
  const g = cv.value!.getContext('2d')!
  const m = unpackBits(seg.medsam.mask_crop, N * N)
  const img = g.createImageData(N, N)
  for (let i = 0; i < N * N; i++) if (m[i]) img.data.set([40, 200, 120, 150], i * 4)
  g.putImageData(img, 0, 0)
})
// Zoom 2.4× on the nodule so the outline is visible from the back of the room
const Z = 2.4
const cx = (x0 + x1) / 2 / 512, cy = (y0 + y1) / 2 / 512
const zoomStyle = { width: `${340 * Z}px`, height: `${340 * Z}px`, left: `${170 - cx * 340 * Z}px`, top: `${170 - cy * 340 * Z}px` }
const maskStyle = { left: `${crops.box.x0 / 5.12}%`, top: `${crops.box.y0 / 5.12}%`, width: `${N / 5.12}%`, height: `${N / 5.12}%` }
</script>

<template>
  <div class="ms">
    <div class="pic">
      <div class="zoom" :style="zoomStyle">
        <img :src="soft" alt="CT slice, soft-tissue window">
        <span class="box rv" :class="{ on: step >= 1 }" :style="box" />
        <canvas ref="cv" :width="N" :height="N" class="mask rv" :class="{ on: step >= 2 }" :style="maskStyle" />
      </div>
    </div>
    <div class="side">
      <p class="st" :class="{ cur: step === 0 }">1 · An image</p>
      <p class="st rv" :class="{ on: step >= 1, cur: step === 1 }">2 · A person draws a rough box</p>
      <p class="st rv" :class="{ on: step >= 2, cur: step === 2 }">3 · MedSAM outlines what is inside, in {{ seg.medsam.inference_s }} s</p>
      <p class="fact">Trained on 1.57 million image–outline pairs from 10 kinds of scan</p>
    </div>
  </div>
</template>

<style scoped>
.ms { display: grid; grid-template-columns: 340px 1fr; gap: 40px; align-items: center; }
.pic { position: relative; width: 340px; height: 340px; border-radius: var(--radius); overflow: hidden; background: var(--image-mat); }
.zoom { position: absolute; }
.zoom img { width: 100%; height: 100%; display: block; }
.box { position: absolute; border: 1px dashed #ffc400; }
.mask { position: absolute; image-rendering: pixelated; }
.st { font-size: var(--fs-body); margin: 0 0 14px; color: var(--ink-2); }
.st.cur { color: var(--ink); font-weight: 600; }
.fact { margin-top: 26px; font-size: var(--fs-label); color: var(--ink-2); border-top: 1px solid var(--rule); padding-top: 12px; }
</style>
