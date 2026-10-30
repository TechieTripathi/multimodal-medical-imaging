"""Build the derived image assets the slide deck uses, from the downloaded public datasets.

The deck never ships original DICOM files (IDEA.md §11). This script writes small derived
arrays, PNGs and JSON into ../data/imaging/, and records what it did in ../data/runs/assets.json.

Usage (from notebook/):  python prepare_deck_assets.py [stage ...]
Stages: ct, dx, mri, gallery. With no stage, all run.
"""
import base64
import datetime as dt
import glob
import json
import os
import sys

import numpy as np
import pydicom
import SimpleITK as sitk
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
RAW = os.path.join(HERE, 'data', 'raw')
OUT = os.path.join(HERE, '..', 'data', 'imaging')
RUNS = os.path.join(HERE, '..', 'data', 'runs')
LIDC = os.path.join(RAW, 'lidc')

# Range used to store CT volumes as 8-bit: HU = LO + value * (HI - LO) / 255
VOL_HU_LO, VOL_HU_HI = -1000, 600


def out(*parts):
    path = os.path.join(OUT, *parts)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    return path


def series_dir(modality):
    return sorted(glob.glob(os.path.join(LIDC, f'{modality}-*')))


def read_ct():
    """CT series as a SimpleITK image in Hounsfield units, slices ordered by position."""
    reader = sitk.ImageSeriesReader()
    files = reader.GetGDCMSeriesFileNames(series_dir('CT')[0])
    reader.SetFileNames(files)
    return reader.Execute(), files


def read_reader_masks(ct):
    """Each radiologist's nodule segmentation (DICOM SEG) as a boolean array on the CT grid."""
    arr_shape = sitk.GetArrayFromImage(ct).shape  # z, y, x
    origin_z, dz = ct.GetOrigin()[2], ct.GetSpacing()[2]
    masks = []
    for d in series_dir('SEG'):
        ds = pydicom.dcmread(glob.glob(os.path.join(d, '*.dcm'))[0])
        frames = ds.pixel_array.astype(bool)
        if frames.ndim == 2:
            frames = frames[None]
        m = np.zeros(arr_shape, bool)
        for i, fr in enumerate(ds.PerFrameFunctionalGroupsSequence):
            z = float(fr.PlanePositionSequence[0].ImagePositionPatient[2])
            k = int(round((z - origin_z) / dz))
            m[k] |= frames[i]
        masks.append({'label': ds.SeriesDescription, 'reader': len(masks) + 1, 'mask': m})
    return masks


def pack_bits(m):
    return base64.b64encode(np.packbits(m.astype(np.uint8).ravel()).tobytes()).decode()


def dice(a, b):
    s = a.sum() + b.sum()
    return float(2 * (a & b).sum() / s) if s else 1.0


