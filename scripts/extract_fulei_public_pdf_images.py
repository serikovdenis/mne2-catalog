#!/usr/bin/env python3
"""Extract high-resolution, unmodified photo candidates from publicly available Fulei PDF brochures.

No catalog data or production image URLs are changed. No upscaling.
"""
import csv
import hashlib
import io
import json
import urllib.request
from pathlib import Path
import fitz
from PIL import Image

ROOT=Path(__file__).resolve().parent.parent
OUT=ROOT/"reports"/"fulei-pdf-photo-candidates"
OUT.mkdir(parents=True,exist_ok=True)
SOURCES=[
 {"sku":"HT-1720P-T2B","url":"https://intamarketgraphics.co.za/wp-content/uploads/2024/02/Fulei-HT-1720P-T2B.pdf"},
 {"sku":"BU-650II-PLUS","url":"https://intamarketgraphics.co.za/wp-content/uploads/2024/05/Complete-Equipment-Brochure.pdf"},
 {"sku":"BU-1600E-Warm","url":"https://intamarketgraphics.co.za/wp-content/uploads/2024/05/Complete-Equipment-Brochure.pdf"},
 {"sku":"BU-1600WL","url":"https://intamarketgraphics.co.za/wp-content/uploads/2024/05/Complete-Equipment-Brochure.pdf"},
]
MIN_LONG_SIDE=700
MAX_PDF_BYTES=35*1024*1024

def download(url):
    req=urllib.request.Request(url,headers={"User-Agent":"Mozilla/5.0 (compatible; MNE2PhotoReview/1.0)","Accept":"application/pdf,*/*"})
    with urllib.request.urlopen(req,timeout=35) as r:
        b=r.read(MAX_PDF_BYTES+1)
    if len(b)>MAX_PDF_BYTES or not b.startswith(b"%PDF"):raise ValueError("Invalid or oversized PDF")
    return b

def main():
    rows=[]
    cache={}
    for src in SOURCES:
        sku,url=src["sku"],src["url"]
        try:
            if url not in cache:cache[url]=download(url)
            doc=fitz.open(stream=cache[url],filetype="pdf")
            for page_i,page in enumerate(doc):
                for item in page.get_images(full=True):
                    xref=item[0]
                    data=doc.extract_image(xref)
                    b=data["image"]
                    im=Image.open(io.BytesIO(b));im.load()
                    if max(im.size)<MIN_LONG_SIDE:continue
                    digest=hashlib.sha256(b).hexdigest()[:12]
                    ext={"JPEG":"jpg","PNG":"png","WEBP":"webp"}.get(im.format)
                    if not ext:continue
                    name=f"{sku}_p{page_i+1}_{digest}.{ext}"
                    (OUT/name).write_bytes(b)
                    rows.append({"sku":sku,"source_pdf":url,"pdf_page":page_i+1,"filename":name,"width":im.width,"height":im.height,"sha256":hashlib.sha256(b).hexdigest(),"status":"visual_model_match_required"})
            doc.close()
        except Exception as exc:
            rows.append({"sku":sku,"source_pdf":url,"pdf_page":"","filename":"","width":"","height":"","sha256":"","status":"download_or_extract_failed: "+str(exc)[:170]})
    fields=["sku","source_pdf","pdf_page","filename","width","height","sha256","status"]
    with (OUT/"audit.csv").open("w",encoding="utf-8-sig",newline="") as f:
        writer=csv.DictWriter(f,fieldnames=fields);writer.writeheader();writer.writerows(rows)
    counts={"extracted":sum(bool(r["filename"]) for r in rows),"failed":sum("failed" in r["status"] for r in rows)}
    (OUT/"summary.json").write_text(json.dumps({"sources":len(SOURCES),"results":counts,"note":"All extracted images require visual SKU match. Never auto-publish."},ensure_ascii=False,indent=2),encoding="utf-8")
    print(json.dumps(counts))

if __name__=="__main__":main()
