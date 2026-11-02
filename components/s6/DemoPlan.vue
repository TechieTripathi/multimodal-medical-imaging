<script setup lang="ts">
import run from '../../data/runs/notebook.json'
import seg from '../../data/runs/segmentation.json'

// Slide 45 — the three workflows, what runs live, and measured run times on this machine.
const t = run.biomedclip_seconds_per_image
</script>

<template>
  <table class="dp">
    <thead><tr><th>Workflow</th><th>Data</th><th>Model</th><th>Time per run</th></tr></thead>
    <tbody>
      <tr><td><strong>A</strong> Load and view a DICOM CT</td><td>Our patient, 133 files</td><td>none</td><td>seconds</td></tr>
      <tr><td><strong>B</strong> Match an X-ray with words</td><td>Our patient’s X-ray (DICOM)</td><td>BiomedCLIP</td><td>{{ t.gpu_s }} s on GPU · {{ t.cpu_s }} s on CPU</td></tr>
      <tr><td><strong>C</strong> Outline anatomy and nodule</td><td>Our patient’s CT</td><td>TotalSegmentator, MedSAM</td><td>about 1–2 min · {{ seg.medsam.inference_s }} s on GPU</td></tr>
      <tr><td><strong>D</strong> Read DICOM from six scanners</td><td>Sample pack: CT, X-ray, MRI, US, mammogram, PET</td><td>none</td><td>seconds</td></tr>
    </tbody>
  </table>
  <p class="foot-note">Run live in the notebook on {{ run.device }}. Every result on the next slides is that run’s real output.</p>
</template>

<style scoped>
.dp { font-size: var(--fs-label); }
.dp td { padding: 9px 12px; }
.foot-note { font-size: var(--fs-label); color: var(--ink-2); margin: 18px 0 0; }
</style>
