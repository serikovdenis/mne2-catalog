#!/usr/bin/env python3
"""Stage exact-model Fulei supplier photographs. No production catalog changes."""
import csv, io, json, re, urllib.request
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urljoin, urlparse
from PIL import Image

ROOT=Path(__file__).resolve().parent.parent
OUT=ROOT/"reports"/"fulei-supplier-photo-candidates"
OUT.mkdir(parents=True,exist_ok=True)
MANIFEST=ROOT/"reports"/"avito-photo-candidates-2026-10-10.json"
LISTING="https://intamarketgraphics.co.za/product-category/printers-equipment/"
HEADERS={"User-Agent":"Mozilla/5.0 (compatible; MNE2PhotoAudit/1.0)","Accept":"text/html,image/*"}
MAX_BYTES=15*1024*1024

class Tags(HTMLParser):
    def __init__(self):
        super().__init__();self.links=[];self.meta={};self.images=[]
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if tag=="a" and a.get("href"):self.links.append(a["href"])
        if tag=="meta" and a.get("content"):
            key=a.get("property") or a.get("name")
            if key:self.meta[key]=a["content"]
        if tag=="img":self.images.append(a)

def get(url):
    with urllib.request.urlopen(urllib.request.Request(url,headers=HEADERS),timeout=22) as r:
        data=r.read(MAX_BYTES+1)
        if len(data)>MAX_BYTES:raise ValueError("Response exceeds 15 MB")
        return data

def parse(url):
    parser=Tags();parser.feed(get(url).decode("utf-8","replace"));return parser

def norm(value):return re.sub(r"[^A-Z0-9]","",value.upper())
def product_urls(page):
    return sorted({urljoin(LISTING,u).split("?")[0] for u in page.links if "/product/" in urljoin(LISTING,u) and urlparse(urljoin(LISTING,u)).hostname=="intamarketgraphics.co.za"})

def main():
    products=json.loads(MANIFEST.read_text(encoding="utf-8"))["products"]
    targets={norm(p["sku"]):p["sku"] for p in products if p["brand"]=="Fulei"}
    rows=[];found=set()
    for category in [
        "https://intamarketgraphics.co.za/product-category/equipment/heat-press/",
        "https://intamarketgraphics.co.za/product-category/printers-equipment/heat-press/",
        "https://intamarketgraphics.co.za/product-category/equipment/laminators/",
    ]:
        try: links=product_urls(parse(category))
        except Exception as e:
            rows.append({"sku":"","product_url":category,"image_url":"","width":"","height":"","file":"","status":"listing_error","note":str(e)[:180]});continue
        for link in links:
            # Only Fulei product links, do not fetch unrelated products.
            if "fulei" not in link.lower():continue
            try:
                p=parse(link)
                title=p.meta.get("og:title","")
                slug=norm(urlparse(link).path.split("/product/")[-1])
                title_norm=norm(title)
                matches=[(key,sku) for key,sku in targets.items() if key in slug or key in title_norm]
                if len(matches)!=1:continue
                sku=matches[0][1]
                if sku in found:continue
                found.add(sku)
                candidates=[]
                if p.meta.get("og:image"):candidates.append(p.meta["og:image"])
                for im in p.images:
                    for field in ("data-large_image","data-src","src"):
                        u=im.get(field,"")
                        if u and ("wp-content/uploads/" in u or "fulei" in u.lower()):
                            candidates.append(urljoin(link,u))
                candidates=list(dict.fromkeys(candidates))[:12]
                best=None;errors=[]
                for u in candidates:
                    try:
                        data=get(u);image=Image.open(io.BytesIO(data));image.load()
                        if image.format not in ("JPEG","PNG","WEBP") or min(image.size)<300:continue
                        if best is None or image.width*image.height>best[1].width*best[1].height:
                            best=(u,image,data)
                    except Exception as exc:errors.append(str(exc)[:100])
                if best:
                    u,image,data=best
                    ext={"JPEG":"jpg","PNG":"png","WEBP":"webp"}[image.format]
                    name=re.sub("[^A-Za-z0-9_-]","_",sku)+"_supplier."+ext
                    (OUT/name).write_bytes(data)
                    status="needs_visual_review" if max(image.size)>=1000 else "low_resolution_do_not_replace"
                    rows.append({"sku":sku,"product_url":link,"image_url":u,"width":image.width,"height":image.height,"file":name,"status":status,"note":"Exact model in supplier product title/slug; compare visually before replacement"})
                else:
                    rows.append({"sku":sku,"product_url":link,"image_url":"","width":"","height":"","file":"","status":"no_usable_image","note":" | ".join(errors[:2])})
            except Exception as exc:
                rows.append({"sku":"","product_url":link,"image_url":"","width":"","height":"","file":"","status":"product_error","note":str(exc)[:180]})
    fields=["sku","product_url","image_url","width","height","file","status","note"]
    with (OUT/"audit.csv").open("w",newline="",encoding="utf-8-sig") as f:
        writer=csv.DictWriter(f,fieldnames=fields);writer.writeheader();writer.writerows(rows)
    statuses={}
    for r in rows:statuses[r["status"]]=statuses.get(r["status"],0)+1
    summary={"source":"Intamarket Graphics product pages","matched_models":len(found),"status_counts":statuses,"no_catalog_changes":True}
    (OUT/"summary.json").write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding="utf-8")
    print(json.dumps(summary,ensure_ascii=False))
if __name__=="__main__":main()
