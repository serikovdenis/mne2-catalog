"""Publish six exact-SKU CE-CP2IN1LBN photographs from BestSub Europe (Italy)."""
import concurrent.futures, ftplib, hashlib, io, os, subprocess, time
from PIL import Image
MANIFEST = [{"name":"CE-CP2IN1LBN_manufacturer_01.jpg","source":"https://shop.bestsub.it/hpeciai/fbf18bbc50406c2788e33ed0ee3dcd0b/ita_pl_Pressa-per-cappelli-Craft-Express-2-in-1-7708_1.jpg","source_sha256":"805f19ae595addc87912409bb106e8066a56ad82301621f4647074fb9885f19b","output_sha256":"805f19ae595addc87912409bb106e8066a56ad82301621f4647074fb9885f19b"},{"name":"CE-CP2IN1LBN_manufacturer_02.jpg","source":"https://shop.bestsub.it/hpeciai/d0045d949c0225839fc32f958b5b31d1/ita_pl_Pressa-per-cappelli-Craft-Express-2-in-1-7708_2.jpg","source_sha256":"0ccdcd66428bfcb1199d49d1ac07755ddc94b8879f56b5fdeba2727759c396fd","crop":[25,25,453],"output_sha256":"d99f74daf4dc234e0dcf86c642a1faa7a94134288f1caf67c061a945d3bd38e3"},{"name":"CE-CP2IN1LBN_manufacturer_03.jpg","source":"https://shop.bestsub.it/hpeciai/d9493a1c7bb842a6e278ba1ec80788fe/ita_pl_Pressa-per-cappelli-Craft-Express-2-in-1-7708_3.jpg","source_sha256":"4b8eeefe27f32f72d02f2e9755023f61fba3f9df1f9da746a65af0434f312454","output_sha256":"4b8eeefe27f32f72d02f2e9755023f61fba3f9df1f9da746a65af0434f312454"},{"name":"CE-CP2IN1LBN_manufacturer_04.jpg","source":"https://shop.bestsub.it/hpeciai/e5020d27834b976aa519a4dd5bbe5376/ita_pl_Pressa-per-cappelli-Craft-Express-2-in-1-7708_4.jpg","source_sha256":"aecea0d5dbe5e8be3453555aab8c728e9f6577d7a0f05311c31ae46d3f1fb54c","output_sha256":"aecea0d5dbe5e8be3453555aab8c728e9f6577d7a0f05311c31ae46d3f1fb54c"},{"name":"CE-CP2IN1LBN_manufacturer_05.jpg","source":"https://shop.bestsub.it/hpeciai/cc61d179503f1aa4ec67575656d990b6/ita_pl_Pressa-per-cappelli-Craft-Express-2-in-1-7708_6.jpg","source_sha256":"6171c88fc4a24d4492ff377bf5cf38fe676458531438182317555c464f5533f4","output_sha256":"6171c88fc4a24d4492ff377bf5cf38fe676458531438182317555c464f5533f4"},{"name":"CE-CP2IN1LBN_manufacturer_06.jpg","source":"https://shop.bestsub.it/hpeciai/49fd55ff7f1e5d820f9f795b9c53ac7d/ita_pl_Pressa-per-cappelli-Craft-Express-2-in-1-7708_7.jpg","source_sha256":"5820bb2e4fcc6478cc1c00c6b43ac784de8b18896c2d1c46c099aa102d6691b2","output_sha256":"5820bb2e4fcc6478cc1c00c6b43ac784de8b18896c2d1c46c099aa102d6691b2"}]
# Source product: https://shop.bestsub.it/product-ita-7708-Pressa-per-cappelli-Craft-Express-2-in-1.html
# Page metadata explicitly identifies CE-CP2IN1LBN; seven source photos reviewed.
# One visually duplicate pressure adjustment view and the old 216x139 thumbnail excluded.
# Only open-press photograph is cropped to 90%; no resampling or AI.
def get(url,optional=False):
    r=subprocess.run(['curl','-fLsS','--retry','3','--retry-all-errors','--connect-timeout','20','--max-time','90',url],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    if r.returncode:
        if optional:return None
        raise RuntimeError('Download failed: '+url)
    return r.stdout
def prepare(entry):
    live=get('https://mne2.ru/catalog/images/'+entry['name'],True)
    if live and hashlib.sha256(live).hexdigest()==entry['output_sha256']:return entry,live
    source=get(entry['source'])
    assert hashlib.sha256(source).hexdigest()==entry['source_sha256'], 'Source changed; review required'
    im=Image.open(io.BytesIO(source));assert im.size==(500,500);im.verify();body=source
    if entry.get('crop'):
        left,top,side=entry['crop']
        canvas=Image.new('RGB',(side,side),'white')
        canvas.paste(Image.open(io.BytesIO(source)).convert('RGB'),(-left,-top))
        out=io.BytesIO();canvas.save(out,'JPEG',quality=97,subsampling=0);body=out.getvalue()
    assert hashlib.sha256(body).hexdigest()==entry['output_sha256']
    return entry,body
def read(f,name):
    parts=[];f.retrbinary('RETR '+name,parts.append);return b''.join(parts)
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:ready=list(pool.map(prepare,MANIFEST))
assert len(ready)==6 and len({e['output_sha256'] for e,b in ready})==6
for attempt in range(5):
    try:
        with ftplib.FTP('p1057897.ftp.ihc.ru',timeout=45) as f:
            f.login('p1057897_chatgpt',os.environ['FTP_PASSWORD'])
            f.cwd('www/mne2.ru/catalog/images');existing=set(f.nlst())
            for entry,body in ready:
                name=entry['name']
                if name in existing:assert read(f,name)==body, 'Refusing to overwrite another image'
                else:
                    temp='.'+name+'.upload-'+os.environ.get('GITHUB_RUN_ID','review')
                    f.storbinary('STOR '+temp,io.BytesIO(body))
                    assert read(f,temp)==body
                    f.rename(temp,name)
                print('FTP_VERIFIED',name,flush=True)
        break
    except Exception:
        if attempt==4:raise
        time.sleep(3)
def verify(pair):
    entry,body=pair
    assert get('https://mne2.ru/catalog/images/'+entry['name'])==body
    print('HTTPS_VERIFIED',entry['name'],flush=True)
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:list(pool.map(verify,ready))
assert hashlib.sha256(get('https://mne2.ru/bestsub/CE-CP2IN1LBN/CE-CP2IN1LBN_01.jpg')).hexdigest()=='9031b4ab807001ed651d6ebadec7bfe0a2e48e5f0e4dadf81e7cc9755f8aff75'
print('CE_CP2IN1LBN_COMPLETE: six unique photographs; old original preserved',flush=True)
