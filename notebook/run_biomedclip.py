"""Real BiomedCLIP runs behind the deck's image–text artifacts.

Writes ../data/runs/biomedclip_*.json and small thumbnails into ../data/imaging/thumbs/.
Every score shown in the deck comes from these files (IDEA.md §9).

Usage (from notebook/):  python run_biomedclip.py [part ...]
Parts: ranking, contrastive, roc, zeroshot, probe, clipcompare, map. With no part, all run.
"""
import datetime as dt
import glob
import json
import os
import platform
import random
import re
import sys
import time
import xml.etree.ElementTree as ET

import numpy as np
import torch
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
RAW = os.path.join(HERE, 'data', 'raw')
WORK = os.path.join(HERE, 'data', 'work')
RUNS = os.path.join(HERE, '..', 'data', 'runs')
IMG = os.path.join(HERE, '..', 'data', 'imaging')
MODEL_ID = 'hf-hub:microsoft/BiomedCLIP-PubMedBERT_256-vit_base_patch16_224'
DEVICE = 'cuda' if torch.cuda.is_available() else 'cpu'
random.seed(0)

_model = None


def model():
    global _model
    if _model is None:
        import open_clip
        m, pre = open_clip.create_model_from_pretrained(MODEL_ID)
        tok = open_clip.get_tokenizer(MODEL_ID)
        m.to(DEVICE).eval()
        _model = (m, pre, tok)
    return _model


@torch.no_grad()
def embed_images(paths, batch=64):
    m, pre, _ = model()
    out = []
    for i in range(0, len(paths), batch):
        ims = torch.stack([pre(Image.open(p).convert('RGB')) for p in paths[i:i + batch]]).to(DEVICE)
        out.append(torch.nn.functional.normalize(m.encode_image(ims), dim=-1).float().cpu())
    return torch.cat(out).numpy()


@torch.no_grad()
def embed_texts(texts):
    m, _, tok = model()
    t = tok(texts, context_length=256).to(DEVICE)
    return torch.nn.functional.normalize(m.encode_text(t), dim=-1).float().cpu().numpy()


def provenance():
    m, _, _ = model()
    return {
        'model': 'BiomedCLIP-PubMedBERT_256-vit_base_patch16_224',
        'model_source': MODEL_ID.replace('hf-hub:', 'https://huggingface.co/'),
        'logit_scale': round(float(m.logit_scale.exp()), 3),
        'device': torch.cuda.get_device_name(0) if DEVICE == 'cuda' else platform.processor() or 'CPU',
        'torch': torch.__version__,
        'run_date': dt.date.today().isoformat(),
        'script': 'notebook/run_biomedclip.py',
        'note': 'Scores are cosine similarities between normalised embeddings. They are not probabilities and not diagnoses.',
    }


def save_run(name, payload):
    os.makedirs(RUNS, exist_ok=True)
    payload = {'provenance': provenance(), **payload}
    with open(os.path.join(RUNS, name), 'w') as f:
        json.dump(payload, f, indent=1)
    print('wrote', name)


def thumb(src, name, size=96):
    d = os.path.join(IMG, 'thumbs')
    os.makedirs(d, exist_ok=True)
    im = Image.open(src).convert('RGB')
    im.thumbnail((size, size), Image.LANCZOS)
    im.save(os.path.join(d, name))
    return f'thumbs/{name}'


def r4(a):
    return [round(float(x), 4) for x in a]


# ---------------------------------------------------------------- IU chest X-rays and reports

def iu_reports():
    """Parse IU report XML: findings, impression, MeSH major terms and the report's image files."""
    rows = []
    for f in glob.glob(os.path.join(RAW, 'iu', 'ecgen-radiology', '*.xml')):
        root = ET.parse(f).getroot()
        txt = {a.get('Label'): (a.text or '').strip() for a in root.iter('AbstractText')}
        mesh = [m.text for m in root.iter('major') if m.text]
        imgs = [p.get('id') for p in root.iter('parentImage')]
        rows.append({'report': os.path.basename(f), 'findings': txt.get('FINDINGS', ''),
                     'impression': txt.get('IMPRESSION', ''), 'mesh': mesh, 'images': imgs})
    return rows


