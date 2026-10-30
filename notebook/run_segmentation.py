"""Real segmentation runs behind Demo C (IDEA.md §9).

1. TotalSegmentator labels for the LIDC-IDRI-0001 CT, grouped into a few structures and resampled
   onto the deck's 2.5 mm volume grid (data/imaging/ct/labels_u8.bin).
2. MedSAM on the nodule, prompted with a box, compared with each radiologist's outline (Dice).

Writes ../data/runs/segmentation.json.  Usage (from notebook/):  python run_segmentation.py
"""
import datetime as dt
import importlib.metadata as md
import json
import os
import subprocess
import sys
import time

import numpy as np
import SimpleITK as sitk
import torch

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import prepare_deck_assets as pda  # noqa: E402

WORK = os.path.join(HERE, 'data', 'work')
DEVICE = 'cuda' if torch.cuda.is_available() else 'cpu'

# Display groups: name -> TotalSegmentator label names (prefix match)
GROUPS = [
    ('Lungs', ['lung_']),
    ('Heart', ['heart']),
    ('Aorta', ['aorta']),
    ('Airway', ['trachea']),
    ('Spine', ['vertebrae_']),
    ('Ribs', ['rib_']),
    ('Liver', ['liver']),
]


def totalsegmentator(ct_dir):
    path = os.path.join(WORK, 'ts', 'total.nii.gz')
    seconds = None
    if not os.path.exists(path):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        t = time.time()
        subprocess.run(['TotalSegmentator', '-i', ct_dir, '-o', path, '--ml', '-d', 'gpu' if DEVICE == 'cuda' else 'cpu'], check=True)
        seconds = round(time.time() - t, 1)
    return sitk.ReadImage(path), seconds


def part_labels(ct):
    from totalsegmentator.map_to_binary import class_map
    names = class_map['total']
    lab, seconds = totalsegmentator(pda.series_dir('CT')[0])
    lab_on_ct = sitk.Resample(lab, ct, sitk.Transform(), sitk.sitkNearestNeighbor, 0)
    full = sitk.GetArrayFromImage(lab_on_ct)
    sp = ct.GetSpacing()
    voxel_ml = sp[0] * sp[1] * sp[2] / 1000
    grouped = np.zeros(full.shape, np.uint8)
    stats = []
    for gi, (gname, prefixes) in enumerate(GROUPS, start=1):
        ids = [i for i, n in names.items() if any(n.startswith(p) for p in prefixes)]
        m = np.isin(full, ids)
        grouped[m] = gi
        stats.append({'id': gi, 'name': gname, 'parts': len(ids), 'volume_ml': round(float(m.sum() * voxel_ml), 1)})
    # Same 2.5 mm grid as data/imaging/ct/volume_u8.bin
    iso = 2.5
    size = [int(round(ct.GetSize()[i] * sp[i] / iso)) for i in range(3)]
    g_img = sitk.GetImageFromArray(grouped)
    g_img.CopyInformation(ct)
    small = sitk.Resample(g_img, size, sitk.Transform(), sitk.sitkNearestNeighbor, ct.GetOrigin(), (iso,) * 3,
                          ct.GetDirection(), 0, sitk.sitkUInt8)
    sitk.GetArrayFromImage(small).astype(np.uint8).tofile(pda.out('ct', 'labels_u8.bin'))
    return {'tool': 'TotalSegmentator', 'version': md.version('TotalSegmentator'), 'task': 'total',
            'input': 'the CT DICOM folder, read directly', 'runtime_s_first_run': seconds,
            'labels_file': 'labels_u8.bin', 'shape_zyx': list(small.GetSize())[::-1], 'groups': stats}


def dice(a, b):
    s = a.sum() + b.sum()
    return float(2 * (a & b).sum() / s) if s else 1.0


