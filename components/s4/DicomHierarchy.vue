<script setup lang="ts">
import { computed, ref } from 'vue'
import { useStep } from '../../composables/useStep'
import meta from '../../data/imaging/dicom/meta.json'

// Artifact 13 — our patient's real DICOM hierarchy: patient → studies → series → instances (files).
// Clicks open each level; click a node to see its details. clicks: 3
const { step } = useStep(3)
const P = meta.patient
const NAMES: Record<string, string> = { CT: 'CT images', DX: 'X-ray images', SEG: 'Outline by one radiologist', SR: 'Ratings by one radiologist' }
const sel = ref<string>('patient')
const detail = computed(() => {
  if (sel.value === 'patient') return [['Patient ID', P.id], ['Studies', String(P.studies.length)]]
  const [si, se] = sel.value.split('-').map(Number)
  const st = P.studies[si]
  if (se === undefined || Number.isNaN(se)) return [['Study date', `${st.date} (shifted)`], ['Contains', st.modality], ['Study UID', st.uid]]
  const s = st.series[se]
  return [['Modality', s.modality], ['Files (instances)', String(s.instances)], ['Size', `${(s.bytes / 1e6).toFixed(1)} MB`], ['Series UID', s.uid]]
})
const grouped = (st: typeof P.studies[number]) => {
  const out: { modality: string, n: number, idx: number, instances: number }[] = []
  st.series.forEach((s, i) => {
    const g = out.find(o => o.modality === s.modality)
    if (g) g.n++
    else out.push({ modality: s.modality, n: 1, idx: i, instances: s.instances })
  })
  return out
}
</script>

<template>
  <div class="dh">
    <div class="tree">
      <button class="node pat" :class="{ sel: sel === 'patient' }" @click="sel = 'patient'"><small>Patient</small>{{ P.id }}</button>
      <div class="studies rv" :class="{ on: step >= 1 }">
        <div v-for="(st, si) in P.studies" :key="st.uid" class="study">
          <button class="node" :class="{ sel: sel === `${si}` }" @click="sel = `${si}`"><small>Study</small>{{ st.modality.includes('CT') ? 'Chest CT' : 'Chest X-ray' }}</button>
          <div class="series rv" :class="{ on: step >= 2 }">
            <div v-for="g in grouped(st)" :key="g.modality" class="ser">
              <button class="node s" :class="{ sel: sel === `${si}-${g.idx}` }" @click="sel = `${si}-${g.idx}`"><small>{{ g.n > 1 ? `${g.n} series` : 'Series' }}</small>{{ NAMES[g.modality] }}</button>
              <div class="inst rv" :class="{ on: step >= 3 }">
                <span v-for="k in Math.min(g.instances, 40)" :key="k" class="f" />
                <em>{{ g.instances }} {{ g.instances === 1 ? 'file' : 'files' }}{{ g.n > 1 ? ' each' : '' }}</em>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
    <dl class="card det">
      <template v-for="[k, v] in detail" :key="k"><dt>{{ k }}</dt><dd>{{ v }}</dd></template>
    </dl>
  </div>
</template>

<style scoped>
.dh { display: grid; grid-template-columns: 1fr 250px; gap: 26px; align-items: center; }
.tree { display: grid; grid-template-columns: 150px 1fr; gap: 14px; align-items: center; }
.studies { display: flex; flex-direction: column; gap: 16px; border-left: 2px solid var(--rule-strong); padding-left: 14px; }
.study { display: grid; grid-template-columns: 130px 1fr; gap: 12px; align-items: center; }
.series { display: flex; flex-direction: column; gap: 8px; border-left: 2px solid var(--rule-strong); padding-left: 12px; }
.ser { display: grid; grid-template-columns: 170px 1fr; gap: 10px; align-items: center; }
.node { text-align: left; font: 500 16px var(--font-sans); background: var(--surface); border: 1.5px solid var(--rule-strong); border-radius: var(--radius); padding: 6px 10px; cursor: pointer; color: var(--ink); display: flex; flex-direction: column; line-height: 1.2; }
.node small { font-size: 14px; color: var(--ink-3); font-weight: 400; }
.node.pat { border-color: var(--accent); }
.node.sel { background: var(--accent-tint); border-color: var(--accent); }
.inst { display: flex; flex-wrap: wrap; gap: 2px; align-items: center; max-width: 170px; }
.f { width: 5px; height: 12px; background: var(--accent-tint-2); border-radius: 1px; }
.inst em { font-style: normal; font-size: 14px; color: var(--ink-2); margin-left: 6px; }
.det { display: grid; grid-template-columns: auto 1fr; gap: 8px 12px; margin: 0; font-size: 15px; }
.det dt { color: var(--ink-2); }
.det dd { margin: 0; word-break: break-all; }
</style>
