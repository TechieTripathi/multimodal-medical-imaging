<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { useStep } from '../../composables/useStep'
import t1 from '../../data/imaging/mri/t1.png'
import t1c from '../../data/imaging/mri/t1_contrast.png'
import t2 from '../../data/imaging/mri/t2.png'
import flair from '../../data/imaging/mri/flair.png'

// Artifact 16 — one brain, four MRI sequences, registered to the same slice. Clicks step through them;
// the wipe slider compares the current sequence with the one before. clicks: 3
const { step } = useStep(3)
const SEQ = [
  { name: 'T1', src: t1, note: 'Anatomy: fat bright, fluid dark' },
  { name: 'T1 + contrast', src: t1c, note: 'Leaky vessels and tumour edges light up after the injection' },
  { name: 'T2', src: t2, note: 'Fluid bright: the swelling around the tumour shows' },
  { name: 'FLAIR', src: flair, note: 'T2 with normal fluid made dark, so swelling stands out' },
]
const cur = ref(0)
const wipe = ref(100)
watch(step, s => { cur.value = s; wipe.value = 100 }, { immediate: true })
const prev = computed(() => SEQ[Math.max(0, cur.value - 1)])
</script>

<template>
  <div class="mr">
    <div class="pic">
      <img :src="prev.src" alt="" class="under">
      <img :src="SEQ[cur].src" :alt="`${SEQ[cur].name} MRI`" class="over" :style="{ clipPath: `inset(0 ${100 - wipe}% 0 0)` }">
      <span class="lab">{{ SEQ[cur].name }}</span>
    </div>
    <div class="side">
      <div class="seqs">
        <button v-for="(s, i) in SEQ" :key="s.name" class="chip" :aria-pressed="cur === i" @click="cur = i; wipe = 100">{{ s.name }}</button>
      </div>
      <p class="note">{{ SEQ[cur].note }}</p>
      <label v-if="cur > 0" class="ctl">Compare with {{ prev.name }} <input v-model.number="wipe" type="range" min="0" max="100" @keydown.stop></label>
      <p class="muted small">Same patient, same scan session; each sequence is a separate series in the DICOM study.</p>
    </div>
  </div>
</template>

<style scoped>
.mr { display: grid; grid-template-columns: 270px 1fr; gap: 40px; align-items: center; }
.pic { position: relative; width: 270px; height: 360px; background: var(--image-mat); border-radius: var(--radius); overflow: hidden; }
.pic img { position: absolute; inset: 0; width: 100%; height: 100%; object-fit: contain; }
.over { transition: opacity var(--dur) var(--ease); }
.lab { position: absolute; left: 10px; top: 8px; color: #ffc400; font-weight: 600; font-size: var(--fs-label); }
.seqs { display: flex; gap: 8px; flex-wrap: wrap; margin-bottom: 18px; }
.note { font-size: var(--fs-body); margin: 0 0 18px; min-height: 60px; }
.small { font-size: 16px; margin-top: 14px; }
</style>