@torch.no_grad()
def part_medsam(ct):
    from transformers import SamModel, SamProcessor
    hu = sitk.GetArrayFromImage(ct).astype(np.float32)
    masks = pda.read_reader_masks(ct)
    union = np.any([m['mask'] for m in masks], axis=0)
    k = int(np.argmax(union.sum(axis=(1, 2))))
    # Box prompt: the readers' combined outline on this slice, padded by 5 pixels
    ys, xs = np.nonzero(union[k])
    box = [int(xs.min()) - 5, int(ys.min()) - 5, int(xs.max()) + 5, int(ys.max()) + 5]
    # MedSAM expects a 3-channel image scaled to 0–255; use a soft-tissue window
    s = np.clip((hu[k] - (40 - 200)) / 400, 0, 1) * 255
    rgb = np.repeat(s[..., None], 3, axis=2).astype(np.uint8)
    proc = SamProcessor.from_pretrained('wanglab/medsam-vit-base')
    model = SamModel.from_pretrained('wanglab/medsam-vit-base').to(DEVICE).eval()
    t = time.time()
    inp = proc(rgb, input_boxes=[[box]], return_tensors='pt').to(DEVICE)
    outp = model(**inp, multimask_output=False)
    prob = proc.image_processor.post_process_masks(outp.pred_masks.sigmoid().cpu(), inp['original_sizes'].cpu(),
                                                   inp['reshaped_input_sizes'].cpu(), binarize=False)[0][0, 0].numpy()
    seconds = round(time.time() - t, 2)
    pred = prob > 0.5
    readers = [m['mask'][k] for m in masks]
    # Crop like data/imaging/ct/reader_crops.json so the deck can overlay it
    crops = json.load(open(pda.out('ct', 'reader_crops.json')))
    b = crops['box']
    crop = pred[b['y0']:b['y0'] + b['size'], b['x0']:b['x0'] + b['size']]
    return {
        'model': 'MedSAM (wanglab/medsam-vit-base, Hugging Face port)',
        'model_source': 'https://huggingface.co/wanglab/medsam-vit-base',
        'slice': k, 'box_xyxy': box, 'prompt': 'box around the radiologists\' combined outline, padded by 5 pixels',
        'window': 'soft tissue (level 40, width 400)', 'inference_s': seconds,
        'mask_crop': pda.pack_bits(crop),
        'dice_vs_readers': [round(dice(pred, r), 3) for r in readers],
        'dice_between_readers_on_slice': [[round(dice(a, c), 3) for c in readers] for a in readers],
        'area_mm2': {'medsam': round(float(pred.sum() * ct.GetSpacing()[0] ** 2), 1),
                     'readers': [round(float(r.sum() * ct.GetSpacing()[0] ** 2), 1) for r in readers]},
    }


def part_nodule_in_lungs(ct):
    """How much of the radiologists' nodule does TotalSegmentator's lung label include? The nodule is
    solid tissue inside the lung; a lung mask that leaves it out would hide it from lung-volume analyses."""
    from totalsegmentator.map_to_binary import class_map
    lab = sitk.GetArrayFromImage(sitk.Resample(sitk.ReadImage(os.path.join(WORK, 'ts', 'total.nii.gz')), ct,
                                               sitk.Transform(), sitk.sitkNearestNeighbor, 0))
    lung_ids = [i for i, n in class_map['total'].items() if n.startswith('lung_')]
    lungs = np.isin(lab, lung_ids)
    nod = np.any([m['mask'] for m in pda.read_reader_masks(ct)], axis=0)
    frac = float((nod & lungs).sum() / nod.sum())
    return {'nodule_voxels': int(nod.sum()), 'fraction_inside_lung_label': round(frac, 3)}


if __name__ == '__main__':
    ct, _ = pda.read_ct()
    run = {'provenance': {'run_date': dt.date.today().isoformat(), 'script': 'notebook/run_segmentation.py',
                          'device': torch.cuda.get_device_name(0) if DEVICE == 'cuda' else 'CPU',
                          'data': 'LIDC-IDRI-0001 chest CT, TCIA, CC BY 3.0',
                          'note': 'Research software. Masks are not validated for clinical use.'}}
    run['totalsegmentator'] = part_labels(ct)
    print(json.dumps(run['totalsegmentator']['groups']))
    run['medsam'] = part_medsam(ct)
    run['nodule_vs_lung_label'] = part_nodule_in_lungs(ct)
    print('nodule inside lung label:', run['nodule_vs_lung_label'])
    print('MedSAM Dice vs readers', run['medsam']['dice_vs_readers'], 'in', run['medsam']['inference_s'], 's')
    json.dump(run, open(os.path.join(pda.RUNS, 'segmentation.json'), 'w'), indent=1)
