"""Publish seven reviewed native white-background crops for four mug press cards."""
import ftplib, hashlib, io, os, subprocess, time
from PIL import Image
MANIFEST = [{"name":"OU-AUMP8MB_original90_01.jpg","source":"https://www.bestsub.com/media/k2/galleries/27526/OU-AUMP8MB.webp","crop":[67,77,734,522],"source_sha256":"3fc5b97ec98c732062ecfaa9b08ee35dc20635747b7491ea4a77d9d29919635c","output_sha256":"dca2d11f9bd9ee045602d1ec7b56fd2d475bcb19993437161456158c753bea75"},{"name":"OU-AUMP8MB_original90_02.jpg","source":"https://www.bestsub.com/media/k2/galleries/27526/OU-AUMP8MB_1.webp","crop":[67,77,734,522],"source_sha256":"b7b2c638a013d210ff9f099074af9ecd3d637285c49229d06688b0a027cd3655","output_sha256":"b8da0a32891782b9090e9b25157eb95a1ed94ff0bf5cdaaef4873aef993e82f9"},{"name":"OU-AUMP8MB_original90_03.jpg","source":"https://www.bestsub.com/media/k2/galleries/27526/OU-AUMP8MB_2.webp","crop":[67,77,734,522],"source_sha256":"9f3e50a8f162e7d511025455bc0f5b038c05ad92fd7ce96c85f09d7dcfac4718","output_sha256":"1c141817fb8502453d6d0694013c94c35072a69b93acdc099278b39a646caf27"},{"name":"OU-AUMP8MB_original90_04.jpg","source":"https://www.bestsub.com/media/k2/galleries/27526/OU-AUMP8MB_3.webp","crop":[66,77,733,522],"source_sha256":"b6c283d5c319051e2c9bd0f6028d204571f7e96fabce02877f101565365ec626","output_sha256":"79ad66149a16bee7c4f141417b18b60b9b7ff69b862bd10f103e2c5913bcdffe"},{"name":"OU-AUMP8MB_original90_05.jpg","source":"https://www.bestsub.com/media/k2/galleries/27526/OU-AUMP8MB_4.webp","crop":[172,71,629,528],"source_sha256":"4eeac1576d54a1a38b6dd6a7a853ccea344450488d19d09b697d54ddbe43b31b","output_sha256":"c00650ab090d9817f14aa0782af1c7a3a27f9254bab57d6cf5a7b28152bc8c37"},{"name":"OT-KYJ30LB_original90_01.jpg","source":"https://www.bestsub.com/media/k2/galleries/25263/OT-KYJ30LB_1.webp","crop":[178,78,621,521],"source_sha256":"e080e2dd8222ba5d646325ea7b33cbc81d6d9faf67b82f4a61b504bb61a21f69","output_sha256":"8d70a5468f55a091a56857c44bc9db541fd3b86fab413b6677a98b8bf52c473c"},{"name":"BHPB18_original90_01.jpg","source":"https://www.bestsub.com/media/k2/galleries/27545/BHPB18.jpg","crop":[101,0,698,600],"source_sha256":"e8e2340259b62eb36f3e650aecc00d44c7c7e8201f91588284bdd0bf08e2ed07","output_sha256":"71c2d5cc72e1032f49cf1932b4a3d2eb0095e2f2cbe2b25dff3ff73d77924386"}]
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
            print('MUG_FOUR_CARDS_FTP_HTTPS_VERIFIED',name,len(body),entry['output_sha256'],flush=True)
            break
        except Exception:
            if attempt==4: raise
            time.sleep(3)

print('MUG_FOUR_CARDS VERIFIED: 7 native crops for 4 cards, no upscaling',flush=True)
