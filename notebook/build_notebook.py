"""Write the companion notebook, multimodal-medical-imaging.ipynb, from the cells below.

Cells tagged with a `deck` id (A1, A2, …) are shown on the demonstration slides: after the notebook has
been executed, `python build_notebook.py --extract` copies their code and text output to
../data/notebook/cells.json, so the slides always show the code that actually ran.

Usage (from notebook/):
  python build_notebook.py                     # write the .ipynb
  jupyter nbconvert --to notebook --execute --inplace multimodal-medical-imaging.ipynb
  python build_notebook.py --extract           # copy tagged cells and outputs for the deck
"""
import base64
import json
import os
import sys

import nbformat as nbf

HERE = os.path.dirname(os.path.abspath(__file__))
NB = os.path.join(HERE, 'multimodal-medical-imaging.ipynb')

CELLS = [
    ('md', None, """# Multimodal AI for medical imaging: hands-on notebook

Companion to the FDP session *Multimodal AI Models for Medical Imaging Analysis*. Three workflows on real, public, de-identified data:

| | Workflow | Data | Model |
|---|---|---|---|
| A | Load and view a DICOM CT study | LIDC-IDRI-0001 (TCIA, CC BY 3.0) | none |
| B | Match an X-ray with descriptions | the same patient's chest X-ray (DICOM), plus Indiana University X-rays (PNG) | BiomedCLIP |
| C | Outline anatomy and a nodule | the same CT | TotalSegmentator, MedSAM |

**Before you start:** run `python download_data.py` once (about 90 MB for workflows A–C; the optional IU X-ray set is 1.4 GB). See `README.md` for setup, runtimes and troubleshooting.

**Privacy.** These datasets were de-identified by their publishers. Hospital DICOM files are not: never upload real patient files to online notebooks or AI services.

**Interpretation.** Every score in this notebook is a research output, not a diagnosis."""),
    ('code', None, """# Colab only: fetch the project and data and install what Colab lacks (about 5 minutes).
# In Colab choose Runtime > Change runtime type > GPU first. Elsewhere this cell does nothing.
import os, subprocess, sys
if 'google.colab' in sys.modules and not os.path.exists('download_data.py'):
    if not os.path.exists('multimodal-medical-imaging'):
        subprocess.run(['git', 'clone', '--depth', '1', 'https://github.com/TechieTripathi/multimodal-medical-imaging.git'], check=True)
    os.chdir('multimodal-medical-imaging/notebook')
    subprocess.run([sys.executable, '-m', 'pip', 'install', '-q', 'pydicom', 'SimpleITK', 'nibabel', 'open_clip_torch', 'TotalSegmentator'], check=True)
    subprocess.run([sys.executable, 'download_data.py'], check=True)
print('Working folder:', os.getcwd())"""),
    ('code', None, """# Setup: libraries and paths. Runs on a GPU if one is available, otherwise on the CPU.
import glob, json, os, time
import numpy as np
import matplotlib.pyplot as plt
import pydicom
import SimpleITK as sitk
import torch

DATA = 'data/raw'
LIDC = os.path.join(DATA, 'lidc')
DEVICE = 'cuda' if torch.cuda.is_available() else 'cpu'
print('Running on', torch.cuda.get_device_name(0) if DEVICE == 'cuda' else 'CPU')"""),

    ('md', None, """## Workflow A — DICOM loading and visualisation

### A1. A folder of files is not yet a scan
A CT series arrives as one file per slice. File names say nothing about where a slice sits in the body."""),
    ('code', 'A1', """# A1. Read every file's header (not the pixels yet) and look at its position
ct_dir = glob.glob(os.path.join(LIDC, 'CT-*'))[0]
files = sorted(glob.glob(os.path.join(ct_dir, '*.dcm')))
headers = [pydicom.dcmread(f, stop_before_pixels=True) for f in files]

for f, h in list(zip(files, headers))[:4]:
    print(os.path.basename(f), '| instance', h.InstanceNumber,
          '| z =', float(h.ImagePositionPatient[2]), 'mm')

# Sort by height in the body (z), not by file name
order = np.argsort([float(h.ImagePositionPatient[2]) for h in headers])
headers = [headers[i] for i in order]
files = [files[i] for i in order]
print(len(files), 'slices, from z =', float(headers[0].ImagePositionPatient[2]),
      'to', float(headers[-1].ImagePositionPatient[2]), 'mm')"""),
    ('code', 'A1b', """# A1b. A few tags that matter for analysis (and one group that matters for privacy)
h = headers[0]
for kw in ['Modality', 'Manufacturer', 'SliceThickness', 'PixelSpacing',
           'RescaleSlope', 'RescaleIntercept', 'PatientName', 'PatientIdentityRemoved']:
    print(f'{kw:24s}', h.get(kw, '(not present)'))"""),

    ('md', None, """### A2. Stored numbers → Hounsfield units → a picture
Each file stores integers. `RescaleSlope` and `RescaleIntercept` turn them into Hounsfield units (HU). A *window* then chooses which HU become black to white."""),
    ('code', 'A2', """# A2. Build the volume in Hounsfield units, then show one slice with three windows
volume = np.stack([pydicom.dcmread(f).pixel_array for f in files]).astype(np.float32)
volume = volume * float(h.RescaleSlope) + float(h.RescaleIntercept)   # stored → HU

def window(img, level, width):
    lo = level - width / 2
    return np.clip((img - lo) / width, 0, 1)

k = 89                                         # the slice through the nodule
fig, axes = plt.subplots(1, 3, figsize=(12, 4))
for ax, (name, L, W) in zip(axes, [('Lung', -600, 1500), ('Soft tissue', 40, 400), ('Bone', 400, 1800)]):
    ax.imshow(window(volume[k], L, W), cmap='gray'); ax.set_title(f'{name} (L {L}, W {W})'); ax.axis('off')
plt.show()
print('HU range on this slice:', int(volume[k].min()), 'to', int(volume[k].max()))"""),

    ('md', None, """### A3. Three planes from one volume
SimpleITK reads a series, sorts it and keeps the spacing, so views in other planes have the right proportions."""),
    ('code', 'A3', """# A3. Let SimpleITK read and sort the series, then cut it three ways
reader = sitk.ImageSeriesReader()
reader.SetFileNames(reader.GetGDCMSeriesFileNames(ct_dir))
ct = reader.Execute()                          # already in HU, with spacing and position
arr = sitk.GetArrayFromImage(ct)               # (z, y, x)
sx, sy, sz = ct.GetSpacing()
print('Size', ct.GetSize(), '| spacing (mm)', tuple(round(s, 2) for s in ct.GetSpacing()))

z, y, x = 89, 367, 316                         # the nodule
fig, axes = plt.subplots(1, 3, figsize=(13, 4.5))
axes[0].imshow(window(arr[z], -600, 1500), cmap='gray'); axes[0].set_title('Axial')
axes[1].imshow(window(arr[::-1, y, :], -600, 1500), cmap='gray', aspect=sz / sx); axes[1].set_title('Coronal')
axes[2].imshow(window(arr[::-1, :, x], -600, 1500), cmap='gray', aspect=sz / sy); axes[2].set_title('Sagittal')
for ax in axes: ax.axis('off')
plt.show()"""),
    ('code', 'A4', """# A4. Other modalities, other rules: the same patient's X-ray, and a brain MRI series
dx = pydicom.dcmread(glob.glob(os.path.join(LIDC, 'DX-*', '*.dcm'))[0])
print('X-ray:', dx.Rows, 'x', dx.Columns, '|', dx.BitsStored, 'bits |', dx.PhotometricInterpretation,
      '| window tags', dx.WindowCenter, dx.WindowWidth, '(these look copied from a CT)')
mri_dir = os.path.join(DATA, 'upenn', 't2_Flair_axial')
if os.path.isdir(mri_dir):
    m = pydicom.dcmread(sorted(glob.glob(os.path.join(mri_dir, '*.dcm')))[0], stop_before_pixels=True)
    print('MRI:', m.SeriesDescription, '| slice', m.SliceThickness, 'mm | no Hounsfield units: values are relative')"""),

    ('md', None, """## Workflow B — Matching an X-ray with descriptions (BiomedCLIP)

BiomedCLIP turns an image and a sentence into 512 numbers each. Cosine similarity says how well they match.

BiomedCLIP does not read DICOM. We prepare the X-ray ourselves: window to 8 bits, then let the model's own preprocessing resize and normalise it."""),
    ('code', 'B1', """# B1. Load BiomedCLIP and prepare our patient's X-ray from DICOM
import open_clip
from PIL import Image

MODEL = 'hf-hub:microsoft/BiomedCLIP-PubMedBERT_256-vit_base_patch16_224'
model, preprocess = open_clip.create_model_from_pretrained(MODEL)
tokenizer = open_clip.get_tokenizer(MODEL)
model = model.to(DEVICE).eval()

px = dx.pixel_array.astype(np.float32)
lo, hi = np.percentile(px, [0.5, 99.5])                  # window: keep 99% of the values
xray = Image.fromarray((np.clip((px - lo) / (hi - lo), 0, 1) * 255).astype(np.uint8)).convert('RGB')
image = preprocess(xray).unsqueeze(0).to(DEVICE)        # resize to 224 x 224, normalise
print('Model input:', tuple(image.shape))"""),
    ('code', 'B2', """# B2. Score candidate descriptions by cosine similarity and rank them
candidates = [
    'a normal chest X-ray',
    'a chest X-ray showing an enlarged heart (cardiomegaly)',
    'a chest X-ray showing fluid around the lung (pleural effusion)',
    'a chest X-ray showing a collapsed lung (pneumothorax)',
    'a chest X-ray showing a mass in the lung',
    'an axial CT scan of the chest',
    'an MRI scan of the brain',
]
with torch.no_grad():
    img_emb = torch.nn.functional.normalize(model.encode_image(image), dim=-1)
    txt_emb = torch.nn.functional.normalize(model.encode_text(tokenizer(candidates, context_length=256).to(DEVICE)), dim=-1)
cosine = (img_emb @ txt_emb.T)[0].cpu().numpy()
for i in np.argsort(-cosine):
    print(f'{cosine[i]:.3f}  {candidates[i]}')"""),
    ('code', 'B3', """# B3. Why these are not probabilities: softmax with the model's temperature exaggerates tiny gaps
scale = model.logit_scale.exp().item()
p = torch.softmax(torch.tensor(cosine) * scale, 0).numpy()
top2 = np.argsort(-cosine)[:2]
print(f'Cosine gap between the top two: {cosine[top2[0]] - cosine[top2[1]]:.3f}')
print(f'After softmax (x{scale:.0f}): {p[top2[0]]:.2f} vs {p[top2[1]]:.2f}  <- looks confident, is not calibrated')"""),
    ('code', 'B4', """# B4. A failure case: an IU X-ray whose report says "Small bilateral pleural effusions"
iu = os.path.join(DATA, 'iu', 'png', 'CXR2747_IM-1198-1001.png')
if os.path.exists(iu):
    with torch.no_grad():
        e = torch.nn.functional.normalize(model.encode_image(preprocess(Image.open(iu).convert('RGB')).unsqueeze(0).to(DEVICE)), dim=-1)
    c = (e @ txt_emb.T)[0].cpu().numpy()
    for i in np.argsort(-c)[:3]:
        print(f'{c[i]:.3f}  {candidates[i]}')
else:
    print('IU images not downloaded; see README (optional, 1.4 GB).')"""),
    ('code', 'B5', """# B5. How long does one image take?
def time_one(device, n=20):
    m = model.to(device)
    x = image.to(device)
    with torch.no_grad():
        m.encode_image(x)                                   # warm-up
        t = time.perf_counter()
        for _ in range(n):
            m.encode_image(x)
        if device == 'cuda': torch.cuda.synchronize()
    return (time.perf_counter() - t) / n

timings = {'cpu_s': round(time_one('cpu', 5), 3)}
if DEVICE == 'cuda':
    timings['gpu_s'] = round(time_one('cuda'), 4)
model = model.to(DEVICE)
print('Seconds per image:', timings)"""),

    ('md', None, """## Workflow C — Outlining anatomy and the nodule

### C1. TotalSegmentator: 117 structures from the CT folder
TotalSegmentator reads the DICOM folder directly. On a GPU this takes about a minute; on a CPU, use `fast=True` and allow several minutes."""),
    ('code', 'C1', """# C1. Run TotalSegmentator (skipped if a result already exists) and overlay a few structures
from totalsegmentator.python_api import totalsegmentator
from totalsegmentator.map_to_binary import class_map

out = 'data/work/ts/total.nii.gz'
if not os.path.exists(out):
    t = time.perf_counter()
    totalsegmentator(ct_dir, out, ml=True, device='gpu' if DEVICE == 'cuda' else 'cpu', fast=DEVICE != 'cuda')
    print(f'TotalSegmentator took {time.perf_counter() - t:.0f} s')
labels = sitk.GetArrayFromImage(sitk.Resample(sitk.ReadImage(out), ct, sitk.Transform(), sitk.sitkNearestNeighbor, 0))
names = class_map['total']
voxel_ml = sx * sy * sz / 1000
for part in ['lung_lower_lobe_left', 'heart', 'aorta', 'liver']:
    i = [k for k, v in names.items() if v == part][0]
    print(f'{part:22s} {np.sum(labels == i) * voxel_ml:8.1f} ml')

plt.figure(figsize=(5, 5))
plt.imshow(window(arr[z], -600, 1500), cmap='gray')
plt.imshow(np.ma.masked_equal(labels[z], 0), cmap='tab20', alpha=0.45, interpolation='nearest')
plt.axis('off'); plt.title('TotalSegmentator labels, slice 89'); plt.show()"""),
    ('code', 'C2', """# C2. Check against the radiologists: does any label mark the nodule? Where does MedSAM agree?
seg_files = sorted(glob.glob(os.path.join(LIDC, 'SEG-*', '*.dcm')))
readers = []
for f in seg_files:
    s = pydicom.dcmread(f)
    m = np.zeros(arr.shape, bool)
    for fr, plane in zip(np.atleast_3d(s.pixel_array.transpose(1, 2, 0)).transpose(2, 0, 1), s.PerFrameFunctionalGroupsSequence):
        kz = int(round((float(plane.PlanePositionSequence[0].ImagePositionPatient[2]) - ct.GetOrigin()[2]) / sz))
        m[kz] |= fr.astype(bool)
    readers.append(m)
nodule = np.any(readers, axis=0)
lung_ids = [k for k, v in names.items() if v.startswith('lung_')]
print(f'Nodule voxels inside the TotalSegmentator lung label: {np.isin(labels[nodule], lung_ids).mean():.1%}')
print('-> the lung outline swallows the tumour; this model outlines anatomy, not disease')

def dice(a, b): return float(2 * (a & b).sum() / (a.sum() + b.sum()))
print('Radiologist vs radiologist (3D Dice):', [round(dice(readers[0], r), 2) for r in readers[1:]])"""),
    ('code', 'C3', """# C3. MedSAM: a box around the nodule on slice 89 -> an outline, compared with each radiologist
from transformers import SamModel, SamProcessor
ys, xs = np.nonzero(nodule[z])
box = [int(xs.min()) - 5, int(ys.min()) - 5, int(xs.max()) + 5, int(ys.max()) + 5]
rgb = np.repeat((window(arr[z], 40, 400) * 255).astype(np.uint8)[..., None], 3, axis=2)
proc = SamProcessor.from_pretrained('wanglab/medsam-vit-base')
sam = SamModel.from_pretrained('wanglab/medsam-vit-base').to(DEVICE).eval()
with torch.no_grad():
    inp = proc(rgb, input_boxes=[[box]], return_tensors='pt').to(DEVICE)
    out_ = sam(**inp, multimask_output=False)
mask = proc.image_processor.post_process_masks(out_.pred_masks.sigmoid().cpu(), inp['original_sizes'].cpu(),
                                               inp['reshaped_input_sizes'].cpu(), binarize=False)[0][0, 0].numpy() > 0.5
print('MedSAM vs each radiologist (Dice on this slice):', [round(dice(mask, r[z]), 2) for r in readers])"""),

    ('md', None, """## Workflow D — Real DICOM files from six kinds of scanner

The sample pack in `../public/dicom/` holds small *teaching copies* of real DICOM files from public collections: every original tag kept, private tags removed, pixels downsampled where needed, and the change written into each file's `DerivationDescription`. The same files open in the deck's DICOM viewer slide and can be downloaded from it."""),
    ('code', 'D1', """# D1. Open every file and print the tags that matter for each kind of scan
pack = sorted(glob.glob('../public/dicom/*.dcm'))
for f in pack:
    d = pydicom.dcmread(f)
    frames = int(d.get('NumberOfFrames', 1))
    print(f"{os.path.basename(f):28s} {d.Modality:3s} {d.Rows}x{d.Columns}"
          f"{f' x{frames} frames' if frames > 1 else ''}  {d.PhotometricInterpretation:11s} {d.BitsStored}-bit"
          f"  units: {'HU' if d.Modality == 'CT' else d.get('Units', '-')}")
print()
print('Change recorded in one file:', pydicom.dcmread(pack[0]).DerivationDescription)"""),
    ('code', 'D2', """# D2. Modality-specific details: which breast (mammogram), and an ultrasound file is a video
mg = pydicom.dcmread('../public/dicom/mammo-cmmd-d2-0333.dcm')
print('Mammogram: ImageLaterality =', mg.ImageLaterality, '| ViewPosition =', mg.get('ViewPosition', 'not recorded'))
us = pydicom.dcmread('../public/dicom/us-liver-ceus.dcm')
cine = us.pixel_array                                   # (frames, rows, columns, 3): colour video
print('Ultrasound:', cine.shape, '| FrameTime', float(us.FrameTime), 'ms | duration', round(cine.shape[0] * float(us.FrameTime) / 1000, 1), 's')
fig, axes = plt.subplots(1, 3, figsize=(12, 3))
for ax, k in zip(axes, [0, cine.shape[0] // 2, cine.shape[0] - 1]):
    ax.imshow(cine[k]); ax.set_title(f'frame {k + 1}'); ax.axis('off')
plt.show()"""),
    ('code', 'D3', """# D3. PET pixels are Bq/ml; the file's own tags turn them into SUV (body weight, decay-corrected)
pet = pydicom.dcmread('../public/dicom/pet-fdg-lung.dcm')
r = pet.RadiopharmaceuticalInformationSequence[0]
tm = lambda t: int(t[:2]) * 3600 + int(t[2:4]) * 60 + float(t[4:])
minutes = (tm(pet.SeriesTime) - tm(r.RadiopharmaceuticalStartTime)) / 60
dose_now = float(r.RadionuclideTotalDose) * 2 ** (-minutes * 60 / float(r.RadionuclideHalfLife))
suv = pet.pixel_array * float(pet.RescaleSlope) * float(pet.PatientWeight) * 1000 / dose_now
print(f'{r.Radiopharmaceutical}: {float(r.RadionuclideTotalDose) / 1e6:.0f} MBq, scan {minutes:.1f} min later'
      f' -> {dose_now / 1e6:.1f} MBq left; weight {pet.PatientWeight} kg; max SUV on this slice {suv.max():.1f}')"""),
    ('code', 'D4', """# D4. PET/CT fusion: the PET and CT files share a frame of reference, so their positions line up
ct2 = pydicom.dcmread('../public/dicom/ct-fdg-lung.dcm')
hu2 = ct2.pixel_array * float(ct2.RescaleSlope) + float(ct2.RescaleIntercept)
print('Same frame of reference:', pet.FrameOfReferenceUID == ct2.FrameOfReferenceUID,
      '| CT', ct2.Rows, 'px at', float(ct2.PixelSpacing[0]), 'mm; PET', pet.Rows, 'px at', float(pet.PixelSpacing[0]), 'mm')
# Place both in millimetres and draw PET on top of CT
ext = lambda d: [float(d.ImagePositionPatient[0]), float(d.ImagePositionPatient[0]) + d.Columns * float(d.PixelSpacing[1]),
                 float(d.ImagePositionPatient[1]) + d.Rows * float(d.PixelSpacing[0]), float(d.ImagePositionPatient[1])]
plt.figure(figsize=(5, 5))
plt.imshow(window(hu2, 40, 400), cmap='gray', extent=ext(ct2))
plt.imshow(np.ma.masked_less(suv, 1.5), cmap='hot', vmin=0, vmax=8, alpha=0.6, extent=ext(pet))
plt.xlim(ext(ct2)[:2]); plt.ylim(ext(ct2)[2:]); plt.axis('off'); plt.title('PET (SUV) on CT'); plt.show()"""),

    ('md', None, """## Workflow E — Analyses and insights from DICOM, in Python

Four short analyses on the sample pack, each ending in one insight. The same code is also written to `dicom_insights.py`, so it runs from a terminal too:

```bash
python dicom_insights.py all        # or: tissue, nodule, pet, audit; figures are saved in figures/
```"""),
    ('code', 'E0', """# E0. Helpers shared by E1-E4 (also the top of dicom_insights.py)
import os
import numpy as np
import pydicom
import matplotlib.pyplot as plt

PACK = '../public/dicom'
FIG_DIR = None                       # set to a folder to save figures instead of showing them


def load(name):
    return pydicom.dcmread(os.path.join(PACK, name))


def values(ds):
    \"\"\"Pixel values in the file's real units (rescale slope and intercept applied).\"\"\"
    return ds.pixel_array * float(ds.get('RescaleSlope', 1)) + float(ds.get('RescaleIntercept', 0))


def seg_on(seg, img):
    \"\"\"A DICOM SEG mask placed on one image slice, using both files' positions and orientations.\"\"\"
    sh = seg.SharedFunctionalGroupsSequence[0]
    sy, sx = (float(v) for v in sh.PixelMeasuresSequence[0].PixelSpacing)
    half = float(sh.PixelMeasuresSequence[0].SliceThickness) / 2
    iop = np.array(sh.PlaneOrientationSequence[0].ImageOrientationPatient, float)
    o, ipp, (py, px) = np.array(img.ImageOrientationPatient, float), np.array(img.ImagePositionPatient, float), (float(v) for v in img.PixelSpacing)
    frames = seg.pixel_array.reshape(-1, seg.Rows, seg.Columns)
    for frame, item in zip(frames, seg.PerFrameFunctionalGroupsSequence):
        pos = np.array(item.PlanePositionSequence[0].ImagePositionPatient, float)
        if abs(pos[2] - ipp[2]) < half:
            r, c = np.mgrid[0:img.Rows, 0:img.Columns]
            p = ipp + c[..., None] * o[:3] * px + r[..., None] * o[3:] * py - pos
            sc, sr = np.rint(p @ iop[:3] / sx).astype(int), np.rint(p @ iop[3:] / sy).astype(int)
            ok = (sr >= 0) & (sr < seg.Rows) & (sc >= 0) & (sc < seg.Columns)
            mask = np.zeros((img.Rows, img.Columns), bool)
            mask[ok] = frame[sr[ok], sc[ok]] > 0
            return mask
    return np.zeros((img.Rows, img.Columns), bool)


def longest(mask, ds):
    \"\"\"Longest distance (mm) between two pixels of a 2D mask.\"\"\"
    ys, xs = np.nonzero(mask)
    pts = np.stack([xs * float(ds.PixelSpacing[1]), ys * float(ds.PixelSpacing[0])], 1)
    return float(np.sqrt(((pts[:, None] - pts[None]) ** 2).sum(-1)).max())


def suv_factor(pet):
    \"\"\"Body-weight SUV per Bq/ml, decay-corrected to series start, from the PET file's tags.\"\"\"
    r = pet.RadiopharmaceuticalInformationSequence[0]
    tm = lambda t: int(t[:2]) * 3600 + int(t[2:4]) * 60 + float(t[4:])
    dose = float(r.RadionuclideTotalDose) * 2 ** (-(tm(pet.SeriesTime) - tm(r.RadiopharmaceuticalStartTime)) / float(r.RadionuclideHalfLife))
    return float(pet.PatientWeight) * 1000 / dose


def show(fig, name):
    if FIG_DIR:
        os.makedirs(FIG_DIR, exist_ok=True)
        fig.savefig(os.path.join(FIG_DIR, f'{name}.png'), dpi=120, bbox_inches='tight')
        plt.close(fig)
        print('figure saved:', os.path.join(FIG_DIR, f'{name}.png'))
    else:
        plt.show()"""),
    ('code', 'E1', """# E1. CT: what tissue is on this slice? Hounsfield units sort the pixels; pixel size gives cm²
ct = load('ct-lidc-0001.dcm')
hu = values(ct)
cm2 = float(ct.PixelSpacing[0]) * float(ct.PixelSpacing[1]) / 100
bands = {'lung': (-950, -500), 'fat': (-150, -30), 'soft tissue': (-30, 100), 'bone': (300, 3000)}
area = {k: ((hu >= lo) & (hu < hi)).sum() * cm2 for k, (lo, hi) in bands.items()}
for k, v in area.items():
    print(f'{k:12s} {v:5.0f} cm²')
print(f"Insight: lung is {100 * area['lung'] / sum(area.values()):.0f}% of the tissue on this slice")
fig, ax = plt.subplots(1, 2, figsize=(10, 3.6))
ax[0].imshow(np.clip((hu + 1350) / 1500, 0, 1), cmap='gray'); ax[0].set_title('CT slice'); ax[0].axis('off')
ax[1].hist(hu.ravel(), bins=130, range=(-1100, 1500), log=True); ax[1].set_xlabel('Hounsfield units'); ax[1].set_title('Pixel values')
show(fig, 'E1_tissue')"""),
    ('code', 'E2', """# E2. CT: measure the nodule each of four radiologists outlined (DICOM SEG files)
ct = load('ct-lidc-0001.dcm')
hu = values(ct)
fig, ax = plt.subplots(figsize=(3.6, 3.6))
ax.imshow(np.clip((hu + 160) / 400, 0, 1), cmap='gray')
volumes = []
for r, colour in zip(range(1, 5), ['gold', 'cyan', 'magenta', 'lime']):
    seg = load(f'seg-lidc-0001-reader{r}.dcm')
    pm = seg.SharedFunctionalGroupsSequence[0].PixelMeasuresSequence[0]
    volumes.append((seg.pixel_array > 0).sum() * float(pm.PixelSpacing[0]) * float(pm.PixelSpacing[1]) * float(pm.SliceThickness) / 1000)
    m = seg_on(seg, ct)
    print(f'Reader {r}: {volumes[-1]:.1f} cm³, longest {longest(m, ct):.0f} mm, mean {hu[m].mean():.0f} HU')
    ax.contour(m, levels=[0.5], colors=colour, linewidths=1)
ys, xs = np.nonzero(m)
ax.set_xlim(xs.min() - 30, xs.max() + 30); ax.set_ylim(ys.max() + 30, ys.min() - 30); ax.axis('off'); ax.set_title('Four outlines')
print(f'Insight: same nodule, same images, volumes differ by {100 * (max(volumes) / min(volumes) - 1):.0f}%')
show(fig, 'E2_nodule')"""),
    ('code', 'E3', """# E3. PET: how hot is the tumour? SUV from the file's own tags; tumour from the expert's DICOM SEG
pet = load('pet-fdg-lung.dcm')
suv = values(pet) * suv_factor(pet)
lesion = seg_on(load('seg-fdg-lung-slice.dcm'), pet)
background = (suv > 0.3) & ~lesion
area = lesion.sum() * float(pet.PixelSpacing[0]) * float(pet.PixelSpacing[1]) / 100
print(f'SUVmax {suv[lesion].max():.1f} | SUVmean {suv[lesion].mean():.1f} | area {area:.1f} cm²')
print(f'Insight: tumour-to-background ratio {suv[lesion].mean() / suv[background].mean():.1f}: about {suv[lesion].mean() / suv[background].mean():.0f}x more sugar')
fig, ax = plt.subplots(figsize=(3.6, 3.6))
ax.imshow(suv, cmap='gray_r', vmin=0, vmax=8); ax.contour(lesion, levels=[0.5], colors='gold', linewidths=1.2)
ys, xs = np.nonzero(lesion)
ax.set_xlim(xs.min() - 50, xs.max() + 50); ax.set_ylim(ys.max() + 50, ys.min() - 50); ax.axis('off'); ax.set_title('SUV, tumour outlined')
show(fig, 'E3_pet')"""),
    ('code', 'E4', """# E4. Audit the metadata of every image file in the pack
print(f"{'File':28s}{'Modality':9s}{'Identity removed':17s}{'Birth date':11s}{'Pixel size':14s}Private tags")
missing = 0
files = sorted(f for f in os.listdir(PACK) if f.endswith('.dcm') and not f.startswith('seg-'))
for f in files:
    d = load(f)
    size = d.get('PixelSpacing') or d.get('ImagerPixelSpacing')
    missing += size is None
    private = sum(e.tag.is_private for e in d)
    print(f"{f:28s}{d.Modality:9s}{d.get('PatientIdentityRemoved', 'not stated'):17s}{d.get('PatientBirthDate') or 'empty':11s}"
          f"{(f'{float(size[0]):.3f} mm' if size else 'not recorded'):14s}{private}")
print(f'Insight: {missing} of {len(files)} files record no pixel size, so nothing in them can be measured in mm')"""),

    ('md', None, """## Interpreting what you saw

* **Cosine scores** rank options for one image. They are not probabilities, and not diagnoses. Small gaps mean the model is unsure.
* **Softmax "probabilities"** from CLIP-style models are not calibrated; do not report them as confidence.
* **Segmentation** is only as good as its purpose: TotalSegmentator outlines anatomy and silently includes the tumour inside "lung".
* **Agreement** between experts is itself imperfect (Dice about 0.84–0.90 here), so a model's Dice must be judged against that.
* **Preparation** choices (window, resize, which series) change results. Write them down.

## Save this run's numbers for the slides"""),
    ('code', 'SAVE', """# Record what this run produced, so the slides can show where their numbers came from
os.makedirs('../data/runs', exist_ok=True)
json.dump({'device': torch.cuda.get_device_name(0) if DEVICE == 'cuda' else 'CPU',
           'biomedclip_seconds_per_image': timings,
           'patient_xray_ranking': {candidates[i]: round(float(cosine[i]), 4) for i in np.argsort(-cosine)},
           'softmax_top2': [round(float(p[top2[0]]), 3), round(float(p[top2[1]]), 3)],
           'medsam_dice_vs_readers': [round(float(dice(mask, rd[z])), 3) for rd in readers],
           'run_date': time.strftime('%Y-%m-%d')},
          open('../data/runs/notebook.json', 'w'), indent=1)
print('saved ../data/runs/notebook.json')"""),
]


