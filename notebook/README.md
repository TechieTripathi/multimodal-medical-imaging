# Companion notebook

`multimodal-medical-imaging.ipynb` runs three workflows on one real, de-identified patient from a public archive:

| | Workflow | Model | GPU | Laptop CPU |
|---|---|---|---|---|
| A | Load a DICOM CT, sort slices, convert to Hounsfield units, window, view in three planes | none | seconds | seconds |
| B | Prepare the patient's X-ray from DICOM and match it with descriptions | BiomedCLIP | 0.025 s per image | about 1.2 s per image |
| C | Outline anatomy (TotalSegmentator) and the nodule (MedSAM); compare with four radiologists | TotalSegmentator, MedSAM | about 1–2.5 min | several minutes (fast mode) |
| D | Open real DICOM from six kinds of scanner; ultrasound frames; PET SUV from tags; PET/CT fusion | none | seconds | seconds |
| E | Analyses and insights: CT tissue composition, the four readers' nodule measurements (DICOM SEG), PET tumour SUV statistics, metadata audit | none | seconds | seconds |

Times were measured on an NVIDIA RTX PRO 4000 Blackwell (24 GB) on 30 October 2026; your CPU times will vary.

## Setup

```bash
conda create -n mmfdp python=3.11 -y && conda activate mmfdp
# PyTorch for your machine (see the comment at the top of requirements.txt), then:
pip install -r requirements.txt
python download_data.py          # about 170 MB: the patient's CT, X-ray, reader files, and one brain MRI
jupyter lab multimodal-medical-imaging.ipynb
```

The first run of each model downloads its weights from Hugging Face or GitHub (BiomedCLIP about 800 MB, MedSAM about 360 MB, TotalSegmentator about 1 GB). On a machine without internet during the session, run the notebook once beforehand.

Workflow E also runs from a terminal, with the same code generated from the notebook cells:

```bash
python dicom_insights.py all        # or: tissue, nodule, pet, audit; figures are saved in figures/ (add --show to display them)
```

Workflow D needs no download: it reads the sample pack in `../public/dicom/`. `python download_data.py --dicom` fetches the originals behind it (about 480 MB).

Optional: `python download_data.py --all` also fetches the Indiana University X-rays (1.4 GB), pathology tiles (800 MB), ultrasound (130 MB) and retina photographs (1.8 GB) used on other slides. Cell B4 needs the IU X-rays.

## Data and licences

| Dataset | What | Licence |
|---|---|---|
| LIDC-IDRI (TCIA), patient LIDC-IDRI-0001 | Chest CT, chest X-ray, four radiologists' outlines and ratings | CC BY 3.0 |
| UPENN-GBM (TCIA), patient UPENN-GBM-00001 | Brain MRI: T1, T1 + contrast, T2, FLAIR | CC BY 4.0 |
| Indiana University chest X-rays (Open-i) | X-rays (PNG) and reports | Check Open-i's terms; we treat it as CC BY-NC-ND 4.0 and show images unmodified |
| CRC-VAL-HE-7K (Zenodo) | Colorectal tissue tiles | CC BY 4.0 |
| HC18 (Zenodo) | Fetal head ultrasound with outlines | CC BY 4.0 |
| FIVES (figshare) | Fundus photographs with vessel outlines | CC BY 4.0 |
| CMMD (TCIA), patient D2-0333 | Mammograms (DICOM) and clinical table | CC BY 4.0 |
| B-mode-and-CEUS-Liver (TCIA), LiverUS-01 | Multi-frame liver ultrasound (DICOM) | CC BY 4.0 |
| FDG-PET-CT-Lesions (TCIA, defaced release), PETCT_b899150306 | PET, CT and lesion SEG (DICOM) | CC BY 4.0 |

## Privacy

These datasets were de-identified by their publishers. Hospital DICOM files are not: they carry names, dates and IDs in their tags, and sometimes burned-in text in the pixels. Do not upload patient files to online notebooks or AI services, and follow your institution's ethics and data-protection rules.

## Interpreting the outputs

* **Cosine scores** (B2) rank descriptions for one image. They sit in a narrow band (about 0.2–0.5 for BiomedCLIP) and only their order is meaningful. They are not probabilities and not diagnoses.
* **Softmax values** (B3) look like probabilities but are not calibrated: a gap of 0.004 in cosine becomes 0.42 against 0.29.
* **Preparation matters.** The notebook prepares the X-ray straight from DICOM; the slides used a masked PNG. The scores differ slightly (0.405 vs 0.409 for the top description).
* **Segmentation** (C1–C3): TotalSegmentator outlines anatomy, not disease; the nodule sits inside its "lung" label. MedSAM outlined the nodule smaller than the radiologists (Dice about 0.75 against readers who agree with each other at 0.84–0.90 in 3D).
* All models here are research software, not medical devices.

## Troubleshooting

| Problem | Fix |
|---|---|
| `FileNotFoundError` for `data/raw/lidc` | Run `python download_data.py` from this folder |
| Model download fails | Check internet access; Hugging Face may be blocked on some networks. Run once on an open network to cache the weights |
| CUDA out of memory | Restart the kernel; set `DEVICE = 'cpu'` in the setup cell |
| TotalSegmentator very slow | Expected on CPU; the notebook uses `fast=True` there. Or use the saved result in `data/work/ts/` |
| `np.float64(...)` in printed lists | Harmless formatting from NumPy 2 |

## Files

| File | Purpose |
|---|---|
| `multimodal-medical-imaging.ipynb` | The notebook (built by `build_notebook.py`; executed outputs included) |
| `download_data.py` | Downloads the datasets into `data/raw/` |
| `prepare_deck_assets.py` | Builds the small derived images and arrays in `../data/imaging/` that the slides use |
| `run_biomedclip.py`, `run_segmentation.py`, `run_cnn_features.py` | Produce the model results in `../data/runs/` that the slides show |
| `build_notebook.py` | Writes the notebook and `dicom_insights.py`; `--extract` copies the executed cells shown on the demo slides |
| `dicom_insights.py` | Workflow E as a terminal script (generated; edit the cells in `build_notebook.py`) |

To rebuild everything the slides show:

```bash
python prepare_deck_assets.py ct dx sr mri gallery dicom pipeline
python run_segmentation.py
python prepare_deck_assets.py attn apps
python download_data.py --dicom && python prepare_deck_assets.py dicom_examples   # the DICOM sample pack and PET/CT arrays
python run_cnn_features.py
python run_biomedclip.py            # all parts; needs the --all datasets
python build_notebook.py && jupyter nbconvert --to notebook --execute --inplace multimodal-medical-imaging.ipynb && python build_notebook.py --extract
```
