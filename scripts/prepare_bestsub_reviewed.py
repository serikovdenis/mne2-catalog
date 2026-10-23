"""Prepare a reviewed BestSub SKU without credentials or FTP writes."""
import argparse, hashlib, json, re, urllib.parse, urllib.request
from pathlib import Path
from bs4 import BeautifulSoup
from PIL import Image
import io

def get(url):
    req=urllib.request.Request(url,headers={"User-Agent":"MNE2-Reviewed-Prepare/1.0"})
    with urllib.request.urlopen(req,timeout=60) as r: return r.read()

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--sku",required=True)
    p.add_argument("--zip",action="store_true",help="Create local ZIP with SKU/ folder for offline publisher")
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
    assert row["image"]==row["images"][0]
    assert row.get("description") and row.get("specifications")
    soup=BeautifulSoup(get(page),"html.parser")
    gallery=list(dict.fromkeys(urllib.parse.urljoin(page,i.get("src","")) for i in soup.select("img[src]") if "/media/k2/galleries/" in i["src"]))
    if row.get("source_gallery_scope")=="exact_sku":
        gallery=[u for u in gallery if re.match(re.escape(sku)+r"(?:[_.])",u.rsplit("/",1)[1],re.I)]
    assert gallery==expected, "Manufacturer gallery changed: abort"
    assert len(set(expected))==len(expected), "Duplicate source URLs"
    assert len(set(row["images"]))==len(row["images"]), "Duplicate live URLs"
    out=Path("prepared")/sku
    out.mkdir(parents=True,exist_ok=True)
    files=[]
    for source,live in zip(expected,row["images"]):
        assert urllib.parse.urlsplit(source).hostname=="www.bestsub.com"
        assert live.startswith("https://mne2.ru/catalog/images/bestsub/"+sku+"/")
        name=source.rsplit("/",1)[1]
        assert name==live.rsplit("/",1)[1] and re.fullmatch(r"[A-Za-z0-9_.-]+",name)
        assert name not in {entry["name"] for entry in files}, "Duplicate destination filename"
        blob=get(source)
        assert len(blob)>1000
        image=Image.open(io.BytesIO(blob))
        image.verify()
        (out/name).write_bytes(blob)
        files.append({"name":name,"source":source,"live":live,"sha256":hashlib.sha256(blob).hexdigest(),"bytes":len(blob)})
    manifest={"sku":sku,"part":part,"files":files,"catalog_prices_untouched":True}
    (out/"manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding="utf-8")
    if args.zip:
        import zipfile
        archive=Path("prepared")/(sku+".zip")
        with zipfile.ZipFile(archive,"w",compression=zipfile.ZIP_DEFLATED) as z:
            for item in files:
                z.write(out/item["name"],arcname=sku+"/"+item["name"])
            z.write(out/"manifest.json",arcname=sku+"/manifest.json")
        print("LOCAL ARCHIVE",archive)
    print("PREPARED",sku,len(files),"original files; no FTP writes")

if __name__=="__main__": main()
