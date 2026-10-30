<script setup lang="ts">
import { computed } from 'vue'
import { refNumber } from '../../composables/useRefs'

// Inline citation marker [n]. The key must also be listed in the slide's `sources` frontmatter.
const props = defineProps<{ k: string | string[] }>()
const nums = computed(() => (Array.isArray(props.k) ? props.k : [props.k]).map(k => refNumber(k) ?? '?').sort((a, b) => (typeof a === 'number' && typeof b === 'number' ? a - b : 0)))
</script>

<template>
  <sup class="cite">[{{ nums.join(', ') }}]</sup>
</template>

<style scoped>
.cite { font: 500 0.6em/1 var(--font-sans); color: var(--accent); margin-left: 2px; vertical-align: super; }
</style>
