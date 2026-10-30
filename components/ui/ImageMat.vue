<script setup lang="ts">
// A medical image on the dark mat (IDEA.md §4.7), with an optional caption and short credit.
// The default slot is laid over the image for annotations, positioned in % of the image itself:
// the image box keeps the image's aspect ratio (`ar` = width / height), so overlays stay aligned.
withDefaults(defineProps<{ src: string, alt: string, credit?: string, caption?: string, h?: number, ar?: number }>(), { h: 300, ar: 1 })
</script>

<template>
  <figure class="mat-fig">
    <div class="mat" :style="{ height: `${h}px` }">
      <div class="box" :style="{ width: `min(100%, ${h * ar}px)`, aspectRatio: String(ar) }">
        <img :src="src" :alt="alt" draggable="false">
        <div class="over"><slot /></div>
      </div>
    </div>
    <figcaption v-if="caption || credit">
      <span v-if="caption" class="cap">{{ caption }}</span>
      <span v-if="credit" class="credit">{{ credit }}</span>
    </figcaption>
  </figure>
</template>

<style scoped>
.mat-fig { margin: 0; display: flex; flex-direction: column; gap: 6px; min-width: 0; }
.mat { background: var(--image-mat); border-radius: var(--radius); display: flex; align-items: center; justify-content: center; overflow: hidden; }
.box { position: relative; max-height: 100%; }
.box img { position: absolute; inset: 0; width: 100%; height: 100%; display: block; user-select: none; }
.over { position: absolute; inset: 0; pointer-events: none; }
figcaption { display: flex; flex-direction: column; gap: 2px; }
.cap { font-size: var(--fs-label); color: var(--ink); font-weight: 500; }
.credit { font-size: var(--fs-micro); color: var(--ink-3); }
</style>
