<script setup lang="ts">
// A short model card: the same six questions for every model (IDEA.md §7, Section 3).
// `reveal` shows rows one at a time (pass the current step), otherwise all rows show.
defineProps<{ rows: [string, string][], reveal?: number }>()
</script>

<template>
  <dl class="mc">
    <template v-for="([k, v], i) in rows" :key="k">
      <dt class="rv" :class="{ on: reveal === undefined || reveal >= i }">{{ k }}</dt>
      <dd class="rv" :class="{ on: reveal === undefined || reveal >= i }">{{ v }}</dd>
    </template>
  </dl>
</template>

<style scoped>
.mc { display: grid; grid-template-columns: 150px 1fr; gap: 10px 18px; margin: 0; align-items: baseline; }
dt { font-size: var(--fs-label); color: var(--ink-2); }
dd { margin: 0; font-size: var(--fs-label); color: var(--ink); line-height: 1.3; }
</style>
