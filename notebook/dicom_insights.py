"""DICOM analyses and insights from the sample pack (Workflow E of the notebook), run from a terminal.

Generated from the notebook cells by build_notebook.py: edit them there, not here.

Usage (from notebook/):  python dicom_insights.py [all|tissue|nodule|pet|audit] [--show]
Figures are saved in figures/ unless --show is given.
"""
# E0. Helpers shared by E1-E4 (also the top of dicom_insights.py)
import os
import numpy as np
import pydicom
import matplotlib.pyplot as plt

PACK = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'public', 'dicom')
FIG_DIR = None                       # set to a folder to save figures instead of showing them


def load(name):
    return pydicom.dcmread(os.path.join(PACK, name))


def values(ds):
    """Pixel values in the file's real units (rescale slope and intercept applied)."""
    return ds.pixel_array * float(ds.get('RescaleSlope', 1)) + float(ds.get('RescaleIntercept', 0))


def seg_on(seg, img):
    """A DICOM SEG mask placed on one image slice, using both files' positions and orientations."""
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
    """Longest distance (mm) between two pixels of a 2D mask."""
    ys, xs = np.nonzero(mask)
    pts = np.stack([xs * float(ds.PixelSpacing[1]), ys * float(ds.PixelSpacing[0])], 1)
    return float(np.sqrt(((pts[:, None] - pts[None]) ** 2).sum(-1)).max())


def suv_factor(pet):
    """Body-weight SUV per Bq/ml, decay-corrected to series start, from the PET file's tags."""
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
        plt.show()

def tissue():
    # E1. CT: what tissue is on this slice? Hounsfield units sort the pixels; pixel size gives cm²
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
    show(fig, 'E1_tissue')


def nodule():
    # E2. CT: measure the nodule each of four radiologists outlined (DICOM SEG files)
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
    show(fig, 'E2_nodule')


def pet():
    # E3. PET: how hot is the tumour? SUV from the file's own tags; tumour from the expert's DICOM SEG
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
    show(fig, 'E3_pet')


def audit():
    # E4. Audit the metadata of every image file in the pack
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
    print(f'Insight: {missing} of {len(files)} files record no pixel size, so nothing in them can be measured in mm')


ANALYSES = [('tissue', tissue), ('nodule', nodule), ('pet', pet), ('audit', audit)]

if __name__ == '__main__':
    import sys
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    if '--show' not in sys.argv:
        FIG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'figures')
    names = [n for n, _ in ANALYSES] if not args or args == ['all'] else args
    for n in names:
        print(f'\n=== {n} ===')
        dict(ANALYSES)[n]()
