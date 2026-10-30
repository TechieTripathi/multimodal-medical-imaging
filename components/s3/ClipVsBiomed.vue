<script setup lang="ts">
import { useStep } from '../../composables/useStep'
import run from '../../data/runs/clip_vs_biomedclip_crc.json'

// Slide 24 — same recipe, different data. Facts from the CLIP and BiomedCLIP papers, then our real
// comparison of the two on the same 900 pathology tiles and four prompt wordings. clicks: 2
const { step } = useStep(2)
const names = Object.keys(run.clip_accuracy)
const pct = (v: number) => `${Math.round(v * 100)}%`
</script>

<template>
  <div class="cb">
    <div class="cards">
      <div class="card">
        <h3>CLIP (2021)</h3>
        <p class="big">400 million</p>
        <p>image–text pairs from the internet: photos and their captions</p>
      </div>
      <div class="card rv" :class="{ on: step >= 1 }">
        <h3>BiomedCLIP (2023–25)</h3>
        <p class="big">15 million</p>
        <p>figures and captions from 4.4 million biomedical articles</p>
      </div>
    </div>
    <div class="cmp rv" :class="{ on: step >= 2 }">
      <p class="lbl">Our test: 900 pathology tiles, zero-shot accuracy</p>
      <div v-for="n in names" :key="n" class="row">
        <span class="name">{{ n }}</span>
        <span class="pair">
          <span class="bar clip" :style="{ width: pct(run.clip_accuracy[n]) }"><em>{{ pct(run.clip_accuracy[n]) }}</em></span>
          <span class="bar bio" :style="{ width: pct(run.biomedclip_accuracy[n]) }"><em>{{ pct(run.biomedclip_accuracy[n]) }}</em></span>
        </span>
      </div>
      <p class="key"><span class="sw clip" />CLIP ViT-L/14 <span class="sw bio" />BiomedCLIP</p>
    </div>
  </div>
</template>

<style scoped>
.cb { display: grid; grid-template-columns: 300px 1fr; gap: 36px; align-items: center; }
.cards { display: flex; flex-direction: column; gap: 14px; }
.card p { margin: 0; font-size: var(--fs-label); }
.big { font-size: 34px !important; font-weight: 600; color: var(--accent); line-height: 1.1; }
.lbl { font-size: var(--fs-label); color: var(--ink-2); margin: 0 0 12px; }
.row { display: grid; grid-template-columns: 160px 1fr; gap: 12px; align-items: center; margin-bottom: 10px; }
.name { font-size: 16px; }
.pair { display: flex; flex-direction: column; gap: 3px; }
.bar { height: 22px; border-radius: 3px; display: flex; align-items: center; justify-content: flex-end; min-width: 40px; }
.bar em { font-style: normal; font: 600 14px var(--font-sans); color: #fff; padding-right: 6px; }
.clip { background: var(--neutral); }
.bio { background: var(--accent); }
.key { font-size: 15px; display: flex; align-items: center; gap: 6px; margin: 6px 0 0; }
.sw { width: 16px; height: 10px; display: inline-block; border-radius: 2px; margin-left: 10px; }
.sw.clip { margin-left: 0; }
</style>
