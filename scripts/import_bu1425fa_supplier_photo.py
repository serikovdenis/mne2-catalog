#!/usr/bin/env python3
"""Import a manufacturer-model-specific supplier photo into the MNE2 site tree.
Run from the site repository root. No fuzzy model substitution.
"""
import csv, io, json, re, sys, urllib.request
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urljoin, urlparse, unquote
from PIL import Image, ImageStat

SKU="BU-1425FA"
PAGE="https://www.kelingraphics.com/blogs-flatbed-laminator/"
ROOT=Path(".")
OUT=ROOT/"reports"/"supplier-photo-import-bu1425fa.json"
OUT.parent.mkdir(exist_ok=True)
DEST=ROOT/"site"/"catalog"/"images"/"external"
DEST.mkdir(parents=True,exist_ok=True)
HEADERS={"User-Agent":"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/120 Safari/537.36","Accept":"image/avif,image/webp,image/png,image/jpeg,text/html,*/*"}

class Photos(HTMLParser):
    def __init__(self):super().__init__();self.candidates=[];self.meta={}
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if tag=="meta":
            key=a.get("property") or a.get("name")
            if key:self.meta[key]=a.get("content","")
        if tag=="img":
            alt=a.get("alt","")
            for field in ("data-src","data-lazy-src","src"):
                u=a.get(field)
                if u:self.candidates.append((u,alt))
def norm(s):return re.sub(r"[^A-Z0-9]","",s.upper())
def fetch(u):
    req=urllib.request.Request(u,headers=HEADERS)
    with urllib.request.urlopen(req,timeout=22) as resp:
        blob=resp.read(16*1024*1024+1)
    if len(blob)>16*1024*1024:raise ValueError("oversize")
    return blob
def report(data):
    OUT.write_text(json.dumps(data,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(data,ensure_ascii=False))
def main():
    result={"sku":SKU,"source_page":PAGE,"status":"not_imported","published":False}
    try:
        p=Photos();p.feed(fetch(PAGE).decode("utf-8","replace"))
        if norm(SKU) not in norm(p.meta.get("og:title","")+" "+p.meta.get("description","")):
            # The verified blog title must still refer to this exact model.
            raise ValueError("Source title does not confirm exact SKU")
        candidates=p.candidates
        if p.meta.get("og:image"):candidates.insert(0,(p.meta["og:image"],p.meta.get("og:title","")))
        choices=[];errors=[]
        for url,alt in candidates:
            u=urljoin(PAGE,url)
            if urlparse(u).hostname not in ("www.kelingraphics.com","kelingraphics.com"):continue
            # Demand explicit model in image filename or image alt; no generic stock photos.
            if norm(SKU) not in norm(unquote(urlparse(u).path).split("/")[-1]) and norm(SKU) not in norm(alt):continue
            try:
                blob=fetch(u)
                im=Image.open(io.BytesIO(blob));im.load()
                if im.format not in ("PNG","JPEG","WEBP") or min(im.size)<1000:continue
                if max(ImageStat.Stat(im.convert("RGB").resize((160,160))).stddev)<18:continue
                choices.append((im.width*im.height,im.width,im.height,im.format,u,blob))
            except Exception as e:errors.append(str(e)[:110])
        if not choices:
            result.update(status="no_qualified_high_resolution_image",candidate_count=len(candidates),errors=errors[:3])
            report(result);return
        choices.sort(reverse=True)
        _,w,h,fmt,u,blob=choices[0]
        ext={"PNG":"png","JPEG":"jpg","WEBP":"webp"}[fmt]
        file=DEST/f"{SKU}_kelin.{ext}"
        urls={}
        modified=False
        for part in sorted((ROOT/"site"/"catalog"/"data").glob("part*.json")):
            rows=json.loads(part.read_text(encoding="utf-8"))
            for row in rows:
                if row.get("sku")!=SKU:continue
                if row.get("brand")!="Fulei":raise ValueError("Unexpected brand")
                old=row.get("image","")
                if "avito.ru/autoload/" not in old:
                    result.update(status="already_has_non_avito_image",current_image=old)
                    report(result);return
                file.write_bytes(blob)
                new=f"https://mne2.ru/catalog/images/external/{file.name}"
                row["image"]=new
                row["images"]=[new]+[x for x in row.get("images",[]) if x!=old and x!=new]
                part.write_text(json.dumps(rows,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
                modified=True
                result.update(status="published_to_site_source",published=True,image=new,width=w,height=h,source_image=u)
                break
            if modified:break
        if not modified:raise ValueError("SKU not found in site catalog")
    except Exception as e:result.update(status="error",error=str(e)[:240])
    report(result)
if __name__=="__main__":main()