COLAB_NB = os.path.join(HERE, 'dicom-analysis-colab.ipynb')
COLAB_URL = 'https://colab.research.google.com/github/TechieTripathi/multimodal-medical-imaging/blob/main/notebook/'


def colab_cells():
    """Cells of dicom-analysis-colab.ipynb: a real-world DICOM analysis that runs on a free Colab CPU
    in about two minutes. Reuses the tested cells A1-A3, D1-D4 and E0-E4, with paths for Colab."""
    src = {tag: code for kind, tag, code in CELLS if tag}
    pack = lambda c: c.replace("'../public/dicom/", "f'{PACK}/")
    cells = [
        ('md', None, """# Real-world DICOM analysis in Python

From the FDP session *Multimodal AI Models for Medical Imaging Analysis*. Everything here uses **real, public, de-identified DICOM files** and runs on a normal (free) Colab machine: no GPU needed, about two minutes.

1. **From the archive:** download a whole CT study and four radiologists' outlines from The Cancer Imaging Archive, sort the slices, convert to Hounsfield units, window them, view three planes and measure the nodule in 3D.
2. **Six kinds of scanner:** CT, X-ray, MRI, mammogram, ultrasound video and PET, with the tags that matter for each.
3. **Analyses and insights:** tissue composition, nodule measurements, PET tumour SUV, and a metadata audit.

**Run it:** *Runtime → Run all*, or press Shift+Enter cell by cell.

**Data:** LIDC-IDRI, UPENN-GBM, CMMD, B-mode-and-CEUS-Liver and FDG-PET-CT-Lesions from TCIA (CC BY). **Privacy:** these files were de-identified by their publishers. Never upload real patient files to Colab or any online service."""),
        ('code', 'C0', """# Setup: get the sample pack and install the DICOM libraries (about a minute)
import glob, io, os, subprocess, sys, zipfile
if os.path.exists('../public/dicom'):                 # running inside the project folder
    PACK = '../public/dicom'
else:                                                 # Colab, or anywhere else: fetch the project
    if not os.path.exists('multimodal-medical-imaging'):
        subprocess.run(['git', 'clone', '--depth', '1', 'https://github.com/TechieTripathi/multimodal-medical-imaging.git'], check=True)
    PACK = 'multimodal-medical-imaging/public/dicom'
subprocess.run([sys.executable, '-m', 'pip', 'install', '-q', 'pydicom', 'SimpleITK'], check=True)
import numpy as np
import pydicom
import requests
import SimpleITK as sitk
import matplotlib.pyplot as plt
print(len(glob.glob(f'{PACK}/*.dcm')), 'DICOM files in the sample pack')"""),
        ('md', None, """## 1. From the archive: a whole CT study

Real analyses start from an archive. Here we download one patient's chest CT (133 files) and the four radiologists' nodule outlines (DICOM SEG) from The Cancer Imaging Archive's public API."""),
        ('code', 'C1', """# 1. Download the CT series and the four outlines of patient LIDC-IDRI-0001 (about 70 MB)
API = 'https://services.cancerimagingarchive.net/nbia-api/services/v1'
DATA = 'data/raw'
LIDC = os.path.join(DATA, 'lidc')
series = requests.get(f'{API}/getSeries', params={'Collection': 'LIDC-IDRI', 'PatientID': 'LIDC-IDRI-0001'}, timeout=60).json()
for s in series:
    if s['Modality'] in ('CT', 'SEG'):
        d = os.path.join(LIDC, f"{s['Modality']}-{s['SeriesInstanceUID']}")
        if not os.path.isdir(d):
            z = requests.get(f'{API}/getImage', params={'SeriesInstanceUID': s['SeriesInstanceUID']}, timeout=600).content
            zipfile.ZipFile(io.BytesIO(z)).extractall(d)
        print(s['Modality'], len(glob.glob(os.path.join(d, '*.dcm'))), 'file(s)', s.get('SeriesDescription', ''))"""),
        ('code', 'A1', src['A1']),
        ('code', 'A1b', src['A1b']),
        ('code', 'A2', src['A2']),
        ('code', 'A3', src['A3']),
        ('code', 'C2', """# 1e. Measure the nodule in 3D from the four radiologists' DICOM SEG files, on the CT grid
z0, dz = ct.GetOrigin()[2], ct.GetSpacing()[2]
readers = []
for f in sorted(glob.glob(os.path.join(LIDC, 'SEG-*', '*.dcm'))):
    s = pydicom.dcmread(f)
    m = np.zeros(arr.shape, bool)
    for frame, item in zip(s.pixel_array.reshape(-1, s.Rows, s.Columns), s.PerFrameFunctionalGroupsSequence):
        m[int(round((float(item.PlanePositionSequence[0].ImagePositionPatient[2]) - z0) / dz))] |= frame > 0
    readers.append(m)
dice = lambda a, b: 2 * (a & b).sum() / (a.sum() + b.sum())
for i, m in enumerate(readers, 1):
    print(f'Reader {i}: {m.sum() * sx * sy * sz / 1000:.1f} ml, mean {arr[m].mean():.0f} HU, on {np.unique(np.nonzero(m)[0]).size} slices')
pairs = [dice(readers[i], readers[j]) for i in range(4) for j in range(i + 1, 4)]
print(f'Insight: the four radiologists agree with Dice {min(pairs):.2f}-{max(pairs):.2f}; judge any model against that spread')"""),
        ('md', None, """## 2. Six kinds of scanner

Small *teaching copies* of real DICOM files: every original tag kept, private tags removed, pixels downsampled where needed, and each change written into the file's `DerivationDescription`."""),
        ('code', 'D1', pack(src['D1'])),
        ('code', 'D2', pack(src['D2'])),
        ('code', 'D3', pack(src['D3'])),
        ('code', 'D4', pack(src['D4'])),
        ('md', None, """## 3. Analyses and insights

Four short analyses, each ending in one insight. The same code exists as `notebook/dicom_insights.py` in the project, for running from a terminal."""),
        ('code', 'E0', src['E0'].replace("PACK = '../public/dicom'\n", '')),
        ('code', 'E1', src['E1']),
        ('code', 'E2', src['E2']),
        ('code', 'E3', src['E3']),
        ('code', 'E4', src['E4']),
        ('md', None, """## What to take away

* **Units and geometry live in the tags.** Hounsfield units, pixel size, slice position, PET dose and timing: without them, the pixels cannot be measured.
* **Experts disagree.** Four radiologists' volumes for one nodule differ by more than a quarter.
* **Check before you trust.** Some files record no pixel size; an audit finds that in seconds.
* These are research analyses on public data, not clinical measurements."""),
    ]
    return cells


