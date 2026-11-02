# Multimodal AI Models for Medical Imaging Analysis

A 66-slide, two-hour Faculty Development Program session, built with [Slidev](https://sli.dev) (Vue 3), with a companion Jupyter notebook. The content specification is [IDEA.md](IDEA.md).

The deck follows one real, de-identified patient (LIDC-IDRI-0001: a chest CT, a chest X-ray and four radiologists' outlines and ratings) through image representation, DICOM, models, demonstrations and responsible use. Every visual carries one honesty label: real image, real model output, published result, illustrative, simulated or teaching picture. Every "real model output" comes from a run file in `data/runs/`, produced by the scripts in `notebook/`.

## Requirements

- Node.js 20 or later (tested with Node 22). Run `npm install` once; for PDF export also `npx playwright install chromium`.
- For the notebook and for rebuilding the data: Python 3.11; see [notebook/README.md](notebook/README.md).

## Present

```bash
npm run dev            # http://localhost:3030
```

- Presenter view with speaker notes and timer: `http://localhost:3030/presenter`
- Advance with → / space / clicker; interactive slides follow the clicker, and their sliders and buttons also work.
- The dark section openers and the institutional cover are not numbered; the 66 core slides are.

### Offline delivery

```bash
npm run build                                  # static site in exports/spa
npx vite preview --outDir exports/spa          # or serve exports/spa with any static server
```

Fonts, images, data and model outputs are bundled; no network is needed. The live notebook runs in a separate window; the demo slides show the same run's saved output as the fallback.

## Export

```bash
npm run export           # every click state, one page each
npm run export:handout   # each slide once, final state
npm run export:notes     # speaker notes
```

## Edit

| What | Where |
|---|---|
| Cover (session label, date), title slide, section order | `slides.md` (cover layout: `layouts/institution-cover.vue`) |
| Slides, one file per section | `pages/01-problem.md` … `pages/07-responsible.md`; Sources appendix `pages/99-sources.md` |
| Interactive artifacts | `components/s1` … `components/s7`; shared parts in `components/ui` |
| Real image assets (derived, small) | `data/imaging/` (built by `notebook/prepare_deck_assets.py`) |
| Model results shown on slides | `data/runs/*.json` (built by `notebook/run_*.py` and the notebook) |
| Notebook cells shown on demo slides | `data/notebook/` (built by `notebook/build_notebook.py --extract`) |
| Real DICOM sample pack (viewer, demos, downloads) | `public/dicom/` (built by `prepare_deck_assets.py dicom_examples`); in-browser reader `composables/dicom.ts` (images and DICOM SEG) |
| Python analyses on DICOM (Demo E) | Notebook Workflow E (cells E0–E4) and `notebook/dicom_insights.py`, generated from the same cells by `build_notebook.py` |
| Sources | `data/refs/*.ts`; list keys in a slide's `sources:` frontmatter |
| Colours, type sizes | `styles/tokens.css` (series theme, larger type scale) |
| Honesty label | `tag:` and `tagText:` in a slide's frontmatter; `actual` also needs `run:` |

Speaker notes are the HTML comment at the end of each slide (Time, Objective, Say, Example, Try / Notice, Ask, Caveat, Transition, Sources; demo slides add Steps, Expected observations, Likely failure modes, Fallback).

## Checks

```bash
npm run check                                       # 66 slides, sections, notes, citation keys, honesty labels, run files, word limits, timing = 120 min
npm run check:urls                                  # every source URL resolves
node --experimental-strip-types scripts/test-wordpiece.mjs   # in-page tokenizer matches BiomedCLIP's
node --experimental-strip-types scripts/test-dicom.mjs       # in-browser DICOM reader matches pydicom; Demo E outputs match the reference values
node scripts/shot.mjs <port> <outDir> 12:0 12:3     # screenshot slides at click states (page numbers include cover and openers)
node scripts/contact-sheet.mjs <port> <outDir> 1 71 # first and last state of every page
```

## Data and honesty

- Real DICOM is shipped only as seven **teaching copies** in `public/dicom/` (CT, X-ray, MRI, mammogram, ultrasound cine, PET, and the PET/CT's CT): private tags removed, pixels downsampled where needed, new UIDs, and each change written into the file's DerivationDescription. All come from CC BY collections at TCIA. Everything else is small derived arrays and images.
- Burned-in letters beside the X-ray's laterality marker were masked. Identifiers in the public data were already removed by TCIA.
- Indiana University X-rays are shown unmodified; their licence on Open-i should be confirmed before public hosting.
- The "generated report" slides are written by us to illustrate; no report-generation model was run (MedGemma's download is gated by terms of use that have not been accepted for this project).
- Model results describe one run on one machine and small samples; they show how to test, not how good the models are in general.