def stage_ct():
    ct, files = read_ct()
    hu = sitk.GetArrayFromImage(ct).astype(np.int16)  # z, y, x
    sp = ct.GetSpacing()
    masks = read_reader_masks(ct)
    union = np.any([m['mask'] for m in masks], axis=0)
    areas = union.sum(axis=(1, 2))
    k = int(np.argmax(areas))  # slice through the widest part of the nodule
    zz, yy, xx = np.nonzero(union)
    cy, cx = int(yy.mean()), int(xx.mean())

    # 1. One full-resolution slice in HU for the windowing artifact
    hu[k].astype('<i2').tofile(out('ct', 'slice_hu.bin'))

    # 2. Whole volume resampled to 2.5 mm cubes, stored 8-bit, for slicing in three planes
    iso = 2.5
    size = [int(round(ct.GetSize()[i] * sp[i] / iso)) for i in range(3)]
    res = sitk.Resample(ct, size, sitk.Transform(), sitk.sitkLinear, ct.GetOrigin(), (iso,) * 3,
                        ct.GetDirection(), -1024, sitk.sitkInt16)
    vol = sitk.GetArrayFromImage(res).astype(np.float32)
    v8 = np.clip((vol - VOL_HU_LO) * 255 / (VOL_HU_HI - VOL_HU_LO), 0, 255).astype(np.uint8)
    v8.tofile(out('ct', 'volume_u8.bin'))

    # 3. Reader masks around the nodule: a crop on the five central slices
    half = 40
    y0, x0 = cy - half, cx - half
    ks = [k + d for d in (-4, -2, 0, 2, 4) if 0 <= k + d < hu.shape[0]]
    crops = {
        'box': {'y0': y0, 'x0': x0, 'size': 2 * half},
        'slices': [{
            'k': kk,
            'z_mm': float(ct.GetOrigin()[2] + kk * sp[2]),
            'hu': base64.b64encode(hu[kk, y0:y0 + 2 * half, x0:x0 + 2 * half].astype('<i2').tobytes()).decode(),
            'readers': [pack_bits(m['mask'][kk, y0:y0 + 2 * half, x0:x0 + 2 * half]) for m in masks],
        } for kk in ks],
    }
    with open(out('ct', 'reader_crops.json'), 'w') as f:
        json.dump(crops, f)

    # Real inter-reader agreement in 3D
    pair = [[round(dice(a['mask'], b['mask']), 3) for b in masks] for a in masks]
    vols = [round(float(m['mask'].sum() * sp[0] * sp[1] * sp[2]), 1) for m in masks]

    # 4. A few display PNGs of the nodule slice (lung and mediastinal windows)
    def win(a, c, w):
        return (np.clip((a - (c - w / 2)) / w, 0, 1) * 255).astype(np.uint8)
    Image.fromarray(win(hu[k], -600, 1500)).save(out('ct', 'slice_lung.png'))
    Image.fromarray(win(hu[k], 40, 400)).save(out('ct', 'slice_soft.png'))

    meta = {
        'source': 'LIDC-IDRI-0001, TCIA, CC BY 3.0',
        'slices': len(files),
        'size_xyz': list(ct.GetSize()),
        'spacing_mm': [round(s, 4) for s in sp],
        'origin_mm': [round(o, 2) for o in ct.GetOrigin()],
        'nodule_slice': k,
        'nodule_center_yx': [cy, cx],
        'nodule_z_mm': float(ct.GetOrigin()[2] + k * sp[2]),
        'slice_hu': {'file': 'slice_hu.bin', 'dtype': 'int16', 'shape': [512, 512],
                     'min': int(hu[k].min()), 'max': int(hu[k].max())},
        'volume': {'file': 'volume_u8.bin', 'dtype': 'uint8', 'shape_zyx': list(v8.shape),
                   'spacing_mm': iso, 'hu_lo': VOL_HU_LO, 'hu_hi': VOL_HU_HI,
                   'nodule_zyx': [int(round(k * sp[2] / iso)), int(round(cy * sp[1] / iso)), int(round(cx * sp[0] / iso))]},
        'readers': {'count': len(masks), 'volume_mm3': vols, 'dice_3d': pair},
    }
    with open(out('ct', 'meta.json'), 'w') as f:
        json.dump(meta, f, indent=1)
    print('ct:', meta['size_xyz'], 'nodule slice', k, 'reader volumes', vols)
    print('pairwise Dice', pair)
    return meta


