"""Restore missing /120 metadata from existing reviewed FTP galleries.

Does not download manufacturer sources, re-encode images, modify prices, or
delete any existing server file. Refuses to replace an existing registry.
"""
import argparse
import concurrent.futures
import ftplib
import hashlib
import io
import json
import os
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import urlopen
from urllib.parse import urlparse
from PIL import Image

BASE = 'https://mne2.ru'
MAPPING = {
    'RAISE3D-PRO3-REVIEWED': ('TEST-04-01', 'Pro3'),
    'CREALITY-K2-PLUS-COMBO-REVIEWED': ('TEST-04-02', 'K2 Plus Combo'),
    'RAISE3D-PRO3-HS-REVIEWED': ('TEST-04-06', 'Pro3 HS'),
    'FEIYA-CTF1501-REVIEWED': ('TEST-06-02', 'CTF1501'),
    'FEIYA-CTF-N-SERIES-REVIEWED': ('TEST-06-04', 'CTF1201N'),
    'FEIYA-CTF1202-REVIEWED': ('TEST-06-06', 'CTF1202'),
    'FEIYA-CTF1502-REVIEWED': ('TEST-06-07', 'CTF1502'),
    'BRIGHT-LC810-REVIEWED': ('TEST-08-01', 'LC810'),
}

def get(path):
    assert path.startswith('/') and '..' not in path
    with urlopen(BASE + path, timeout=30) as response:
        assert response.status == 200
        return response.read()

def json_bytes(value):
    return json.dumps(value, ensure_ascii=False, indent=2).encode('utf-8')

def verify(photo):
    path = photo['path']
    assert path.startswith('/catalog/images/120/')
    raw = get(path)
    digest = hashlib.sha256(raw).hexdigest()
    provenance = 'reviewed_manifest_sha256'
    if photo.get('sha256') != digest:
        # A past deploy restored the unmodified Feiya original over a JPEG
        # derivative. Accept it only on exact byte equality with that source.
        source = photo.get('source', '')
        assert urlparse(source).hostname == 'www.feiya.com', ('Checksum changed', path)
        with urlopen(source, timeout=30) as response:
            assert response.status == 200 and response.read() == raw, path
        provenance = 'byte_identical_manufacturer_original'
    with Image.open(io.BytesIO(raw)) as im:
        assert im.size == (photo['width'], photo['height']), path
        im.verify()
    return dict(photo, http_status=200, verified_sha256=digest, provenance=provenance)

def main(publish=False):
    try:
        get('/120/photo-registry.json')
    except HTTPError as error:
        if error.code != 404:
            raise
    else:
        raise SystemExit('Registry already exists; inspect it instead of overwriting')
    data_raw = get('/120/data.json')
    data = json.loads(data_raw)
    assert len(data['cards']) == 120
    cards = {c['id']: c for c in data['cards']}
    assert len(cards) == 120
    registry = {cid: dict(images=[], status='NO_EXACT_PHOTOS',
                         issue='Не подтверждены фотографии точной модели и комплектации.')
                for cid in cards}
    checks = []
    for folder, (cid, model) in MAPPING.items():
        assert any(c.get('model') == model for c in cards[cid]['supplier_candidates'])
        manifest = json.loads(get('/catalog/images/120/' + folder + '/manifest.json'))
        assert manifest['match_scope'] == 'EXACT_MODEL'
        assert manifest['related_draft_cards'] == [cid]
        assert manifest['images']
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
            photos = list(pool.map(verify, manifest['images']))
        assert len({p['verified_sha256'] for p in photos}) == len(photos)
        checks.extend(photos)
        registry[cid] = dict(images=photos, status='EXACT_MODEL',
                             model=manifest['model'], source_page=manifest['source_page'],
                             note=manifest.get('note', ''),
                             issue='Фото модели подтверждено; комплектация и цена требуют отдельной проверки.')
        print('VERIFIED_EXISTING_GALLERY', cid, model, len(photos), flush=True)
    report = dict(total_cards=120, cards_with_exact_photos=len(MAPPING),
                  cards_with_multiple_photos=len(MAPPING), verified_image_urls=len(checks),
                  http_verification='PASSED', publication_readiness='NOT_COMPLETE',
                  fully_published_cards=0,
                  note='Проверены существующие файлы и SHA256 ранее просмотренных галерей. Цены и характеристики не подтверждаются этим отчётом.',
                  remaining_problems=[dict(id=cid, issue=r['issue']) for cid,r in registry.items()])
    out = Path('recovery-120'); out.mkdir(exist_ok=True)
    payloads = {'photo-registry.json': json_bytes(registry),
                'photo-report.json': json_bytes(report)}
    for name, raw in payloads.items():
        (out/name).write_bytes(raw)
    if not publish:
        print('DRY_RUN_COMPLETE', len(MAPPING), len(checks))
        return
    # Existing credentials stay in Actions; they are never exported or printed.
    with ftplib.FTP_TLS('p1057897.ftp.ihc.ru', timeout=30) as ftp:
        ftp.login('p1057897_chatgpt', os.environ['FTP_PASSWORD'])
        ftp.prot_p(); ftp.cwd('www/mne2.ru/120')
        assert 'photo-registry.json' not in ftp.nlst(), 'Registry appeared concurrently'
        assert get('/120/data.json') == data_raw, 'Card data changed during review'
        for name, raw in payloads.items():
            assert name not in ftp.nlst(), ('Refusing to replace existing file', name)
            temp = '.' + name + '.recovery-' + os.environ['GITHUB_RUN_ID']
            ftp.storbinary('STOR ' + temp, io.BytesIO(raw))
            readback = io.BytesIO(); ftp.retrbinary('RETR ' + temp, readback.write)
            assert readback.getvalue() == raw
            ftp.rename(temp, name)
            assert get('/120/' + name) == raw, ('HTTPS differs from uploaded bytes', name)
            print('ATOMICALLY_PUBLISHED_AND_HTTPS_VERIFIED', name)
    print('RECOVERED_METADATA_ONLY', len(MAPPING), 'cards;', len(checks), 'existing images')

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--publish', action='store_true')
    main(parser.parse_args().publish)
