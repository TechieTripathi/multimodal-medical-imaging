<script setup lang="ts">
import { ref, watch } from 'vue'
import { useStep } from '../../composables/useStep'
import ct from '../../data/imaging/ct/slice_lung.png'
import reports from '../../data/imaging/ct/reports.json'
import meta from '../../data/imaging/ct/meta.json'

// Artifact 23 — checking a generated report sentence by sentence against the evidence we hold for our
// patient. The report text is written by us to illustrate; the evidence is real. clicks: 4
const { step } = useStep(4)
const r = reports.readers.map(x => x.items)
const high = r.filter(x => x.Malignancy.startsWith('5')).length
const SENT = [
  { s: 'A 3 cm spiculated mass in the left lower lobe.', state: 'ok', ev: `CT shows it; four radiologists measured ${r.map(x => x.Diameter).join(', ')}` },
  { s: 'Features are suspicious for malignancy.', state: 'ok', ev: `${high} of ${r.length} radiologists rated it 5 of 5; still needs a biopsy` },
  { s: 'No enlarged lymph nodes.', state: 'warn', ev: 'Not checked by anyone in our data: a person must look' },
  { s: 'Unchanged since the previous scan.', state: 'bad', ev: 'There is no previous scan: invented' },
]
const sel = ref(0)
watch(step, s => { sel.value = Math.max(0, s - 1) }, { immediate: true })
const [cy, cx] = meta.nodule_center_yx
</script>

<template>
  <div class="rc">
    <div class="pic">
      <img :src="ct" alt="Our patient's CT slice">
      <span v-if="step >= 1 && sel <= 1" class="ring" :style="{ left: `${cx / 5.12}%`, top: `${cy / 5.12}%` }" />
    </div>
    <div class="side">
      <p class="lbl">A generated report</p>
      <button v-for="(x, i) in SENT" :key="x.s" class="sent" :class="[step > i ? x.state : '', { sel: sel === i && step > 0 }]" @click="sel = i">“{{ x.s }}”</button>
      <p v-if="step > 0" class="ev" :class="SENT[sel].state">{{ SENT[sel].ev }}</p>
    </div>
  </div>
</template>

<style scoped>
.rc { display: grid; grid-template-columns: 300px 1fr; gap: 32px; align-items: center; }
.pic { position: relative; width: 300px; height: 300px; }
.pic img { width: 100%; height: 100%; border-radius: var(--radius); }
.ring { position: absolute; width: 22%; aspect-ratio: 1; border: 2px solid #ffc400; border-radius: 50%; transform: translate(-50%, -50%); }
.lbl { font-size: var(--fs-label); color: var(--ink-2); margin: 0 0 8px; }
.sent { display: block; width: 100%; text-align: left; font: italic 400 var(--fs-label) var(--font-sans); background: var(--surface); border: 1px solid var(--rule); border-left: 4px solid var(--rule-strong); padding: 8px 12px; margin-bottom: 6px; border-radius: 4px; cursor: pointer; color: var(--ink); }
.sent.ok { border-left-color: var(--ok); }
.sent.warn { border-left-color: var(--warn); }
.sent.bad { border-left-color: var(--bad); background: var(--bad-tint); }
.sent.sel { outline: 2px solid var(--accent); }
.ev { font-size: var(--fs-label); font-weight: 600; margin: 10px 0 0; }
.ev.ok { color: var(--ok); }
.ev.warn { color: var(--warn); }
.ev.bad { color: var(--bad); }
</style>