def stage_dx():
    files = sorted(glob.glob(os.path.join(series_dir('DX')[0], '*.dcm')))
    info = []
    for i, f in enumerate(files):
        ds = pydicom.dcmread(f)
        a = ds.pixel_array.astype(np.float32)
        lo, hi = np.percentile(a, [0.5, 99.5])
        disp = (np.clip((a - lo) / (hi - lo), 0, 1) * 255).astype(np.uint8)
        if ds.PhotometricInterpretation == 'MONOCHROME1':
            disp = 255 - disp
        # Mask burned-in letters beside the laterality marker (possibly a technologist's initials);
        # the "L" marker itself stays because it carries clinical meaning.
        y0, y1, x0, x1 = 50, 240, 1785, 1870
        disp[y0:y1, x0:x1] = np.median(disp[y0:y1, x0 - 30:x0])
        im = Image.fromarray(disp)
        im.resize((1024, 1024), Image.LANCZOS).save(out('dx', f'dx{i + 1}.png'))
        im.resize((224, 224), Image.BICUBIC).save(out('dx', f'dx{i + 1}_224.png'))
        info.append({'file': f'dx{i + 1}.png', 'rows': ds.Rows, 'cols': ds.Columns,
                     'bits_stored': int(ds.BitsStored), 'photometric': ds.PhotometricInterpretation,
                     'stored_min': int(a.min()), 'stored_max': int(a.max()),
                     'display_window': [float(lo), float(hi)],
                     'window_tags': [str(ds.get('WindowCenter')), str(ds.get('WindowWidth'))]})
        # Raw stored values of a small region, for the pixels-to-numbers artifact
        if i == 0:
            r0, c0 = 760, 560  # inside the patient's right lung
            region = ds.pixel_array[r0:r0 + 12, c0:c0 + 12].astype(int).tolist()
            info[-1]['region'] = {'row0': r0, 'col0': c0, 'values': region}
    with open(out('dx', 'meta.json'), 'w') as f:
        json.dump({'source': 'LIDC-IDRI-0001 chest radiograph, TCIA, CC BY 3.0', 'images': info}, f, indent=1)
    print('dx:', [(d['rows'], d['photometric'], d['stored_min'], d['stored_max']) for d in info])


def stage_sr():
    """The four radiologists' structured assessments of the nodule (DICOM SR), as plain text."""
    keep = ['Diameter', 'Volume', 'Subtlety score', 'Internal structure', 'Calcification', 'Sphericity',
            'Margin', 'Lobular Pattern', 'Spiculation', 'Texture', 'Malignancy', 'Finding Site', 'Finding']
    readers = []
    for d in series_dir('SR'):
        ds = pydicom.dcmread(glob.glob(os.path.join(d, '*.dcm'))[0])
        found = {}

        def walk(seq):
            for it in seq:
                name = it.ConceptNameCodeSequence[0].CodeMeaning if 'ConceptNameCodeSequence' in it else ''
                if name in keep and name not in found:
                    if 'ConceptCodeSequence' in it:
                        found[name] = it.ConceptCodeSequence[0].CodeMeaning
                    elif 'MeasuredValueSequence' in it:
                        mv = it.MeasuredValueSequence[0]
                        found[name] = f'{float(mv.NumericValue):.0f} {mv.MeasurementUnitsCodeSequence[0].CodeValue}'
                if 'ContentSequence' in it:
                    walk(it.ContentSequence)
        walk(ds.ContentSequence)
        readers.append({'series': ds.SeriesDescription, 'items': found})
    json.dump({'source': 'LIDC-IDRI-0001 DICOM SR (Fedorov et al. conversion), TCIA, CC BY 3.0',
               'note': 'Diameter and volume were computed by pylidc from each reader\'s outline; ratings are the reader\'s own.',
               'readers': readers}, open(out('ct', 'reports.json'), 'w'), indent=1)
    for r in readers:
        print('sr:', r['items'].get('Malignancy'), '|', r['items'].get('Spiculation'), '|', r['items'].get('Diameter'))


