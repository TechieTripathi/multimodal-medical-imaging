<script setup lang="ts">
// Standard slide: title (markdown `#`), optional <p class="sub"> directly under it, then one visual.
</script>

<template>
  <div class="slidev-layout l-default">
    <div class="body">
      <slot />
    </div>
  </div>
</template>

<style scoped>
.l-default {
  height: 100%;
  padding: 44px var(--gutter) 52px;
  display: flex;
  flex-direction: column;
}
.body { flex: 1 1 auto; display: flex; flex-direction: column; gap: var(--s5); min-height: 0; }
</style>
