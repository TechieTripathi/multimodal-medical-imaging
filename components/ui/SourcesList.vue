<script setup lang="ts">
import { computed } from 'vue'
import { missingKeys, orderedRefs } from '../../composables/useRefs'

// One page of the numbered source list (numbered by first citation in the deck).
const props = withDefaults(defineProps<{ page?: number, perPage?: number }>(), { page: 1, perPage: 16 })
const items = computed(() => orderedRefs.value.slice((props.page - 1) * props.perPage, props.page * props.perPage))
const total = computed(() => orderedRefs.value.length)
const pages = computed(() => Math.ceil(total.value / props.perPage))

// Keep entries compact: at most three named authors, then "et al."
function shortAuthors(a: string) {
  if (a.length <= 60)
    return a
  const m = a.match(/^[^,]+,\s(?:[A-ZÀ-ŽŁ][a-z]?\.\s?-?\s?)+/)
  return m ? `${m[0].trim().replace(/,$/, '')} et al.` : a
}
const shortUrl = (u: string) => u.replace(/^https?:\/\/(www\.)?/, '').replace(/\/$/, '')
</script>

<template>
  <ol class="sources">
    <li v-for="r in items" :key="r.key">
      <span class="n">{{ r.n }}</span>
      <span class="entry">
        {{ shortAuthors(r.authors) }} ({{ r.year }}). <em>{{ r.title }}</em>. {{ r.venue }}.
        <a :href="r.url" target="_blank" rel="noopener">{{ shortUrl(r.url) }}</a>
      </span>
    </li>
  </ol>
  <p class="meta">
    Page {{ page }} of {{ pages }} · {{ total }} sources, numbered in order of first citation · links checked October 2026
    <span v-if="missingKeys.length" class="miss"> · Missing keys: {{ missingKeys.join(', ') }}</span>
  </p>
</template>

<style scoped>
.sources { list-style: none; padding: 0; margin: 0; columns: 2; column-fill: auto; height: 412px; column-gap: 32px; font-size: 14px; line-height: 1.32; flex: 1 1 auto; min-height: 0; }
.sources li { break-inside: avoid; display: flex; gap: 7px; margin: 0 0 6px; padding: 0; font-size: 14px; line-height: 1.32; }
.n { flex: 0 0 22px; text-align: right; font-weight: 600; color: var(--accent); font-variant-numeric: tabular-nums; }
.entry { color: var(--ink); min-width: 0; }
.entry a { color: var(--ink-2); overflow-wrap: anywhere; text-decoration: none; border: none; }
.meta { font-size: var(--fs-micro); color: var(--ink-3); margin: 0; }
.miss { color: var(--bad); font-weight: 600; }
</style>
