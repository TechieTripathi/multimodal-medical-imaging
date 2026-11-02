# Multimodal AI Models for Medical Imaging Analysis
## Artifact-First Presentation Build Specification

**Audience:** Interdisciplinary Faculty Development Program (FDP) participants: AI/CS, medical and radiology, biomedical engineering, and non-technical faculty, plus students
**Duration:** 120 minutes, including Q&A *(confirm)*
**Deck size:** 66 numbered core slides (raised from 58 on 2 November 2026 to add real DICOM examples and runnable DICOM code), plus an unnumbered institutional cover and a Sources appendix that do not count toward the total
**Format:** 16:9 Slidev presentation built around interactive artifacts (Vue 3 components) and purposeful animation, light theme, speaker notes, a static SPA build for offline delivery, and PDF exports (all click states, handout, speaker notes). Optional PowerPoint export (see §12).
**Companion:** A runnable Jupyter notebook that produces every real model output shown in the deck
**Primary goal:** Show how AI systems connect medical images with clinical text and other patient information, how real medical imaging data is stored and prepared, and how to run and interpret real models responsibly.

This deck belongs to the same FDP series as `../AI-model-evaluation` (S11) and `../llm-to-agents`. It uses the same visual theme, institutional cover and build tooling (§4.8, §12), but deliberately does **not** follow the dense slide design of `llm-to-agents` (§4). This specification is self-contained.

---

## 1. Project Objective

Build a complete, polished, artifact-first presentation for a two-hour FDP session.

The presentation must not be a superficial overview or an overly technical lecture. Participants without AI, programming or medical imaging expertise should follow the main narrative; technical participants should gain real insight into architectures, model behaviour, implementation and evaluation.

### Core design philosophy

**Technically meaningful. Visually intuitive. Easy for everyone to understand.**

Teaching sequence for each major concept:

**Real-world problem → simple analogy → visual explanation → technical concept → medical application → limitations.**

### Priorities when requirements conflict

1. Accuracy and honesty (never fabricate, always label).
2. Clarity: a participant without an AI background can follow every slide (§4).
3. Interactivity and animation, in service of clarity (§6).
4. Completeness of the outline.
5. Hitting the exact slide count.

### Learning outcomes

By the end, participants should be able to:

1. Explain multimodal AI in simple language.
2. Explain why combining medical images with clinical text or other information can help.
3. Distinguish unimodal image analysis from multimodal learning.
4. Describe the basic ideas behind neural networks, image and text encoders, embeddings, attention and fusion.
5. Recognize representative medical vision-language and imaging foundation models and the tasks each supports.
6. Explain how DICOM studies, series, instances, pixel data and metadata relate to one another.
7. Follow a practical workflow for loading and visualizing a CT series, and recognize how X-ray and MRI data differ.
8. Follow a real pretrained-model inference from input to output.
9. Interpret scores without confusing them with validated diagnoses.
10. Identify limitations, ethical and regulatory considerations, and research opportunities.

---

## 2. Timing and Slide Allocation

| Section | Slides | Time |
|---|---:|---:|
| 1. The medical imaging problem and multimodal AI | 1–8 | 11 min |
| 2. How multimodal AI works | 9–18 | 18 min |
| 3. Training, evaluation and representative models | 19–28 | 16 min |
| 4. DICOM fundamentals and imaging workflows | 29–40 | 22 min |
| 5. Medical-domain applications | 41–49 | 14 min |
| 6. Practical demonstrations | 50–61 | 26 min |
| 7. Responsible AI, research and takeaways | 62–66 | 13 min |
| **Total** | **66 slides** | **120 min** |

Slide numbers in §7 below are the original 58-slide plan; the six DICOM slides were inserted in Parts 4–6 (see §12, decisions).

Each slide's speaker notes carry a `Time:` line; the times must sum to each section's budget (enforced by `npm run check`). If the session length changes, rebalance this table first.

---

## 3. Audience and Teaching Principles

- Assume no prior knowledge of neural networks, programming or medical image processing.
- Treat participants as experienced academics, not as beginners to be entertained or as AI enthusiasts looking for hype.
- Plain language first, then the correct technical term. Intuition before terminology; terminology before caveats.
- Use equations only when they help, and explain every symbol in plain language.
- Connect each technical concept to a clinical or research scenario.
- Keep slide text short; detail goes in speaker notes.
- Make clear that AI assistance does not transfer clinical accountability to the model.

---

## 4. Clarity Rules and Visual Design

The `llm-to-agents` deck was accurate and richly interactive, but too hard to follow. Its slides read like dashboards: small text, several panels per slide, step counters, Reset buttons, instructions, "Notice" lines and labels all competing for attention, and new terms on almost every slide. **This deck must be understandable at first glance. When interactivity and clarity conflict, clarity wins.** Keep the series' visual theme (§4.8), but do not copy that deck's layouts, density or on-slide controls.

### 4.1 The five-second test

A participant with no AI background should be able to say what a slide is about within five seconds of seeing it. The title states the idea as a plain sentence ("A CT scan is a stack of slices", not "Volumetric reconstruction"); the visual shows that one idea and nothing else.

### 4.2 Limits per slide

