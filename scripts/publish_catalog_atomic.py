"""Publish a complete catalog snapshot without exposing partially uploaded files."""
import ftplib,hashlib,io,json,os,re,sys,time
from pathlib import Path

def public_record(row):
    # Confidential supplier data stays in private source files, never in public JSON.
    def blocked(key):
        return key in {'price_source','price_status','needs_review'} or bool(re.search(r'factory_price|purchase|procurement|cost_price|price_cny|price_usd|price_rmb|markup|margin|formula|exchange_rate',key,re.I))
    if isinstance(row,dict):return {k:public_record(v) for k,v in row.items() if not blocked(k)}
    if isinstance(row,list):return [public_record(v) for v in row]
    return row

def prepare(root):
    records=[]
    for n in range(1,5):
        path=root/'data'/f'part{n}.json'
        rows=public_record(json.loads(path.read_text(encoding='utf-8')))
        path.write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        records+=rows
    assert records and len({r['sku'] for r in records})==len(records)
    html=(root/'index.html').read_text(encoding='utf-8')
    payload=json.dumps(records,ensure_ascii=False,separators=(',',':')).replace('<','\\u003c')
    pattern=r'(<script id="catalogBootstrap" type="application/json">)[\s\S]*?(</script>)'
    html,count=re.subn(pattern,lambda m:m[1]+payload+m[2],html,count=1)
    assert count==1,'Missing embedded catalog snapshot'
    (root/'index.html').write_text(html,encoding='utf-8')
    print('COMPLETE_CATALOG_SNAPSHOT',len(records),flush=True)
    return records

def read(ftp,name):
    out=io.BytesIO();ftp.retrbinary('RETR '+name,out.write);return out.getvalue()

def publish(ftp,name,body,run):
    try:
        if read(ftp,name)==body:
            print('UNCHANGED_SKIPPED',name,flush=True);return
    except ftplib.error_perm as e:
        if not str(e).startswith('550'):raise
    temp='.'+name+'.upload-'+run
    ftp.storbinary('STOR '+temp,io.BytesIO(body))
    assert hashlib.sha256(read(ftp,temp)).digest()==hashlib.sha256(body).digest(),'Incomplete FTP upload'
    # Rename only after the entire temporary file is verified. Never truncate live files.
    ftp.rename(temp,name)
    assert read(ftp,name)==body
    print('ATOMIC_CATALOG_PUBLISHED',name,flush=True)

def main(root):
    prepare(root)
    for relative in [f'data/part{n}.json' for n in range(1,5)]+['index.html']:
        for attempt in range(5):
            ftp=None
            try:
                ftp=ftplib.FTP('p1057897.ftp.ihc.ru',timeout=40)
                ftp.login('p1057897_chatgpt',os.environ['FTP_PASSWORD'])
                ftp.cwd('www/mne2.ru/catalog')
                if '/' in relative:ftp.cwd(relative.rsplit('/',1)[0])
                publish(ftp,relative.rsplit('/',1)[-1],(root/relative).read_bytes(),os.environ.get('GITHUB_RUN_ID','manual'))
                break
            except Exception as e:
                print('CATALOG_RETRY',relative,attempt+1,repr(e),flush=True)
                if attempt==4:raise
                time.sleep(3)
            finally:
                if ftp:ftp.close()
if __name__=='__main__':main(Path(sys.argv[1] if len(sys.argv)>1 else 'catalog'))