def stage_attn():
    """Anatomical masks on the nodule slice, for the cross-attention teaching picture.
    Lungs come from TotalSegmentator (run_segmentation.py must have run), the nodule from the readers."""
    ct, _ = read_ct()
    k = json.load(open(out('ct', 'meta.json')))['nodule_slice']
    lab = sitk.ReadImage(os.path.join(HERE, 'data', 'work', 'ts', 'total.nii.gz'))
    lab = sitk.GetArrayFromImage(sitk.Resample(lab, ct, sitk.Transform(), sitk.sitkNearestNeighbor, 0))[k]
    from totalsegmentator.map_to_binary import class_map
    ids = {n: i for i, n in class_map['total'].items()}
    left = np.isin(lab, [ids['lung_upper_lobe_left'], ids['lung_lower_lobe_left']])
    right = np.isin(lab, [ids['lung_upper_lobe_right'], ids['lung_middle_lobe_right'], ids['lung_lower_lobe_right']])
    lower_left = lab == ids['lung_lower_lobe_left']
    nod = np.any([m['mask'][k] for m in read_reader_masks(ct)], axis=0)
    edge = nod & ~np.asarray(sitk.GetArrayFromImage(sitk.BinaryErode(sitk.GetImageFromArray(nod.astype(np.uint8)), [3, 3])), bool)
    heart = lab == ids['heart']
    for name, m in [('left_lung', left), ('right_lung', right), ('left_lower_lobe', lower_left), ('nodule', nod),
                    ('nodule_edge', edge), ('heart', heart)]:
        alpha = Image.fromarray((m * 255).astype(np.uint8)).resize((256, 256), Image.BILINEAR)
        rgba = Image.new('RGBA', (256, 256), (255, 255, 255, 0))
        rgba.putalpha(alpha)
        rgba.save(out('attn', f'{name}.png'))  # white with the mask as transparency, for CSS mask-image
    print('attn: masks on slice', k, {n: int(m.sum()) for n, m in [('left', left), ('right', right), ('nodule', nod)]})


def stage_dicom():
    """The patient's DICOM hierarchy (patient → studies → series → instances) and real tag values for the
    DICOM slides. Long UIDs are shortened for display; the data are already de-identified by TCIA."""
    def short(uid):
        return f'{uid[:18]}…{uid[-6:]}' if uid and len(uid) > 28 else uid

    def tagrow(ds, kw):
        el = ds.data_element(kw) if kw in ds else None
        if el is None:
            return {'keyword': kw, 'tag': '', 'value': '(not present)'}
        v = el.value
        if isinstance(v, (bytes, bytearray)):
            v = f'{len(v):,} bytes'
        elif isinstance(v, pydicom.multival.MultiValue):
            v = ' \\ '.join(str(x) for x in v)
        v = str(v)
        if kw.endswith('UID'):
            v = short(v)
        return {'keyword': kw, 'tag': f'({el.tag.group:04X},{el.tag.element:04X})', 'value': v if v != '' else '(empty)'}

    studies = {}
    for d in sorted(glob.glob(os.path.join(LIDC, '*-*'))):
        if not os.path.isdir(d):
            continue
        files = sorted(glob.glob(os.path.join(d, '*.dcm')))
        ds = pydicom.dcmread(files[0], stop_before_pixels=True)
        st = studies.setdefault(ds.StudyInstanceUID, {'uid': short(ds.StudyInstanceUID), 'date': str(ds.get('StudyDate', '')),
                                                       'description': str(ds.get('StudyDescription', '')), 'series': []})
        st['series'].append({'modality': ds.Modality, 'description': str(ds.get('SeriesDescription', '') or ''),
                             'uid': short(ds.SeriesInstanceUID), 'instances': len(files),
                             'bytes': int(sum(os.path.getsize(f) for f in files))})
    order = {'DX': 0, 'CT': 1, 'SEG': 2, 'SR': 3}
    for st in studies.values():
        st['series'].sort(key=lambda s: (order.get(s['modality'], 9), s['description']))
        st['modality'] = ', '.join(sorted({s['modality'] for s in st['series']}, key=lambda m: order.get(m, 9)))

    ct_files = sorted(glob.glob(os.path.join(series_dir('CT')[0], '*.dcm')))
    full = pydicom.dcmread(ct_files[0])
    groups = {
        'Who (privacy-sensitive)': ['PatientName', 'PatientID', 'PatientBirthDate', 'PatientSex', 'PatientAge', 'AccessionNumber',
                                    'InstitutionName', 'ReferringPhysicianName', 'StudyDate', 'PatientIdentityRemoved', 'DeidentificationMethod'],
        'How it was acquired': ['Modality', 'Manufacturer', 'ManufacturerModelName', 'KVP', 'ConvolutionKernel', 'SliceThickness'],
        'Where in space': ['Rows', 'Columns', 'PixelSpacing', 'ImagePositionPatient', 'ImageOrientationPatient', 'InstanceNumber'],
        'How to read the pixels': ['BitsAllocated', 'BitsStored', 'PixelRepresentation', 'PhotometricInterpretation', 'RescaleSlope',
                                   'RescaleIntercept', 'WindowCenter', 'WindowWidth', 'PixelData'],
    }
    tags = {g: [tagrow(full, k) for k in ks] for g, ks in groups.items()}
    dx = pydicom.dcmread(glob.glob(os.path.join(series_dir('DX')[0], '*.dcm'))[0], stop_before_pixels=True)
    # File-name order versus spatial order, for the slice-ordering slide
    order_rows = []
    for f in ct_files:
        h = pydicom.dcmread(f, stop_before_pixels=True)
        order_rows.append({'file': os.path.basename(f), 'instance': int(h.InstanceNumber), 'z': float(h.ImagePositionPatient[2])})
    out_json = {
        'source': 'LIDC-IDRI-0001, TCIA, CC BY 3.0 (de-identified by TCIA)',
        'patient': {'id': str(full.PatientID), 'studies': list(studies.values())},
        'ct_tags': tags,
        'ct_file': {'elements': len(full), 'bytes': os.path.getsize(ct_files[0]), 'pixel_bytes': len(full.PixelData)},
        'dx_window_tags': [str(dx.get('WindowCenter')), str(dx.get('WindowWidth'))],
        'ct_file_order': order_rows,
    }
    json.dump(out_json, open(out('dicom', 'meta.json'), 'w'), indent=1)
    print('dicom:', [(s['modality'], len(s['series'])) for s in studies.values()], out_json['ct_file'])


