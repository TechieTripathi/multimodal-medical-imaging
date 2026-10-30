import { computed, ref, watch } from 'vue'
import { useSlideContext } from '@slidev/client'

/**
 * Step state for an artifact driven by the presenter's clicker (Slidev clicks, so the PDF export
 * captures every state). Free controls may set the step directly with `go()`; the next clicker
 * press clears that override.
 *
 * Declare `clicks: <max>` in the slide frontmatter. `offset` skips clicks spent on v-click reveals.
 */
export function useStep(max: number, opts: { offset?: number } = {}) {
  const { $clicks } = useSlideContext()
  const offset = opts.offset ?? 0
  const manual = ref<number | null>(null)

  watch($clicks, () => { manual.value = null })

  const fromClicks = computed(() => Math.min(max, Math.max(0, ($clicks.value ?? 0) - offset)))
  const step = computed(() => manual.value ?? fromClicks.value)
  const go = (n: number) => { manual.value = Math.min(max, Math.max(0, n)) }

  return { step, max, go }
}
