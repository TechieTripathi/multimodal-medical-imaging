<script setup lang="ts">
import xray from '../../data/imaging/gallery/xray.png'
import ct from '../../data/imaging/gallery/ct.png'
import reports from '../../data/imaging/ct/reports.json'

// Title slide picture: the session's one real patient — an X-ray, a CT slice and a radiologist's words.
const r = reports.readers[0].items
</script>

<template>
  <div class="tv">
    <img :src="xray" alt="Chest X-ray of the session's example patient">
    <span class="plus" aria-hidden="true">+</span>
    <img :src="ct" alt="CT slice of the same patient">
    <span class="plus" aria-hidden="true">+</span>
    <div class="words">
      <span>“{{ r.Texture }}, {{ r.Diameter }}”</span>
      <span>“Malignancy {{ r.Malignancy.split(' (')[0] }}”</span>
    </div>
  </div>
</template>

<style scoped>
.tv { display: flex; align-items: center; gap: 18px; }
.tv img { height: 190px; width: 190px; object-fit: cover; border-radius: var(--radius); background: var(--image-mat); }
.plus { font-size: 32px; color: var(--ink-3); font-weight: 300; }
.words { display: flex; flex-direction: column; gap: 8px; font-size: var(--fs-label); color: var(--ink); max-width: 230px; font-style: italic; }
</style>