def stage_pipeline():
    """Images for each preparation stage of our patient's X-ray, as BiomedCLIP receives it."""
    ds = pydicom.dcmread(glob.glob(os.path.join(series_dir('DX')[0], '*.dcm'))[0])
    a = ds.pixel_array.astype(np.float32)
    # Same masking of burned-in letters as stage_dx, applied to the stored values
    a[50:240, 1785:1870] = np.median(a[50:240, 1755:1785])
    # 1. Stored values shown with a plain min–max mapping (how a naive viewer might show them)
    raw = ((a - a.min()) / (a.max() - a.min()) * 255).astype(np.uint8)
    Image.fromarray(raw).resize((300, 300), Image.LANCZOS).save(out('pipeline', 'raw.png'))
    # 2. Windowed to 8 bits (percentiles), as in prepare_deck_assets.stage_dx
    lo, hi = np.percentile(a, [0.5, 99.5])
    win = (np.clip((a - lo) / (hi - lo), 0, 1) * 255).astype(np.uint8)
    Image.fromarray(win).resize((300, 300), Image.LANCZOS).save(out('pipeline', 'windowed.png'))
    # The X-ray displayed with its own window tags (centre -600, width 1600, which look copied from a CT):
    # nearly every stored value lies above the window, so the image turns white
    c, w = float(ds.WindowCenter), float(ds.WindowWidth)
    tagwin = (np.clip((a - (c - w / 2)) / w, 0, 1) * 255).astype(np.uint8)
    Image.fromarray(tagwin).resize((300, 300), Image.LANCZOS).save(out('pipeline', 'tag_window.png'))
    # 3. Resized to the model's 224 × 224 input
    small = Image.fromarray(win).resize((224, 224), Image.BICUBIC)
    small.save(out('pipeline', 'resized.png'))
    # 4. Normalised with BiomedCLIP's mean and std (shown rescaled for display)
    x = np.asarray(small, np.float32) / 255
    z = (x - 0.48145466) / 0.26862954
    json.dump({'stored_bits': int(ds.BitsStored), 'stored_range': [int(a.min()), int(a.max())], 'rows': ds.Rows,
               'cols': ds.Columns, 'window': [float(lo), float(hi)], 'model_input': 224,
               'normalised_range': [round(float(z.min()), 2), round(float(z.max()), 2)],
               'pixels_kept_pct': round(224 * 224 / (ds.Rows * ds.Columns) * 100, 1)},
              open(out('pipeline', 'meta.json'), 'w'), indent=1)
    print('pipeline: kept', round(224 * 224 / (ds.Rows * ds.Columns) * 100, 1), '% of pixels')


