<script setup lang="ts">
import { ref } from 'vue'
import { useStep } from '../../composables/useStep'
import xray from '../../data/imaging/gallery/xray.png'
import ct from '../../data/imaging/gallery/ct.png'
import mri from '../../data/imaging/gallery/mri.png'
import us from '../../data/imaging/gallery/ultrasound.png'
import path from '../../data/imaging/gallery/pathology.png'
import retina from '../../data/imaging/gallery/retina.png'
import meta from '../../data/imaging/gallery/meta.json'

// Artifact 1 — modality gallery. Clicks 1–5 add modalities; click 6 stamps how each is usually stored.
// Clicking a tile enlarges it. clicks: 6
const { step } = useStep(6)
const tiles = [
  { key: 'xray', name: 'X-ray', what: 'Shadows of the body', src: xray, dicom: true },
  { key: 'ct', name: 'CT', what: 'X-ray slices, a 3D stack', src: ct, dicom: true },
  { key: 'mri', name: 'MRI', what: 'Magnetism, many contrasts', src: mri, dicom: true },
  { key: 'ultrasound', name: 'Ultrasound', what: 'Sound echoes, live', src: us, dicom: true },
  { key: 'pathology', name: 'Pathology', what: 'Stained tissue, microscope', src: path, dicom: false },
  { key: 'retina', name: 'Retina', what: 'Photo of the eye’s back', src: retina, dicom: false },
] as const
const open = ref<string | null>(null)
const credit = (k: string) => (meta as any)[k].credit
</script>

<template>
  <div class="gal">
    <button
      v-for="(t, i) in tiles" :key="t.key" class="tile rv" :class="{ on: step >= i || i === 0 }"
      :aria-label="`Enlarge ${t.name}`" @click="open = t.key"
    >
      <img :src="t.src" :alt="t.name">
      <span class="txt">
        <span class="name">{{ t.name }}</span>
        <span class="what">{{ t.what }}</span>
        <span class="stamp rv" :class="[{ on: step >= 6 }, t.dicom ? 'yes' : 'no']">{{ t.dicom ? 'Usually DICOM' : 'Often not DICOM' }}</span>
      </span>
    </button>
    <Transition name="zoom">
      <div v-if="open" class="big" @click="open = null">
        <img :src="tiles.find(t => t.key === open)!.src" :alt="open">
        <p>{{ tiles.find(t => t.key === open)!.name }} · {{ credit(open) }}</p>
      </div>
    </Transition>
  </div>
</template>

<style scoped>
.gal { position: relative; display: grid; grid-template-columns: repeat(3, 1fr); gap: 18px 24px; }
.tile { display: flex; gap: 14px; align-items: center; background: none; border: 0; padding: 0; text-align: left; cursor: zoom-in; font: inherit; color: inherit; }
.tile img { width: 140px; height: 140px; object-fit: cover; border-radius: var(--radius); background: var(--image-mat); flex: none; }
.txt { display: flex; flex-direction: column; gap: 6px; min-width: 0; }
.name { font-size: var(--fs-body); font-weight: 600; }
.what { font-size: var(--fs-label); color: var(--ink-2); line-height: 1.25; }
.stamp { white-space: nowrap; align-self: flex-start; font-size: var(--fs-micro); font-weight: 600; padding: 3px 8px; border-radius: 999px; margin-top: 4px; }
.stamp.yes { color: var(--accent); background: var(--accent-tint); }
.stamp.no { color: var(--warn); background: var(--warn-tint); }
.big { position: absolute; inset: -6px; background: var(--image-mat); border-radius: var(--radius); display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 8px; cursor: zoom-out; z-index: 5; }
.big img { height: 300px; width: auto; }
.big p { color: var(--image-ink); font-size: var(--fs-micro); margin: 0; }
.zoom-enter-active, .zoom-leave-active { transition: opacity var(--dur) var(--ease); }
.zoom-enter-from, .zoom-leave-to { opacity: 0; }
</style>
