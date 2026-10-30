<script setup lang="ts">
import { useSlideContext } from '@slidev/client'

// Application slide (Section 5): one picture on the left, the same five questions on the right,
// revealed one per click. The default slot is the picture. clicks: rows.length - 1
defineProps<{ rows: [string, string][], illustrative?: boolean }>()
const { $clicks } = useSlideContext()
const KIND: Record<string, string> = { Benefit: 'ok', Limit: 'bad' }
</script>

<template>
  <div class="app">
    <div class="vis"><slot /></div>
    <dl>
      <template v-for="([k, v], i) in rows" :key="k">
        <dt class="rv" :class="[{ on: $clicks >= i || i === 0 }, KIND[k]]">{{ k }}</dt>
        <dd class="rv" :class="{ on: $clicks >= i || i === 0 }">{{ v }}</dd>
      </template>
    </dl>
  </div>
  <p v-if="illustrative" class="ill">Scenario is illustrative, not a validated clinical workflow</p>
</template>

<style scoped>
.app { display: grid; grid-template-columns: 340px 1fr; gap: 36px; align-items: center; }
.vis { min-width: 0; }
dl { display: grid; grid-template-columns: 110px 1fr; gap: 12px 16px; margin: 0; align-items: baseline; }
dt { font-size: var(--fs-label); color: var(--ink-2); font-weight: 500; }
dt.ok { color: var(--ok); }
dt.bad { color: var(--bad); }
dd { margin: 0; font-size: var(--fs-label); line-height: 1.3; }
.ill { position: absolute; right: var(--gutter); bottom: 44px; margin: 0; font-size: var(--fs-micro); color: var(--ink-3); }
</style>