def stage_apps():
    """TotalSegmentator labels over the nodule slice at full resolution, and the HC18 measurement."""
    ct, _ = read_ct()
    k = json.load(open(out('ct', 'meta.json')))['nodule_slice']
    hu = sitk.GetArrayFromImage(ct)[k].astype(np.float32)
    lab = sitk.GetArrayFromImage(sitk.Resample(sitk.ReadImage(os.path.join(HERE, 'data', 'work', 'ts', 'total.nii.gz')), ct,
                                               sitk.Transform(), sitk.sitkNearestNeighbor, 0))[k]
    from totalsegmentator.map_to_binary import class_map
    names = class_map['total']
    colours = {'lung_': (90, 140, 255), 'heart': (230, 70, 70), 'aorta': (255, 160, 40), 'vertebrae_': (240, 240, 120),
               'rib_': (200, 200, 200), 'esophagus': (120, 220, 140), 'pulmonary': (180, 110, 220)}
    g = np.clip((hu + 1350) / 1500, 0, 1) * 255
    rgb = np.repeat(g[..., None], 3, axis=2)
    for i, n in names.items():
        c = next((v for p, v in colours.items() if n.startswith(p)), None)
        if c is not None:
            m = lab == i
            rgb[m] = rgb[m] * 0.5 + np.array(c) * 0.5
    Image.fromarray(rgb.astype(np.uint8)).save(out('apps', 'ct_labels.png'))
    import csv
    rows = {r['filename']: r for r in csv.DictReader(open(os.path.join(RAW, 'hc18', 'training_set_pixel_size_and_HC.csv')))}
    r = rows['010_HC.png']
    json.dump({'hc18_010': {'pixel_size_mm': float(r['pixel size(mm)']), 'head_circumference_mm': float(r['head circumference (mm)'])},
               'ct_label_colours': {k2: list(v) for k2, v in colours.items()}}, open(out('apps', 'meta.json'), 'w'), indent=1)
    print('apps: HC', r['head circumference (mm)'])


