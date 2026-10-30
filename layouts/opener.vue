<script setup lang="ts">
import { computed } from 'vue'
import { useSlideContext } from '@slidev/client'
import { sectionFor } from '../data/sections'

// Section opener on the dark surface: the section's name, then the one plain question it answers.
const { $frontmatter } = useSlideContext()
const section = computed(() => sectionFor(Number($frontmatter.section)))
</script>

<template>
  <div class="slidev-layout l-opener">
    <div class="inner">
      <p v-if="section" class="kicker">Part {{ section.no }} · {{ section.name }}</p>
      <slot />
    </div>
  </div>
</template>

<style scoped>
.l-opener {
  height: 100%;
  background: var(--night);
  color: var(--ink-inverse);
  padding: 60px var(--gutter) 52px;
  display: flex;
  align-items: center;
}
.inner { width: 100%; display: flex; flex-direction: column; gap: var(--s5); }
.kicker { font-size: var(--fs-label); color: #9aa0a8; margin: 0; }
.inner :deep(h1) { color: #fff; font-size: var(--fs-display); max-width: 20ch; line-height: 1.05; }
.inner :deep(p:not(.kicker)) { color: #c9cdd3; font-size: var(--fs-lead); max-width: 44ch; }
.inner :deep(strong) { color: #fff; }
</style>
