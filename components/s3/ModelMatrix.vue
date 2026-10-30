<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { useStep } from '../../composables/useStep'
import ModelCard from '../ui/ModelCard.vue'

// Artifact 12 — which model does what. Grouped by task so no more than three rows show at once;
// click a model for its card. Licences checked on the model pages and repositories, October 2026. clicks: 3
const { step } = useStep(3)
interface M { name: string, io: string, lic: string, card: [string, string][] }
const TASKS: { task: string, models: M[] }[] = [
  { task: 'Match images and text', models: [
    { name: 'BiomedCLIP', io: 'image + text → similarity', lic: 'MIT', card: [['Trained on', '15 million figure–caption pairs from PubMed Central'], ['Good for', 'Search, zero-shot labels, fingerprints for other models'], ['Limits', 'Scores are not probabilities; figures differ from clinical images']] },
    { name: 'MedCLIP', io: 'chest X-ray + text → similarity', lic: 'none stated', card: [['Trained on', 'Chest X-rays and texts that need not be paired'], ['Good for', 'Learning from smaller medical datasets'], ['Limits', 'Chest X-ray only; research code']] },
  ] },
  { task: 'Find conditions', models: [
    { name: 'CheXzero', io: 'chest X-ray + prompts → scores', lic: 'MIT', card: [['Trained on', 'Chest X-rays and their reports, no hand labels'], ['Good for', 'Zero-shot detection of chest X-ray findings'], ['Limits', 'Chest X-ray only; accuracy varies by finding']] },
  ] },
  { task: 'Outline structures', models: [
    { name: 'MedSAM', io: 'image + box → outline', lic: 'Apache-2.0', card: [['Trained on', '1.57 million image–outline pairs, 10 kinds of scan'], ['Good for', 'Fast outlining when a person points to the target'], ['Limits', 'Needs a box; 2D slices; can miss fine edges']] },
    { name: 'TotalSegmentator', io: 'CT → 100+ labelled structures', lic: 'Apache-2.0', card: [['Trained on', '1,204 CT scans with 104 outlined structures'], ['Good for', 'Organ volumes and anatomy, fully automatic'], ['Limits', 'Does not find disease; some extra tasks need a separate licence']] },
  ] },
  { task: 'Describe and answer', models: [
    { name: 'LLaVA-Med', io: 'image + question → text', lic: 'Apache-2.0', card: [['Trained on', 'PubMed Central figures and captions, plus GPT-4-written dialogues'], ['Good for', 'Research on medical visual question answering'], ['Limits', 'Can write fluent, wrong text; research only']] },
    { name: 'MedGemma', io: 'image + text → text', lic: 'HAI-DEF terms', card: [['Trained on', 'Medical images and text on top of Gemma 3'], ['Good for', 'Starting point for medical image–text applications'], ['Limits', 'Not for clinical use without validation; gated download']] },
  ] },
]
const t = ref(0)
watch(step, s => { t.value = s }, { immediate: true })
const open = ref<string | null>(null)
watch(t, () => { open.value = null })
const card = computed(() => TASKS[t.value].models.find(m => m.name === open.value))
</script>

<template>
  <div class="mm">
    <div class="tabs">
      <button v-for="(g, i) in TASKS" :key="g.task" class="chip" :aria-pressed="t === i" @click="t = i">{{ g.task }}</button>
    </div>
    <div class="body">
      <table>
        <thead><tr><th>Model</th><th>Input → output</th><th>Licence</th></tr></thead>
        <TransitionGroup tag="tbody" name="row">
          <tr v-for="m in TASKS[t].models" :key="m.name" :class="{ sel: open === m.name }" @click="open = m.name">
            <td><strong>{{ m.name }}</strong></td><td>{{ m.io }}</td><td>{{ m.lic }}</td>
          </tr>
        </TransitionGroup>
      </table>
      <div v-if="card" class="card"><h3>{{ card.name }}</h3><ModelCard :rows="card.card" /></div>
      <p v-else class="hint">All are research models, not cleared medical devices.</p>
    </div>
  </div>
</template>

<style scoped>
.mm { display: flex; flex-direction: column; gap: 18px; }
.tabs { display: flex; gap: 8px; flex-wrap: wrap; }
.body { display: grid; grid-template-columns: 1.45fr 1fr; gap: 24px; align-items: start; }
table { font-size: var(--fs-label); }
td:last-child { white-space: nowrap; }
tbody tr { cursor: pointer; }
tr.sel td { background: var(--accent-tint); }
.hint { font-size: var(--fs-label); color: var(--ink-2); margin: 0; }
.row-enter-active { transition: opacity var(--dur) var(--ease); }
.row-enter-from { opacity: 0; }
.card :deep(.mc) { grid-template-columns: 100px 1fr; }
</style>
