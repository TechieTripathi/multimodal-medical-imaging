<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { useStep } from '../../composables/useStep'
import ct from '../../data/imaging/ct/slice_lung.png'
import reports from '../../data/imaging/ct/reports.json'
import ImageMat from '../ui/ImageMat.vue'

// Artifact 2 — what each kind of evidence adds about the same nodule. Clicks add the report,
// then the history; the toggles let the presenter remove any piece again. clicks: 2
const { step } = useStep(2)
const useReport = ref(false)
const useHistory = ref(false)
watch(step, (s) => { useReport.value = s >= 1; useHistory.value = s >= 2 }, { immediate: true })
const r = reports.readers
const malignant = r.filter(x => x.items.Malignancy.startsWith('5')).length
const lines = computed(() => [
  { on: true, from: 'Image', text: 'A round 3 cm lump in the left lung, with a spiky edge.' },
  { on: useReport.value, from: 'Report', text: `${malignant} of ${r.length} radiologists rated it highly suspicious for cancer.` },
  { on: useHistory.value, from: 'History', text: 'Was it there two years ago? Has it grown? Only an earlier scan can say.' },
])
</script>

<template>
  <div class="umc">
    <div class="left">
      <ImageMat :src="ct" alt="CT slice with the nodule" :h="250" />
      <div class="toggles">
        <button class="chip" aria-pressed="true" disabled>Image</button>
        <button class="chip" :aria-pressed="useReport" @click="useReport = !useReport">+ Report</button>
        <button class="chip" :aria-pressed="useHistory" @click="useHistory = !useHistory">+ History</button>
      </div>
    </div>
    <div class="answer">
      <h3>What we can say</h3>
      <TransitionGroup name="line" tag="div" class="lines">
        <p v-for="l in lines.filter(l => l.on)" :key="l.from"><span class="from">{{ l.from }}</span>{{ l.text }}</p>
      </TransitionGroup>
    </div>
  </div>
</template>

<style scoped>
.umc { display: grid; grid-template-columns: 340px 1fr; gap: 40px; align-items: center; }
.left { display: flex; flex-direction: column; gap: 14px; }
.toggles { display: flex; gap: 6px; }
.toggles .chip { padding: 8px 12px; }
.toggles .chip:disabled { opacity: 1; cursor: default; }
.answer h3 { font-size: var(--fs-label); color: var(--ink-2); font-weight: 500; margin: 0 0 12px; }
.lines { display: flex; flex-direction: column; gap: 14px; }
.lines p { margin: 0; font-size: var(--fs-body); line-height: 1.3; display: flex; flex-direction: column; gap: 2px; border-left: 3px solid var(--accent); padding-left: 14px; }
.from { font-size: var(--fs-micro); font-weight: 600; color: var(--accent); }
.line-enter-active, .line-leave-active { transition: opacity var(--dur) var(--ease), transform var(--dur) var(--ease); }
.line-enter-from, .line-leave-to { opacity: 0; transform: translateY(8px); }
</style>
