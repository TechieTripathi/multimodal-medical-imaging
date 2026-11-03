<script setup lang="ts">
import run from '../../data/runs/notebook.json'
import seg from '../../data/runs/segmentation.json'
import ColabLink from '../ui/ColabLink.vue'

// The five workflows, what runs live, and measured run times on this machine.
const t = run.biomedclip_seconds_per_image
</script>

<template>
  <table class="dp">
    <colgroup><col style="width:30%"><col style="width:31%"><col style="width:17%"><col style="width:22%"></colgroup>
    <thead><tr><th>Workflow</th><th>Data</th><th>Model</th><th>Time per run</th></tr></thead>
    <tbody>
      <tr><td><strong>A</strong> Load and view a DICOM CT</td><td>Our patient, 133 files</td><td>none</td><td>seconds</td></tr>
      <tr><td><strong>B</strong> Match an X-ray with words</td><td>Our patient’s X-ray (DICOM)</td><td>BiomedCLIP</td><td>{{ t.gpu_s }} s GPU · {{ t.cpu_s }} s CPU</td></tr>
      <tr><td><strong>C</strong> Outline anatomy and nodule</td><td>Our patient’s CT</td><td>TotalSegmentator<br>MedSAM</td><td>1–2 min · {{ seg.medsam.inference_s }} s GPU</td></tr>
      <tr><td><strong>D</strong> Read DICOM from six scanners</td><td>Sample pack: CT, X-ray, MRI, US, mammogram, PET</td><td>none</td><td>seconds</td></tr>
      <tr><td><strong>E</strong> Measure DICOM in Python</td><td>Our patient’s CT and outlines, a PET</td><td>none</td><td>seconds</td></tr>
    </tbody>
  </table>
  <div class="colab-row">
    <p class="foot-note">Times measured on {{ run.device }}. Run it yourself:</p>
    <ColabLink which="dicom" label="DICOM notebook in Colab (2 min, no GPU)" qr />
    <ColabLink which="full" label="Full notebook (GPU)" small />
  </div>
</template>

<style scoped>
.dp { font-size: 16px; line-height: 1.3; }
.dp td, .dp th { padding: 5px 10px; }
.dp td:nth-child(3) { white-space: nowrap; }
.dp { table-layout: fixed; width: 100%; }
.foot-note { font-size: 14px; color: var(--ink-2); margin: 0; max-width: 26ch; }
.colab-row { display: flex; gap: 16px; align-items: center; margin-top: 8px; }
.colab-row > * { flex-shrink: 0; }
.colab-row :deep(.qr) { width: 78px; height: 78px; }
</style>
