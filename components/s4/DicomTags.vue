<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { useStep } from '../../composables/useStep'
import meta from '../../data/imaging/dicom/meta.json'

// Slide 31 — real tags from one CT file of our patient, four groups, one at a time.
// The "who" group shows what de-identification removed. clicks: 3
const { step } = useStep(3)
const groups = Object.keys(meta.ct_tags) as (keyof typeof meta.ct_tags)[]
const g = ref(0)
watch(step, s => { g.value = s }, { immediate: true })
const PICK: Record<string, string[]> = {
  'Who (privacy-sensitive)': ['PatientName', 'PatientID', 'PatientBirthDate', 'StudyDate', 'AccessionNumber', 'PatientIdentityRemoved'],
  'How it was acquired': ['Modality', 'Manufacturer', 'ManufacturerModelName', 'KVP', 'SliceThickness'],
  'Where in space': ['Rows', 'Columns', 'PixelSpacing', 'ImagePositionPatient', 'InstanceNumber'],
  'How to read the pixels': ['BitsStored', 'PhotometricInterpretation', 'RescaleSlope', 'RescaleIntercept', 'PixelData'],
}
const NOTE: Record<string, string> = {
  PatientName: 'removed', PatientBirthDate: 'removed', AccessionNumber: 'removed',
  PatientID: 'replaced by a code', StudyDate: 'shifted to a fake date', PatientIdentityRemoved: 'flag set by TCIA',
}
const rows = computed(() => {
  const name = groups[g.value]
  return meta.ct_tags[name].filter(r => PICK[name].includes(r.keyword))
})
</script>

<template>
  <div class="dt">
    <div class="tabs">
      <button v-for="(n, i) in groups" :key="n" class="chip" :aria-pressed="g === i" @click="g = i">{{ n }}</button>
    </div>
    <table>
      <thead><tr><th>Tag</th><th>Name</th><th>Value in our file</th></tr></thead>
      <TransitionGroup tag="tbody" name="row">
        <tr v-for="r in rows" :key="r.keyword">
          <td class="mono">{{ r.tag }}</td>
          <td>{{ r.keyword }}</td>
          <td><span class="mono val">{{ r.value.length > 34 ? `${r.value.slice(0, 34)}…` : r.value }}</span> <span v-if="g === 0 && NOTE[r.keyword]" class="note">{{ NOTE[r.keyword] }}</span></td>
        </tr>
      </TransitionGroup>
    </table>
  </div>
</template>

<style scoped>
.dt { display: flex; flex-direction: column; gap: 16px; }
.tabs { display: flex; gap: 8px; flex-wrap: wrap; }
.tabs .chip { padding: 6px 12px; }
table { font-size: 17px; }
.mono { font-size: 16px; }
td.mono { color: var(--ink-3); width: 120px; }
.val { background: var(--stage); padding: 1px 6px; border-radius: 3px; }
.note { color: var(--warn); font-size: 15px; font-weight: 600; margin-left: 6px; }
.row-enter-active { transition: opacity var(--dur) var(--ease); }
.row-enter-from { opacity: 0; }
</style>
