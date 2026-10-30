<script setup lang="ts">
// Title slide. Content is fully authored in the slide markdown or a component.
</script>

<template>
  <div class="slidev-layout l-cover">
    <slot />
  </div>
</template>

<style scoped>
.l-cover {
  height: 100%;
  padding: 56px var(--gutter) 48px;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}
</style>
