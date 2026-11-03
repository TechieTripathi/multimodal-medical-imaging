<script setup lang="ts">
import links from '../../data/imaging/qr/links.json'
import qrDicom from '../../data/imaging/qr/dicom.png'
import qrFull from '../../data/imaging/qr/full.png'

// A link that opens a companion notebook in Google Colab (runs in the browser on Google's machines,
// free with a Google account). `qr` adds a code participants can scan with a phone or laptop camera.
const props = withDefaults(defineProps<{ which?: 'dicom' | 'full', qr?: boolean, small?: boolean, label?: string }>(), { which: 'dicom' })
const url = links[props.which]
const qrSrc = props.which === 'dicom' ? qrDicom : qrFull
const text = props.label ?? (props.which === 'dicom' ? 'Open the DICOM notebook in Colab' : 'Open the full notebook in Colab')
</script>

<template>
  <span class="colab" :class="{ small }">
    <a :href="url" target="_blank" rel="noopener" class="btn-colab">▶ {{ text }}</a>
    <img v-if="qr" :src="qrSrc" :alt="`QR code for ${url}`" class="qr">
  </span>
</template>

<style scoped>
.colab { display: inline-flex; align-items: center; gap: 12px; }
.btn-colab { font: 600 16px var(--font-sans); color: #fff !important; background: #e8710a; border-radius: 999px; padding: 7px 16px; text-decoration: none !important; border-bottom: none !important; white-space: nowrap; }
.btn-colab:hover { background: #c45f08; }
.small .btn-colab { font-size: 13px; padding: 4px 11px; }
.qr { width: 104px; height: 104px; image-rendering: pixelated; border: 1px solid var(--rule); border-radius: 4px; }
</style>
