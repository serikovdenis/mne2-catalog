#!/usr/bin/env python3
"""Audit factory PDF photo resolution and extract candidates. Never modify live catalog.

Run: python scripts/extract_fulei_factory_pdf.py 'source-documents/Fulei Catalogue(2).pdf'
"""
import csv, hashlib, io, json, re, sys
from pathlib import Path
import fitz
from PIL import Image

ROOT=Path(__file__).resolve().parent.parent
SRC=Path(sys.argv[1]) if len(sys.argv)>1 else ROOT/"source-documents"/"Fulei Catalogue(2).pdf"
OUT=ROOT/"reports"/"fulei-factory-photo-candidates"
OUT.mkdir(parents=True,exist_ok=True)
MANIFEST=ROOT/"reports"/"avito-photo-candidates-2026-10-10.json"
PRODUCTS=json.loads(MANIFEST.read_text(encoding="utf-8"))["products"]

def page_for(s):
    k=re.sub(r"[-\s]","",s.upper())
    if k=="BU650IIPLUS":return 3
    if k in ("BU1600II","BU2040II"):return 4
    m=re.fullmatch(r"BU(1400|1600|1700)E(COLD|WARM)",k)
    if m:return 5 if m[2]=="COLD" else 6
    m=re.fullmatch(r"LITE(140|170)(C|W|H)(E|P)",k)
    if m:return 7 if m[3]=="E" else 8
    if re.fullmatch(r"MATE(140|160|170)(W|H)",k):return 9
    if re.fullmatch(r"BU(1400|1600|1700)H(WARM|HOT)",k):return 10
    if re.fullmatch(r"BU(1600|2200)WL",k):return 11
    if k=="BU3300WL":return 12
    if re.fullmatch(r"BU(1425|1440|1640)FA",k):return 13
    if re.fullmatch(r"HT(1220|1720)PT2B",k):return 14
    if re.fullmatch(r"HT(1232|1732|1742|2042)T2B",k):return 15
    if re.fullmatch(r"HT(1732|1742|1860|2042|3342)B2T",k):return 16
    if re.fullmatch(r"RM(160|210)BASE",k):return 18
    return None

def main():
    if not SRC.exists():raise SystemExit(f"Factory PDF not found: {SRC}")
    doc=fitz.open(SRC)
    rows=[]
    for p in PRODUCTS:
        if p["brand"]!="Fulei":continue
        sku=p["sku"]; page_num=page_for(sku)
        if not page_num:
            rows.append({"sku":sku,"page":"","file":"","width":"","height":"","status":"not_in_2023_factory_pdf"})
            continue
        page=doc[page_num-1]
        found=[]
        for info in page.get_images(full=True):
            try:
                b=doc.extract_image(info[0])["image"]
                im=Image.open(io.BytesIO(b));im.load()
                if im.format not in ("JPEG","PNG","WEBP"):continue
                if im.width<400 or im.height<250:continue
                found.append((im.width*im.height,b,im))
            except Exception:continue
        found.sort(key=lambda x:x[0],reverse=True)
        if not found:
            rows.append({"sku":sku,"page":page_num,"file":"","width":"","height":"","status":"no_embedded_photo_over_400x250"})
            continue
        _,b,im=found[0]
        ext={"JPEG":"jpg","PNG":"png","WEBP":"webp"}[im.format]
        filename=f"{sku}_factory_p{page_num}.{ext}"
        (OUT/filename).write_bytes(b)
        status="review_original_model_variant" if max(im.size)>=1000 else "low_resolution_do_not_replace"
        rows.append({"sku":sku,"page":page_num,"file":filename,"width":im.width,"height":im.height,"status":status})
    fields=["sku","page","file","width","height","status"]
    with (OUT/"audit.csv").open("w",encoding="utf-8-sig",newline="") as f:
        w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)
    summary={"models":len(rows),"extracted":sum(bool(r["file"]) for r in rows),"candidate_resolution_ge_1000":sum(r["status"]=="review_original_model_variant" for r in rows),"low_resolution":sum(r["status"]=="low_resolution_do_not_replace" for r in rows),"no_catalog_changes":True}
    (OUT/"summary.json").write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding="utf-8")
    print(json.dumps(summary,ensure_ascii=False))
if __name__=="__main__":main()
