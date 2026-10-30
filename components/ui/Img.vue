<script setup lang="ts">
import ImageMat from './ImageMat.vue'

// An image from data/imaging by its path there (e.g. "apps/us_annotated.png"), on the dark mat.
// Lets slide markdown place bundled images without imports.
const props = withDefaults(defineProps<{ name: string, alt: string, credit?: string, caption?: string, h?: number, ar?: number }>(), { h: 300, ar: 1 })
const all = import.meta.glob('../../data/imaging/**/*.png', { eager: true, import: 'default' }) as Record<string, string>
const src = all[`../../data/imaging/${props.name}`]
</script>

<template>
  <ImageMat :src="src" :alt="alt" :credit="credit" :caption="caption" :h="h" :ar="ar"><slot /></ImageMat>
</template>
