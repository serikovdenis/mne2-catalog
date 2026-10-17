"""Publish two reviewed exact-model OT-DQSPBY4060LB photographs with native-pixel crops."""
import ftplib, hashlib, io, os, subprocess, time
from PIL import Image
MANIFEST = [{"name":"OT-DQSPBY4060LB_manufacturer90_01.jpg","source":"https://www.bestsub.com/media/k2/galleries/27540/OT-DQSPBY4060LB.jpg","source_sha256":"13a841e3add8b40215ed9daec199af80a684417354799000411b9a7b37a5f0d1","crop":[177,77,622,522],"output_sha256":"a24f2a9ff6d74329fb97ef05a8cb7573d4d3d2e92c79ee2ac5533878d9b095b6"},{"name":"OT-DQSPBY4060LB_manufacturer90_02.jpg","source":"https://www.bestsub.com/media/k2/galleries/27540/OT-DQSPBY4060LB_1.jpg","source_sha256":"ddeb274180ec5e92291d72acf7c8b668dccfbed4f4b311df57d698256d096a63","crop":[178,78,623,523],"output_sha256":"2d40aedc4e5dd388f44500ce58cf680a22db676cc1df2a8e5839c44981db38c1"},{"name":"OT-DQSPBY4060LB_manufacturer90_03.jpg","source":"https://www.bestsub.com/media/k2/galleries/27540/OT-DQSPBY4060LB_2.jpg","source_sha256":"040f2a97cb5aad58ef8ae0646c8b02badd7b597ea87ccdf41af964361bdc4f65","crop":[154,54,646,546],"output_sha256":"c0889556a14abf3d99702a5ac208977fefa129113a4ab429ce9559a680de9c9d"},{"name":"OT-DQSPBY4060LB_manufacturer90_04.jpg","source":"https://www.bestsub.com/media/k2/galleries/27540/OT-DQSPBY4060LB_3.jpg","source_sha256":"57e3218bcfea2f679eb9ac85ba9db512b589e079c27b146c93fe9b8f6c1d3ef9","crop":[177,77,622,522],"output_sha256":"cc3e6607d8f9798a609d2c50d44929fd0d0f7f155806a379eb42c0e7e1b08364"},{"name":"OT-DQSPBY4060LB_manufacturer90_05.jpg","source":"https://www.bestsub.com/media/k2/galleries/27540/OT-DQSPBY4060LB_4.jpg","source_sha256":"e2dd9111513e68a42ee58933e4091f0b93cd72fdd66741b84a030b5a66cce54a","crop":[177,77,622,522],"output_sha256":"96e2cf1b7dedd758011b6a4a098daa8211da1e1ed126a0acea66eabde4892f28"},{"name":"OT-DQSPBY4060LB_manufacturer90_06.jpg","source":"https://www.bestsub.com/media/k2/galleries/27540/OT-DQSPBY4060LB_5.jpg","source_sha256":"2feed9ac95fe6f0457da6ff1d7b06315a9b23c26dfd77db0f2890fa098d30fa4","crop":[177,77,622,522],"output_sha256":"cdb6f541f70be6d172d4da692ca50c84b8c7e2a002cd364bff33f9cf31dcb372"}]
# BestSub gallery 24410: open and closed OT-DQSPBY4060LB, 800x600 originals.
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
            print('OT-DQSPBY4060LB_FTP_HTTPS_VERIFIED',name,len(body),entry['output_sha256'],flush=True)
            break
        except Exception:
            if attempt==4: raise
            time.sleep(3)

print('Seven unique photographs: six native crops and one preserved original')
