<script setup lang="ts">
import { computed, ref } from 'vue'
import { useStep } from '../../composables/useStep'
import { loadVocab, tokenize } from '../../composables/wordpiece'
import vocabRaw from '../../data/biomedclip/vocab.txt?raw'

// Artifact 4 — the real BiomedCLIP tokenizer (BiomedBERT WordPiece vocabulary), running in the page.
// Click 1 splits the sentence into tokens; click 2 shows each token's number. Typing re-tokenizes. clicks: 2
const { step } = useStep(2)
const vocab = loadVocab(vocabRaw)
const presets = ['Solid spiculated nodule in the left lower lobe.', 'No acute cardiopulmonary abnormality.', 'Cardiomegaly with small bilateral pleural effusions.']
const text = ref(presets[0])
const toks = computed(() => tokenize(text.value, vocab))
</script>

<template>
  <div class="tk">
    <div class="presets">
      <button v-for="p in presets" :key="p" class="chip" :aria-pressed="text === p" @click="text = p">{{ p.split(' ').slice(0, 2).join(' ') }}…</button>
    </div>
    <input v-model="text" class="input" aria-label="Sentence to tokenize" @keydown.stop>
    <TransitionGroup v-if="step >= 1" tag="div" name="tok" class="tokens">
      <span v-for="(t, i) in toks" :key="`${i}-${t.text}`" class="tok" :class="{ special: t.text.startsWith('['), piece: t.text.startsWith('##') }" :style="{ transitionDelay: `${i * 40}ms` }">
        <span class="t">{{ t.text }}</span>
        <span class="id" :class="{ show: step >= 2 }">{{ t.id }}</span>
      </span>
    </TransitionGroup>
    <p class="count rv" :class="{ on: step >= 1 }">{{ toks.length }} tokens · this model reads at most 256</p>
  </div>
</template>

<style scoped>
.tk { display: flex; flex-direction: column; gap: 18px; }
.presets { display: flex; gap: 8px; }
.input { font: 400 var(--fs-body) var(--font-sans); padding: 10px 14px; border: 1px solid var(--rule-strong); border-radius: var(--radius); background: var(--surface); color: var(--ink); width: 100%; }
.tokens { display: flex; flex-wrap: wrap; gap: 8px; min-height: 120px; align-content: flex-start; }
.tok { display: flex; flex-direction: column; align-items: center; gap: 4px; }
.t { font: 500 var(--fs-label) var(--font-mono); padding: 6px 10px; border-radius: var(--radius-sm); background: var(--accent-tint); color: var(--ink); }
.special .t { background: var(--stage); color: var(--ink-3); }
.piece .t { background: var(--warn-tint); }
.id { font: 400 15px var(--font-mono); color: var(--ink-2); opacity: 0; transition: opacity var(--dur) var(--ease); }
.id.show { opacity: 1; }
.count { font-size: var(--fs-label); color: var(--ink-2); margin: 0; }
.tok-enter-active { transition: opacity var(--dur) var(--ease), transform var(--dur) var(--ease); }
.tok-enter-from { opacity: 0; transform: translateY(8px); }
</style>
