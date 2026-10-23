"""Prepare a reviewed BestSub SKU without credentials or FTP writes."""
import argparse, hashlib, json, re, urllib.parse, urllib.request
from pathlib import Path
from html.parser import HTMLParser

class Gallery(HTMLParser):
    def __init__(self):
        super().__init__()
        self.images = []
    def handle_starttag(self, tag, attrs):
        if tag != "img": return
        src = dict(attrs).get("src", "")
        if "/media/k2/galleries/" in src: self.images.append(src)

def get(url):
    req=urllib.request.Request(url,headers={"User-Agent":"MNE2-Reviewed-Prepare/1.0"})
    with urllib.request.urlopen(req,timeout=60) as r: return r.read()

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--sku",required=True)
    args=p.parse_args()
    sku=args.sku
    assert re.fullmatch(r"[A-Za-z0-9_-]+",sku)
    matches=[]
    for path in sorted(Path("data").glob("part*.json")):
        for row in json.loads(path.read_text(encoding="utf-8")):
            if row.get("sku")==sku: matches.append((path.name,row))
    assert len(matches)==1, "SKU must appear exactly once"
    part,row=matches[0]
    page=row["source_url"]
    assert urllib.parse.urlsplit(page).hostname=="www.bestsub.com"
    expected=row["source_images"]
    assert expected and len(expected)==len(row["images"])
    parser=Gallery()
    parser.feed(get(page).decode("utf-8","replace"))
    gallery=list(dict.fromkeys(urllib.parse.urljoin(page,u) for u in parser.images))
    if row.get("source_gallery_scope")=="exact_sku":
        gallery=[u for u in gallery if re.match(re.escape(sku)+r"(?:[_.])",u.rsplit("/",1)[1],re.I)]
    assert gallery==expected, "Manufacturer gallery changed: abort"
    out=Path("prepared")/sku
    out.mkdir(parents=True,exist_ok=True)
    files=[]
    for source,live in zip(expected,row["images"]):
        assert urllib.parse.urlsplit(source).hostname=="www.bestsub.com"
        assert live.startswith("https://mne2.ru/catalog/images/bestsub/"+sku+"/")
        name=source.rsplit("/",1)[1]
        assert name==live.rsplit("/",1)[1] and re.fullmatch(r"[A-Za-z0-9_.-]+",name)
        blob=get(source)
        assert len(blob)>1000
        (out/name).write_bytes(blob)
        files.append({"name":name,"source":source,"live":live,"sha256":hashlib.sha256(blob).hexdigest(),"bytes":len(blob)})
    manifest={"sku":sku,"part":part,"files":files,"catalog_prices_untouched":True}
    (out/"manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding="utf-8")
    print("PREPARED",sku,len(files),"original files; no FTP writes")

if __name__=="__main__": main()
