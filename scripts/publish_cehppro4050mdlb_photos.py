"""Publish only visually reviewed CEHPPRO4050MDLB originals, without overwrites."""
import ftplib,hashlib,io,json,os,subprocess,time,urllib.request
from pathlib import Path
MANIFEST = [{'name': 'CEHPPRO4050MDLB_official_03.jpg', 'source': 'https://shop.bestsub.com/image/catalog/pyd/Machine/Heat_Press_Machine/CEHPPRO4050MDLB.jpg', 'sha256': 'b120f057dc58f1801794493c1c03f4a252a82412449779c87771dcdd2cae2994'}, {'name': 'CEHPPRO4050MDLB_official_04.jpg', 'source': 'https://www.bestsub.com/media/k2/galleries/23691/CEHPPRO4050MDLB_1.jpg', 'sha256': '150374eaac52643c8403d662ea3b2295938276dfaa62ccb13e755df605b1d186'}, {'name': 'CEHPPRO4050MDLB_official_05.jpg', 'source': 'https://www.bestsub.com/media/k2/galleries/23691/CEHPPRO4050MDLB_2.jpg', 'sha256': 'b0fa13596aa15706a12bdac38e2189e7892b870507537a562005c2accffcc588'}, {'name': 'CEHPPRO4050MDLB_official_06.jpg', 'source': 'https://www.bestsub.com/media/k2/galleries/23691/CEHPPRO4050MDLB_3.jpg', 'sha256': 'b6a9d66ba8d93a014f47f06fb586d05eb3b21a1a0b189c7d1001abe9332398b6'}, {'name': 'CEHPPRO4050MDLB_official_07.jpg', 'source': 'https://www.bestsub.com/media/k2/galleries/23691/CEHPPRO4050MDLB_4.jpg', 'sha256': '5085338b9c8f0d4a5ed05cb9a7d4186f04a211f2f608f6ed83f8de713bd8a245'}, {'name': 'CEHPPRO4050MDLB_official_08.jpg', 'source': 'https://www.bestsub.com/media/k2/galleries/23691/CEHPPRO4050MDLB_5.jpg', 'sha256': '1fbd86c720fad49e7d088596223ee7cde408ec27333eaf6c027b77269bc65980'}, {'name': 'CEHPPRO4050MDLB_official_09.jpg', 'source': 'https://www.bestsub.com/media/k2/galleries/23691/CEHPPRO4050MDLB_6.jpg', 'sha256': '2f907eae91bd35aea2790131ed081ce360c4ec8cf7ade050378b39a9bd1c368b'}, {'name': 'CEHPPRO4050MDLB_official_10.jpg', 'source': 'https://www.bestsub.com/media/k2/galleries/23691/CEHPPRO4050MDLB_7.jpg', 'sha256': 'a57a79ed2b7af7ef33414c4d44a3c72a488a0e98ba2d636bbbc84ef0122afcaf'}, {'name': 'CEHPPRO4050MDLB_official_11.jpg', 'source': 'https://www.bestsub.com/media/k2/galleries/23691/CEHPPRO4050MDLB_8.jpg', 'sha256': 'd4a452c3ab6206f8ff7ddc6869d16e5db34789069c4f414bad17fefa45b601a9'}, {'name': 'CEHPPRO4050MDLB_official_12.jpg', 'source': 'https://www.bestsub.com/media/k2/galleries/23691/CEHPPRO4050MDLB_9.jpg', 'sha256': 'f5cecea686aba85f3c8a22c09782bcc24b06f123224a8c0ff306e0db4a9667bd'}, {'name': 'CEHPPRO4050MDLB_official_13.jpg', 'source': 'https://www.bestsub.com/media/k2/galleries/23691/CEHPPRO4050MDLB_10.jpg', 'sha256': '4d9b0f032db0ac0b185550e063214914b378ae3f11dc8893b4231df2aec097c1'}, {'name': 'CEHPPRO4050MDLB_official_14.jpg', 'source': 'https://www.bestsub.com/media/k2/galleries/23691/CEHPPRO4050MDLB_11.jpg', 'sha256': 'dfae6ed675b3074cc86a8e86d19e09f3d68b4b3b53af4d924a6228826ad2087d'}, {'name': 'CEHPPRO4050MDLB_official_15.jpg', 'source': 'https://www.bestsub.com/media/k2/galleries/23691/CEHPPRO4050MDLB_12.jpg', 'sha256': '0ae3b09ad1af58afa7e1490429d9a160facf237b9532ffa975d94f0446e682b4'}, {'name': 'CEHPPRO4050MDLB_official_16.jpg', 'source': 'https://www.bestsub.com/media/k2/galleries/23691/CEHPPRO4050MDLB_13.jpg', 'sha256': 'e2cc279637d5ccae80aea410c49fda73f6ea324b4cc1abdc1314006ffff0b8af'}, {'name': 'CEHPPRO4050MDLB_official_17.jpg', 'source': 'https://www.bestsub.com/media/k2/galleries/23691/CEHPPRO4050MDLB_14.jpg', 'sha256': '3a22682d0c46a82d57641f5781dd282d20571374a80a0f9ab55bbb54595d9370'}, {'name': 'CEHPPRO4050MDLB_official_18.jpg', 'source': 'https://www.bestsub.com/media/k2/galleries/23691/CEHPPRO4050MDLB_15.jpg', 'sha256': 'c6897721509643418b12b2cfba29026fae94faf9aa8374e2f81025dcc7f50d1e'}, {'name': 'CEHPPRO4050MDLB_official_19.jpg', 'source': 'https://www.bestsub.com/media/k2/galleries/23691/CEHPPRO4050MDLB_16.jpg', 'sha256': 'd30a2a852f4089d054624f22b43caa90b41ba5eb73b34e53c227437728f00f1e'}]
EXISTING = {'CEHPPRO4050MDLB_01.jpg': '7dc267fb6fb81822193b88047a8e97be56c33e55075e679a2962d250f5d1f66c', 'CEHPPRO4050MDLB_02.jpg': 'b55b04faf7d1291796ea93ee852e2ea6253d3c47cc0cb51549e6d81529417108'}
def get(url):
    return subprocess.check_output(['curl','-fLsS','--retry','4','--retry-all-errors','--connect-timeout','20','--max-time','90',url])
