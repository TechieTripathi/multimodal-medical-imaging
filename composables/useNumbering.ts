import { computed } from 'vue'
import { slides } from '#slidev/slides'

// Layouts that are not numbered core slides: the institutional cover, the dark section openers
// and the Sources appendix. Core slide numbers skip them.
export const UNNUMBERED = ['institution-cover', 'opener', 'sources']

const layouts = computed(() => slides.value.map(r => String(r.meta?.slide?.frontmatter?.layout ?? 'default')))

/** Core number of the slide at 1-based Slidev page `page`, or undefined for unnumbered slides. */
export function coreNumber(page: number): number | undefined {
  const ls = layouts.value
  if (UNNUMBERED.includes(ls[page - 1]))
    return undefined
  return ls.slice(0, page).filter(l => !UNNUMBERED.includes(l)).length
}

/** 1-based position within the Sources appendix, or undefined. */
export function appendixNumber(page: number): number | undefined {
  const ls = layouts.value
  if (ls[page - 1] !== 'sources')
    return undefined
  return ls.slice(0, page).filter(l => l === 'sources').length
}
