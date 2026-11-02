<script setup lang="ts">
import { onMounted, ref, shallowRef, watch } from 'vue'
import { useStep } from '../../composables/useStep'
import { type Dicom, loadDicom } from '../../composables/dicom'
import { drawGrey, percentileWindow, pub } from '../../composables/draw'
import manifest from '../../data/imaging/dicom_examples/manifest.json'

// Slide — a mammogram's DICOM tags already carry context (which breast, how to display), and the
// dataset adds a clinical row: image + table, a multimodal pair. clicks: 2
const { step } = useStep(2)
const d = shallowRef<Dicom | null>(null)
const cv = ref<HTMLCanvasElement>()
const info = (manifest.files as any[]).find(f => f.file === 'mammo-cmmd-d2-0333.dcm')
const c = info.clinical
onMounted(async () => { d.value = await loadDicom(pub('dicom/mammo-cmmd-d2-0333.dcm')) })
watch([d, cv], () => {
  if (!d.value || !cv.value) return
  const v = d.value.frame(0) as Float32Array
  const w = percentileWindow(v)
  drawGrey(cv.value, v, d.value.cols, d.value.rows, w.level, w.width, d.value.monochrome1)
}, { flush: 'post' })
</script>

<template>
  <div class="mm">
    <div>
      <div class="mat"><canvas ref="cv" /></div>
      <p class="credit">{{ info.credit }}</p>
    </div>
    <div class="side">
      <p class="lbl">Read from the DICOM file</p>
      <dl v-if="d" class="tags">
        <dt>Modality</dt><dd class="mono">{{ d.str('Modality') }}</dd>
        <dt>Which breast</dt><dd class="mono">ImageLaterality = {{ d.str('ImageLaterality') ?? '—' }}</dd>
        <dt>Which view</dt><dd class="mono">ViewPosition = {{ d.str('ViewPosition') ?? 'not recorded' }}</dd>
        <dt>Display</dt><dd class="mono">{{ d.str('PhotometricInterpretation') }}, {{ d.num('BitsStored') }}-bit</dd>
      </dl>
      <div class="card rv" :class="{ on: step >= 1 }">
        <h3>From the dataset’s clinical table</h3>
        <p>Age {{ c.age }} · {{ c.side === 'R' ? 'right' : 'left' }} breast · {{ c.abnormality }}</p>
        <p><strong>{{ c.classification }}</strong> on biopsy · subtype {{ c.subtype }}</p>
      </div>
      <p class="rv note" :class="{ on: step >= 2 }">Tags and table together: an image plus structured data, the simplest multimodal input. The subtype needed a biopsy; no image alone gives it.</p>
    </div>
  </div>
</template>

<style scoped>
.mm { display: grid; grid-template-columns: 290px 1fr; gap: 32px; align-items: center; }
.mat { width: 290px; height: 340px; background: var(--image-mat); border-radius: var(--radius); display: flex; align-items: center; justify-content: center; overflow: hidden; }
.mat canvas { max-width: 100%; max-height: 100%; }
.credit { font-size: var(--fs-micro); color: var(--ink-3); margin: 6px 0 0; }
.lbl { font-size: var(--fs-label); color: var(--ink-2); margin: 0 0 8px; }
.tags { display: grid; grid-template-columns: 130px 1fr; gap: 6px 12px; margin: 0 0 14px; font-size: 16px; }
.tags dt { color: var(--ink-2); }
.tags dd { margin: 0; font-size: 15px; }
.card p { margin: 0 0 4px; font-size: var(--fs-label); }
.note { font-size: 16px; margin: 12px 0 0; }
</style>
