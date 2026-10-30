<script setup lang="ts">
import { useStep } from '../../composables/useStep'
import ct from '../../data/imaging/ct/slice_lung.png'
import meta from '../../data/imaging/dicom/meta.json'

// Slide 29 — a PNG is only pixels; a DICOM file is pixels plus the facts needed to use them. clicks: 2
const { step } = useStep(2)
const f = meta.ct_file
const pctPixels = ((f.pixel_bytes / f.bytes) * 100).toFixed(1)
</script>

<template>
  <div class="dp">
    <div class="side">
      <h3>A PNG or JPEG</h3>
      <img :src="ct" alt="CT slice as an ordinary picture">
      <ul><li>Brightness 0–255, no units</li><li>No size in millimetres</li><li>No idea where it sits in the body</li></ul>
    </div>
    <div class="side rv" :class="{ on: step >= 1 }">
      <h3>A DICOM file (our patient’s CT, one slice)</h3>
      <div class="file">
        <div class="tags">
          <span>Who: patient, study, dates</span>
          <span>How: scanner, settings</span>
          <span>Where: position, spacing</span>
          <span>How to read the pixels</span>
          <span class="count">{{ f.elements }} tags in all</span>
        </div>
        <img :src="ct" alt="The same slice inside a DICOM file">
      </div>
      <p class="rv" :class="{ on: step >= 2 }">Values in real units (Hounsfield), 0.70 mm per pixel. The pixels are {{ pctPixels }}% of the file; the tags are small but essential.</p>
    </div>
  </div>
</template>

<style scoped>
.dp { display: grid; grid-template-columns: 1fr 1.5fr; gap: 40px; align-items: start; }
h3 { font-size: var(--fs-label) !important; margin-bottom: 10px !important; }
.side > img { width: 170px; height: 170px; border-radius: var(--radius); display: block; margin-bottom: 12px; }
ul { font-size: var(--fs-label); }
.file { display: flex; gap: 0; border: 2px solid var(--accent); border-radius: var(--radius); overflow: hidden; margin-bottom: 12px; }
.tags { display: flex; flex-direction: column; justify-content: center; gap: 6px; padding: 12px 16px; background: var(--accent-tint); font-size: 16px; flex: 1; }
.tags span { border-bottom: 1px dashed var(--accent-tint-2); padding-bottom: 4px; }
.tags .count { border: 0; font-weight: 600; color: var(--accent); }
.file img { width: 190px; height: 190px; display: block; }
.side p { font-size: var(--fs-label); margin: 0; }
</style>