def iu_png(img_id):
    return os.path.join(RAW, 'iu', 'png', f'{img_id}.png')


def symmetry(path):
    """Left–right mirror correlation. Frontal radiographs are roughly symmetric; laterals are not."""
    a = np.asarray(Image.open(path).convert('L').resize((128, 128)), np.float32)
    b = a[:, ::-1]
    a, b = a - a.mean(), b - b.mean()
    return float((a * b).sum() / (np.sqrt((a * a).sum() * (b * b).sum()) + 1e-6))


def frontal_image(rep, floor=0.55):
    """The report's most left–right symmetric image, if symmetric enough to be a frontal view.
    Spot check on 24 reports: 22 frontal, 2 lateral slipped through before the 0.55 floor was added."""
    cands = [(symmetry(iu_png(i)), i) for i in rep['images'] if os.path.exists(iu_png(i))]
    if not cands:
        return None
    s, i = max(cands)
    return i if s > floor else None


def label_of(rep):
    mesh = [m.lower() for m in rep['mesh']]
    if mesh == ['normal']:
        return 'normal'
    if len(mesh) == 1 and mesh[0].startswith('cardiomegaly'):
        return 'cardiomegaly'
    if len(mesh) == 1 and mesh[0].startswith('pleural effusion'):
        return 'pleural effusion'
    if len(mesh) == 1 and mesh[0].startswith('pneumothorax'):
        return 'pneumothorax'
    return None


# ---------------------------------------------------------------- parts

CANDIDATES = [
    'a normal chest X-ray',
    'a chest X-ray showing an enlarged heart (cardiomegaly)',
    'a chest X-ray showing fluid around the lung (pleural effusion)',
    'a chest X-ray showing a collapsed lung (pneumothorax)',
    'a chest X-ray showing a mass in the lung',
    'an axial CT scan of the chest',
    'an MRI scan of the brain',
    'a microscope image of stained tissue',
]


# Four IU examples, fixed by ID so the slides stay stable (one per finding; not chosen for the model's
# answer). part_ranking also reports how often the top choice matches the report across all eligible X-rays.
FIXED_EXAMPLES = ['CXR100_IM-0002-1001', 'CXR2416_IM-0961-1001', 'CXR2747_IM-1198-1001', 'CXR1339_IM-0218-2001']
EXPECTED = {'normal': 'a normal chest X-ray',
            'cardiomegaly': 'a chest X-ray showing an enlarged heart (cardiomegaly)',
            'pleural effusion': 'a chest X-ray showing fluid around the lung (pleural effusion)',
            'pneumothorax': 'a chest X-ray showing a collapsed lung (pneumothorax)'}


def part_ranking():
    """Demo B: rank candidate descriptions for our patient's X-ray and four IU examples, plus the
    top-1 agreement with the report over every frontal IU X-ray with exactly one of four findings."""
    reps = iu_reports()
    by_img = {i: r for r in reps for i in r['images']}
    images = [{'id': 'lidc-dx', 'path': os.path.join(IMG, 'dx', 'dx1.png'), 'source': 'LIDC-IDRI-0001, TCIA, CC BY 3.0',
               'truth': 'Our patient: a 3 cm nodule in the left lower lobe, rated "obvious" by radiologists on CT'}]
    for fi in FIXED_EXAMPLES:
        rep = by_img[fi]
        images.append({'id': fi, 'path': iu_png(fi), 'source': 'Indiana University chest X-ray collection (Open-i)',
                       'truth': f'Report impression: {rep["impression"]}', 'mesh': rep['mesh']})
    ie = embed_images([i['path'] for i in images])
    te = embed_texts(CANDIDATES)
    sims = ie @ te.T
    out = []
    for k, im in enumerate(images):
        rank = np.argsort(-sims[k])
        out.append({'id': im['id'], 'thumb': thumb(im['path'], f'rank_{k}.png', 360), 'source': im['source'],
                    'truth': im['truth'], 'mesh': im.get('mesh'), 'embedding': r4(ie[k]),
                    'scores': r4(sims[k]), 'ranking': [CANDIDATES[j] for j in rank]})
    # Aggregate: every frontal IU X-ray whose report has exactly one of the four findings
    rows = [(frontal_image(r), label_of(r)) for r in reps if label_of(r)]
    rows = [(f, l) for f, l in rows if f]
    agg_e = embed_images([iu_png(f) for f, _ in rows])
    top = [CANDIDATES[j] for j in np.argmax(agg_e @ te.T, 1)]
    agg = {}
    for lab in EXPECTED:
        idx = [i for i, (_, l) in enumerate(rows) if l == lab]
        agg[lab] = {'n': len(idx), 'top1_matches_report': sum(top[i] == EXPECTED[lab] for i in idx)}
    save_run('biomedclip_ranking.json', {'candidates': CANDIDATES, 'text_embeddings': [r4(t) for t in te], 'images': out,
             'examples_rule': 'IU examples fixed by ID, one per finding, before looking at the model output on the full set',
             'aggregate': agg})
    for o in out:
        print(o['id'], '→', o['ranking'][0], '|', o['truth'][:70])
    print('aggregate', agg)


