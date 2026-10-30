<script setup lang="ts">
import { useStep } from '../../composables/useStep'
import ct from '../../data/imaging/ct/slice_lung.png'
import meta from '../../data/imaging/ct/meta.json'
import ImageMat from '../ui/ImageMat.vue'
import Status from '../ui/Status.vue'

// Slide 5 — what an image-only system can and cannot know. clicks: 4
const { step } = useStep(4)
const [cy, cx] = meta.nodule_center_yx
const unknowns = ['Is it new, or unchanged for years?', 'Does the patient have symptoms?', 'Smoking or other risk factors?', 'Why was the scan done?']
</script>

<template>
  <div class="iol">
    <ImageMat :src="ct" alt="CT slice with the nodule marked" :h="330">
      <span class="box" :style="{ left: `${cx / 5.12}%`, top: `${cy / 5.12}%` }" />
      <span class="tag" :style="{ right: `${100 - cx / 5.12 + 10}%`, top: `${cy / 5.12}%` }">nodule, ~3 cm</span>
    </ImageMat>
    <div class="side">
      <p class="can"><Status state="ok" compact /> The image shows <strong>where</strong> and <strong>how big</strong></p>
      <p class="hd">It cannot tell us</p>
      <p v-for="(u, i) in unknowns" :key="u" class="q rv" :class="{ on: step >= i + 1 }"><Status state="neutral" compact /> {{ u }}</p>
    </div>
  </div>
</template>

<style scoped>
.iol { display: grid; grid-template-columns: 330px 1fr; gap: 40px; align-items: center; }
.box { position: absolute; width: 17%; aspect-ratio: 1; border: 2px solid #ffc400; transform: translate(-50%, -50%); }
.tag { position: absolute; transform: translateY(-50%); color: #ffc400; background: rgba(11, 13, 16, 0.75); padding: 2px 6px; border-radius: 3px; font-size: var(--fs-micro); font-weight: 600; white-space: nowrap; }
.side p { margin: 0 0 14px; font-size: var(--fs-body); display: flex; gap: 10px; align-items: center; }
.hd { color: var(--ink-2); font-size: var(--fs-label) !important; margin-top: 18px !important; }
</style>
