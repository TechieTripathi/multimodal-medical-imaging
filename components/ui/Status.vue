<script setup lang="ts">
// Status marker: color is always paired with an icon and a text label.
withDefaults(defineProps<{ state?: 'ok' | 'warn' | 'bad' | 'neutral' | 'active', label?: string, compact?: boolean }>(), { state: 'neutral' })
</script>

<template>
  <span class="status" :class="[state, { compact }]">
    <svg width="14" height="14" viewBox="0 0 14 14" aria-hidden="true">
      <template v-if="state === 'ok'"><circle cx="7" cy="7" r="6.5" fill="currentColor" /><path d="M4 7.2l2 2 4-4.4" stroke="#fff" stroke-width="1.6" fill="none" stroke-linecap="round" stroke-linejoin="round" /></template>
      <template v-else-if="state === 'warn'"><path d="M7 1l6.2 11H.8z" fill="currentColor" /><path d="M7 5v3.2" stroke="#fff" stroke-width="1.6" stroke-linecap="round" /><circle cx="7" cy="10.2" r="0.9" fill="#fff" /></template>
      <template v-else-if="state === 'bad'"><circle cx="7" cy="7" r="6.5" fill="currentColor" /><path d="M4.6 4.6l4.8 4.8M9.4 4.6l-4.8 4.8" stroke="#fff" stroke-width="1.6" stroke-linecap="round" /></template>
      <template v-else-if="state === 'active'"><circle cx="7" cy="7" r="6.5" fill="currentColor" /><circle cx="7" cy="7" r="2.5" fill="#fff" /></template>
      <template v-else><circle cx="7" cy="7" r="5.8" fill="none" stroke="currentColor" stroke-width="1.4" /></template>
    </svg>
    <span v-if="label || $slots.default" class="txt"><slot>{{ label }}</slot></span>
  </span>
</template>

<style scoped>
.status {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  font: 500 var(--fs-label)/1.2 var(--font-sans);
  padding: 3px 9px 3px 6px;
  border-radius: 999px;
  white-space: nowrap;
}
.compact { padding: 0; background: none !important; }
.ok { color: var(--ok); background: var(--ok-tint); }
.warn { color: var(--warn); background: var(--warn-tint); }
.bad { color: var(--bad); background: var(--bad-tint); }
.neutral { color: var(--neutral); background: var(--neutral-tint); }
.active { color: var(--accent); background: var(--accent-tint); }
.txt { color: var(--ink); }
</style>