def finding_sentence(rep, keys):
    """The first sentence of the report that mentions one of `keys` (and has no de-identification marks)."""
    text = f"{rep['findings']} {rep['impression']}"
    for sent in re.split(r'(?<=\.)\s+', text):
        if 'XXXX' not in sent and 15 < len(sent) < 90 and any(k in sent.lower() for k in keys):
            return sent.strip()
    return None


def part_contrastive():
    """Six X-rays with six different findings, each paired with the report sentence that describes it,
    and their real 6×6 similarity matrix."""
    reps = sorted(iu_reports(), key=lambda r: r['report'])
    want = [('normal', ['normal chest', 'no acute']), ('Cardiomegaly', ['enlarged', 'cardiomegaly']),
            ('Calcified Granuloma', ['granuloma']), ('Scoliosis', ['scoliosis']),
            ('Surgical Instruments', ['sternotomy', 'wires', 'clips']), ('Opacity', ['opacity', 'opacities'])]
    chosen = []
    for term, keys in want:
        for rep in reps:
            if len(rep['mesh']) == 1 and rep['mesh'][0].split('/')[0] == term:
                sent = finding_sentence(rep, keys)
                fi = frontal_image(rep, floor=0.75) if sent else None
                if fi:
                    chosen.append(({**rep, 'impression': sent}, fi, term.lower()))
                    break
    ie = embed_images([iu_png(fi) for _, fi, _ in chosen])
    te = embed_texts([rep['impression'] for rep, _, _ in chosen])
    sims = ie @ te.T
    save_run('biomedclip_contrastive.json', {
        'pairs': [{'image': thumb(iu_png(fi), f'pair_{k}.png', 160), 'text': rep['impression'], 'label': lab,
                   'source': 'Indiana University chest X-ray collection (Open-i)'} for k, (rep, fi, lab) in enumerate(chosen)],
        'similarity': [r4(row) for row in sims],
        'diagonal_is_max_in_row': [bool(np.argmax(sims[i]) == i) for i in range(len(chosen))],
    })
    print(np.round(sims, 3))


