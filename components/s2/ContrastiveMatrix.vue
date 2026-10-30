<script setup lang="ts">
import { computed, ref } from 'vue'
import { useStep } from '../../composables/useStep'
import run from '../../data/runs/biomedclip_contrastive.json'

// Artifact 6 — contrastive training on a batch of image–report pairs. Steps 1–2 are a cartoon of
// training (matching pairs pulled together, the rest pushed apart); step 3 shows the real similarity
// matrix BiomedCLIP gives these six real pairs. Click a cell to see its pair. clicks: 3
const { step } = useStep(3)
const thumbs = import.meta.glob('../../data/imaging/thumbs/pair_*.png', { eager: true, import: 'default' }) as Record<string, string>
const src = (p: string) => thumbs[`../../data/imaging/${p}`]
const n = run.pairs.length
const S = run.similarity
const lo = Math.min(...S.flat())
const hi = Math.max(...S.flat())
const cartoon = (i: number, j: number, t: number) => (i === j ? 0.35 + 0.6 * t : 0.35 - 0.25 * t)
const value = (i: number, j: number) => {
  if (step.value === 0) return 0
  if (step.value === 1) return 0.35
  if (step.value === 2) return cartoon(i, j, 1)
  return (S[i][j] - lo) / (hi - lo)
}
const sel = ref<[number, number] | null>(null)
const picked = computed(() => sel.value ? { img: run.pairs[sel.value[0]], txt: run.pairs[sel.value[1]], s: S[sel.value[0]][sel.value[1]] } : null)
const correct = run.diagonal_is_max_in_row.filter(Boolean).length
const caption = computed(() => [
  'Six X-rays and the reports written about them',
  'Before training: every picture looks equally like every report',
  'Training pulls matching pairs together and pushes the rest apart',
  `Real BiomedCLIP scores: the right report scores highest for ${correct} of ${n} X-rays`,
][step.value])
</script>

<template>
  <div class="cm">
    <div class="mat" :style="{ gridTemplateColumns: `300px repeat(${n}, 52px)` }">
      <span />
      <img v-for="(p, j) in run.pairs" :key="`c${j}`" :src="src(p.image)" alt="" class="th">
      <template v-for="(p, i) in run.pairs" :key="`r${i}`">
        <span class="txt" :title="p.text">{{ p.text }}</span>
        <button
          v-for="j in n" :key="j" class="cell" :class="{ diag: i === j - 1 && step >= 2, sel: sel && sel[1] === i && sel[0] === j - 1 }"
          :style="{ background: `color-mix(in srgb, var(--accent) ${Math.round(value(j - 1, i) * 100)}%, var(--surface))` }"
          :aria-label="`Image ${j}, report ${i + 1}`" @click="sel = [j - 1, i]"
        >
          <span v-if="step >= 3" class="v" :style="{ color: value(j - 1, i) > 0.55 ? '#fff' : 'var(--ink)' }">{{ S[j - 1][i].toFixed(2) }}</span>
        </button>
      </template>
    </div>
    <div class="side">
      <p class="cap">{{ caption }}</p>
      <div v-if="picked && step >= 3" class="card">
        <img :src="src(picked.img.image)" alt="">
        <p>“{{ picked.txt.text }}”</p>
        <p class="muted">cosine {{ picked.s.toFixed(3) }}</p>
      </div>
    </div>
  </div>
</template>

<style scoped>
.cm { display: grid; grid-template-columns: auto 1fr; gap: 28px; align-items: center; }
.mat { display: grid; grid-auto-rows: 50px; gap: 3px; align-items: center; }
.th { width: 50px; height: 50px; object-fit: cover; border-radius: 3px; background: var(--image-mat); }
.txt { font-size: 15px; line-height: 1.2; color: var(--ink); overflow: hidden; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; padding-right: 8px; }
.cell { width: 50px; height: 50px; border: 1px solid var(--rule); border-radius: 3px; cursor: pointer; padding: 0; transition: background 0.6s var(--ease); }
.cell.diag { outline: 2px solid var(--ink); outline-offset: -2px; }
.cell.sel { outline: 3px solid #ffc400; }
.v { font: 500 13px var(--font-mono); }
.cap { font-size: var(--fs-label); margin: 0 0 14px; }
.card { display: flex; flex-direction: column; gap: 6px; padding: 12px; }
.card img { width: 110px; height: 110px; object-fit: cover; }
.card p { margin: 0; font-size: 15px; }
</style>
