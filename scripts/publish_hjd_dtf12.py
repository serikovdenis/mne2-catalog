import ftplib,io,json,os,re,hashlib,time,urllib.request
from pathlib import Path
root=Path('imports/hjd-dtf12');r=json.loads((root/'product.json').read_text());sku=r['sku']
ftp=ftplib.FTP_TLS('p1057897.ftp.ihc.ru',timeout=90);ftp.login('p1057897_chatgpt',os.environ['FTP_PASSWORD']);ftp.prot_p();ftp.cwd('www/mne2.ru/catalog')
def read(name):
 b=io.BytesIO();ftp.retrbinary('RETR '+name,b.write);return b.getvalue()
def publish(name,body):
 try:
  if read(name)==body:print('UNCHANGED',name);return
 except ftplib.error_perm as e:
  if not str(e).startswith('550'):raise
 temp=name+'.hjd-upload';ftp.storbinary('STOR '+temp,io.BytesIO(body));assert read(temp)==body;ftp.rename(temp,name);assert read(name)==body;print('VERIFIED',name,len(body),flush=True)
# Read production first. Keep every existing product field, order and other data parts.
parts={f'data/part{i}.json':read(f'data/part{i}.json') for i in range(1,5)}
allrows=sum([json.loads(v) for v in parts.values()],[]);matches=[x for x in allrows if x['sku']==sku];assert not matches or matches==[r],'Conflicting existing SKU; abort'
assert not [x for x in allrows if x['sku']!=sku and (x.get('model')=='DTF-12' or 'HJD DTF-12' in x.get('title',''))],'Duplicate model'
old=read('index.html').decode();pat=r'(<script id="catalogBootstrap" type="application/json">)(.*?)(</script>)';m=re.search(pat,old,re.S);assert m
snapshot=json.loads(m[2]);assert not any(x['sku']==sku and x!=r for x in snapshot)
if not any(x['sku']==sku for x in snapshot):snapshot.append(r)
new=re.sub(pat,lambda m:m[1]+json.dumps(snapshot,ensure_ascii=False,separators=(',',':')).replace('<','\\u003c')+m[3],old,count=1,flags=re.S)
media=(root/'media.txt').read_text();anchor="+'<h2>'+cost+'</h2>'"
if media not in new:assert new.count(anchor)==1;new=new.replace(anchor,media+anchor,1)
for directory in ['images','images/'+sku]:
 try:ftp.mkd(directory)
 except ftplib.error_perm:pass
for name in ['11.jpg','12.jpg','1.png','2.png','13.png','specification.docx']:publish('images/'+sku+'/'+name,(root/name).read_bytes())
video=b''.join(p.read_bytes() for p in sorted(root.glob('video.part*')));assert len(video)==19422733;publish('images/'+sku+'/video.mp4',video)
if not matches:
 rows=json.loads(parts['data/part4.json']);rows.append(r);publish('data/part4.json',(json.dumps(rows,ensure_ascii=False,indent=2)+'\n').encode())
publish('index.html',new.encode())
for n in range(1,4):assert read(f'data/part{n}.json')==parts[f'data/part{n}.json']
after=sum([json.loads(read(f'data/part{i}.json')) for i in range(1,5)],[])
assert [x for x in after if x['sku']!=sku]==[x for x in allrows if x['sku']!=sku]
assert len([x for x in after if x['sku']==sku])==1
ftp.quit()
for path in ['data/part4.json','index.html','images/'+sku+'/video.mp4','images/'+sku+'/specification.docx']:
 req=urllib.request.Request('https://mne2.ru/catalog/'+path+'?hjd_check='+str(time.time()),headers={'User-Agent':'MNE2-single-product-check'})
 with urllib.request.urlopen(req,timeout=60) as resp:
  assert resp.status==200
  if path=='data/part4.json':assert [x for x in json.load(resp) if x['sku']==sku]==[r]
  elif path=='index.html':assert sku.encode() in resp.read()
 print('LIVE_OK',path,flush=True)
print('SUCCESS: one new product; all existing products unchanged. https://mne2.ru/catalog/?sku='+sku)