def part_roc():
    """Zero-shot cardiomegaly vs normal on IU frontal radiographs: real scores and labels for the ROC."""
    reps = iu_reports()
    pos = [r for r in reps if any(m.lower().startswith('cardiomegaly') for m in r['mesh'])]
    neg = [r for r in reps if label_of(r) == 'normal']
    random.shuffle(neg)
    rows = []
    for r in pos + neg[:400]:
        fi = frontal_image(r)
        if fi:
            rows.append((fi, 0 if label_of(r) == 'normal' else 1))
    ie = embed_images([iu_png(f) for f, _ in rows])
    tp, tn = embed_texts(['a chest X-ray showing an enlarged heart (cardiomegaly)', 'a normal chest X-ray'])
    score = ie @ tp - ie @ tn
    y = np.array([l for _, l in rows])
    from sklearn.metrics import roc_auc_score
    auc = roc_auc_score(y, score)
    save_run('biomedclip_cxr_roc.json', {
        'task': 'Cardiomegaly versus normal, zero-shot, frontal chest radiographs',
        'labels_from': 'MeSH major terms in each IU report: positive = any term starting "Cardiomegaly" (other findings may also be present); negative = exactly "normal"',
        'view': 'frontal view chosen automatically by left–right symmetry',
        'images_available': 'partial download of the IU PNG collection' if len(glob.glob(os.path.join(RAW, 'iu', 'png', '*.png'))) < 7000 else 'full IU PNG collection',
        'score': 'cosine(image, "…enlarged heart (cardiomegaly)") minus cosine(image, "a normal chest X-ray")',
        'n_positive': int(y.sum()), 'n_negative': int((1 - y).sum()), 'auroc': round(float(auc), 3),
        'scores': r4(score), 'labels': y.tolist(),
    })
    print('ROC: n', len(y), 'pos', int(y.sum()), 'AUROC', round(auc, 3))


CRC = {'ADI': 'adipose tissue', 'BACK': 'background', 'DEB': 'debris', 'LYM': 'lymphocytes', 'MUC': 'mucus',
       'MUS': 'smooth muscle', 'NORM': 'normal colon mucosa', 'STR': 'cancer-associated stroma',
       'TUM': 'colorectal adenocarcinoma epithelium'}
PROMPT_VARIANTS = {
    'abbreviation': lambda code, name: code,
    'plain name': lambda code, name: name,
    'photo template': lambda code, name: f'this is a photo of {name}',
    'histology template': lambda code, name: f'an H&E stained histopathology image of {name}',
}


def part_zeroshot():
    """Zero-shot tissue classification on CRC-VAL-HE-7K: accuracy under four prompt wordings."""
    base = os.path.join(RAW, 'crc', 'CRC-VAL-HE-7K')
    paths, labels = [], []
    for k, code in enumerate(CRC):
        fs = sorted(glob.glob(os.path.join(base, code, '*.tif')))
        random.shuffle(fs)
        paths += fs[:100]
        labels += [k] * len(fs[:100])
    labels = np.array(labels)
    ie = embed_images(paths)
    variants = {}
    for vname, fn in PROMPT_VARIANTS.items():
        prompts = [fn(c, n) for c, n in CRC.items()]
        pred = np.argmax(ie @ embed_texts(prompts).T, axis=1)
        cm = np.zeros((9, 9), int)
        for t, p in zip(labels, pred):
            cm[t, p] += 1
        variants[vname] = {'prompts': prompts, 'accuracy': round(float((pred == labels).mean()), 3),
                           'per_class_accuracy': r4(cm.diagonal() / cm.sum(1)), 'confusion': cm.tolist()}
        print(f'{vname:20s} accuracy {variants[vname]["accuracy"]}')
    # One example tile per class, with its scores under each wording
    examples = []
    for k, code in enumerate(CRC):
        i = int(np.where(labels == k)[0][0])
        examples.append({'class': CRC[code], 'thumb': thumb(paths[i], f'crc_{code}.png', 160),
                         'scores': {v: r4(ie[i] @ embed_texts([PROMPT_VARIANTS[v](c, n) for c, n in CRC.items()]).T)
                                    for v in PROMPT_VARIANTS}})
    save_run('biomedclip_zeroshot_crc.json', {
        'dataset': 'CRC-VAL-HE-7K (Kather et al.), 100 random tiles per class, 9 classes',
        'chance_accuracy': round(1 / 9, 3), 'classes': list(CRC.values()), 'variants': variants, 'examples': examples})