def build_colab():
    nb = nbf.v4.new_notebook()
    for kind, tag, src in colab_cells():
        nb.cells.append(nbf.v4.new_markdown_cell(src) if kind == 'md' else nbf.v4.new_code_cell(src))
    nb.metadata['kernelspec'] = {'name': 'python3', 'display_name': 'Python 3', 'language': 'python'}
    nb.metadata['colab'] = {'provenance': [], 'name': 'dicom-analysis-colab.ipynb'}
    nbf.write(nb, COLAB_NB)
    print('wrote', COLAB_NB)


def build():
    nb = nbf.v4.new_notebook()
    for kind, tag, src in CELLS:
        cell = nbf.v4.new_markdown_cell(src) if kind == 'md' else nbf.v4.new_code_cell(src)
        if tag:
            cell.metadata['deck'] = tag
        nb.cells.append(cell)
    nb.metadata['kernelspec'] = {'name': 'python3', 'display_name': 'Python 3', 'language': 'python'}
    nbf.write(nb, NB)
    print('wrote', NB)
    write_script()
    build_colab()


SCRIPT_ANALYSES = [('tissue', 'E1'), ('nodule', 'E2'), ('pet', 'E3'), ('audit', 'E4')]


def write_script():
    """dicom_insights.py: the Workflow E cells as a command-line script (same code, generated)."""
    src = {tag: code for kind, tag, code in CELLS if tag}
    head = '"""DICOM analyses and insights from the sample pack (Workflow E of the notebook), run from a terminal.\n\n' \
           'Generated from the notebook cells by build_notebook.py: edit them there, not here.\n\n' \
           'Usage (from notebook/):  python dicom_insights.py [all|tissue|nodule|pet|audit] [--show]\n' \
           'Figures are saved in figures/ unless --show is given.\n"""\n'
    body = src['E0'].replace("PACK = '../public/dicom'", "PACK = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'public', 'dicom')")
    funcs = ''
    for name, tag in SCRIPT_ANALYSES:
        code = '\n'.join(('    ' + line) if line.strip() else '' for line in src[tag].split('\n'))
        funcs += f'\n\ndef {name}():\n{code}\n'
    main = '''

if __name__ == '__main__':
    import sys
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    if '--show' not in sys.argv:
        FIG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'figures')
    names = [n for n, _ in ANALYSES] if not args or args == ['all'] else args
    for n in names:
        print(f'\\n=== {n} ===')
        dict(ANALYSES)[n]()
'''
    table = '\n\nANALYSES = [' + ', '.join(f"('{n}', {n})" for n, _ in SCRIPT_ANALYSES) + ']'
    with open(os.path.join(HERE, 'dicom_insights.py'), 'w') as f:
        f.write(head + body + funcs + table + main)
    print('wrote', os.path.join(HERE, 'dicom_insights.py'))


def extract():
    nb = nbf.read(NB, as_version=4)
    out = {}
    fig_dir = os.path.join(HERE, '..', 'data', 'notebook')
    os.makedirs(fig_dir, exist_ok=True)
    for c in nb.cells:
        tag = c.metadata.get('deck')
        if c.cell_type != 'code' or not tag:
            continue
        text = ''.join(o.get('text', '') for o in c.get('outputs', []) if o.get('output_type') == 'stream')
        figs = []
        for j, o in enumerate(o for o in c.get('outputs', []) if 'image/png' in o.get('data', {})):
            name = f'{tag}_{j}.png'
            with open(os.path.join(fig_dir, name), 'wb') as f:
                f.write(base64.b64decode(o['data']['image/png']))
            figs.append(name)
        out[tag] = {'code': c.source, 'output': text.strip(), 'figures': figs}
    dest = os.path.join(HERE, '..', 'data', 'notebook', 'cells.json')
    json.dump(out, open(dest, 'w'), indent=1)
    print('extracted', list(out))


if __name__ == '__main__':
    extract() if '--extract' in sys.argv else build()
