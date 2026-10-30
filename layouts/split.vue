<script setup lang="ts">
// Two columns under a title. Default slot = title (+ sub); `::left::` and `::right::` named slots.
withDefaults(defineProps<{ ratio?: string }>(), { ratio: '1fr 1fr' })
</script>

<template>
  <div class="slidev-layout l-split">
    <div class="head"><slot /></div>
    <div class="cols" :style="{ gridTemplateColumns: ratio }">
      <div class="col"><slot name="left" /></div>
      <div class="col"><slot name="right" /></div>
    </div>
  </div>
</template>

<style scoped>
.l-split {
  height: 100%;
  padding: 44px var(--gutter) 52px;
  display: flex;
  flex-direction: column;
  gap: var(--s5);
}
.cols { flex: 1 1 auto; display: grid; gap: var(--s6); min-height: 0; align-items: start; padding-top: var(--s4); }
.col { min-width: 0; display: flex; flex-direction: column; gap: var(--s4); justify-content: center; }
</style>