def part_map():
    """Image embeddings from six modalities, projected to 2D with PCA (the 'fingerprint' map)."""
    groups = {
        'Chest X-ray': [iu_png(f) for f in [frontal_image(r) for r in sorted(iu_reports(), key=lambda r: r['report'])[:600:40]] if f][:8],
        'Chest CT': sorted(glob.glob(os.path.join(WORK, 'map', 'ct_*.png'))),
        'Brain MRI': sorted(glob.glob(os.path.join(WORK, 'map', 'mri_*.png'))),
        'Pathology': [sorted(glob.glob(os.path.join(RAW, 'crc', 'CRC-VAL-HE-7K', c, '*.tif')))[7] for c in ['ADI', 'LYM', 'MUC', 'MUS', 'NORM', 'STR', 'TUM', 'DEB']],
        'Retina': sorted(glob.glob(os.path.join(RAW, 'fives', 'FIVES', 'test', 'Original', '*.png')))[:200:25],
        'Ultrasound': sorted(glob.glob(os.path.join(RAW, 'hc18', 'training_set', '*_HC.png')))[:400:50],
    }
    paths, group = [], []
    for g, ps in groups.items():
        paths += ps
        group += [g] * len(ps)
    ie = embed_images(paths)
    from sklearn.decomposition import PCA
    pca = PCA(2, random_state=0).fit(ie)
    xy = pca.transform(ie)
    captions = {g: f'a {g.lower()} image' for g in groups}
    te = embed_texts(list(captions.values()))
    txy = pca.transform(te)
    pts = [{'group': g, 'x': round(float(x), 4), 'y': round(float(y), 4), 'thumb': thumb(p, f'map_{i}.png', 96)}
           for i, (g, p, (x, y)) in enumerate(zip(group, paths, xy))]
    save_run('biomedclip_embedding_map.json', {
        'projection': 'PCA of the 512-number image embeddings to 2 numbers',
        'explained_variance': r4(pca.explained_variance_ratio_),
        'points': pts,
        'text_points': [{'text': t, 'x': round(float(x), 4), 'y': round(float(y), 4)} for t, (x, y) in zip(captions.values(), txy)],
    })


def part_probe():
    """Few labelled examples: a small classifier (logistic regression) on top of frozen BiomedCLIP image
    embeddings, trained with k tiles per class, tested on the same 900 tiles as the zero-shot run."""
    from sklearn.linear_model import LogisticRegression
    base = os.path.join(RAW, 'crc', 'CRC-VAL-HE-7K')
    rng = random.Random(0)
    test_p, test_y, pool = [], [], {}
    for k, code in enumerate(CRC):
        fs = sorted(glob.glob(os.path.join(base, code, '*.tif')))
        random.Random(0).shuffle(fs)
        test_p += fs[:100]
        test_y += [k] * len(fs[:100])
        pool[k] = fs[100:300]
    test_e = embed_images(test_p)
    pool_e = {k: embed_images(v) for k, v in pool.items()}
    test_y = np.array(test_y)
    curve = []
    for shots in [1, 2, 5, 10, 25, 50]:
        accs = []
        for rep in range(5):
            X, y = [], []
            for k in pool_e:
                idx = rng.sample(range(len(pool_e[k])), shots)
                X.append(pool_e[k][idx])
                y += [k] * shots
            clf = LogisticRegression(max_iter=2000, C=10).fit(np.concatenate(X), y)
            accs.append(float((clf.predict(test_e) == test_y).mean()))
        curve.append({'per_class': shots, 'total_labelled': shots * 9, 'accuracy_mean': round(float(np.mean(accs)), 3),
                      'accuracy_min': round(min(accs), 3), 'accuracy_max': round(max(accs), 3)})
        print(shots, curve[-1]['accuracy_mean'])
    zs = json.load(open(os.path.join(RUNS, 'biomedclip_zeroshot_crc.json')))
    best = max(zs['variants'].items(), key=lambda kv: kv[1]['accuracy'])
    save_run('biomedclip_fewshot_crc.json', {
        'dataset': 'CRC-VAL-HE-7K: test = the same 900 tiles as the zero-shot run; training tiles drawn from the rest',
        'method': 'Logistic regression on frozen BiomedCLIP image embeddings; 5 random draws per point',
        'curve': curve, 'zero_shot_best': {'wording': best[0], 'accuracy': best[1]['accuracy']}, 'chance_accuracy': round(1 / 9, 3)})


