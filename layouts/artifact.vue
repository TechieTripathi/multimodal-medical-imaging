<script setup lang="ts">
// Artifact slide: title (and optional one-line `sub`) on top, then one artifact centred in the
// remaining space at full size. No side captions, no shrinking (IDEA.md §4.4, §4.8).
defineProps<{ sub?: string }>()
</script>

<template>
  <div class="slidev-layout l-artifact">
    <header class="head">
      <slot name="title" />
      <p v-if="sub" class="sub">{{ sub }}</p>
    </header>
    <div class="body">
      <slot />
    </div>
  </div>
</template>

<style scoped>
.l-artifact {
  height: 100%;
  padding: 40px var(--gutter) 52px;
  display: flex;
  flex-direction: column;
  gap: var(--s4);
}
.head :deep(h1) { max-width: none; }
.head .sub { margin-top: 6px; }
.body { flex: 1 1 auto; min-height: 0; display: flex; flex-direction: column; justify-content: center; align-items: stretch; }
.body > :deep(*) { flex: 0 1 auto; }
</style>
