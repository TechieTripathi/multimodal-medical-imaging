<script setup lang="ts">
// Appendix: numbered source list. Content is a <SourcesList> component.
</script>

<template>
  <div class="slidev-layout l-sources">
    <slot />
  </div>
</template>

<style scoped>
.l-sources {
  height: 100%;
  padding: 44px var(--gutter) 40px;
  display: flex;
  flex-direction: column;
  gap: var(--s4);
}
.l-sources :deep(h1) { font-size: 30px; }
</style>
