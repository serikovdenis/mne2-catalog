"""Read-only audit of catalog metadata required for reviewed BestSub preparation."""
import json
from pathlib import Path

def audit(root=Path("data")):
    rows=[]
    for path in sorted(root.glob("part*.json")):
        for item in json.loads(path.read_text(encoding="utf-8")):
            sku=item.get("sku", "")
            reasons=[]
            if not item.get("source_url"): reasons.append("missing_source_url")
            if not item.get("source_images"): reasons.append("missing_source_images")
            images=item.get("images") or []
            sources=item.get("source_images") or []
            if sources and len(sources)!=len(images): reasons.append("image_count_mismatch")
            if sources and images and any(s.rsplit("/",1)[-1]!=d.rsplit("/",1)[-1] for s,d in zip(sources,images)): reasons.append("filename_mismatch")
            if sources and images and any(not d.startswith("https://mne2.ru/catalog/images/bestsub/"+sku+"/") for d in images): reasons.append("destination_path_mismatch")
            if not item.get("specifications"): reasons.append("missing_specifications")
            if not item.get("description"): reasons.append("missing_description")
            rows.append({"sku":sku,"part":path.name,"ready":not reasons,"reasons":reasons})
    return rows

if __name__=="__main__":
    rows=audit()
    summary={"total":len(rows),"ready":sum(x["ready"] for x in rows),"blocked":sum(not x["ready"] for x in rows)}
    print(json.dumps(summary,ensure_ascii=False))
    for item in rows:
        if item["ready"] or item["sku"]=="OT-QSH4050SCB":
            print(json.dumps(item,ensure_ascii=False))
