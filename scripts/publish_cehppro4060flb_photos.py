"""Publish ten reviewed CEHPPRO4060FLB photographs with native-pixel crops."""
import ftplib, hashlib, io, os, subprocess, time
from PIL import Image
MANIFEST = [{"name":"CEHPPRO4060FLB_manufacturer_01.jpg","source":"https://craftexpress24.eu/hpeciai/9c8aa7c110d3cb08f64fc18268480630/eng_pl_Craft-Express-Manual-Flat-Press-40-x-60-cm-Blue-64_1.jpg","source_sha256":"ea2b8e4c3a0f1b01ffa116653e33c0128fee37537c16fd7c6d51beaadf0aae11","crop":[100,161,900,961],"output_sha256":"57e23acff5fc68b206bbefbbe114b8d140ab63cec244d6506f4f007f9998192c"},{"name":"CEHPPRO4060FLB_manufacturer_02.jpg","source":"https://craftexpress24.eu/hpeciai/5d51ed1e80947f521592425e529c0fb5/eng_pl_Craft-Express-Manual-Flat-Press-40-x-60-cm-Blue-64_4.jpg","source_sha256":"556c1d908d1dc66dd466539ff0aa0f50648b2f8a7e9678e959acb3d3a84fbdcc","crop":[100,160,900,960],"output_sha256":"1c36eb422da06e64d29e96aaaa6e1bf386a6bc0a4390e6e18987a1293215061e"},{"name":"CEHPPRO4060FLB_manufacturer_03.jpg","source":"https://craftexpress24.eu/hpeciai/4b63f86a76473c008d0b84a125570931/eng_pl_Craft-Express-Manual-Flat-Press-40-x-60-cm-Blue-64_8.jpg","source_sha256":"a5271f21715a2165dfd900486e4c25b9093af432cfdd07ef31cd16a5330489a7","crop":[100,160,900,960],"output_sha256":"119091b66812cac53a8f6bf96f9a0bbabfbfd202200f660fbad6a139833e8d24"},{"name":"CEHPPRO4060FLB_manufacturer_04.jpg","source":"https://craftexpress24.eu/hpeciai/cb10851aa403110bf467f1e5a2d21a91/eng_pl_Craft-Express-Manual-Flat-Press-40-x-60-cm-Blue-64_9.jpg","source_sha256":"d0c166d48c26cc2f5493a25f9ea2b04edb30169171f8f9505ac043ab2c9e9d34","crop":[100,160,900,960],"output_sha256":"338b0dac2cfbe6fd70870aa6bc4c49e5c7b50f8a507dbf80b3baf6cd91641278"},{"name":"CEHPPRO4060FLB_manufacturer_05.jpg","source":"https://craftexpress24.eu/hpeciai/23167b6292c04276e0b39fafefb8cc54/eng_pl_Craft-Express-Manual-Flat-Press-40-x-60-cm-Blue-64_7.jpg","source_sha256":"a940f0ed27079e70ce26d9ea91728ecd7fab5d7b4237f327e51e9eacb63b3136","crop":[100,160,900,960],"output_sha256":"c230bf8b25fd0be1fe9f26bf567c16e94add74a048ddb87d72cd81a744aecc08"},{"name":"CEHPPRO4060FLB_manufacturer_06.jpg","source":"https://www.bestsub.com/media/k2/galleries/23692/CEHPPRO4060FLB.jpg","source_sha256":"c2438a87a9b6d2146eeeda9ffe5f4f9e715b5535e81981653e3914439c031f1d","crop":[177,78,622,523],"output_sha256":"d10c7a80f5bf8a2b02b8396a6be6e46c7eb37b20d984cb186b5a871fc2195fde"},{"name":"CEHPPRO4060FLB_manufacturer_07.jpg","source":"https://craftexpress24.eu/hpeciai/ca95fc53276c4eccfca97fe0e38d3f5b/eng_pl_Craft-Express-Manual-Flat-Press-40-x-60-cm-Blue-64_2.jpg","source_sha256":"6a9a65aea258e6fb0e495f7e88e1788e83ecb3c2a8a446f826b80ad1291b719a","crop":None,"output_sha256":"6a9a65aea258e6fb0e495f7e88e1788e83ecb3c2a8a446f826b80ad1291b719a"},{"name":"CEHPPRO4060FLB_manufacturer_08.jpg","source":"https://craftexpress24.eu/hpeciai/2ad0599c73e06405ed2098e572224851/eng_pl_Craft-Express-Manual-Flat-Press-40-x-60-cm-Blue-64_3.jpg","source_sha256":"1d78401ab8cbaa46467a90ed3a6c1e28c04dc4077fecbfab996e4f205a629d13","crop":None,"output_sha256":"1d78401ab8cbaa46467a90ed3a6c1e28c04dc4077fecbfab996e4f205a629d13"},{"name":"CEHPPRO4060FLB_manufacturer_09.jpg","source":"https://craftexpress24.eu/hpeciai/a3b3661ce4ff3aaae278049a22e72245/eng_pl_Craft-Express-Manual-Flat-Press-40-x-60-cm-Blue-64_5.jpg","source_sha256":"4e16a4a8fdc081188fadf18bcfc948ad2c565f526c373606eeaca611dc613310","crop":None,"output_sha256":"4e16a4a8fdc081188fadf18bcfc948ad2c565f526c373606eeaca611dc613310"},{"name":"CEHPPRO4060FLB_manufacturer_10.jpg","source":"https://craftexpress24.eu/hpeciai/8010870a11076ff865749b60af258a1a/eng_pl_Craft-Express-Manual-Flat-Press-40-x-60-cm-Blue-64_6.jpg","source_sha256":"165c5cd11491dafb973aec401d86c14e6f0c55ac4f4e35942082235fcf706f8e","crop":None,"output_sha256":"165c5cd11491dafb973aec401d86c14e6f0c55ac4f4e35942082235fcf706f8e"}]
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
            print('CEHPPRO4060FLB_FTP_HTTPS_VERIFIED',name,len(body),entry['output_sha256'],flush=True)
            break
        except Exception:
            if attempt==4: raise
            time.sleep(3)

print('CEHPPRO4060FLB VERIFIED: 10 unique photographs, 6 native crops, 4 untouched originals',flush=True)
