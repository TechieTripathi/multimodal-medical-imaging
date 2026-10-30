<script setup lang="ts">
import zerozeta from '../assets/logos/zerozeta.png'
import srhu from '../assets/logos/srhu-naac.png'
import iitr from '../assets/logos/iit-roorkee.png'

// Institutional cover, matching the AI-model-evaluation deck's cover (logos, session title, centre,
// presenter, affiliation, date, navy band). Built on that deck's 1280×720 canvas and scaled to
// this deck's 980px canvas so proportions match exactly. Text comes from frontmatter.
withDefaults(defineProps<{
  session?: string
  heading?: string
  date?: string
}>(), { session: '', heading: '', date: '' })
</script>

<template>
  <div class="slidev-layout icover">
    <div class="cv">
      <div class="cvlogos">
        <span class="cvlogo l"><img :src="zerozeta" alt="ZeroZeta"></span>
        <span class="cvlogo c"><img :src="srhu" alt="Swami Rama Himalayan University — NAAC A+"></span>
        <span class="cvlogo r"><img :src="iitr" alt="Indian Institute of Technology Roorkee"></span>
      </div>

      <h1 class="cvtitle"><span v-if="session" class="cvsession">{{ session }}: </span>{{ heading }}</h1>

      <div class="cvcentre">Center for Artificial Intelligence Research</div>
      <div class="cvname">Prof. (Dr.) Neel Mani</div>
      <div class="cvaff">
        <span>PhD (DCU, Ireland), Post Doc(UCD, Ireland)</span>
        <span>Department of Computer Science &amp; Engineering</span>
        <span>School of Science &amp; Technology</span>
        <span>Swami Rama Himalayan University (SRHU)</span>
        <span>Dehradun - 248016</span>
      </div>
      <div v-if="date" class="cvdate">{{ date }}</div>

      <span class="cvmark"><img :src="srhu" alt="SRHU — NAAC A+"></span>
      <span class="cvband" aria-hidden="true" />
      <slot />
    </div>
  </div>
</template>

<style scoped>
/* 'Inter Cover' is defined in styles/cover-fonts.css. */

.icover { height: 100%; padding: 0; background: #fff; overflow: hidden; position: relative; }
/* Source deck canvas is 1280×720; this deck is 980 wide → 0.765625. */
.cv {
  position: absolute; left: 0; top: 0;
  width: 1280px; height: 720px; zoom: 0.765625;
  display: flex; flex-direction: column; align-items: center; text-align: center;
  padding: 14px 26px 0; box-sizing: border-box;
  font-family: 'Inter Cover', Inter, system-ui, sans-serif; color: #0E161E;
}
.cvlogos { width: 100%; display: flex; align-items: flex-start; justify-content: space-between; gap: 24px; flex: none; }
.cvlogo { display: flex; align-items: flex-start; min-height: 150px; flex: none; }
.cvlogo.l img { width: 270px; height: auto; margin-top: 14px; }
.cvlogo.c img { height: 172px; width: auto; }
.cvlogo.r img { height: 140px; width: auto; }
.cvtitle {
  font-family: 'Inter Cover', Inter, system-ui, sans-serif; font-size: 44px; font-weight: 700;
  letter-spacing: -0.012em; line-height: 1.15; color: #1F3864; margin: 22px 0 0; max-width: 1100px; flex: none;
}
.cvcentre {
  font-family: Georgia, 'Times New Roman', serif; font-size: 27px; line-height: 1.2; color: #0E161E;
  margin-top: 44px; padding: 0 32px 9px; border-bottom: 2px solid #0E161E; flex: none;
}
.cvname { font-size: 22px; font-weight: 700; color: #1F3864; margin-top: 10px; flex: none; }
.cvaff {
  display: flex; flex-direction: column; gap: 3px; margin-top: 5px; flex: none;
  font-size: 14.5px; font-weight: 700; color: #2E74B5; line-height: 1.35;
}
.cvdate { font-size: 19px; color: #0E161E; margin-top: 8px; flex: none; }
.cvband { position: absolute; left: 285px; right: 0; bottom: 0; height: 44px; background: #1F3864; }
.cvmark { position: absolute; left: 18px; bottom: 12px; }
.cvmark img { height: 66px; width: auto; }
</style>
