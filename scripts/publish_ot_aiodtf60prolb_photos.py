"""Publish reviewed exact-SKU OT-AIODTF60PROLB gallery before exposing any links."""
import concurrent.futures, ftplib, hashlib, io, os, subprocess, time
from PIL import Image
MANIFEST = [{"name":"OT-AIODTF60PROLB_manufacturer_01.jpg","source":"https://www.bestsub.com/media/k2/galleries/27524/OT-AIODTF60PROLB.jpg","source_sha256":"1d72dc22b51f44c3af7b69d7fd49fbfecd346e7f87e059d9995398617c22c266","crop":[52,-41,688],"product_bounds":[87,72,706,534],"output_sha256":"9fbd74c2b8b5261a900f8f187de83909c0c24af6068db0f7b9ac4987744deee8"},{"name":"OT-AIODTF60PROLB_manufacturer_02.jpg","source":"https://www.bestsub.com/media/k2/galleries/27524/OT-AIODTF60PROLB_1.jpg","source_sha256":"30ae854080713573229dc25ebc9a316df02cfd30de4f6a22e0b74fc6d178614e","crop":[27,-84,735],"product_bounds":[64,0,725,567],"output_sha256":"c1fd137a333aa89ddebf98cc0a4057c96804f3dd182deb717e76866a98b6898b"},{"name":"OT-AIODTF60PROLB_manufacturer_03.jpg","source":"https://www.bestsub.com/media/k2/galleries/27524/OT-AIODTF60PROLB_1_image.jpg","source_sha256":"fcb8e0c03bda25425fa0229bd8246024c6924148d8422eca358038479ba50df9","output_sha256":"fcb8e0c03bda25425fa0229bd8246024c6924148d8422eca358038479ba50df9"},{"name":"OT-AIODTF60PROLB_manufacturer_04.jpg","source":"https://www.bestsub.com/media/k2/galleries/27524/OT-AIODTF60PROLB_2_image.jpg","source_sha256":"c97beb5f7faa18162a54836d6fe8f001322200b8f659a00088e2e61f1ccd1aa0","output_sha256":"c97beb5f7faa18162a54836d6fe8f001322200b8f659a00088e2e61f1ccd1aa0"},{"name":"OT-AIODTF60PROLB_manufacturer_05.jpg","source":"https://www.bestsub.com/media/k2/galleries/27524/OT-AIODTF60PROLB_3_image.jpg","source_sha256":"34e60289015dc36b847cc75337e8b971dbe34ca095b54ef164e03cb8f0729339","output_sha256":"34e60289015dc36b847cc75337e8b971dbe34ca095b54ef164e03cb8f0729339"},{"name":"OT-AIODTF60PROLB_manufacturer_06.jpg","source":"https://www.bestsub.com/media/k2/galleries/27524/OT-AIODTF60PROLB_4_image.jpg","source_sha256":"d741e25a3535987e9d1231d42da587a58b0bca3ffb863104260ed69aa5ed2f3c","output_sha256":"d741e25a3535987e9d1231d42da587a58b0bca3ffb863104260ed69aa5ed2f3c"},{"name":"OT-AIODTF60PROLB_manufacturer_07.jpg","source":"https://www.bestsub.com/media/k2/galleries/27524/OT-AIODTF60PROLB_5_image.jpg","source_sha256":"c5b55fa8e9c555da75a79c5c04edbd250f98759d73d88d428cc2789a89a3ac2f","output_sha256":"c5b55fa8e9c555da75a79c5c04edbd250f98759d73d88d428cc2789a89a3ac2f"},{"name":"OT-AIODTF60PROLB_manufacturer_08.jpg","source":"https://www.bestsub.com/media/k2/galleries/27524/OT-AIODTF60PROLB_6_image.jpg","source_sha256":"3a748da10c4b81e6930677f4050e324d06a571fbd2903c75e47474b59c3654c9","output_sha256":"3a748da10c4b81e6930677f4050e324d06a571fbd2903c75e47474b59c3654c9"},{"name":"OT-AIODTF60PROLB_manufacturer_09.jpg","source":"https://www.bestsub.com/media/k2/galleries/27524/OT-AIODTF60PROLB_7_image.jpg","source_sha256":"6cdc15d574bd9acce4dbb14dfb9da170e88aacf04e5a684a4033da3b0be66a37","output_sha256":"6cdc15d574bd9acce4dbb14dfb9da170e88aacf04e5a684a4033da3b0be66a37"},{"name":"OT-AIODTF60PROLB_manufacturer_10.jpg","source":"https://www.bestsub.com/media/k2/galleries/27524/OT-AIODTF60PROLB_8_image.jpg","source_sha256":"a36123dcf39cdfafad7ca09fd6b28048a83303a9238af0dccd086a308aca526d","output_sha256":"a36123dcf39cdfafad7ca09fd6b28048a83303a9238af0dccd086a308aca526d"},{"name":"OT-AIODTF60PROLB_manufacturer_11.jpg","source":"https://www.bestsub.com/media/k2/galleries/27524/OT-AIODTF60PROLB_9_image.jpg","source_sha256":"4cdba902a10ebd7d6c2d316d2b278875a9aa4564db0af3820c87aa8d4c38ae50","output_sha256":"4cdba902a10ebd7d6c2d316d2b278875a9aa4564db0af3820c87aa8d4c38ae50"},{"name":"OT-AIODTF60PROLB_manufacturer_12.jpg","source":"https://www.bestsub.com/media/k2/galleries/27524/OT-AIODTF60PROLB_10_image.jpg","source_sha256":"716fc15aa0c70374a8fdcbdeaebde89c800ed8b4888543980280fa3fcdfcc295","output_sha256":"716fc15aa0c70374a8fdcbdeaebde89c800ed8b4888543980280fa3fcdfcc295"},{"name":"OT-AIODTF60PROLB_manufacturer_13.jpg","source":"https://www.bestsub.com/media/k2/galleries/27524/OT-AIODTF60PROLB_11_image.jpg","source_sha256":"50dcdd102c1ed14c1194a6689d01287d83ac74662f1e6411bc8655a9b0c81ba2","output_sha256":"50dcdd102c1ed14c1194a6689d01287d83ac74662f1e6411bc8655a9b0c81ba2"},{"name":"OT-AIODTF60PROLB_manufacturer_14.jpg","source":"https://www.bestsub.com/media/k2/galleries/27524/OT-AIODTF60PROLB_12_image.jpg","source_sha256":"5530ae746c53ae37007823d8938eb6b9bb8903bcda05b15f21ebd4e4e659f371","output_sha256":"5530ae746c53ae37007823d8938eb6b9bb8903bcda05b15f21ebd4e4e659f371"},{"name":"OT-AIODTF60PROLB_manufacturer_15.jpg","source":"https://www.bestsub.com/media/k2/galleries/27524/OT-AIODTF60PROLB_13_image.jpg","source_sha256":"065a09936c80f4e76f8ca77c53d2b6943023137b608d25193250a41b017ab379","output_sha256":"065a09936c80f4e76f8ca77c53d2b6943023137b608d25193250a41b017ab379"}]
# Exact manufacturer SKU: BestSub gallery 27524, Model S 60 Pro.
# Fifteen visually reviewed unique images; news banner and 182x137 old thumbnail excluded.
# First two use native pixels on white canvas, longest product side approximately 90%.
# Remaining thirteen manufacturer detail panels are copied byte-for-byte.
def get(url, optional=False):
    r=subprocess.run(['curl','-fLsS','--retry','2','--retry-all-errors','--connect-timeout','20','--max-time','90',url],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    if r.returncode:
        if optional:return None
        raise RuntimeError('Download failed: '+url)
    return r.stdout
def prepare(entry):
    live=get('https://mne2.ru/catalog/images/'+entry['name'],optional=True)
    if live and hashlib.sha256(live).hexdigest()==entry['output_sha256']:
        return entry,live
    source=get(entry['source'])
    assert hashlib.sha256(source).hexdigest()==entry['source_sha256'], 'Manufacturer original changed: '+entry['name']
    im=Image.open(io.BytesIO(source))
    assert im.size==(800,600)
    im.verify()
    body=source
    if entry.get('crop'):
        left,top,side=entry['crop']
        canvas=Image.new('RGB',(side,side),'white')
        canvas.paste(Image.open(io.BytesIO(source)).convert('RGB'),(-left,-top))
        out=io.BytesIO();canvas.save(out,'JPEG',quality=97,subsampling=0);body=out.getvalue()
    assert hashlib.sha256(body).hexdigest()==entry['output_sha256']
    return entry,body
def read(f,name):
    parts=[];f.retrbinary('RETR '+name,parts.append);return b''.join(parts)
def connect():
    f=ftplib.FTP('p1057897.ftp.ihc.ru',timeout=45)
    f.login('p1057897_chatgpt',os.environ['FTP_PASSWORD'])
    f.cwd('www/mne2.ru/catalog/images')
    return f
with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:
    ready=list(pool.map(prepare,MANIFEST))
assert len(ready)==15 and len({e['output_sha256'] for e,b in ready})==15
# All originals are validated before any write. Publish each complete temporary file by rename.
for attempt in range(5):
    try:
        with connect() as f:
            existing=set(f.nlst())
            for entry,body in ready:
                name=entry['name']
                if name in existing:
                    assert read(f,name)==body, 'Refusing to overwrite a different image: '+name
                else:
                    temporary='.'+name+'.upload-'+os.environ.get('GITHUB_RUN_ID','review')
                    f.storbinary('STOR '+temporary,io.BytesIO(body))
                    assert read(f,temporary)==body
                    f.rename(temporary,name)
                print('FTP_VERIFIED',name,flush=True)
        break
    except Exception:
        if attempt==4:raise
        time.sleep(3)
def verify(pair):
    entry,body=pair
    assert get('https://mne2.ru/catalog/images/'+entry['name'])==body
    print('HTTPS_VERIFIED',entry['name'],len(body),flush=True)
with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:list(pool.map(verify,ready))
assert hashlib.sha256(get('https://mne2.ru/bestsub/OT-AIODTF60PROLB/OT-AIODTF60PROLB_01.png')).hexdigest()=='9cd50f0df9b3607814d39f41432d5c2dbb47e20d2f3fae5e794af7affc9531cf'
print('OT_AIODTF60PROLB_COMPLETE: 15 unique photographs; previous file preserved',flush=True)
