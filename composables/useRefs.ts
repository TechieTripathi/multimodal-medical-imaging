import { computed } from 'vue'
import { slides } from '#slidev/slides'
import type { Ref } from '../data/refs/types'

// Merge every data/refs/*.ts file that exports `refs`. First definition of a key wins.
const modules = import.meta.glob<{ refs?: Ref[] }>('../data/refs/*.ts', { eager: true })
const byKey = new Map<string, Ref>()
for (const path of Object.keys(modules).sort()) {
  for (const r of modules[path].refs ?? []) {
    if (!byKey.has(r.key))
      byKey.set(r.key, r)
  }
}

function slideSources(fm: Record<string, any> | undefined): string[] {
  const s = fm?.sources
  return Array.isArray(s) ? s : typeof s === 'string' ? [s] : []
}

/**
 * Sources are numbered in order of first citation across the deck
 * (frontmatter `sources:` lists, in slide order). Uncited sources follow.
 */
export const orderedRefs = computed(() => {
  const order: string[] = []
  for (const route of slides.value) {
    for (const k of slideSources(route.meta?.slide?.frontmatter)) {
      if (!order.includes(k))
        order.push(k)
    }
  }
  for (const k of byKey.keys()) {
    if (!order.includes(k))
      order.push(k)
  }
  return order.filter(k => byKey.has(k)).map((k, i) => ({ n: i + 1, ...byKey.get(k)! }))
})

export const missingKeys = computed(() => {
  const missing = new Set<string>()
  for (const route of slides.value) {
    for (const k of slideSources(route.meta?.slide?.frontmatter)) {
      if (!byKey.has(k))
        missing.add(k)
    }
  }
  return [...missing]
})

export function refNumber(key: string): number | undefined {
  return orderedRefs.value.find(r => r.key === key)?.n
}

export { slideSources }
