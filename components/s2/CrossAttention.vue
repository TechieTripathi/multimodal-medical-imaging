<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { useStep } from '../../composables/useStep'
import ct from '../../data/imaging/ct/slice_lung.png'

// Artifact 8 — cross-attention as "each word looks for the parts of the image it is about".
// Teaching picture: the regions are real anatomy (TotalSegmentator lungs, the readers' nodule outline),
// but the word-to-region weights are drawn by hand. clicks: 4
const { step } = useStep(4)
const masks = import.meta.glob('../../data/imaging/attn/*.png', { eager: true, import: 'default' }) as Record<string, string>
const m = (n: string) => masks[`../../data/imaging/attn/${n}.png`]
const WORDS: { w: string, looks: [string, number][] }[] = [
  { w: 'Solid', looks: [['nodule', 0.9]] },
  { w: 'nodule', looks: [['nodule', 1]] },
  { w: 'in', looks: [['left_lung', 0.15], ['right_lung', 0.15]] },
  { w: 'the', looks: [['left_lung', 0.12], ['right_lung', 0.12]] },
  { w: 'left', looks: [['left_lung', 0.75]] },
  { w: 'lower', looks: [['left_lower_lobe', 0.8]] },
  { w: 'lobe', looks: [['left_lower_lobe', 0.6]] },
  { w: 'with', looks: [['left_lung', 0.12], ['right_lung', 0.12]] },
  { w: 'spiculated', looks: [['nodule_edge', 1]] },
  { w: 'margin', looks: [['nodule_edge', 0.9]] },
]
const order = [1, 4, 5, 8]
const picked = ref(1)
watch(step, s => { picked.value = order[Math.max(0, s - 1)] ?? 1 }, { immediate: true })
const looks = computed(() => step.value === 0 ? [] : WORDS[picked.value].looks)
</script>

<template>
  <div class="xa">
    <div class="img">
      <img :src="ct" alt="CT slice">
      <TransitionGroup name="heat">
        <span v-for="[name, w] in looks" :key="`${picked}-${name}`" class="heat" :style="{ maskImage: `url(${m(name)})`, WebkitMaskImage: `url(${m(name)})`, opacity: w * 0.8 }" />
      </TransitionGroup>
    </div>
    <div class="side">
      <p class="lbl">A sentence from the report</p>
      <p class="sentence">
        <button v-for="(x, i) in WORDS" :key="x.w" class="word" :class="{ on: step > 0 && picked === i }" @click="picked = i">{{ x.w }}</button>
      </p>
      <p class="hint rv" :class="{ on: step >= 1 }">Each word gets its own map of where to look</p>
    </div>
  </div>
</template>

<style scoped>
.xa { display: grid; grid-template-columns: 330px 1fr; gap: 40px; align-items: center; }
.img { position: relative; width: 330px; height: 330px; border-radius: var(--radius); overflow: hidden; background: var(--image-mat); }
.img img { width: 100%; height: 100%; display: block; }
.heat { position: absolute; inset: 0; background: #ffc400; -webkit-mask-size: 100% 100%; mask-size: 100% 100%; transition: opacity var(--dur) var(--ease); }
.heat-enter-from, .heat-leave-to { opacity: 0 !important; }
.heat-enter-active, .heat-leave-active { transition: opacity var(--dur) var(--ease); }
.lbl { font-size: var(--fs-label); color: var(--ink-2); margin: 0 0 10px; }
.sentence { display: flex; flex-wrap: wrap; gap: 6px; margin: 0; }
.word { font: 500 var(--fs-body) var(--font-sans); border: 1px solid var(--rule); background: var(--surface); padding: 6px 10px; border-radius: var(--radius-sm); cursor: pointer; color: var(--ink); transition: background var(--dur) var(--ease); }
.word.on { background: #ffc400; border-color: #e0ac00; }
.hint { margin-top: 20px; font-size: var(--fs-label); color: var(--ink-2); }
</style>
