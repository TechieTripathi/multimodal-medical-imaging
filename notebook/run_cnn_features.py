"""Real feature maps from a pretrained convolutional network, for the 'what a neural network does' slide.

ResNet-50 (trained on everyday photographs, ImageNet) is run on the patient's CT slice. We save a few
channels from an early, a middle and a late layer: early layers respond to edges, later ones to larger
blobs and shapes. Writes ../data/imaging/cnn/*.png and ../data/runs/cnn_features.json.

Usage (from notebook/):  python run_cnn_features.py
"""
import datetime as dt
import json
import os

import numpy as np
import timm
import torch
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, '..', 'data', 'imaging', 'cnn')
RUNS = os.path.join(HERE, '..', 'data', 'runs')
MODEL = 'resnet50.a1_in1k'


@torch.no_grad()
def main():
    os.makedirs(OUT, exist_ok=True)
    m = timm.create_model(MODEL, pretrained=True, features_only=True, out_indices=(1, 2, 4)).eval()
    cfg = m.pretrained_cfg
    src = Image.open(os.path.join(HERE, '..', 'data', 'imaging', 'ct', 'slice_lung.png')).convert('RGB').resize((448, 448))
    x = torch.tensor(np.asarray(src, np.float32) / 255).permute(2, 0, 1)
    x = (x - torch.tensor(cfg['mean'])[:, None, None]) / torch.tensor(cfg['std'])[:, None, None]
    feats = m(x[None])
    layers = []
    for name, f in zip(['early', 'middle', 'late'], feats):
        f = f[0]
        # Channels that respond to part of the image (not everything, not nothing), strongest first
        hi = torch.quantile(f.flatten(1), 0.99, dim=1).clamp_min(1e-6)
        norm = (f.flatten(1) / hi[:, None]).clamp(0, 1)
        active = (norm > 0.3).float().mean(1)
        ok = (active > 0.08) & (active < 0.35)
        score = torch.where(ok, norm.std(1), torch.zeros_like(active))
        idx = torch.argsort(score, descending=True)[:3].tolist()
        files = []
        for j, c in enumerate(idx):
            a = f[c].numpy()
            lo, top = np.percentile(a, [2, 99.5])
            a = np.clip((a - lo) / (top - lo + 1e-6), 0, 1)
            fn = f'{name}_{j}.png'
            Image.fromarray((a * 255).astype(np.uint8)).resize((160, 160), Image.NEAREST).save(os.path.join(OUT, fn))
            files.append(fn)
        layers.append({'layer': name, 'grid': list(f.shape[1:]), 'channels': int(f.shape[0]), 'files': files})
        print(name, tuple(f.shape))
    json.dump({'provenance': {'model': f'ResNet-50 ({MODEL}, timm), trained on ImageNet photographs',
                              'run_date': dt.date.today().isoformat(), 'script': 'notebook/run_cnn_features.py',
                              'input': 'LIDC-IDRI-0001 CT slice, lung window, 448×448',
                              'note': 'Real activations of a general-purpose image model; not a medical model.'},
               'layers': layers}, open(os.path.join(RUNS, 'cnn_features.json'), 'w'), indent=1)


if __name__ == '__main__':
    main()