@torch.no_grad()
def part_clipcompare():
    """The same 900 pathology tiles and four prompt wordings, run through general-purpose CLIP (OpenAI
    ViT-L/14, trained on internet photos) for comparison with BiomedCLIP."""
    from transformers import CLIPModel, CLIPProcessor
    name = 'openai/clip-vit-large-patch14'
    m = CLIPModel.from_pretrained(name).to(DEVICE).eval()
    proc = CLIPProcessor.from_pretrained(name)
    base = os.path.join(RAW, 'crc', 'CRC-VAL-HE-7K')
    paths, labels = [], []
    rnd = random.Random(0)
    for k, code in enumerate(CRC):
        fs = sorted(glob.glob(os.path.join(base, code, '*.tif')))
        random.Random(0).shuffle(fs)
        paths += fs[:100]
        labels += [k] * len(fs[:100])
    feats = []
    for i in range(0, len(paths), 64):
        ims = [Image.open(p).convert('RGB') for p in paths[i:i + 64]]
        x = proc(images=ims, return_tensors='pt').to(DEVICE)
        v = m.visual_projection(m.vision_model(pixel_values=x['pixel_values']).pooler_output)
        feats.append(torch.nn.functional.normalize(v, dim=-1).float().cpu())
    ie = torch.cat(feats).numpy()
    labels = np.array(labels)
    out = {}
    for vname, fn in PROMPT_VARIANTS.items():
        t = proc(text=[fn(c, n) for c, n in CRC.items()], return_tensors='pt', padding=True).to(DEVICE)
        tv = m.text_projection(m.text_model(input_ids=t['input_ids'], attention_mask=t['attention_mask']).pooler_output)
        te = torch.nn.functional.normalize(tv, dim=-1).float().cpu().numpy()
        out[vname] = round(float((np.argmax(ie @ te.T, 1) == labels).mean()), 3)
        print(f'CLIP {vname:20s} {out[vname]}')
    zs = json.load(open(os.path.join(RUNS, 'biomedclip_zeroshot_crc.json')))
    json.dump({'provenance': {**provenance(), 'model': f'CLIP ViT-L/14 ({name}) vs BiomedCLIP'},
               'dataset': zs['dataset'], 'clip_accuracy': out,
               'biomedclip_accuracy': {k: v['accuracy'] for k, v in zs['variants'].items()},
               'chance_accuracy': zs['chance_accuracy']},
              open(os.path.join(RUNS, 'clip_vs_biomedclip_crc.json'), 'w'), indent=1)


FIVES = {'A': 'age-related macular degeneration', 'D': 'diabetic retinopathy', 'G': 'glaucoma', 'N': 'a normal retina'}


def part_fives():
    """Zero-shot diagnosis on the 200 FIVES test fundus photographs (50 per class)."""
    fs = sorted(glob.glob(os.path.join(RAW, 'fives', 'FIVES', 'test', 'Original', '*.png')))
    codes = list(FIVES)
    y = np.array([codes.index(os.path.basename(f).split('_')[1][0]) for f in fs])
    ie = embed_images(fs)
    te = embed_texts([f'a retinal fundus photograph showing {v}' for v in FIVES.values()])
    pred = np.argmax(ie @ te.T, 1)
    cm = np.zeros((4, 4), int)
    for t, p in zip(y, pred):
        cm[t, p] += 1
    save_run('biomedclip_fives.json', {'dataset': 'FIVES test set, 200 fundus photographs, 50 per class',
             'prompts': [f'a retinal fundus photograph showing {v}' for v in FIVES.values()], 'classes': list(FIVES.values()),
             'accuracy': round(float((pred == y).mean()), 3), 'chance_accuracy': 0.25, 'confusion': cm.tolist()})
    print('FIVES zero-shot accuracy', round(float((pred == y).mean()), 3), cm.tolist())


