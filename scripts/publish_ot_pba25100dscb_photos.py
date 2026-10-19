"""Publish two reviewed exact-model OT-PBA25100DSCB native crops."""
import ftplib, hashlib, io, os, subprocess, time
from PIL import Image
MANIFEST = [{"name":"OT-PBA25100DSCB_manufacturer90_01.jpg","source":"https://www.bestsub.com/media/k2/galleries/25460/OT-PBA25100DSCB.jpg","source_sha256":"d7fd2b8aa2b05dd9521c271909b05b0555e6ad238ddba0e14b504bf1cb84aaf5","crop":[100,0,700,600],"output_sha256":"9805a970de0ad97a370423dd0cc03717ca31e7ee8400150d244bcfb62467d0a9"},{"name":"OT-PBA25100DSCB_manufacturer90_02.jpg","source":"https://www.bestsub.com/media/k2/galleries/25460/OT-PBA25100DSCB_1_1.jpg","source_sha256":"15819628ef483a529f453442386e308dabf2c5afa99ac1909e76ef307b2e4036","crop":[177,78,622,523],"output_sha256":"6f6d49131c55d5dd5135ab464dc72d12e9dc1f7f7f3c0995c22f6ef0b127b302"}]
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
    assert im.size in ((1000,1000),(800,600))
    body=source
    if entry['crop'] is not None:
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
            print('OT-PBA25100DSCB_FTP_HTTPS_VERIFIED',name,len(body),entry['output_sha256'],flush=True)
            break
        except Exception:
            if attempt==4: raise
            time.sleep(3)

print('OT-PBA25100DSCB VERIFIED: 2 unique photographs, 2 native crops, no upscaling',flush=True)
