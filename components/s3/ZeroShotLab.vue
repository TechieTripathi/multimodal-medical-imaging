<script setup lang="ts">
import { ref, watch } from 'vue'
import { useStep } from '../../composables/useStep'
import run from '../../data/runs/biomedclip_zeroshot_crc.json'

// Artifact 22 — zero-shot: the class names are the only "training". Real BiomedCLIP accuracy on 900
// pathology tiles under four wordings of the same nine prompts. Click a wording to see its prompts. clicks: 4
const { step } = useStep(4)
const thumbs = import.meta.glob('../../data/imaging/thumbs/crc_*.png', { eager: true, import: 'default' }) as Record<string, string>
const src = (p: string) => thumbs[`../../data/imaging/${p}`]
const names = Object.keys(run.variants)
const picked = ref(names[0])
watch(step, s => { if (s >= 1) picked.value = names[s - 1] }, { immediate: true })
const pct = (v: number) => `${Math.round(v * 100)}%`
</script>

<template>
  <div class="zs">
    <div class="tiles">
      <figure v-for="e in run.examples" :key="e.class">
        <img :src="src(e.thumb)" alt="">
        <figcaption>{{ e.class }}</figcaption>
      </figure>
    </div>
    <div class="right">
      <p class="lbl">Accuracy on 900 tiles, nine classes · <span class="cl-key">red line = guessing ({{ pct(run.chance_accuracy) }})</span></p>
      <div class="bars">
        <button v-for="(n, i) in names" :key="n" class="row rv" :class="{ on: step >= i + 1, sel: picked === n }" @click="picked = n">
          <span class="name">{{ n }}</span>
          <span class="track"><span class="fill" :style="{ width: step >= i + 1 ? pct(run.variants[n].accuracy) : '0%' }" /><span class="cl" :style="{ left: pct(run.chance_accuracy) }" /></span>
          <strong>{{ pct(run.variants[n].accuracy) }}</strong>
        </button>
      </div>
      <p v-if="step >= 1" class="prompt">Prompt for one class: <span class="mono">“{{ run.variants[picked].prompts[3] }}”</span></p>
    </div>
  </div>
</template>

<style scoped>
.zs { display: grid; grid-template-columns: 290px 1fr; gap: 36px; align-items: center; }
.tiles { display: grid; grid-template-columns: repeat(3, 1fr); gap: 4px 8px; }
figure { margin: 0; display: flex; flex-direction: column; gap: 3px; }
figure img { width: 100%; height: 72px; object-fit: cover; border-radius: 3px; }
figcaption { font-size: 14px; color: var(--ink-2); line-height: 1.1; height: 31px; overflow: hidden; }
.lbl { font-size: var(--fs-label); color: var(--ink-2); margin: 0 0 14px; }
.bars { position: relative; display: flex; flex-direction: column; gap: 12px; }
.row { display: grid; grid-template-columns: 170px 1fr 52px; gap: 12px; align-items: center; background: none; border: 0; padding: 4px; text-align: left; font: inherit; color: inherit; cursor: pointer; border-radius: 4px; }
.row.sel { background: var(--accent-tint); }
.name { font-size: var(--fs-label); }
.track { height: 22px; background: var(--stage); border-radius: 3px; overflow: hidden; }
.fill { display: block; height: 100%; background: var(--accent); transition: width 0.7s var(--ease); }
.row strong { font-size: var(--fs-label); text-align: right; }
.track { position: relative; }
.cl { position: absolute; top: -3px; bottom: -3px; border-left: 2px dashed var(--bad); }
.cl-key { color: var(--bad); }
.prompt { margin: 16px 0 0; font-size: var(--fs-label); }
.mono { font-size: 16px; }
</style>
