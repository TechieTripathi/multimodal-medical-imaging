<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { useStep } from '../../composables/useStep'
import cells from '../../data/notebook/cells.json'
import run from '../../data/runs/notebook.json'
import ColabLink from '../ui/ColabLink.vue'

// Demo E — two Python cells of the companion notebook (Workflow E), exactly as they ran in Jupyter,
// with their printed insights and figures. The same code runs from a terminal as dicom_insights.py.
// Clicks: first cell's code → its output → second cell's code → its output. clicks: 3
const props = defineProps<{ cells: [keyof typeof cells, keyof typeof cells], script: [string, string] }>()
const { step } = useStep(3)
const figs = import.meta.glob('../../data/notebook/*.png', { eager: true, import: 'default' }) as Record<string, string>
const which = ref(0)
const showOut = ref(false)
watch(step, (s) => { which.value = s >= 2 ? 1 : 0; showOut.value = s === 1 || s === 3 }, { immediate: true })
const cell = computed(() => cells[props.cells[which.value]])
const fig = computed(() => cell.value.figures[0] ? figs[`../../data/notebook/${cell.value.figures[0]}`] : null)
const insight = computed(() => cell.value.output.split('\n').filter(l => l.startsWith('Insight:')).map(l => l.replace('Insight: ', '')).map(l => l[0].toUpperCase() + l.slice(1)))
const text = computed(() => cell.value.output.split('\n').filter(l => !l.startsWith('Insight:') && !l.startsWith('figure saved')).join('\n'))
const pick = (i: number) => { which.value = i; showOut.value = true }
</script>

<template>
  <div class="np">
    <div class="bar">
      <button v-for="(c, i) in props.cells" :key="c" class="chip" :aria-pressed="which === i" @click="pick(i)">cell {{ c }}</button>
      <span class="cmd mono">python dicom_insights.py {{ props.script[which] }}</span>
      <ColabLink which="dicom" label="Open in Colab" small />
    </div>
    <pre class="code" :class="{ small: showOut }">{{ cell.code }}</pre>
    <div v-if="showOut" class="out rv on">
      <img v-if="fig" :src="fig" alt="Figure produced by this notebook cell" class="fig" :class="{ wide: props.cells[which] === 'E1' }">
      <div class="txt">
        <p class="hd">output · run {{ run.run_date }} on {{ run.device }}</p>
        <pre class="term">{{ text }}</pre>
        <p v-for="s in insight" :key="s" class="say">{{ s }}</p>
      </div>
    </div>
  </div>
</template>

<style scoped>
.np { display: flex; flex-direction: column; gap: 8px; }
.bar { display: flex; gap: 8px; align-items: center; }
.bar .chip { padding: 5px 12px; font-size: 15px; }
.cmd { margin-left: auto; margin-right: 4px; font-size: 14px; background: var(--night); color: #e8eaed; padding: 5px 10px; border-radius: 4px; }
.code { margin: 0; font: 400 13px/1.45 var(--font-mono); background: var(--surface); border: 1px solid var(--rule); border-radius: var(--radius); padding: 8px 12px; white-space: pre-wrap; max-height: 330px; overflow: auto; transition: max-height var(--dur) var(--ease); }
.code.small { max-height: 58px; -webkit-mask-image: linear-gradient(#000 50%, transparent); mask-image: linear-gradient(#000 50%, transparent); }
.out { display: flex; gap: 16px; align-items: flex-start; }
.fig { height: 230px; border: 1px solid var(--rule); border-radius: var(--radius); background: #fff; }
.fig.wide { height: auto; width: 430px; }
.txt { flex: 1; min-width: 0; display: flex; flex-direction: column; gap: 6px; }
.hd { font-size: 13px; color: var(--ink-3); margin: 0; }
.term { margin: 0; font: 400 13.5px/1.4 var(--font-mono); background: var(--night); color: #e8eaed; border-radius: var(--radius); padding: 8px 10px; white-space: pre; overflow-x: auto; }
.say { margin: 0; font-size: 17px; font-weight: 600; color: var(--accent); }
</style>
