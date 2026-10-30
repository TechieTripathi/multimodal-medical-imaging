<script setup lang="ts">
import { computed } from 'vue'
import { useSlideContext } from '@slidev/client'
import { appendixNumber, coreNumber } from './composables/useNumbering'
import { refNumber, slideSources } from './composables/useRefs'
import HonestyTag from './components/ui/HonestyTag.vue'

// Quiet footer: the slide's one honesty label (or nothing), its source numbers, and the slide number.
const { $frontmatter, $page } = useSlideContext()
const show = computed(() => $frontmatter.chrome !== false && $frontmatter.layout !== 'opener')
const nums = computed(() =>
  slideSources($frontmatter)
    .map(k => refNumber(k))
    .filter((n): n is number => n !== undefined)
    .sort((a, b) => a - b),
)
const label = computed(() => {
  const a = appendixNumber($page.value)
  if (a)
    return `A${a}`
  return coreNumber($page.value)
})
</script>

<template>
  <footer v-if="show" class="foot">
    <span class="left">
      <HonestyTag v-if="$frontmatter.tag" :kind="$frontmatter.tag" :text="$frontmatter.tagText" />
    </span>
    <span v-if="nums.length" class="src">Sources {{ nums.map(n => `[${n}]`).join(' ') }}</span>
    <span class="no">{{ label }}</span>
  </footer>
</template>

<style scoped>
.foot {
  position: absolute;
  left: var(--gutter);
  right: var(--gutter);
  bottom: 14px;
  display: flex;
  align-items: center;
  gap: 20px;
  font: 400 var(--fs-micro)/1.2 var(--font-sans);
  color: var(--ink-3);
  z-index: 10;
}
.left { flex: 1 1 auto; min-width: 0; }
.src { flex: 0 0 auto; }
.no { flex: 0 0 auto; font-variant-numeric: tabular-nums; color: var(--ink-2); font-weight: 500; min-width: 2em; text-align: right; }
</style>