def square(im, size):
    """Centre-crop to a square and resize."""
    w, h = im.size
    s = min(w, h)
    return im.crop(((w - s) // 2, (h - s) // 2, (w - s) // 2 + s, (h - s) // 2 + s)).resize((size, size), Image.LANCZOS)


def stage_gallery():
    """One image per modality for the gallery, plus annotated ultrasound and retina images."""
    g = {}
    Image.open(out('dx', 'dx1.png')).convert('L').resize((360, 360), Image.LANCZOS).save(out('gallery', 'xray.png'))
    g['xray'] = {'file': 'xray.png', 'credit': 'LIDC-IDRI, TCIA · CC BY 3.0', 'dicom': 'usually DICOM'}
    Image.open(out('ct', 'slice_lung.png')).resize((360, 360), Image.LANCZOS).save(out('gallery', 'ct.png'))
    g['ct'] = {'file': 'ct.png', 'credit': 'LIDC-IDRI, TCIA · CC BY 3.0', 'dicom': 'usually DICOM'}
    mri = Image.open(out('mri', 'flair.png'))
    mri.resize((270, 360), Image.LANCZOS).save(out('gallery', 'mri.png'))
    g['mri'] = {'file': 'mri.png', 'credit': 'UPENN-GBM, TCIA · CC BY 4.0', 'dicom': 'usually DICOM'}

    hc = os.path.join(RAW, 'hc18', 'training_set')
    us = Image.open(os.path.join(hc, '010_HC.png')).convert('L')
    square(us, 360).save(out('gallery', 'ultrasound.png'))
    g['ultrasound'] = {'file': 'ultrasound.png', 'credit': 'HC18 (van den Heuvel et al.), Zenodo · CC BY 4.0',
                       'dicom': 'often DICOM, often exported as video or images'}
    # Ultrasound with the expert's head outline drawn in, for the applications slide
    ann = np.asarray(Image.open(os.path.join(hc, '010_HC_Annotation.png')).convert('L')) > 0
    rgb = np.repeat(np.asarray(us)[..., None], 3, axis=2).copy()
    rgb[ann] = [255, 196, 0]
    Image.fromarray(rgb).resize((480, int(480 * us.size[1] / us.size[0])), Image.LANCZOS).save(out('apps', 'us_annotated.png'))
    us.resize((480, int(480 * us.size[1] / us.size[0])), Image.LANCZOS).save(out('apps', 'us_plain.png'))

    crc = os.path.join(RAW, 'crc', 'CRC-VAL-HE-7K')
    tiles = [sorted(glob.glob(os.path.join(crc, c, '*.tif')))[3] for c in ['TUM', 'STR', 'LYM', 'NORM']]
    mosaic = Image.new('RGB', (448, 448))
    for i, t in enumerate(tiles):
        mosaic.paste(Image.open(t).convert('RGB').resize((224, 224)), ((i % 2) * 224, (i // 2) * 224))
    mosaic.resize((360, 360), Image.LANCZOS).save(out('gallery', 'pathology.png'))
    g['pathology'] = {'file': 'pathology.png', 'credit': 'CRC-VAL-HE-7K (Kather et al.), Zenodo · CC BY 4.0',
                      'dicom': 'rarely DICOM: whole-slide images use vendor formats'}
    for c in ['TUM', 'STR', 'LYM', 'NORM', 'ADI', 'MUC', 'MUS', 'DEB', 'BACK']:
        Image.open(sorted(glob.glob(os.path.join(crc, c, '*.tif')))[3]).convert('RGB').save(out('apps', f'crc_{c}.png'))

    fives = os.path.join(RAW, 'fives', 'FIVES', 'test')
    fundus = Image.open(os.path.join(fives, 'Original', '1_A.png')).convert('RGB')
    square(fundus, 360).save(out('gallery', 'retina.png'))
    g['retina'] = {'file': 'retina.png', 'credit': 'FIVES (Jin et al.), figshare · CC BY 4.0',
                   'dicom': 'often not DICOM: cameras export JPEG or PNG'}
    for name in ['1_A', '151_N']:
        f = Image.open(os.path.join(fives, 'Original', f'{name}.png')).convert('RGB')
        v = Image.open(os.path.join(fives, 'Ground truth', f'{name}.png')).convert('L')
        square(f, 420).save(out('apps', f'fundus_{name}.png'))
        square(v, 420).save(out('apps', f'vessels_{name}.png'))
    json.dump(g, open(out('gallery', 'meta.json'), 'w'), indent=1)

    # CT and MRI slices for the embedding map (kept out of the deck build)
    mdir = os.path.join(HERE, 'data', 'work', 'map')
    os.makedirs(mdir, exist_ok=True)
    ct, _ = read_ct()
    hu = sitk.GetArrayFromImage(ct)
    for i, k in enumerate(np.linspace(30, 120, 8).astype(int)):
        s = (np.clip((hu[k] + 1350) / 1500, 0, 1) * 255).astype(np.uint8)
        Image.fromarray(s).save(os.path.join(mdir, f'ct_{i}.png'))
    for i, fn in enumerate(['t1.png', 't1_contrast.png', 't2.png', 'flair.png']):
        Image.open(out('mri', fn)).save(os.path.join(mdir, f'mri_{i}.png'))
    print('gallery:', list(g))


def read_series(d):
    r = sitk.ImageSeriesReader()
    r.SetFileNames(r.GetGDCMSeriesFileNames(d))
    return sitk.Cast(r.Execute(), sitk.sitkFloat32)


def register_rigid(fixed, moving):
    """Rigid (rotation + shift) registration by mutual information, then resample onto `fixed`."""
    init = sitk.CenteredTransformInitializer(fixed, moving, sitk.Euler3DTransform(),
                                             sitk.CenteredTransformInitializerFilter.GEOMETRY)
    reg = sitk.ImageRegistrationMethod()
    reg.SetMetricAsMattesMutualInformation(32)
    reg.SetMetricSamplingStrategy(reg.RANDOM)
    reg.SetMetricSamplingPercentage(0.05, seed=1)
    reg.SetInterpolator(sitk.sitkLinear)
    reg.SetOptimizerAsRegularStepGradientDescent(2.0, 1e-4, 200)
    reg.SetOptimizerScalesFromPhysicalShift()
    reg.SetShrinkFactorsPerLevel([4, 2, 1])
    reg.SetSmoothingSigmasPerLevel([2, 1, 0])
    reg.SetInitialTransform(init, inPlace=False)
    t = reg.Execute(fixed, moving)
    return sitk.Resample(moving, fixed, t, sitk.sitkLinear, 0.0), reg.GetMetricValue()


def stage_mri():
    base = os.path.join(RAW, 'upenn')
    seqs = {'T1': 't1_axial', 'T1 + contrast': 't1_axial_stealthpost', 'T2': 'T2_SAG_SPACE', 'FLAIR': 't2_Flair_axial'}
    fixed = read_series(os.path.join(base, seqs['T1']))
    vols, metrics = {'T1': fixed}, {}
    for name in ['T1 + contrast', 'T2', 'FLAIR']:
        vols[name], metrics[name] = register_rigid(fixed, read_series(os.path.join(base, seqs[name])))
    arr = {k: sitk.GetArrayFromImage(v) for k, v in vols.items()}  # z, y, x
    # Slice through the right temporal lesion, chosen by eye from a grid of registered FLAIR
    # slices (automatic picks landed on enhancing vessels at the skull base).
    k = 70
    files = {}
    for name, a in arr.items():
        s = a[k]
        lo, hi = np.percentile(s[s > 0], [1, 99.5]) if (s > 0).any() else (s.min(), s.max())
        img = (np.clip((s - lo) / (hi - lo), 0, 1) * 255).astype(np.uint8)
        fn = name.lower().replace(' + ', '_').replace(' ', '_') + '.png'
        Image.fromarray(img).save(out('mri', fn))
        files[name] = fn
    meta = {'source': 'UPENN-GBM-00001, TCIA, CC BY 4.0', 'slice': k, 'grid': list(fixed.GetSize()),
            'spacing_mm': [round(s, 3) for s in fixed.GetSpacing()], 'files': files,
            'registration': 'rigid, Mattes mutual information, onto the T1 series', 'slice_choice': 'chosen by eye through the lesion',
            'registration_metric': {k2: round(v, 4) for k2, v in metrics.items()}}
    json.dump(meta, open(out('mri', 'meta.json'), 'w'), indent=1)
    print('mri: slice', k, metrics)


if __name__ == '__main__':
    stages = sys.argv[1:] or ['ct', 'dx']
    for s in stages:
        globals()[f'stage_{s}']()
    os.makedirs(RUNS, exist_ok=True)
    log = os.path.join(RUNS, 'assets.json')
    prev = json.load(open(log)) if os.path.exists(log) else {}
    for s in stages:
        prev[s] = {'built': dt.date.today().isoformat(), 'script': 'notebook/prepare_deck_assets.py'}
    json.dump(prev, open(log, 'w'), indent=1)
