"""Download unmodified BestSub manufacturer gallery images, retaining original order.
Source: https://www.bestsub.com/dtf-heat-press/25445-otter-ultra-heat-press-g1-16-x20-40-50cm-marine-blue.html
Do not transcode, resize, recompress or edit source files.
"""
from pathlib import Path
import concurrent.futures
import hashlib
import json
import subprocess
import time

SKU = "OU-G14050MB"
BASE = "https://www.bestsub.com/media/k2/galleries/25445/"
DEST = Path("site/catalog/images/bestsub") / SKU
NAMES = ["OU-G14050MB.webp","OU-G14050MB_1.webp","OU-G14050MB_10.webp","OU-G14050MB_11.webp","OU-G14050MB_12.webp","OU-G14050MB_13.webp","OU-G14050MB_14.webp","OU-G14050MB_15.webp","OU-G14050MB_16.webp","OU-G14050MB_1_1.webp","OU-G14050MB_1_10.webp","OU-G14050MB_1_2.webp","OU-G14050MB_1_4.webp","OU-G14050MB_1_5.webp","OU-G14050MB_1_6.webp","OU-G14050MB_1_7.webp","OU-G14050MB_1_8.webp","OU-G14050MB_1_9.webp","OU-G14050MB_2.webp","OU-G14050MB_3.webp","OU-G14050MB_4.webp","OU-G14050MB_5.webp","OU-G14050MB_6.webp","OU-G14050MB_7.webp","OU-G14050MB_8.webp","OU-G14050MB_9.webp"]
DEST.mkdir(parents=True, exist_ok=True)

def fetch_one(index_name):
    i, name = index_name
    destination = DEST / f"{i:02d}.webp"
    url = BASE + name
    if destination.is_file():
        data = destination.read_bytes()
        if data[:4] == b"RIFF" and data[8:12] == b"WEBP":
            return {"order": i, "filename": destination.name, "original_filename": name, "source_url": url, "sha256": hashlib.sha256(data).hexdigest(), "bytes": len(data)}
    tmp = destination.with_suffix(".webp.download")
    last_error = None
    for attempt in range(4):
        try:
            subprocess.run(["curl","--fail","--location","--silent","--show-error","--retry","2","--retry-delay","2","--connect-timeout","20","--max-time","100","--user-agent","Mozilla/5.0","--output",str(tmp),url], check=True)
            data = tmp.read_bytes()
            if len(data) < 1000 or data[:4] != b"RIFF" or data[8:12] != b"WEBP":
                raise ValueError(f"Invalid WEBP or unexpectedly small image: {name} ({len(data)} bytes)")
            tmp.replace(destination)
            return {"order": i, "filename": destination.name, "original_filename": name, "source_url": url, "sha256": hashlib.sha256(data).hexdigest(), "bytes": len(data)}
        except Exception as error:
            last_error = str(error)
            tmp.unlink(missing_ok=True)
            time.sleep(2 * (attempt + 1))
    return {"order": i, "original_filename": name, "source_url": url, "error": last_error}

with concurrent.futures.ThreadPoolExecutor(max_workers=5) as pool:
    results = sorted(pool.map(fetch_one, enumerate(NAMES, 1)), key=lambda r:r["order"])
seen = set()
for r in results:
    if "sha256" in r:
        r["duplicate_of"] = next((a["filename"] for a in results[:r["order"]-1] if a.get("sha256") == r["sha256"]), None)
        seen.add(r["sha256"])
manifest = {"sku": SKU, "source": "https://www.bestsub.com/dtf-heat-press/25445-otter-ultra-heat-press-g1-16-x20-40-50cm-marine-blue.html", "expected_gallery_count": len(NAMES), "files": results}
(DEST / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
for r in results:
    print("OK" if "sha256" in r else "MISSING", r.get("filename",r["original_filename"]), r.get("sha256",r.get("error")),flush=True)
if "sha256" not in results[0]:
    raise SystemExit("Main manufacturer image unavailable; do not publish incomplete product")
if any("error" in r for r in results):
    raise SystemExit("Some manufacturer gallery files could not be downloaded; review manifest before publishing")
print("All",len(results),"original WEBP files downloaded unchanged")
