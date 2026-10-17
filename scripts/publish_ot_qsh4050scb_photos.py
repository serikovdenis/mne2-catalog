"""Publish two reviewed exact-model OT-QSH4050SCB photographs with native-pixel crops."""
import ftplib, hashlib, io, os, subprocess, time
from PIL import Image
MANIFEST = [{"name":"OT-QSH4050SCB_manufacturer90_01.jpg","source":"https://www.bestsub.com/media/k2/galleries/25130/OT-QSH4050SCB.jpg","source_sha256":"a73a9444600a9c23d32c3187427d50e5cac4d80308da5afcbed166474f1f0916","crop":[67,77,734,522],"output_sha256":"1dd3160861866b6b3bac05575ccab63b6921b5b8c60c0be7d79911c04fb18021"},{"name":"OT-QSH4050SCB_manufacturer90_02.jpg","source":"https://www.bestsub.com/media/k2/galleries/25130/OT-QSH4050SCB_1_1.jpg","source_sha256":"b1b51c1cfee1cd65bfc7c8f0510f04be5258c04f14d733a8df41444241592164","crop":[177,77,622,522],"output_sha256":"086ef548cab246bb20e0a3680270c1e0b376bceb231e593c1079e5c8ef7f6d96"}]
def get(url):
    return subprocess.check_output(['curl','-fLsS','--retry','3','--retry-all-errors','--connect-timeout','20','--max-time','90',url])
def read(f,name):
    chunks=[]
    f.retrbinary('RETR '+name,chunks.append)
    return b''.join(chunks)
ready=[]
for entry in MANIFEST:
    source=get(entry['source'])
    assert hashlib.sha256(source).hexdigest()==entry['source_sha256'], 'Manufacturer original changed; review required'
    im=Image.open(io.BytesIO(source)).convert('RGB')
    assert im.size==(800,600)
    im=im.crop(entry['crop'])
    out=io.BytesIO()
    im.save(out,'JPEG',quality=97,subsampling=0)
    body=out.getvalue()
    assert hashlib.sha256(body).hexdigest()==entry['output_sha256']
    ready.append((entry,body))
for entry,body in ready:
    name=entry['name']
    for attempt in range(5):
        try:
            with ftplib.FTP('p1057897.ftp.ihc.ru',timeout=45) as f:
                f.login('p1057897_chatgpt',os.environ['FTP_PASSWORD'])
                f.cwd('www/mne2.ru/catalog/images')
                if name in f.nlst():
                    assert read(f,name)==body, 'Refusing to overwrite different image'
                else:
                    temporary='.'+name+'.upload-'+os.environ.get('GITHUB_RUN_ID','review')
                    f.storbinary('STOR '+temporary,io.BytesIO(body))
                    assert read(f,temporary)==body
                    f.rename(temporary,name)
                assert read(f,name)==body
            assert get('https://mne2.ru/catalog/images/'+name)==body
            print('OT-QSH4050SCB_FTP_HTTPS_VERIFIED',name,len(body),entry['output_sha256'],flush=True)
            break
        except Exception:
            if attempt==4: raise
            time.sleep(3)

print('OT-QSH4050SCB: two native crops verified; originals preserved')
