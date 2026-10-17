"""Publish fifteen reviewed exact-model CEHPPRO3838FPK photographs with native-pixel crops."""
import ftplib, hashlib, io, os, subprocess, time
from PIL import Image
MANIFEST = [{"name":"CEHPPRO3838FPK_manufacturer_01.jpg","source":"https://craftexpress24.eu/hpeciai/df96ecdc4c675229356f4d92a564635c/eng_pl_Craft-Express-Manual-Flat-Press-38-x-38-cm-Pink-61_1.jpg","source_sha256":"6b734e2ffde2f89a6eb4c0d54773fdc60d622c97f53bc798991ccc03f72b3d7c","crop":[100,160,900,960],"output_sha256":"ff7ec5a2f021d5e8beb115465255022d4f01b0bbffecf06aa74aac4753fab609"},{"name":"CEHPPRO3838FPK_manufacturer_02.jpg","source":"https://craftexpress24.eu/hpeciai/9187a4fe7c1ecaed1b173c709ac7fe0b/eng_pl_Craft-Express-Manual-Flat-Press-38-x-38-cm-Pink-61_10.jpg","source_sha256":"b3b447c5cc51d84e35759b1e0ec40ea1315aa3790304db4fdfdd8a5b460507e5","crop":[100,160,900,960],"output_sha256":"1836ffdf9e9bdfd0451710c8a13d6145920c4a81e95cd3c7681627bec0beee5d"},{"name":"CEHPPRO3838FPK_manufacturer_03.jpg","source":"https://craftexpress24.eu/hpeciai/785ee78ccef0d264d4d62e854a95a67c/eng_pl_Craft-Express-Manual-Flat-Press-38-x-38-cm-Pink-61_4.jpg","source_sha256":"6b33673ff5334226e480419bec6224bc838bc6a246965a2f5a9df82721ace79e","crop":[80,160,880,960],"output_sha256":"9af92e95d0a7d123744c46bff4190e083bcea4e3deb02674384984f61a2f0d16"},{"name":"CEHPPRO3838FPK_manufacturer_04.jpg","source":"https://craftexpress24.eu/hpeciai/cfbff471f791829f0eb84739bebe5673/eng_pl_Craft-Express-Manual-Flat-Press-38-x-38-cm-Pink-61_8.jpg","source_sha256":"a45e1cedc03e9dd29770a9ffcab7ee50171de74020d0dfb67f460499073ad7e8","crop":[100,160,900,960],"output_sha256":"6551cd05d05a19f1efeb5dafa567e4e0dd241bd23e1de43605201157e4a446f9"},{"name":"CEHPPRO3838FPK_manufacturer_05.jpg","source":"https://craftexpress24.eu/hpeciai/e5ac2e86771e1fad63fe216cc2eb95a2/eng_pl_Craft-Express-Manual-Flat-Press-38-x-38-cm-Pink-61_14.jpg","source_sha256":"09782e6d0975d90fae416af76218394c32224dc185ec7cccf8af6216afdddc6b","crop":[100,160,900,960],"output_sha256":"9aa0dec3b90a923191ec82cc1fac940c044344e752954993a106bcff0a1d6b94"},{"name":"CEHPPRO3838FPK_manufacturer_06.jpg","source":"https://craftexpress24.eu/hpeciai/9c05dea0ddfed3b2d0584d1e3217366e/eng_pl_Craft-Express-Manual-Flat-Press-38-x-38-cm-Pink-61_2.jpg","source_sha256":"60beba9b851c7d2cc2af39eaca718d7e089b922260f14261c4d9a9b62ca1eee8","crop":None,"output_sha256":"60beba9b851c7d2cc2af39eaca718d7e089b922260f14261c4d9a9b62ca1eee8"},{"name":"CEHPPRO3838FPK_manufacturer_07.jpg","source":"https://craftexpress24.eu/hpeciai/105a5bbed055bfbff40c317d811a3e64/eng_pl_Craft-Express-Manual-Flat-Press-38-x-38-cm-Pink-61_3.jpg","source_sha256":"7add3cd5433a9e0203096b86ede0746ff8cda53d4e938eddde1ca0df4d9d4ab3","crop":None,"output_sha256":"7add3cd5433a9e0203096b86ede0746ff8cda53d4e938eddde1ca0df4d9d4ab3"},{"name":"CEHPPRO3838FPK_manufacturer_08.jpg","source":"https://craftexpress24.eu/hpeciai/ae9451eb01bf134bccd7b4e90177c8b9/eng_pl_Craft-Express-Manual-Flat-Press-38-x-38-cm-Pink-61_5.jpg","source_sha256":"ab4b86f103355a72c5462ab8169c24c26586c8aa5c0b2d5ad7991b51df143f52","crop":None,"output_sha256":"ab4b86f103355a72c5462ab8169c24c26586c8aa5c0b2d5ad7991b51df143f52"},{"name":"CEHPPRO3838FPK_manufacturer_09.jpg","source":"https://craftexpress24.eu/hpeciai/ad992cf54c46d3bf2caf088472ee72d5/eng_pl_Craft-Express-Manual-Flat-Press-38-x-38-cm-Pink-61_6.jpg","source_sha256":"22cbda055fc54a5dde86ec1b509e81729418c1b02d12266c0b6c623b4b55a1e9","crop":None,"output_sha256":"22cbda055fc54a5dde86ec1b509e81729418c1b02d12266c0b6c623b4b55a1e9"},{"name":"CEHPPRO3838FPK_manufacturer_10.jpg","source":"https://craftexpress24.eu/hpeciai/f413415b5b0be88a298fa75945d1137a/eng_pl_Craft-Express-Manual-Flat-Press-38-x-38-cm-Pink-61_7.jpg","source_sha256":"ffc9cbf7809a8534ed38916a33171f0f2a2facf88932a18d4771bd6b91fea919","crop":None,"output_sha256":"ffc9cbf7809a8534ed38916a33171f0f2a2facf88932a18d4771bd6b91fea919"},{"name":"CEHPPRO3838FPK_manufacturer_11.jpg","source":"https://craftexpress24.eu/hpeciai/39ad225092e024a99235ba73dbc71bcb/eng_pl_Craft-Express-Manual-Flat-Press-38-x-38-cm-Pink-61_9.jpg","source_sha256":"c85164971ffbbcafcfe60ddd9b639482bb7a6d288726ffa943c8a1d36058e9a4","crop":None,"output_sha256":"c85164971ffbbcafcfe60ddd9b639482bb7a6d288726ffa943c8a1d36058e9a4"},{"name":"CEHPPRO3838FPK_manufacturer_12.jpg","source":"https://craftexpress24.eu/hpeciai/ebeee49b8807276b92b88ebeef939203/eng_pl_Craft-Express-Manual-Flat-Press-38-x-38-cm-Pink-61_11.jpg","source_sha256":"a84e53d1962ef4e27e9c07771ab655431fe517bd442839454393de50f6b34320","crop":None,"output_sha256":"a84e53d1962ef4e27e9c07771ab655431fe517bd442839454393de50f6b34320"},{"name":"CEHPPRO3838FPK_manufacturer_13.jpg","source":"https://craftexpress24.eu/hpeciai/be9c2e235e8ec6c10efa2f988465dc9b/eng_pl_Craft-Express-Manual-Flat-Press-38-x-38-cm-Pink-61_12.jpg","source_sha256":"98af5a8b1c010f0e53582085cee59ba495720812d2067a02c4a78de915c2f3ae","crop":None,"output_sha256":"98af5a8b1c010f0e53582085cee59ba495720812d2067a02c4a78de915c2f3ae"},{"name":"CEHPPRO3838FPK_manufacturer_14.jpg","source":"https://craftexpress24.eu/hpeciai/5eac4e31128e1645282e2651e11784c8/eng_pl_Craft-Express-Manual-Flat-Press-38-x-38-cm-Pink-61_13.jpg","source_sha256":"54aab9894ca255a5fd1400d329b503c652c3b194da9a259c211348dc2869037a","crop":None,"output_sha256":"54aab9894ca255a5fd1400d329b503c652c3b194da9a259c211348dc2869037a"},{"name":"CEHPPRO3838FPK_manufacturer_15.jpg","source":"https://craftexpress24.eu/hpeciai/fabfeb1b8ec3ec906cd6811eaaf0da06/eng_pl_Craft-Express-Manual-Flat-Press-38-x-38-cm-Pink-61_15.jpg","source_sha256":"9c4509a620e1a2d796cae2d2e85b99f3295aea6fb163dccf452c3bc68c85e637","crop":None,"output_sha256":"9c4509a620e1a2d796cae2d2e85b99f3295aea6fb163dccf452c3bc68c85e637"}]
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
    assert im.size==(1000,1000)
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
            print('CEHPPRO3838FPK_FTP_HTTPS_VERIFIED',name,len(body),entry['output_sha256'],flush=True)
            break
        except Exception:
            if attempt==4: raise
            time.sleep(3)

print('CEHPPRO3838FPK VERIFIED: 15 unique photographs, 5 native crops, 10 untouched originals',flush=True)