| | Limit |
|---|---|
| Main ideas | 1 |
| Artifacts or main images | 1 |
| Visible words (excluding image labels and code) | about 40 |
| New technical terms | at most 2, each defined in plain words on the slide |
| Labelled items visible at once in an artifact | about 6; reveal the rest with clicks |
| Tables | at most 4 rows × 4 columns on screen; larger tables become a filter or a click-through |
| Code | at most 8 lines |

If a slide breaks a limit, split the idea, cut detail into the speaker notes, or reveal it in steps. Do not shrink text to make it fit.

### 4.3 Text size

On the 980 × 552 canvas, after any scaling:
- Titles 34–36px; body 22px; artifact labels, table text and code at least 18px; image credits and honesty labels at least 14px.
- Never scale an artifact down below these sizes. If it does not fit, show less.
- Every slide must stay readable in a contact sheet at quarter size (a proxy for the back row).

### 4.4 No on-slide controls or instructions

- No step counters ("3/8"), Reset or Previous/Next buttons, "Select a…" / "Click a…" instructions, or "Notice" lines on the slide. The presenter drives with the clicker; what to try and what to notice go in the speaker notes.
- Free controls (sliders, toggles) are part of the picture: few, large, and labelled with what they change ("Window width"), never generic buttons. Hide anything the presenter does not need on screen.
- No progress strip, no side captions, no eyebrow labels. A slide has only: the title, an optional one-line subtitle directly under it, the visual, and a quiet footer (slide number and source numbers).
- At most one honesty label per slide (§5), always in the same position (bottom-left of the visual).

### 4.5 Build up, never dump

- Every artifact starts at its simplest state and adds one thing per click. The first state is understandable on its own; the final state may be richer but still respects §4.2.
- Animate only the thing that changes; everything else stays still.
- After a build, end on a one-sentence takeaway.

### 4.6 One story thread

Follow one real, de-identified case through the deck (a chest CT study and a chest X-ray with its report, from the datasets in §9). The same images reappear in the modality slide, the embedding explanation, the DICOM section, the demos and the limitations. Do not invent fictional hospitals, staff, budgets or dates that the audience has to keep track of.

### 4.7 Pictures over boxes

- Real medical images are the main visual on most slides: at least half the slide area on image slides, on a near-black mat (an `--image-mat` token) so greyscale reads correctly on a projector.
- Prefer one large diagram with a few boxes over grids of small panels. Arrows show real flow. Label things in plain words.
- Avoid grids of identical cards, log or trace dumps, dense tables, stock "AI brain" or glowing-scan imagery, gradients, glassmorphism and emoji.

### 4.8 Theme: the series look

Use the same visual theme as the other decks in the series, so this session looks like part of the same programme. Take `../llm-to-agents/styles/tokens.css` and its bundled fonts as the starting point, and keep these unchanged:

| Element | Value |
|---|---|
| Slide background | `--paper` #f7f7f5 (cool off-white, low projector glare); panels `--surface` #ffffff |
| Text | `--ink` #1a1a1a; secondary `--ink-2` #4a4f57; captions `--ink-3` #6b7078 |
| Accent | `--accent` #2340c8 (deep ultramarine), `--accent-strong` #1a2f96, tints `--accent-tint` / `--accent-tint-2` |
| Status (always with a text label) | `--ok` #1e7a46, `--warn` #a35f00, `--bad` #c0352b, `--neutral` #6b7078, each with its tint |
| Section openers | `--night` #16181c / `--night-2` #2a2e35 |
| Fonts | IBM Plex Sans for text; IBM Plex Mono only for code, DICOM tags and numbers from the machine. Bundled locally, no CDN |
| Shape and motion | `--radius` 6px, 1.5px strokes, `--dur` 0.4s, `--ease`, reduced-motion support |
| Cover | The shared institutional cover: ZeroZeta, SRHU and IIT Roorkee logos, presenter block, navy band |
| Footer | Section name left, slide number right, source numbers between, in the same quiet style |
| Honesty label | The same dashed-outline pill as the series, with this deck's label kinds (§5) |

