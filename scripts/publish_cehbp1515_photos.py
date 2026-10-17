"""Publish two reviewed exact-model CEHBP1515 photographs with native-pixel crops."""
import ftplib, hashlib, io, os, subprocess, time
from PIL import Image
MANIFEST = [{"name":"CEHBP1515_manufacturer90_01.jpg","source":"https://www.bestsub.com/media/k2/galleries/24410/CEHBP1515.jpg","source_sha256":"43b5531303e923a0e16cb7f22482d559d52eb20b7e469e57142df1f86e552566","crop":[178,78,623,523],"output_sha256":"fad9beda7f13e7e40657ba0fa9ad67d9ed48aaf5b282035a1e2f8a8e90924f9c"},{"name":"CEHBP1515_manufacturer90_02.jpg","source":"https://www.bestsub.com/media/k2/galleries/24410/CEHBP1515_1.jpg","source_sha256":"53b665ca74be4227578e6f03e80d1057631ef58d5f4a273b214bfe67d8a7818b","crop":[177,78,622,523],"output_sha256":"b0e66ed92a6749a1552d8b3bf633f079a3c5eabd20ad888e6b8f8cc6d1b5f605"}]
# BestSub gallery 24410: open and closed CEHBP1515, 800x600 originals.
# Each product is 400px high: 400/445 = 89.89% after cropping.
# No resampling, AI, sharpening or reconstruction. Original MNE2 files retained.
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
            print('CEHBP1515_FTP_HTTPS_VERIFIED',name,len(body),entry['output_sha256'],flush=True)
            break
        except Exception:
            if attempt==4: raise
            time.sleep(3)
for i,entry in enumerate(MANIFEST,1):
    original=get('https://mne2.ru/catalog/images/bestsub/CEHBP1515/'+str(i).zfill(2)+'.jpg')
    assert hashlib.sha256(original).hexdigest()==entry['source_sha256']
print('CEHBP1515_VERIFIED: two unique native photographs; originals preserved',flush=True)
