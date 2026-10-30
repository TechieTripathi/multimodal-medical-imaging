"""Download the public datasets used by the notebook and the slides into data/raw/.

Usage (from notebook/):
  python download_data.py            # workflows A–C: LIDC-IDRI-0001 (≈ 90 MB) and UPENN-GBM-00001 MRI (≈ 80 MB)
  python download_data.py --all      # also the extra datasets the slides use (≈ 4 GB, see README)

All data are public and de-identified by their publishers; check each licence before reuse.
"""
import json
import os
import sys
import tarfile
import zipfile

import requests

HERE = os.path.dirname(os.path.abspath(__file__))
RAW = os.path.join(HERE, 'data', 'raw')
NBIA = 'https://services.cancerimagingarchive.net/nbia-api/services/v1'


def get(url, dest):
    if os.path.exists(dest):
        print('have', os.path.relpath(dest, HERE))
        return dest
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    print('downloading', url)
    with requests.get(url, stream=True, timeout=120) as r:
        r.raise_for_status()
        with open(dest + '.part', 'wb') as f:
            for chunk in r.iter_content(1 << 20):
                f.write(chunk)
    os.replace(dest + '.part', dest)
    return dest


def tcia_series(collection, patient, keep=lambda s: True, name=lambda s: f"{s['Modality']}-{s['SeriesInstanceUID']}", folder=''):
    """Every series of one TCIA patient that `keep` accepts, unzipped into data/raw/<folder>/<name>/."""
    series = requests.get(f'{NBIA}/getSeries', params={'Collection': collection, 'PatientID': patient}, timeout=60).json()
    for s in series:
        if not keep(s):
            continue
        d = os.path.join(RAW, folder, name(s))
        if os.path.isdir(d) and os.listdir(d):
            print('have', os.path.relpath(d, HERE))
            continue
        z = get(f"{NBIA}/getImage?SeriesInstanceUID={s['SeriesInstanceUID']}", d + '.zip')
        zipfile.ZipFile(z).extractall(d)
        os.remove(z)
        print('  ', len(os.listdir(d)), 'files in', os.path.relpath(d, HERE))


def core():
    # LIDC-IDRI-0001: chest CT, chest X-ray, four readers' outlines (SEG) and ratings (SR). CC BY 3.0.
    tcia_series('LIDC-IDRI', 'LIDC-IDRI-0001', folder='lidc')
    # UPENN-GBM-00001: the four processed MRI sequences. CC BY 4.0.
    tcia_series('UPENN-GBM', 'UPENN-GBM-00001', folder='upenn',
                keep=lambda s: 'Processed' in s.get('SeriesDescription', ''),
                name=lambda s: s['SeriesDescription'].split(':')[0].strip().replace(' ', '_').replace('-', ''))


def extras():
    # Indiana University chest X-rays (PNG) and reports, via Open-i. Check the licence on openi.nlm.nih.gov.
    base = 'https://openi.nlm.nih.gov/imgs/collections'
    for f, d in [('NLMCXR_reports.tgz', 'iu'), ('NLMCXR_png.tgz', os.path.join('iu', 'png'))]:
        t = get(f'{base}/{f}', os.path.join(RAW, 'iu', f))
        tarfile.open(t).extractall(os.path.join(RAW, d))
    # CRC-VAL-HE-7K pathology tiles (Kather et al., Zenodo, CC BY 4.0)
    z = get('https://zenodo.org/api/records/1214456/files/CRC-VAL-HE-7K.zip/content', os.path.join(RAW, 'crc', 'CRC-VAL-HE-7K.zip'))
    zipfile.ZipFile(z).extractall(os.path.join(RAW, 'crc'))
    # HC18 fetal head ultrasound (van den Heuvel et al., Zenodo, CC BY 4.0)
    z = get('https://zenodo.org/api/records/1327317/files/training_set.zip/content', os.path.join(RAW, 'hc18', 'training_set.zip'))
    zipfile.ZipFile(z).extractall(os.path.join(RAW, 'hc18'))
    get('https://zenodo.org/api/records/1327317/files/training_set_pixel_size_and_HC.csv/content',
        os.path.join(RAW, 'hc18', 'training_set_pixel_size_and_HC.csv'))
    # FIVES fundus photographs (Jin et al., figshare, CC BY 4.0): a RAR archive; extract the test split with
    #   bsdtar -xf fives.rar "FIVES A Fundus Image Dataset for AI-based Vessel Segmentation/test"
    get('https://ndownloader.figshare.com/files/34969398', os.path.join(RAW, 'fives', 'fives.rar'))
    print('Extract FIVES manually (see comment in download_data.py), then rename the folder to data/raw/fives/FIVES')


if __name__ == '__main__':
    core()
    if '--all' in sys.argv:
        extras()
    print('done')
