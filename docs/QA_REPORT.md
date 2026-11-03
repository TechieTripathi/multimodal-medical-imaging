# QA report

Deck: *Multimodal AI Models for Medical Imaging Analysis*. Checked 30 October 2026.

## Result

| Check | Result |
|---|---|
| Core slides | 66, in 7 sections (8 / 10 / 10 / 12 / 9 / 12 / 5), plus an unnumbered cover, 7 unnumbered section openers and a 5-page Sources appendix |
| Timing | Speaker-note times sum to exactly 120 min; every section matches its budget |
| Speaker notes | On every slide; demo slides add Steps, Expected observations, Likely failure modes, Fallback |
| Honesty labels | One per slide where a visual needs it; every "Real model output" label points to a run file that exists (checked by script) |
| Artifacts | All 26 artifacts in IDEA.md §6.3 built (25: live DICOM viewer, 26: PET/CT fusion, added 2 November 2026); artifacts 3, 4, 5, 6, 7, 10, 11, 14, 15, 18, 19, 20, 22 compute from real data in the page |
| Sources | 34, all used on slides. DOIs checked against Crossref or DataCite; arXiv abstracts read; legal sources opened on official sites |
| Offline build | `exports/spa`, 23 MB including the 5.3 MB DICOM sample pack, no runtime network calls |
| PDF | All click states (246 pages), handout (77 pages), speaker notes (35 pages); DICOM slides render their real files |
| Notebook | Executes top to bottom on GPU (RTX PRO 4000) in a clean env; outputs saved; demo slides show its cells and outputs |
| Colab notebook | `dicom-analysis-colab.ipynb` run end to end from an empty folder (clone the repo, download from TCIA): 16 code cells in 27 s, outputs match the main notebook; Colab buttons and QR codes point to the GitHub copies |

## Tests performed

1. **Static checks** (`npm run check`): slide count, sections, notes, placeholders, citation keys, honesty tags, run files, word limit (no slide over the limit), timing.
2. **DICOM reader** (`scripts/test-dicom.mjs`): the in-browser reader (`composables/dicom.ts`, dicom-parser) matches pydicom on all 7 sample files: tags, pixel min/max/mean after rescale, and the PET SUV factor. Demo E's Python outputs (notebook cells E2, E3; same code as `dicom_insights.py`) match the nodule volumes, diameters and mean HU per reader and the PET SUVmax, SUVmean, area and ratio computed independently in `prepare_deck_assets.py`. Privacy gate in `prepare_deck_assets.py`: identifying tags empty, private tags removed; every image inspected for burned-in text (ultrasound header band blacked out).
3. **Tokenizer** (`scripts/test-wordpiece.mjs`): the in-page WordPiece tokenizer matches the Hugging Face BiomedBERT tokenizer on 6 sentences, tokens and IDs.
3. **Links** (`npm run check:urls`): 29 of 34 URLs return 200; the 5 that return 403 are publisher DOI pages (NEJM AI ×2, RSNA, Wiley, Oxford) that block scripts, each confirmed through Crossref.
4. **Visual review**: every slide screenshotted at its first and last click state (and intermediate states for step-driven artifacts) and inspected; overflow, overlap and clipping fixed.
5. **Interaction tests** (Playwright): the DICOM viewer switches files and opens a local `.dcm` (read in the browser, no upload); the ultrasound frame slider and PET/CT opacity slider change the image; the windowing slider changes the rendered CT; typing in the tokenizer re-tokenizes ("Pneumothorax" → one token); removing the top description in the ranking viewer re-ranks it. Typing does not advance the slide.
6. **PDF**: canvas-based slides (windowing, three planes, segmentation overlay) render correctly in the export.
7. **Facts in notes checked against data**: nodule HU (83) and stored value (1,107); nodule in the left lower lobe (99.9% of reader voxels inside TotalSegmentator's label); reader agreement; all model numbers read from run files.

## Real results the deck reports (from `data/runs/`)

| Experiment | Result |
|---|---|
| Zero-shot pathology, 900 tiles, 4 wordings | 8% → 36% → 38% → 52% (chance 11%) |
| Same task, general CLIP ViT-L/14 | best 48% |
| Few labelled tiles + small classifier | 1 per class 75%; 10 per class 91% |
| Zero-shot cardiomegaly vs normal, 645 IU X-rays | AUROC 0.90 |
| Top-1 description over 1,262 single-finding IU X-rays | normal 90%; cardiomegaly 7/25; effusion 1/5; pneumothorax 0/2 |
| Six image–report pairs | right report ranked first for 2 of 6 |
| Search "enlarged heart" | 5 of top 5 correct |
| Simulated scanner changes | AUROC 0.90 → 0.85 |
| Retina zero-shot, 4 diagnoses, 200 photos | 27% (chance 25%) |
| MedSAM vs 4 radiologists (nodule slice) | Dice 0.75–0.77; readers among themselves 0.91–0.94 (slice), 0.84–0.90 (3D) |
| TotalSegmentator | lungs 3.7 L, heart 370 ml; nodule 99.9% inside "lung" |
| BiomedCLIP speed | 0.0051 s per image on GPU, 0.032 s on the workstation CPU (re-run 3 November 2026) |
| PET SUV from DICOM tags | 300 MBq FDG, scan 60.1 min after injection, 205.3 MBq left, 61 kg; tumour SUVmax 18.1 (3D), 14.2 on the shown slice; volume 134 ml |

## Known limitations and open items

- **IU X-ray licence.** Not confirmed from NLM's own site (automated access blocked). Treated as CC BY-NC-ND 4.0: images shown unmodified with credit. **Confirm before publishing the deck publicly.**
- **No report-generation model was run.** MedGemma's download is gated by terms only the account holder can accept. Slides 27 and 57 use labelled simulated text checked against real evidence. If the terms are accepted, a real run can replace them.
- **Cover details.** Session label and date are blank in `slides.md`.
- **Small samples.** Several experiments use one patient or a few hundred images; the notes say so.
- **Preparation differences.** The slides' X-ray (masked PNG) and the notebook's (straight from DICOM) give slightly different scores (0.409 vs 0.405); slide 50 uses this as a teaching point.
- **Laws change.** DPDP Rules phase in until about May 2027; CDSCO's software guidance is from July 2026. Re-check before each delivery.
- **No PowerPoint export** was made; the deck runs as a website or PDF.
- **Not yet rehearsed live** with a projector, a clinician and a non-technical colleague (IDEA.md §13).
