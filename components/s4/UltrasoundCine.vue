<script setup lang="ts">
import { onBeforeUnmount, onMounted, ref, shallowRef, watch } from 'vue'
import { useStep } from '../../composables/useStep'
import { type Dicom, loadDicom } from '../../composables/dicom'
import { drawRGB, pub } from '../../composables/draw'
import { rafThrottle } from '../../composables/raf'
import manifest from '../../data/imaging/dicom_examples/manifest.json'

// Slide — ultrasound DICOM is a video: one multi-frame file, frame timing read from its tags.
// Step 1 plays the loop once; the slider scrubs freely. clicks: 2
const { step } = useStep(2)
const d = shallowRef<Dicom | null>(null)
const frame = ref(0)
const cv = ref<HTMLCanvasElement>()
const info = (manifest.files as any[]).find(f => f.file === 'us-liver-ceus.dcm')
onMounted(async () => { d.value = await loadDicom(pub('dicom/us-liver-ceus.dcm')) })
watch([d, frame, cv], rafThrottle(() => { if (d.value && cv.value) drawRGB(cv.value, d.value.frame(frame.value) as Uint8Array, d.value.cols, d.value.rows) }), { flush: 'post' })
let timer: ReturnType<typeof setTimeout> | null = null
function play() {
  if (!d.value) return
  if (timer) clearTimeout(timer)
  frame.value = 0
  const ms = d.value.num('FrameTime') ?? 500
  const tick = () => { if (frame.value < d.value!.frames - 1) { frame.value++; timer = setTimeout(tick, ms) } }
  timer = setTimeout(tick, ms)
}
watch(step, s => { if (s === 1) play() })
onBeforeUnmount(() => { if (timer) clearTimeout(timer) })
</script>

<template>
  <div class="uc">
    <div>
      <div class="mat">
        <canvas ref="cv" />
        <span class="lab l rv" :class="{ on: step >= 2 }">B-mode</span>
        <span class="lab r rv" :class="{ on: step >= 2 }">with contrast</span>
      </div>
      <div class="bar">
        <button class="chip" @click="play">Play</button>
        <input v-if="d" v-model.number="frame" type="range" min="0" :max="d.frames - 1" aria-label="Frame" @keydown.stop>
      </div>
      <p class="credit">{{ info.credit }} · every 5th frame shown</p>
    </div>
    <dl v-if="d" class="tags">
      <dt>Modality</dt><dd>{{ d.str('Modality') }}</dd>
      <dt>Number of frames</dt><dd>{{ d.frames }} <span class="muted">(original {{ info.original.frames }})</span></dd>
      <dt>Time per frame</dt><dd>{{ d.num('FrameTime')?.toFixed(0) }} ms <span class="muted">(original {{ info.original.frame_time_ms.toFixed(0) }} ms)</span></dd>
      <dt>Colour</dt><dd>{{ d.str('PhotometricInterpretation') }}, {{ d.num('SamplesPerPixel') }} samples</dd>
      <dt>Frame now</dt><dd>{{ frame + 1 }} / {{ d.frames }} · {{ ((frame * (d.num('FrameTime') ?? 0)) / 1000).toFixed(1) }} s</dd>
    </dl>
  </div>
</template>

<style scoped>
.uc { display: grid; grid-template-columns: 1.25fr 1fr; gap: 28px; align-items: center; }
.mat { position: relative; background: var(--image-mat); border-radius: var(--radius); overflow: hidden; }
.mat canvas { width: 100%; display: block; image-rendering: auto; }
.lab { position: absolute; bottom: 8px; color: #ffc400; font-weight: 600; font-size: 15px; background: rgba(11, 13, 16, 0.7); padding: 2px 8px; border-radius: 3px; }
.lab.l { left: 10px; }
.lab.r { right: 10px; }
.bar { display: flex; gap: 12px; align-items: center; margin-top: 8px; }
.bar .chip { padding: 5px 14px; }
.bar input { flex: 1; accent-color: var(--accent); }
.credit { font-size: var(--fs-micro); color: var(--ink-3); margin: 4px 0 0; }
.tags { display: grid; grid-template-columns: 150px 1fr; gap: 8px 14px; margin: 0; font-size: var(--fs-label); }
.tags dt { color: var(--ink-2); }
.tags dd { margin: 0; }
</style>