def roc_rows():
    """The same frontal images and labels as part_roc (same seed and order)."""
    random.seed(0)
    reps = iu_reports()
    pos = [r for r in reps if any(m.lower().startswith('cardiomegaly') for m in r['mesh'])]
    neg = [r for r in reps if label_of(r) == 'normal']
    random.shuffle(neg)
    rows = []
    for r in pos + neg[:400]:
        fi = frontal_image(r)
        if fi:
            rows.append((fi, 0 if label_of(r) == 'normal' else 1, r))
    return rows


def part_retrieval():
    """Search by sentence: rank the ROC images against one query and look at the top five."""
    rows = roc_rows()
    ie = embed_images([iu_png(f) for f, _, _ in rows])
    q = 'a chest X-ray showing an enlarged heart (cardiomegaly)'
    s = ie @ embed_texts([q])[0]
    top = np.argsort(-s)[:5]
    out = [{'thumb': thumb(iu_png(rows[i][0]), f'ret_{k}.png', 200), 'score': round(float(s[i]), 4),
            'label': 'cardiomegaly in report' if rows[i][1] else 'normal report',
            'mesh': rows[i][2]['mesh'], 'impression': rows[i][2]['impression']} for k, i in enumerate(top)]
    save_run('biomedclip_retrieval.json', {'query': q, 'searched': len(rows), 'top5': out,
             'precision_at_5': sum(1 for o in out if o['label'].startswith('cardio')) / 5,
             'source': 'Indiana University chest X-ray collection (Open-i)'})
    print('retrieval P@5', sum(1 for o in out if o['label'].startswith('cardio')) / 5)


def part_shift():
    """Simulated scanner differences: change the same X-rays slightly and measure the zero-shot AUROC."""
    from PIL import ImageEnhance, ImageFilter
    from sklearn.metrics import roc_auc_score
    rows = roc_rows()
    y = np.array([l for _, l, _ in rows])
    tp, tn = embed_texts(['a chest X-ray showing an enlarged heart (cardiomegaly)', 'a normal chest X-ray'])
    shifts = {
        'original': lambda im: im,
        'darker (gamma 1.6)': lambda im: im.point(lambda v: int(255 * (v / 255) ** 1.6)),
        'lower contrast (×0.6)': lambda im: ImageEnhance.Contrast(im).enhance(0.6),
        'blurred (radius 3)': lambda im: im.filter(ImageFilter.GaussianBlur(3)),
        'low resolution (64 px)': lambda im: im.resize((64, 64), Image.BILINEAR).resize(im.size, Image.BILINEAR),
    }
    m, pre, _ = model()
    res = {}
    examples = {}
    # Example image for the slide: the most clearly frontal (most symmetric) of the first 40
    src = Image.open(iu_png(max(rows[:40], key=lambda r: symmetry(iu_png(r[0])))[0])).convert('RGB')
    for name, fn in shifts.items():
        feats = []
        with torch.no_grad():
            for i in range(0, len(rows), 64):
                ims = torch.stack([pre(fn(Image.open(iu_png(f)).convert('RGB'))) for f, _, _ in rows[i:i + 64]]).to(DEVICE)
                feats.append(torch.nn.functional.normalize(m.encode_image(ims), dim=-1).float().cpu())
        ie = torch.cat(feats).numpy()
        sc = ie @ tp - ie @ tn
        res[name] = round(float(roc_auc_score(y, sc)), 3)
        d = os.path.join(IMG, 'thumbs')
        fn(src).resize((160, 160)).save(os.path.join(d, f'shift_{len(examples)}.png'))
        examples[name] = f'thumbs/shift_{len(examples)}.png'
        print(f'{name:24s} AUROC {res[name]}')
    save_run('biomedclip_shift.json', {'task': 'Cardiomegaly vs normal, zero-shot, same images as biomedclip_cxr_roc.json',
             'auroc': res, 'examples': examples,
             'note': 'Changes applied in software to imitate differences between scanners or settings; not real other-hospital data.'})


if __name__ == '__main__':
    parts = sys.argv[1:] or ['ranking', 'contrastive', 'roc', 'zeroshot', 'probe', 'clipcompare', 'map']
    for p in parts:
        t = time.time()
        globals()[f'part_{p}']()
        print(f'{p}: {time.time() - t:.1f}s')
