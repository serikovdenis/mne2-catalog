#!/usr/bin/env python3
"""Mirror external catalog photos into a local, self-hosted images directory.

Run from catalog repository root:
    python3 scripts/mirror_external_photos.py
    python3 scripts/mirror_external_photos.py --apply

After --apply, deploy BOTH data/part*.json and images/external/ to the
website document root (mne2.ru/catalog/). This script does not FTP/upload.
Never change a catalog URL unless the corresponding image was downloaded,
validated and written successfully.
"""
import argparse
import csv
import json
import os
import re
import tempfile
import urllib.request
from collections import Counter
from pathlib import Path
from urllib.parse import urlparse

HOST = "mne2.ru"
MAX_BYTES = 20 * 1024 * 1024
HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; MNE2CatalogPhotoMirror/1.0)"}


def kind_of_image(blob):
    if blob.startswith(b"\xff\xd8\xff"):
        return "jpg"
    if blob.startswith(b"\x89PNG\r\n\x1a\n"):
        return "png"
    if blob[:4] == b"RIFF" and blob[8:12] == b"WEBP":
        return "webp"
    if blob[:6] in (b"GIF87a", b"GIF89a"):
        return "gif"
    return None


def is_external(url):
    try:
        p = urlparse(url)
        return p.scheme in ("http", "https") and (p.hostname or "").lower() not in ("mne2.ru", "www.mne2.ru")
    except (TypeError, ValueError):
        return False


def fetch_image(url):
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=25) as response:
        mime = response.headers.get("Content-Type", "").lower()
        if mime and not mime.startswith("image/") and "octet-stream" not in mime:
            raise ValueError("not an image Content-Type: " + mime)
        blob = response.read(MAX_BYTES + 1)
    if len(blob) > MAX_BYTES:
        raise ValueError("image exceeds 20 MiB")
    kind = kind_of_image(blob)
    if not kind:
        raise ValueError("unknown image signature")
    return blob, kind


def safe_sku(sku):
    return re.sub(r"[^A-Za-z0-9_-]+", "-", str(sku))[:100] or "unknown"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true", help="Download, validate and update catalog JSON")
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parent.parent)
    args = parser.parse_args()
    root = args.root.resolve()
    entries = []
    parts = {}
    for path in sorted((root / "data").glob("part[0-9]*.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        parts[path] = data
        for product in data:
            for index, url in enumerate(product.get("images") or []):
                if is_external(url):
                    entries.append((path, product, index, url))
    print("External image links:", len(entries))
    print("Affected SKUs:", len({str(p.get("sku")) for _, p, _, _ in entries}))
    print("Domains:", dict(Counter(urlparse(u).hostname for _, _, _, u in entries)))
    if not args.apply:
        print("Dry run only. Use --apply to download images and change catalog JSON.")
        return
    output = root / "images" / "external"
    output.mkdir(parents=True, exist_ok=True)
    results = []
    successful = 0
    for path, product, index, url in entries:
        sku = safe_sku(product.get("sku", "unknown"))
        try:
            blob, ext = fetch_image(url)
            filename = sku + "_" + str(index + 1).zfill(2) + "." + ext
            dest = output / filename
            # Do not overwrite an existing file with different contents.
            if dest.exists() and dest.read_bytes() != blob:
                raise ValueError("filename collision; manual review required: " + filename)
            if not dest.exists():
                with tempfile.NamedTemporaryFile(dir=output, delete=False) as tmp:
                    tmp.write(blob)
                    temp_name = tmp.name
                os.replace(temp_name, dest)
            new_url = "https://" + HOST + "/catalog/images/external/" + filename
            product["images"][index] = new_url
            if index == 0:
                product["image"] = new_url
            successful += 1
            status = "mirrored"
            detail = new_url
        except Exception as exc:
            status = "failed"
            detail = str(exc)
        results.append([sku, index + 1, url, status, detail])
        print(sku, index + 1, status, detail[:140])
    # Save JSON only after image writes. Each successful reference has a file.
    if successful:
        for path, data in parts.items():
            path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    report = root / "reports" / "external-photo-mirror-results.csv"
    report.parent.mkdir(parents=True, exist_ok=True)
    with report.open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        writer.writerow(["sku", "image_number", "original_url", "status", "new_url_or_error"])
        writer.writerows(results)
    print("Mirrored:", successful, "Failed:", len(entries) - successful)
    print("IMPORTANT: Upload images/external/ and data/part*.json together before verifying live URLs.")


if __name__ == "__main__":
    main()
