<script setup lang="ts">
import { useStep } from '../../composables/useStep'
import xray from '../../data/imaging/gallery/xray.png'
import ct from '../../data/imaging/gallery/ct.png'
import mri from '../../data/imaging/gallery/mri.png'
import path from '../../data/imaging/gallery/pathology.png'

// Slide 13 — two encoders, one shared space. Before training, words land anywhere; after training,
// each description lands next to the images it describes. clicks: 2
const { step } = useStep(2)
const items = [
  { img: xray, text: 'a chest X-ray', at: [70, 70], before: [330, 230] },
  { img: ct, text: 'a CT slice of the chest', at: [120, 210], before: [300, 60] },
  { img: mri, text: 'a brain MRI', at: [300, 90], before: [90, 240] },
  { img: path, text: 'stained tissue', at: [330, 220], before: [180, 40] },
]
const textPos = (i: number) => {
  const it = items[i]
  const p = step.value >= 2 ? [it.at[0] + 18, it.at[1] + 44] : it.before
  return { left: `${p[0]}px`, top: `${p[1]}px` }
}
</script>

<template>
  <div class="ss">
    <div class="enc">Image encoder<span>pictures → numbers</span></div>
    <div class="space">
      <span class="axis">shared space</span>
      <img v-for="it in items" :key="it.text" :src="it.img" alt="" class="pt" :style="{ left: `${it.at[0]}px`, top: `${it.at[1]}px` }">
      <span v-for="(it, i) in items" :key="`t${i}`" class="word rv" :class="{ on: step >= 1 }" :style="textPos(i)">{{ it.text }}</span>
    </div>
    <div class="enc">Text encoder<span>words → numbers</span></div>
  </div>
</template>

<style scoped>
.ss { display: grid; grid-template-columns: 150px 440px 150px; gap: 24px; align-items: center; justify-content: center; }
.enc { border: 2px solid var(--accent); border-radius: var(--radius); padding: 16px; font-weight: 600; color: var(--accent); display: flex; flex-direction: column; gap: 4px; font-size: var(--fs-label); }
.enc span { font-weight: 400; color: var(--ink-2); font-size: 15px; }
.space { position: relative; width: 440px; height: 320px; border: 1px dashed var(--rule-strong); border-radius: var(--radius); background: var(--surface); }
.axis { position: absolute; right: 10px; bottom: 8px; font-size: var(--fs-micro); color: var(--ink-3); }
.pt { position: absolute; width: 56px; height: 56px; object-fit: cover; border-radius: 4px; background: var(--image-mat); }
.word { position: absolute; font-size: 15px; font-weight: 500; background: var(--accent-tint); color: var(--ink); padding: 3px 8px; border-radius: 999px; white-space: nowrap; transition: left 0.9s var(--ease), top 0.9s var(--ease), opacity var(--dur) var(--ease); }
</style>
