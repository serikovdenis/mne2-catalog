"""Publish the exact BPRO4060SMDLB manufacturer photograph, cropped without resampling."""
import ftplib, hashlib, io, os, subprocess, time
from PIL import Image

SOURCE = 'https://www.bestsub.com/media/k2/galleries/26999/BPRO4060SMDLB.jpg'
SOURCE_SHA = 'f6e13e22b0a3d0570d93f5006479ee3b567f170bdb922d68cae143074015aeb1'
NAME = 'BPRO4060SMDLB_manufacturer90_01.jpg'
OUTPUT_SHA = '2ecab6023132a88592ccf1b89d28339a31f193341b6706b32603bab36f2dc4ee'
def get(url):
    return subprocess.check_output(['curl','-fLsS','--retry','3','--retry-all-errors','--connect-timeout','20','--max-time','90',url])
source = get(SOURCE)
assert hashlib.sha256(source).hexdigest() == SOURCE_SHA, 'Manufacturer source changed; review required'
im = Image.open(io.BytesIO(source)).convert('RGB')
assert im.size == (800,600)
# Reviewed product bounds: (195,100,604,500); 409/455 = 89.89%.
# Native pixels retained. No resize, sharpening, AI or detail reconstruction.
im = im.crop((172,72,627,527))
out = io.BytesIO()
im.save(out,'JPEG',quality=97,subsampling=0)
body = out.getvalue()
assert hashlib.sha256(body).hexdigest() == OUTPUT_SHA
def read(f,name):
    chunks=[]
    f.retrbinary('RETR '+name,chunks.append)
    return b''.join(chunks)
for attempt in range(5):
    try:
        with ftplib.FTP('p1057897.ftp.ihc.ru',timeout=45) as f:
            f.login('p1057897_chatgpt',os.environ['FTP_PASSWORD'])
            f.cwd('www/mne2.ru/catalog/images')
            if NAME in f.nlst():
                assert read(f,NAME)==body, 'Refusing to overwrite a different existing image'
            else:
                temporary='.'+NAME+'.upload-'+os.environ.get('GITHUB_RUN_ID','review')
                f.storbinary('STOR '+temporary,io.BytesIO(body))
                assert read(f,temporary)==body
                f.rename(temporary,NAME)
            assert read(f,NAME)==body
        assert get('https://mne2.ru/catalog/images/'+NAME)==body
        print('BPRO4060SMDLB_FTP_HTTPS_VERIFIED',NAME,len(body),OUTPUT_SHA,flush=True)
        break
    except Exception:
        if attempt==4: raise
        time.sleep(3)
assert hashlib.sha256(get('https://mne2.ru/catalog/images/bestsub/BPRO4060SMDLB/01.jpg')).hexdigest()==SOURCE_SHA, 'Existing original changed'
print('BPRO4060SMDLB_ORIGINAL_PRESERVED; one unique photograph',flush=True)
