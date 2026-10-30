<script setup lang="ts">
import { computed } from 'vue'

// Honesty label (IDEA.md §5). At most one per slide; the footer renders it from `tag` / `tagText`
// frontmatter so it always sits in the same place. Solid dot = real data or real output;
// dashed ring = not measured.
export type TagKind = 'actual' | 'real-data' | 'illustrative' | 'simulated' | 'teaching' | 'published'
const props = defineProps<{ kind: TagKind, text?: string }>()
const label = computed(() => ({
  'actual': `Real model output${props.text ? ` · ${props.text}` : ''}`,
  'real-data': `Real de-identified image${props.text ? ` · ${props.text}` : ''}`,
  'illustrative': 'Illustrative values, not measured',
  'simulated': 'Simulated: no model was run',
  'teaching': 'Teaching picture, not real model internals',
  'published': `Reported in ${props.text ?? 'the cited paper'}`,
}[props.kind]))
const real = computed(() => ['actual', 'real-data', 'published'].includes(props.kind))
</script>

<template>
  <span class="tag" :class="{ real }">
    <svg width="12" height="12" viewBox="0 0 12 12" aria-hidden="true">
      <circle v-if="real" cx="6" cy="6" r="4.5" fill="currentColor" />
      <circle v-else cx="6" cy="6" r="4.5" fill="none" stroke="currentColor" stroke-width="1.4" stroke-dasharray="2.2 1.6" />
    </svg>
    {{ label }}
  </span>
</template>

<style scoped>
.tag {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  font: 500 var(--fs-micro)/1 var(--font-sans);
  color: var(--ink-2);
  border: 1px dashed var(--rule-strong);
  border-radius: 999px;
  padding: 4px 10px;
  white-space: nowrap;
}
.tag.real { border-style: solid; border-color: var(--accent-tint-2); color: var(--ink); }
.tag.real svg { color: var(--accent); }
</style>
