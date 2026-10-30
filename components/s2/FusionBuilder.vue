<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { useStep } from '../../composables/useStep'

// Artifact 9 — where image, text and numbers meet: early, intermediate or late fusion.
// Clicks walk through the three; the chips switch freely; "Text missing" shows what breaks. clicks: 2
const { step } = useStep(2)
const MODES = ['early', 'intermediate', 'late'] as const
const mode = ref<typeof MODES[number]>('early')
watch(step, s => { mode.value = MODES[s] }, { immediate: true })
const textMissing = ref(false)
const INPUTS = [{ y: 30, t: 'Image' }, { y: 125, t: 'Text' }, { y: 220, t: 'Numbers' }]
const note = computed(() => ({
  early: { what: 'Join the raw inputs, then one model learns everything.', missing: 'A blank input the model never saw in training: answers become unreliable.' },
  intermediate: { what: 'Each input gets its own encoder; their fingerprints are joined.', missing: 'The missing fingerprint can be masked out; the others still work.' },
  late: { what: 'Separate models each answer; the answers are combined.', missing: 'Simply drop one vote, but the models never learned from each other.' },
}[mode.value]))
const dim = (i: number) => textMissing.value && i === 1
</script>

<template>
  <div class="fb">
    <div class="bar">
      <button v-for="m in MODES" :key="m" class="chip" :aria-pressed="mode === m" @click="mode = m">{{ m[0].toUpperCase() + m.slice(1) }} fusion</button>
      <button class="chip miss" :aria-pressed="textMissing" @click="textMissing = !textMissing">Text missing</button>
    </div>
    <svg viewBox="0 0 760 280" class="dia" role="img" :aria-label="`${mode} fusion diagram`">
      <defs><marker id="fa" viewBox="0 0 8 8" refX="7" refY="4" markerWidth="7" markerHeight="7" orient="auto"><path d="M0 0L8 4L0 8z" class="ah" /></marker></defs>
      <g v-for="(inp, i) in INPUTS" :key="inp.t" :class="{ off: dim(i) }">
        <rect x="0" :y="inp.y" width="110" height="44" rx="5" class="in" />
        <text x="55" :y="inp.y + 28" class="tc">{{ inp.t }}</text>
      </g>
      <Transition name="fade" mode="out-in">
        <g v-if="mode === 'early'" key="e">
          <path v-for="(inp, i) in INPUTS" :key="i" :class="{ off: dim(i) }" :d="`M110 ${inp.y + 22} C 160 ${inp.y + 22}, 160 140, 200 140`" class="ln" marker-end="url(#fa)" />
          <rect x="202" y="112" width="96" height="56" rx="5" class="join" /><text x="250" y="145" class="tc s">Join</text>
          <path d="M298 140H350" class="ln" marker-end="url(#fa)" />
          <rect x="352" y="80" width="220" height="120" rx="6" class="model" /><text x="462" y="145" class="tc">One model</text>
          <path d="M572 140H630" class="ln" marker-end="url(#fa)" /><text x="690" y="145" class="tc">Answer</text>
        </g>
        <g v-else-if="mode === 'intermediate'" key="i">
          <g v-for="(inp, i) in INPUTS" :key="i" :class="{ off: dim(i) }">
            <path :d="`M110 ${inp.y + 22}H160`" class="ln" marker-end="url(#fa)" />
            <rect x="162" :y="inp.y" width="120" height="44" rx="5" class="enc" /><text x="222" :y="inp.y + 28" class="tc s">encoder</text>
            <path :d="`M282 ${inp.y + 22} C 330 ${inp.y + 22}, 330 140, 372 140`" class="ln" marker-end="url(#fa)" />
          </g>
          <rect x="374" y="112" width="96" height="56" rx="5" class="join" /><text x="422" y="145" class="tc s">Join</text>
          <path d="M470 140H500" class="ln" marker-end="url(#fa)" />
          <rect x="502" y="105" width="110" height="70" rx="6" class="model" /><text x="557" y="145" class="tc s">Model</text>
          <path d="M612 140H640" class="ln" marker-end="url(#fa)" /><text x="700" y="145" class="tc">Answer</text>
        </g>
        <g v-else key="l">
          <g v-for="(inp, i) in INPUTS" :key="i" :class="{ off: dim(i) }">
            <path :d="`M110 ${inp.y + 22}H160`" class="ln" marker-end="url(#fa)" />
            <rect x="162" :y="inp.y" width="150" height="44" rx="5" class="model" /><text x="237" :y="inp.y + 28" class="tc s">own model</text>
            <path :d="`M312 ${inp.y + 22}H340`" class="ln" marker-end="url(#fa)" />
            <text x="380" :y="inp.y + 28" class="tc s">answer</text>
            <path :d="`M420 ${inp.y + 22} C 460 ${inp.y + 22}, 460 140, 492 140`" class="ln" marker-end="url(#fa)" />
          </g>
          <rect x="494" y="112" width="120" height="56" rx="5" class="join" /><text x="554" y="145" class="tc s">Vote</text>
          <path d="M614 140H640" class="ln" marker-end="url(#fa)" /><text x="700" y="145" class="tc">Answer</text>
        </g>
      </Transition>
    </svg>
    <p class="note"><strong>{{ note.what }}</strong><span v-if="textMissing" class="warn"> If text is missing: {{ note.missing }}</span></p>
  </div>
</template>

<style scoped>
.fb { display: flex; flex-direction: column; gap: 10px; }
.bar { display: flex; gap: 8px; }
.miss { margin-left: auto; }
.dia { width: 100%; height: 260px; }
.in { fill: var(--surface); stroke: var(--ink-2); stroke-width: 1.5; }
.enc { fill: var(--accent-tint); stroke: var(--accent); stroke-width: 1.5; }
.model { fill: var(--accent); }
.model + .tc { fill: #fff; }
.join { fill: var(--surface); stroke: var(--accent); stroke-width: 1.5; stroke-dasharray: 4 3; }
.ln { fill: none; stroke: var(--ink-2); stroke-width: 1.5; }
.ah { fill: var(--ink-2); }
.tc { font: 500 18px var(--font-sans); text-anchor: middle; fill: var(--ink); }
.tc.s { font-size: 16px; }
.off { opacity: 0.25; }
.note { margin: 0; font-size: var(--fs-label); min-height: 52px; }
.warn { color: var(--warn); }
.fade-enter-active, .fade-leave-active { transition: opacity var(--dur) var(--ease); }
.fade-enter-from, .fade-leave-to { opacity: 0; }
</style>