Changes from the series theme, all in favour of clarity:
- **Type scale** replaced by §4.3: `--fs-display` 48px, `--fs-title` 36px, `--fs-lead` 24px, `--fs-body` 22px, `--fs-small` 20px, `--fs-label` 18px, `--fs-micro` 14px (footer, credits and honesty labels only).
- **`--artifact-scale` is 1**: artifacts are never shrunk.
- **New token `--image-mat`** (#0b0d10) for the dark panel behind medical images.
- **Not carried over:** the journey strip, the side caption beside the title, and the grey `--stage` frame around every artifact.

Layout rules on top of the theme:
- Generous whitespace: roughly a third of each slide stays empty.
- Each section opens on a dark (`--night`) slide with the one plain question it answers ("How does a computer read an X-ray?"). The last slide of each section ends with a one-sentence recap.
- One subtle slide transition (`fade`) throughout.

### 4.9 Images: privacy and credit

- **Never show identifiers.** No patient names, IDs, dates of birth, accession numbers or burned-in annotations on any slide, even from public datasets. Crop or mask burned-in text.
- **Every image carries a short credit** (dataset and licence) under the image; the full citation goes in the Sources appendix.
- **Annotations** use the accent colour for the thing being explained, and status colours only for correct, incorrect or uncertain, always with a text label.

---

## 5. Honesty Labels

Extend the shared `SimTag` / `Stage` component with the kinds this deck needs. Every visual output carries exactly one:

| Kind | Label text | Use for |
|---|---|---|
| `actual` | Actual model output: <model>, run <date> | Output produced by the notebook (§9); must reference a run file in `data/runs/` |
| `real-data` | Real de-identified image: <dataset> | Unmodified or windowed real images |
| `illustrative` | Illustrative values, not measured | Invented numbers used to explain a concept |
| `simulated` | Simulated: no model was run | Mock outputs of a process |
| `teaching` | Teaching visualization, not real model internals | Conceptual diagrams of attention, embeddings, fusion |
| `published` | Reported in <paper> | Numbers quoted from a paper (not reproduced by us) |

Rules:
- Never present published benchmark numbers as if we measured them, or our numbers as if they were benchmarks.
- Never present a similarity score as a probability or a diagnosis.
- Scenarios in §7 Section 5 that describe a workflow, not a validated clinical deployment, say so.

---

## 6. Interactivity and Animation (Mandatory)

Interactivity and animation are core teaching mechanisms in this deck, not decoration, and every artifact obeys the clarity rules in §4: one question per artifact, large text, no on-screen step counters or instructions, built up one step at a time. Participants should watch an X-ray dissolve into numbers, see a report sentence split into tokens, drag a CT window and watch lung tissue appear, slide a threshold and watch sensitivity trade against specificity, and watch real model scores re-rank as candidate descriptions change. A static screenshot or a decorative image never counts as an interactive artifact.

### 6.1 Minimum coverage

- Build all **24 artifacts** in §6.3. If one proves impractical, record why in the QA report; at least 20 must ship.
- At least **35 of the 58 slides** contain an interactive artifact, an animated build, a real image or a worked example. No section has more than two consecutive static text slides.
- Every section has at least two interactive artifacts; Sections 2, 4 and 6 have at least four.
- Every technical concept has an animated or interactive explanation.
- Where an artifact can run on real data (a real CT slice, real embeddings, real masks), it does, and carries the matching label (§5).

### 6.2 Three layers of interaction

1. **Clicker steps (presenter-driven).** Every artifact advances through meaningful states with the presenter's remote, using Slidev's click system (`useArtifactStep`, `v-click`, `$clicks`). The PDF export captures each step, so every step must read on its own and step 0 is never empty.
2. **Free controls (live exploration).** Sliders, toggles, hover, drag, select and text input on top of the steps, operable with a mouse from the lectern. Typing in an input never advances the slide. The default state is meaningful because it is what the PDF shows.
3. **Live in-browser computation.** Where it is cheap, compute the result live from bundled data rather than swapping precomputed pictures: windowing on the Hounsfield array, cosine similarity on real embedding vectors, tokenization with the real vocabulary, the confusion matrix from the threshold, Dice from mask positions, and multiplanar slicing of the volume.

### 6.3 Required artifacts

| # | Artifact | Slide | Clicker steps (animated) | Free controls |
|---:|---|---:|---|---|
| 1 | Modality gallery | 3 | Modalities appear one by one; a DICOM / not-DICOM tag stamps onto each | Click a modality to enlarge it with its credit and typical file format |
| 2 | Unimodal vs multimodal comparator | 7 | Image-only answer appears; clinical text slides in; the answer revises | Toggle each piece of evidence on and off |
| 3 | Pixels to numbers | 10 | Zoom from a real X-ray into a region, into the pixel grid with values, into 16×16 patches lining up as a sequence | Hover a pixel to read its value; move the zoom window |
| 4 | Radiology-sentence tokenizer | 11 | A report sentence splits into tokens one at a time, then each token turns into its ID | Type or pick a sentence; tokens update live (real WordPiece vocabulary, offline) |
| 5 | Embedding space map | 12 | Image points appear, then text points, then matching pairs are connected | Hover a point to see its image or text; filter by finding |
| 6 | Contrastive training matrix | 14 | A batch similarity grid; over training steps the diagonal brightens and off-diagonal cells fade | Scrub a training-step slider; click a cell to see the pair |
| 7 | Cosine similarity worked example | 15 | Two arrows rotate, the angle and score update; then the same formula runs on real 512-number embeddings | Drag either vector; pick real image–text pairs |
| 8 | Cross-attention explorer | 16 | Lines grow from a selected word to image regions in order of weight | Click any word in the report; heat overlay updates |
| 9 | Fusion builder | 17 | Image, text and tabular streams flow in and merge early, midway or late | Switch fusion point; remove a modality and see what breaks |
| 10 | Threshold and metrics explorer | 22 | Cases sort along a score axis; the threshold sweeps; the confusion matrix and the ROC point move together | Drag the threshold; screening vs confirmation presets |
| 11 | Overlap explorer | 23 | Predicted mask slides over the reference; overlap fills; Dice and IoU count up | Drag or resize the predicted mask |
| 12 | Model comparison matrix | 28 | Rows reveal model by model in four columns only (model, what it does, input → output, research-only or cleared) | Click a model to open its card (training data, licence, limits) in place of the table |
| 13 | DICOM hierarchy explorer | 30 | Study expands into series, series into instances | Click a node to see its metadata; privacy-sensitive tags highlighted |
| 14 | CT windowing slider | 33 | HU histogram appears; the window bracket moves through presets as the image contrast changes | Window width and level sliders; lung, mediastinum, bone and brain presets |
| 15 | Volume and multiplanar explorer | 34 | Slices stack into a volume, then the volume is cut into coronal and sagittal planes | Slice sliders per plane; click to move linked crosshairs |
| 16 | MRI sequence comparator | 35 | The same slice cross-fades T1 → T2 → FLAIR (→ DWI) with tissue labels | Wipe slider between any two sequences |
| 17 | Preparation pipeline | 36 | The image travels through each stage; a "kept / lost" ledger fills in | Click a stage to see before and after |
| 18 | Similarity ranking viewer | 49 | Score bars grow, then re-sort into rank order | Add or remove candidate descriptions; rankings re-compute live from real embeddings |
| 19 | Segmentation overlay | 51 | Structures fade in one by one over the CT | Opacity slider; structure toggles; slice slider |
| 20 | Domain shift illustrator | 55 | One site's intensity distribution appears, a second site's shifts beside it, and scores drift | Switch site or scanner; toggle normalization |
| 21 | Neural network intuition | 9 | Pixels flow through layers into features, then into a decision | Swap the input image; highlight one layer |
| 22 | Zero-shot prompt laboratory | 20 | Class prompts appear; real scores fill in; a reworded prompt changes the winner | Pick from prompt variants (precomputed real scores) |
| 23 | Report claim checker | 57 | Generated report sentences appear; each is linked to image evidence or flagged as unsupported | Click a sentence to see its supporting region or the gap |
| 25 | Live DICOM viewer | new, Part 4 | Each click opens the next real file (CT, X-ray, MRI, mammogram, PET, ultrasound) | Switch files, window level and width, frame slider, download the file, open your own file locally |
| 26 | PET/CT fusion | new, Part 5 | CT, then PET in SUV, then fused, then the expert lesion outline (DICOM SEG) | Opacity slider; hover reads HU and SUV |
| 24 | Notebook walkthrough | 46–52 | Code morphs cell by cell (Shiki Magic Move) with the active lines highlighted; the real output appears beside each step | Jump between cells; toggle "live run" vs "precomputed run" view |

Other slides use animated builds rather than full artifacts. Examples: the opening case (slide 2) assembles image, report and history; the clinician workflow (slide 4) animates as a sequence; model mechanism diagrams (slides 24–27) build up step by step; and application slides (37–44) reveal the workflow over a real image.

### 6.4 Required animated sequences

- An image dissolving into pixel values and then patch tokens.
- A report sentence splitting into tokens.
- Image and text embeddings moving into a shared space, with matching pairs pulled together during contrastive training.
- Vectors rotating as cosine similarity changes.
- Cross-attention links growing from a word to image regions.
- Data streams merging at different fusion points.
- Cases crossing a moving threshold while the confusion matrix updates.
- Masks overlapping as the Dice score counts up.
- A DICOM study expanding into series and instances.
- Slices stacking into a volume and being re-cut into other planes.
- A window bracket moving over the HU histogram while tissue contrast changes.
- Data passing through the preparation pipeline while the kept/lost ledger fills.
- Score bars growing and re-sorting into a ranking.
- A segmentation mask fading in over the CT.
- Notebook code morphing step by step as real outputs appear.

### 6.5 Audience interaction moments

Use short **predict, then reveal** moments. Show of hands only: no phones, sign-ups or installs. At least six, protected in the time budget:

| Slide | Ask before revealing |
|---:|---|
| 2 | What would you look at first: the image, the report or the history? |
| 7 | Which answer would you trust more, and why? |
| 15 | Which pair is closer: these two images, or this image and this sentence? |
| 22 | Where would you set the threshold for screening? For confirmation? |
| 33 | Which window will show the lung nodule? |
| 49 | Which description will rank first? |
| 50 | Why did the model get this one wrong? |
| 55 | Will this model work at another hospital? |

### 6.6 Animation style and accessibility

- Motion explains sequence, change or causality only.
- Use `v-click` / `v-clicks` / `v-after` for reveals, Vue `<Transition>` / `<TransitionGroup>` for state changes and re-sorting, click-indexed SVG groups for diagrams that build up, `v-mark` sparingly for emphasis, and Shiki Magic Move for code.
- One subtle slide transition (`fade`), set in the headmatter.
- Durations about 0.3–0.6 s (`var(--dur)`, `var(--ease)`). No looping, bouncing, spinning, flashing or continuous motion.
- Respect `prefers-reduced-motion` (shorten or skip motion, keep the end state).
- Essential content is understandable without animation; the end state of every animation is what the PDF shows.

### 6.7 Artifact quality criteria

Each artifact answers one question (the slide title) and has a meaningful interaction, a realistic medical example drawn from the story case (§4.6), and a meaningful static state at every click step. What to try, what to notice, and technical and clinical caveats go in the speaker notes, not on the slide.

### 6.8 Implementation rules

- Each artifact is a self-contained Vue 3 single-file component in `components/`, using inline SVG, HTML/CSS or `<canvas>`, with its data in `data/`.
- Clicker steps use Slidev's click system (`clicks:` frontmatter with `$clicks`, `v-click`); on-slide controls are optional extras, never required to follow the story.
- Real image data used by artifacts lives in `data/imaging/` as derived arrays or PNGs (for example, a downsampled int16 CT volume). Real DICOM files are shipped only as **teaching copies** in `public/dicom/` (see §11).
- Artifacts that show real model outputs read them from `data/runs/*.json` generated by the notebook; they never hard-code scores. Artifacts that need live re-ranking load the real embedding vectors from the same files.
- Render images with `<canvas>` (or WebGL where needed). Windowing, slicing and overlay controls must respond without visible lag (under about 50 ms per update) on the lecture-room laptop; preload image data when the slide is entered.
- Every free control works in the offline SPA build.
- Keep the built SPA small enough to load on a lecture-room machine (target under 25 MB).

---

## 7. Authoritative 58-Slide Content Outline

### Section 1: The medical imaging problem and multimodal AI (slides 1–8, 12 min)

1. Title: presenter and FDP context.
2. One patient, three kinds of evidence: an image, a report and a clinical history (opening case).
3. Medical imaging modalities: X-ray, CT, MRI, ultrasound, pathology, retina. *(Artifact 1)*
4. How clinicians combine images, reports and patient context.
5. Image-only AI: what it can and cannot do.
6. What is multimodal AI? Images, text, and structured data such as labs, vitals and history.
7. Unimodal versus multimodal: a side-by-side example. *(Artifact 2)*
8. Learning outcomes and the roadmap for the session.

### Section 2: How multimodal AI works (slides 9–18, 22 min)

9. What a neural network does, intuitively. *(Artifact 21)*
10. How an image becomes numbers: pixels, CNN features and ViT patches. *(Artifact 3)*
11. How text becomes numbers: tokens and the text encoder. *(Artifact 4)*
12. Embeddings as numerical "fingerprints". *(Artifact 5)*
13. Aligning image and text in one shared space.
14. Contrastive learning and CLIP. *(Artifact 6)*
15. Cosine similarity: a small worked example. *(Artifact 7)*
16. Attention and cross-attention, with a visual analogy. *(Artifact 8)*
17. Early, intermediate and late fusion. *(Artifact 9)*
18. Beyond image and text: adding structured clinical data, and what goes wrong when it is missing.

### Section 3: Training, evaluation and representative models (slides 19–28, 20 min)

19. Training versus inference.
20. Zero-shot classification and its limitations. *(Artifact 22)*
21. Fine-tuning and transfer learning.
22. Classification metrics: sensitivity (recall), specificity, precision and AUROC, in plain language. *(Artifact 10)*
23. Segmentation and retrieval metrics: Dice, IoU and Recall@K. *(Artifact 11)*
24. From CLIP to BiomedCLIP: biomedical image–text pretraining.
25. CheXzero and chest X-ray image–report learning (MedCLIP, Wang et al. 2022, as a related approach in notes).
26. MedSAM and promptable medical image segmentation.
27. Medical vision-language assistants and report generation (for example LLaVA-Med, MedGemma; verify current options and licences at build time).
28. Which model does what: comparison matrix. *(Artifact 12)*

For each model: the problem it addresses, input, output, high-level mechanism, training data, practical significance and limitations. Verify every description against the original paper and official repository. Distinguish retrieval, classification, segmentation, report generation and question answering; do not imply all models support the same tasks or modalities.

### Section 4: DICOM fundamentals and imaging workflows (slides 29–36, 16 min)

29. What DICOM is and why it is used, compared with PNG/JPEG.
30. Study, series and instance. *(Artifact 13)*
31. Metadata and pixel data, including privacy-sensitive tags.
32. Stored values versus displayed intensities (rescale slope/intercept, bit depth).
33. CT Hounsfield units, window width and window level. *(Artifact 14)*
34. From slices to a 3D volume: spacing, orientation, slice ordering and multiplanar views. *(Artifact 15)*
35. MRI sequences and why they matter. *(Artifact 16)*
36. From raw DICOM to a model-ready input: what is kept and what is lost. *(Artifact 17)*

### Section 5: Medical-domain applications (slides 37–44, 14 min)

Each application slide applies the concepts and models from Sections 2–3 to a real case: a short scenario, a real image, the AI workflow, the intended output, and an honest account of benefits and limitations. State clearly when a scenario is illustrative rather than a validated clinical workflow.

37. Chest X-ray: zero-shot findings and report matching.
38. CT: anatomical segmentation and lesion-region analysis.
39. Brain MRI: multi-sequence analysis.
40. Digital pathology: whole-slide images and tissue classification.
41. Retinal imaging and ophthalmology.
42. Ultrasound and other modalities.
43. Image–text retrieval: finding similar cases and reports.
44. Combining imaging with clinical history: potential and limitations.

### Section 6: Practical demonstrations (slides 45–53, 22 min)

The presenter runs the notebook live in a separate window; every demo slide also shows the same run's real outputs in the deck as the fallback. Participants do not install anything during the session; the notebook is a take-home resource. Slides 46–52 use the notebook walkthrough *(Artifact 24)*: the code morphs cell by cell beside the real output of each step.

45. The demo plan: three workflows, what runs live, what was precomputed, and on what hardware.
46. Demo A1: load a CT series, inspect metadata, order slices by position (`pydicom`).
47. Demo A2: windowing and multiplanar views (`SimpleITK`); visualization is not inference.
48. Demo B1: an image and candidate descriptions through the image and text encoders (BiomedCLIP).
49. Demo B2: cosine similarity and ranking; what the scores mean and do not mean. *(Artifact 18)*
50. Demo B3: a failure or ambiguous case, and why it happened.
51. Demo C1: CT segmentation and overlay. *(Artifact 19)*
52. Demo C2: checking a mask against a reference (Dice), and where segmentation fails.
53. Reading model outputs responsibly: scores versus probabilities versus diagnoses.

### Section 7: Responsible AI, research opportunities and takeaways (slides 54–58, 14 min including Q&A)

54. Data quality, missing labels and dataset limitations.
55. Bias, domain shift and differences between hospitals and scanners. *(Artifact 20)*
56. Privacy, de-identification, security and regulation (for an Indian audience: the DPDP Act 2023 and CDSCO's regulation of software as a medical device; verify current status).
57. Explainability, hallucination, validation and human oversight. *(Artifact 23)*
58. Research opportunities, key takeaways and Q&A.

**Sources appendix** (A1, A2, …) follows slide 58 and does not count toward the 58.

---

## 8. DICOM as a Thread Through the Deck

DICOM is a practical thread, not just a definition slide:

- Slide 3: mark which modalities arrive as DICOM and which (pathology whole-slide images, many fundus photos) usually do not.
- Section 4: the full treatment, using the same real CT study as Demo A.
- Slide 36 → Section 6: the preparation pipeline is exactly what Demos A–C execute.
- Slide 56: DICOM metadata as a privacy risk.

Cover at an accessible level: the standard; study/series/instance; pixel data and metadata; dimensions, pixel spacing, orientation and acquisition details; Hounsfield units and windowing; MRI sequences; slice ordering and spatial geometry; de-identification; and the difference between visualization, preprocessing and inference.

Use real DICOM files wherever feasible. Confirm a dataset genuinely contains DICOM before calling it DICOM; never label PNG/JPEG-only data as DICOM.

---

## 9. Practical Workflows, Notebook and Reproducibility

### Workflows

| | Workflow | Data | Model | Required? |
|---|---|---|---|---|
| A | DICOM loading and visualization | Real CT series (DICOM) | None | Yes |
| B | Medical image–text matching | Real chest X-rays with reports | BiomedCLIP | Yes: the genuine pretrained-model inference |
| C | CT segmentation | Same CT series as A | TotalSegmentator or MedSAM | Yes if feasible; otherwise a clearly labelled illustrative workflow |

The notebook also loads one X-ray DICOM and one MRI series briefly, so learning outcome 7's contrast between modalities is shown, not just described.

**Demo B details:** load an image and a small set of candidate descriptions; run each through the model's encoders; compute cosine similarities; rank and display. Explain why the scores are not diagnostic probabilities. Include at least one failure or ambiguous result.

**Demo C details:** generate a mask for an anatomical structure; overlay it on the original image; compute Dice against a reference mask where one exists; explain the need for validation.

### Candidate datasets and models (verify all before use)

| Candidate | Why | Check |
|---|---|---|
| A CT collection on TCIA under CC BY (for example LIDC-IDRI) | Genuine DICOM, public | Licence allows redistribution of derived images in a public deck |
| Indiana University chest X-ray collection (Open-i) | DICOM images with free-text reports, no credentialing | Current download format and licence (may be non-commercial / no-derivatives) |
| A TCIA MRI collection with T1/T2/FLAIR | Real sequence comparison | Licence; sequences present |
| BiomedCLIP (`open_clip`, Hugging Face) | Documented, runs on CPU | Licence; preprocessing; trained on PubMed figures, not DICOM |
| TotalSegmentator | Accepts DICOM/NIfTI, CPU `--fast` mode | Licence of the task weights used |
| MedSAM | Promptable 2D segmentation | Needs a bounding-box prompt; realistically a GPU |

MIMIC-CXR requires PhysioNet credentialing and cannot be shared with participants; do not use it in the shipped materials.

### Runs and provenance

- Real outputs are produced on the build machine (RTX PRO 4000, 24 GB) and saved as `data/runs/<demo>.json`, recording model name and version or hash, dataset and case IDs, preprocessing, hardware, date and runtime.
- The deck reads its `actual` outputs from those files; nothing is typed in by hand.
- The notebook states CPU runtimes as well, so participants without a GPU know what to expect.

### Notebook contents

Setup instructions and a pinned `requirements.txt`; a data download script; brief explanations before each step; clear, commented cells; visual outputs at key stages; expected outputs and troubleshooting tips; model and dataset citations; hardware and runtime expectations; privacy and data-handling notes; and interpretation guidance.

Keep general-purpose DICOM loading separate from model-specific preprocessing. Do not assume a model accepts raw DICOM. Preserve spatial and intensity information and explain every conversion to arrays or image formats. Keep the original data for comparison.

---

## 10. Speaker Notes and Facilitation

Every slide ends with an HTML comment in this shape:

```md
<!--
**Time:** ~2 min
**Objective:** What participants should understand.
**Say:** Plain-language explanation, 3–6 sentences, in the presenter's voice.
**Example:** A clinical example or everyday analogy.
**Try / Notice:** What to click or drag, and what to point at.
**Ask:** Optional discussion or predict-then-reveal question.
**Caveat:** Technical or clinical caveat, if any.
**Transition:** One line into the next slide.
**Sources:** Keys used and what each supports (or "None — conceptual").
-->
```

Demo slides add **Steps**, **Expected observations**, **Likely failure modes** and **Fallback**.

Notes support natural delivery rather than repeating slide text. Put optional technical depth (loss functions, architecture details) in notes, not on the slide.

---

## 11. Research, Accuracy and Citation Requirements

Prioritize original papers, peer-reviewed publications, official model repositories, dataset documentation, the DICOM standard, and clinical or regulatory guidance.

- Open every URL you cite and confirm it supports the exact claim. Never cite from memory alone.
- Cite claims, benchmark results, model capabilities and dataset statistics on the slide (footer source numbers), and collect them in the Sources appendix.
- Distinguish research prototypes from clinically validated or regulator-cleared systems.
- Do not invent citations, results, model capabilities or diagnostic claims.
- Do not present similarity scores as calibrated diagnostic confidence unless that has been specifically validated.
- Explain that performance changes across populations, scanners, institutions and acquisition protocols.
- Use exact model names (BiomedCLIP, not BioMedCLIP) and name the specific paper when a name is shared by several works (MedCLIP).

### Data licensing and privacy

- Handle all data according to its licence, access rules and privacy requirements. Do not assume de-identification just because a dataset is public.
- The deck may be published publicly (as `llm-to-agents` is on GitHub Pages). Only include images whose licence permits public redistribution of derived images, with attribution. Ship DICOM only as teaching copies: every public tag kept, private tags removed, pixels downsampled where needed, a new SOP Instance UID, and the change recorded in the file's DerivationDescription, each from a CC BY collection and checked for identifiers.
- Strip or mask any residual identifiers and burned-in text.

---

## 12. Technical Implementation

- **Framework:** Slidev, pinned in `package.json` with the lockfile committed.
- **What to reuse from `../llm-to-agents`:** the theme (`styles/tokens.css`, bundled IBM Plex fonts, base styles, footer and honesty-pill styling) with the changes in §4.8; the `institution-cover` layout and logos; the check scripts (slide count, notes, timing, citation keys, URLs, screenshots, contact sheets); and the export setup.
- **What not to reuse:** its slide layouts, `Stage` frame with on-slide task and notice text, step controls, journey strip, side captions, type scale and `--artifact-scale` shrink. These are the source of its density; build new, simpler layouts to §4.
- **Check scripts** additionally flag slides over the word limit, text below the minimum sizes, and more than one honesty label (§4.2–4.4).
- **Cover:** `institution-cover` layout with session label *(confirm: S13?)*, title and date *(confirm)*.
- **Sections:** one file per section in `pages/01-…` to `pages/07-…`, plus `pages/99-sources.md`; `dev-s1.md`…`dev-s7.md` for isolated previews; `data/sections.ts` updated for 7 sections and 58 slides.
- **Offline:** everything bundled; no network during the talk. The live notebook runs in its own window, with in-deck fallbacks.
- **Exports:** all-steps PDF, handout PDF, speaker-notes PDF. If a PowerPoint copy is needed, reuse the `pptx` scripts from `../AI-model-evaluation/slidev`.

### Decisions made during the build (30 October 2026)

- **Section openers are unnumbered.** The seven dark openers (§4.8) sit outside the 58 core slides, like the cover and the Sources appendix; their half-minute each is counted in the section budgets.
- **One story patient:** LIDC-IDRI-0001 (TCIA, CC BY 3.0), which has a chest CT, a chest X-ray (both DICOM), four radiologists' outlines (DICOM SEG) and ratings (DICOM SR).
- **Image–text data:** the Indiana University X-rays are used as PNG (the DICOM release is 80 GB). Their Open-i licence could not be confirmed from NLM's site, so they are treated as CC BY-NC-ND 4.0 and shown unmodified. **Confirm before public hosting.**
- **Report generation was not run.** MedGemma's download is gated by terms that only the account holder can accept; Artifact 23 and slide 27 use clearly labelled simulated text, checked against the patient's real evidence.
- **Brain MRI:** UPENN-GBM-00001 (CC BY 4.0), four sequences rigidly registered in the notebook; slice chosen by eye through the lesion.
- **Real DICOM examples (2 November 2026).** Six slides added (deck now 64, still 120 minutes): a live DICOM viewer (Artifact 25), ultrasound cine, mammogram tags with the clinical table, PET SUV from tags (Part 4); PET/CT fusion (Artifact 26, Part 5); Demo D (Part 6). New data, all CC BY 4.0 from TCIA: CMMD (mammography, patient D2-0333), B-mode-and-CEUS-Liver (ultrasound cine, LiverUS-01), FDG-PET-CT-Lesions defaced release (lung cancer patient PETCT_b899150306). Seven teaching copies in `public/dicom/` form the downloadable sample pack; `scripts/test-dicom.mjs` checks the in-browser reader against pydicom.
- **Runnable DICOM code (Demo E, slides 59–60).** A Run button executes the code shown on the slide against the real files in the browser: CT tissue composition from Hounsfield units, the four readers' nodule measurements from DICOM SEG, PET tumour SUV statistics, and a metadata audit. Five SEG teaching copies added to the pack; every number is checked against pydicom.

### Project organization

    Multimodal-AI-Models-for-Medical-Imaging-Analysis/
    ├── IDEA.md                    # this specification
    ├── README.md                  # run, edit, present, export instructions
    ├── package.json               # pinned Slidev, Playwright
    ├── slides.md                  # headmatter, cover, title, section includes
    ├── pages/                     # 01-problem … 07-responsible, 99-sources
    ├── components/                # artifacts; ui/ shared primitives
    ├── layouts/  styles/  composables/  scripts/
    ├── data/
    │   ├── sections.ts
    │   ├── refs/                  # citations per section
    │   ├── imaging/               # derived arrays/PNGs from real data, with credits
    │   └── runs/                  # notebook outputs consumed by the deck
    ├── notebook/
    │   ├── multimodal-medical-imaging.ipynb
    │   ├── requirements.txt
    │   ├── download_data.py
    │   └── README.md              # setup, runtimes, troubleshooting, interpretation guide
    ├── docs/                      # QA_REPORT.md
    └── exports/                   # SPA and PDFs (not committed)

---

## 13. Quality Assurance and Definition of Done

Do not declare completion until all of the following are checked.

### Content
- 58 numbered core slides (55–60 if rebalanced), seven sections, plus cover and Sources appendix.
- Speaker notes on every slide; `Time:` lines sum to 120 minutes and match each section's budget.
- X-ray, CT and MRI are each covered explicitly.
- Every source opened and supporting its claim; URL check passes.

### Artifacts and data
- All 24 artifacts built (at least 20, with reasons recorded for any dropped); at least 35 slides with an artifact, animated build, real image or worked example; no more than two consecutive static text slides.
- Every visual output carries the correct honesty label (§5); every `actual` label points to a run file.
- Every real image has a credit line and a licence that permits its use.
- No identifiers visible anywhere.

### Workflows
- Notebook runs top to bottom on a clean environment, on GPU and (for A and B) on CPU.
- Demo A and Demo B produce real outputs; Demo C either does too or is labelled illustrative.
- Failure and fallback paths tested.

### Interaction and animation
- Every artifact steps cleanly with the clicker, and every click state reads on its own in the all-steps PDF.
- Every free control visibly changes its output, driven with Playwright and screenshotted.
- Live computations (windowing, similarity, tokenizer, metrics, Dice, slicing) give correct results, spot-checked against the notebook.
- Image controls respond without visible lag on the lecture-room laptop.
- Typing in inputs never advances the slide.
- Animations follow §6.6; the reduced-motion setting is tested.
- The predict-then-reveal moments (§6.5) are in the notes, with their time budgeted.

### Clarity
- Every slide passes the five-second test (§4.1), checked by a non-technical reviewer on contact sheets.
- No slide exceeds the limits in §4.2 or uses text below §4.3; checked by script and on quarter-size contact sheets.
- No step counters, Reset buttons or on-slide instructions are visible (§4.4).
- The story case (§4.6) appears consistently across sections.

### Visuals and delivery
- No clipping, overlap or unreadable labels; images legible on a projector.
- Static SPA runs offline; PDFs exported and inspected.
- A dry run with at least one clinician and one non-technical colleague, before delivery.

---

## 14. Final Deliverables

1. The 58-slide presentation (editable Slidev source).
2. Speaker notes for every slide.
3. The 24 interactive, animated artifacts in §6.3 (at least 20).
4. A runnable notebook covering Workflows A and B, and C where feasible.
5. Dataset acquisition and preparation instructions; pinned requirements.
6. Run files for every real output shown in the deck.
7. Verified references in the Sources appendix.
8. A short guide to interpreting outputs, common errors and limitations (in `notebook/README.md`).
9. PDF exports (and PowerPoint if requested).
10. README and QA report listing tests performed and known limitations.

### Final direction

Create a presentation that is **easy to follow without being superficial, technical without being intimidating, and informative without overwhelming the audience**.

Participants should leave with a clear mental model of how multimodal AI connects images, text and clinical information; how real medical imaging data is stored and processed; how representative models operate; how to run and interpret a practical demonstration; and why validation and human oversight remain essential.

The central message:

**Multimodal AI can connect medical images with clinical language and other patient information to support representation learning, retrieval, classification, segmentation and clinical decision support, but its outputs must be interpreted carefully and validated for their intended use.**

**Build the complete deck and notebook, run the real workflows, inspect the rendered slides, and only then report completion.**
