<script setup lang="ts">
import { computed, ref, shallowRef, watch } from 'vue'
import { useStep } from '../../composables/useStep'
import { type Dicom, loadDicom } from '../../composables/dicom'
import { drawGrey, drawRGB, percentileWindow, pub } from '../../composables/draw'
import manifest from '../../data/imaging/dicom_examples/manifest.json'

// Artifact 25 — a real DICOM viewer in the slide. Each click opens the next real file (teaching copies
// of public TCIA data); tags are read from the file itself, not from a table. Participants can also open
// their own .dcm file: it is read in the browser and never uploaded. clicks: 5
const FILES = ['ct-lidc-0001.dcm', 'xray-lidc-0001.dcm', 'mri-flair-upenn-00001.dcm', 'mammo-cmmd-d2-0333.dcm', 'pet-fdg-lung.dcm', 'us-liver-ceus.dcm']
const LABEL: Record<string, string> = { 'ct-lidc-0001.dcm': 'CT', 'xray-lidc-0001.dcm': 'X-ray', 'mri-flair-upenn-00001.dcm': 'MRI', 'mammo-cmmd-d2-0333.dcm': 'Mammogram', 'pet-fdg-lung.dcm': 'PET', 'us-liver-ceus.dcm': 'Ultrasound' }
const { step } = useStep(FILES.length - 1)
const name = ref(FILES[0])
const d = shallowRef<Dicom | null>(null)
const err = ref('')
const frame = ref(0)
const level = ref(0)
const width = ref(1)
const cv = ref<HTMLCanvasElement>()
const credit = computed(() => (manifest.files as any[]).find(f => f.file === name.value)?.credit ?? 'Your own file, read in this browser only')

async function open(src: string | File, label: string) {
  err.value = ''
  try {
    const x = await loadDicom(typeof src === 'string' ? pub(`dicom/${src}`) : src)
    name.value = label
    frame.value = 0
    if (!x.rgb) {
      const isCT = x.str('Modality') === 'CT'
      const wc = x.num('WindowCenter'), ww = x.num('WindowWidth')
      const w = isCT && wc !== undefined && ww ? { level: wc, width: ww } : percentileWindow(x.frame(0) as Float32Array)
      level.value = Math.round(w.level)
      width.value = Math.max(1, Math.round(w.width))
    }
    d.value = x
  }
  catch (e) { err.value = String((e as Error).message ?? e) }
}
watch(step, s => open(FILES[s], FILES[s]), { immediate: true })
const pet = computed(() => d.value?.str('Modality') === 'PT')
function draw() {
  const x = d.value
  if (!x || !cv.value) return
  if (x.rgb) drawRGB(cv.value, x.frame(frame.value) as Uint8Array, x.cols, x.rows)
  else drawGrey(cv.value, x.frame(frame.value) as Float32Array, x.cols, x.rows, level.value, width.value, x.monochrome1 || pet.value)
}
watch([d, frame, level, width, cv], draw, { flush: 'post' })
const rows = computed(() => {
  const x = d.value
  if (!x) return []
  const sp = x.nums('PixelSpacing').length ? x.nums('PixelSpacing') : x.nums('ImagerPixelSpacing')
  return [
    ['Modality', x.str('Modality') ?? '—'],
    ['Size', `${x.cols} × ${x.rows} pixels${x.frames > 1 ? `, ${x.frames} frames` : ''}`],
    ['Pixel size', sp.length ? `${sp[0].toFixed(2)} mm` : 'not recorded'],
    ['Stored as', `${x.num('BitsStored')}-bit ${x.rgb ? 'colour' : (x.str('PhotometricInterpretation') ?? '')}`],
    ['Units', x.str('Modality') === 'CT' ? 'Hounsfield units' : x.str('Units') ?? 'none (relative)'],
    ['Scanner', [x.str('Manufacturer'), x.str('ManufacturerModelName')].filter(Boolean).join(' ') || '—'],
  ]
})
const pick = (e: Event) => { const f = (e.target as HTMLInputElement).files?.[0]; if (f) open(f, f.name) }
</script>

<template>
  <div class="dv">
    <div class="pic">
      <div class="mat"><canvas ref="cv" /></div>
      <p class="credit">{{ credit }}</p>
    </div>
    <div class="side">
      <div class="chips">
        <button v-for="f in FILES" :key="f" class="chip" :aria-pressed="name === f" @click="open(f, f)">{{ LABEL[f] }}</button>
      </div>
      <p v-if="err" class="err">{{ err }}</p>
      <dl class="tags">
        <template v-for="[k, v] in rows" :key="k"><dt>{{ k }}</dt><dd>{{ v }}</dd></template>
      </dl>
      <template v-if="d && !d.rgb">
        <label class="ctl">Level <input v-model.number="level" type="range" :min="level - width * 2" :max="level + width * 2" :step="width / 100" @keydown.stop></label>
        <label class="ctl">Width <input v-model.number="width" type="range" :min="width / 10" :max="width * 4" :step="width / 100" @keydown.stop></label>
      </template>
      <label v-if="d && d.frames > 1" class="ctl">Frame <input v-model.number="frame" type="range" min="0" :max="d.frames - 1" @keydown.stop> {{ frame + 1 }} / {{ d.frames }}</label>
      <div class="files">
        <a v-if="FILES.includes(name)" :href="pub(`dicom/${name}`)" :download="name">Download this .dcm</a>
        <label class="own">Open your own .dcm <input type="file" accept=".dcm,application/dicom" @change="pick"></label>
      </div>
    </div>
  </div>
</template>

<style scoped>
.dv { display: grid; grid-template-columns: 330px 1fr; gap: 30px; align-items: start; }
.mat { width: 330px; height: 330px; background: var(--image-mat); border-radius: var(--radius); display: flex; align-items: center; justify-content: center; overflow: hidden; }
.mat canvas { max-width: 100%; max-height: 100%; }
.credit { font-size: var(--fs-micro); color: var(--ink-3); margin: 6px 0 0; }
.chips { display: flex; flex-wrap: wrap; gap: 6px; margin-bottom: 12px; }
.chips .chip { padding: 5px 11px; font-size: 16px; }
.tags { display: grid; grid-template-columns: 110px 1fr; gap: 5px 14px; margin: 0 0 10px; font-size: 16px; }
.tags dt { color: var(--ink-2); }
.tags dd { margin: 0; font-family: var(--font-mono); font-size: 15px; }
.ctl { font-size: 15px; margin-right: 14px; }
.ctl input { width: 150px; }
.files { display: flex; gap: 18px; margin-top: 10px; font-size: 15px; align-items: center; }
.own { color: var(--accent); cursor: pointer; text-decoration: underline; }
.own input { display: none; }
.err { color: var(--bad); font-size: 15px; }
</style>
