#!/usr/bin/env python3
"""Download Avito candidates from owner's spreadsheet, compare quality, stage only.

This NEVER changes production catalog image URLs.
"""
import csv, io, json, re, time, urllib.request, urllib.error
from pathlib import Path
from urllib.parse import urlparse
from PIL import Image, ImageFilter, ImageStat

ROOT=Path(__file__).resolve().parent.parent
MANIFEST=ROOT/"reports/avito-photo-candidates-2026-10-10.json"
OUT=ROOT/"reports/avito-photo-review"
OUT.mkdir(parents=True,exist_ok=True)
MAX_BYTES=24*1024*1024
HEADERS={"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36","Accept":"image/avif,image/webp,image/apng,image/*,*/*;q=0.8","Accept-Language":"ru-RU,ru;q=0.9,en-US;q=0.8"}

def variants(url):
    urls=[url]
    p=urlparse(url)
    if p.hostname and "avito.ru" in p.hostname:
        path=p.path
        query=("?"+p.query) if p.query else ""
        for host in ["www.avito.ru","avito.ru"]:
            urls.append("https://"+host+path+query)
        slug=re.search(r"(?:imageSlug=)(/image/1/1\.[^&]+)",url)
        if slug:
            suffix=slug.group(1)
            for host in ["a.cdn.avito.ru","images.avito.ru","img.avito.st"]:
                urls.append("https://"+host+suffix)
    return list(dict.fromkeys(urls))

def get(url):
    req=urllib.request.Request(url,headers=HEADERS)
    with urllib.request.urlopen(req,timeout=17) as resp:
        blob=resp.read(MAX_BYTES+1)
    if len(blob)>MAX_BYTES:raise ValueError("oversize")
    im=Image.open(io.BytesIO(blob))
    im.load()
    if im.width<120 or im.height<120:raise ValueError("thumbnail")
    if im.format not in ("JPEG","PNG","WEBP"):raise ValueError("invalid image")
    return blob,im

def sharpness(im):
    g=im.convert("L")
    g.thumbnail((1000,1000))
    return round(ImageStat.Stat(g.filter(ImageFilter.FIND_EDGES)).var[0],2)

def quality(im):
    return {"width":im.width,"height":im.height,"pixels":im.width*im.height,"sharpness":sharpness(im),"format":im.format}

def fetch_one(urls):
    errors=[]
    for u in urls:
        try:
            b,im=get(u)
            return b,im,u
        except Exception as exc:
            errors.append(type(exc).__name__+":"+str(exc)[:90])
    raise RuntimeError(" | ".join(errors[:3]))

def main():
    data=json.loads(MANIFEST.read_text(encoding="utf-8"))
    rows=[]
    for p in data["products"]:
        sku=p["sku"]
        old_quality=None
        old_url=None
        for u in p.get("existing_catalog_images",[]):
            if "avito.ru" in u:continue
            try:
                _,im,_=fetch_one([u])
                q=quality(im)
                if not old_quality or q["pixels"]>old_quality["pixels"]:
                    old_quality=q;old_url=u
            except Exception:
                pass
        for i,u in enumerate(p["source_image_urls"],1):
            item={"sku":sku,"candidate_index":i,"source_url":u,"baseline_url":old_url or "","baseline_pixels":old_quality["pixels"] if old_quality else "","status":"","download_url":"","width":"","height":"","sharpness":"","quality_note":""}
            try:
                blob,im,used=fetch_one(variants(u))
                q=quality(im)
                item.update({"download_url":used,"width":q["width"],"height":q["height"],"sharpness":q["sharpness"]})
                if old_quality and (q["width"]<old_quality["width"] or q["height"]<old_quality["height"]):
                    item["status"]="inferior_resolution"
                elif old_quality and q["sharpness"]<old_quality["sharpness"]*0.5:
                    item["status"]="possible_blur"
                elif not old_quality:
                    item["status"]="needs_baseline_or_visual_review"
                else:
                    item["status"]="quality_candidate_needs_visual_review"
                # Preserve candidate originals for visual verification, no catalog edits.
                ext={"JPEG":"jpg","PNG":"png","WEBP":"webp"}[im.format]
                fname=re.sub(r"[^A-Za-z0-9_-]","_",sku)+"_"+str(i).zfill(2)+"."+ext
                (OUT/fname).write_bytes(blob)
            except Exception as exc:
                item["status"]="download_failed"
                item["quality_note"]=str(exc)[:250]
            rows.append(item)
            print(sku,i,item["status"],item["width"],item["height"],flush=True)
            time.sleep(0.1)
    fields=list(rows[0].keys())
    with (OUT/"audit.csv").open("w",newline="",encoding="utf-8-sig") as f:
        w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)
    counts={}
    for row in rows:counts[row["status"]]=counts.get(row["status"],0)+1
    (OUT/"summary.json").write_text(json.dumps({"count":len(rows),"status_counts":counts,"no_catalog_changes":True},ensure_ascii=False,indent=2),encoding="utf-8")
    print(json.dumps(counts,ensure_ascii=False))

if __name__=="__main__":
    main()