def connect():
    f=ftplib.FTP('p1057897.ftp.ihc.ru',timeout=45)
    f.login('p1057897_chatgpt',os.environ['FTP_PASSWORD'])
    f.cwd('www/mne2.ru/catalog/images')
    return f
def read(f,name):
    chunks=[];f.retrbinary('RETR '+name,chunks.append);return b''.join(chunks)
# Fetch and hash-check every source before writing anything to FTP.
ready=[]
for entry in MANIFEST:
    try:
        live=get('https://mne2.ru/catalog/images/'+entry['name'])
        if hashlib.sha256(live).hexdigest()==entry['sha256']:
            print('EXISTING_HTTPS_VERIFIED',entry['name'],flush=True)
            continue
    except subprocess.CalledProcessError:
        pass
    body=get(entry['source'])
    assert hashlib.sha256(body).hexdigest()==entry['sha256'],entry
    assert body[:3]==bytes.fromhex('ffd8ff') and body[-2:]==bytes.fromhex('ffd9')
    ready.append((entry,body))
# Existing 01 and 02 are retained, with their original bytes.
for name,sha in EXISTING.items():
    assert hashlib.sha256(get('https://mne2.ru/catalog/images/'+name)).hexdigest()==sha
for entry,body in ready:
    name=entry['name']
    for attempt in range(5):
        try:
            with connect() as f:
                if name in f.nlst():
                    assert read(f,name)==body,'Refusing to overwrite different existing image: '+name
                else:f.storbinary('STOR '+name,io.BytesIO(body))
                assert read(f,name)==body
            assert get('https://mne2.ru/catalog/images/'+name)==body
            print('FTP_HTTPS_VERIFIED',name,len(body),entry['sha256'],flush=True)
            break
        except Exception:
            if attempt==4:raise
            time.sleep(3)
print('ALL_REVIEWED_IMAGES_VERIFIED',len(ready)+len(EXISTING),flush=True)
