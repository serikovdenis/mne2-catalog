"""Offline safety checks for the credential-free BestSub preparation stage."""
import io
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from PIL import Image
from scripts import prepare_bestsub_reviewed as mod

SKU="OT-QSH4050SCB"
PAGE="https://www.bestsub.com/example"
SOURCE="https://www.bestsub.com/media/k2/galleries/123/"+SKU+".webp"
LIVE="https://mne2.ru/catalog/images/bestsub/"+SKU+"/"+SKU+".webp"

class PrepareTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.cwd=patch("os.getcwd")
        self.root=Path(self.tmp.name)
        (self.root/"data").mkdir()
        self.row={"sku":SKU,"source_url":PAGE,"source_images":[SOURCE],"images":[LIVE],"image":LIVE,
                  "description":"Reviewed","specifications":"Reviewed"}
        (self.root/"data"/"part1.json").write_text(json.dumps([self.row]),encoding="utf-8")
        self.image=io.BytesIO()
        Image.effect_noise((256,256),80).convert("RGB").save(self.image,format="WEBP",quality=90)
        self.original=self.image.getvalue()
    def run_prepare(self,html=None):
        import os,sys
        old=os.getcwd()
        os.chdir(self.root)
        try:
            with patch.object(sys,"argv",["prepare","--sku",SKU]), patch.object(mod,"get",side_effect=[
                (html or '<img src="'+SOURCE+'">').encode(),self.original
            ]):
                mod.main()
        finally:
            os.chdir(old)
    def test_prepares_only_expected_image(self):
        self.run_prepare()
        out=self.root/"prepared"/SKU
        self.assertEqual((out/(SKU+".webp")).read_bytes(),self.original)
        self.assertEqual(json.loads((out/"manifest.json").read_text())["sku"],SKU)
    def test_rejects_changed_manufacturer_gallery(self):
        with self.assertRaises(AssertionError):
            self.run_prepare('<img src="https://www.bestsub.com/media/k2/galleries/123/OTHER.webp">')
    def test_rejects_duplicate_destination_names(self):
        self.row["source_images"]=[SOURCE,SOURCE]
        self.row["images"]=[LIVE,LIVE]
        (self.root/"data"/"part1.json").write_text(json.dumps([self.row]),encoding="utf-8")
        with self.assertRaises(AssertionError):
            self.run_prepare()
    def test_rejects_price_or_other_catalog_writes(self):
        before=(self.root/"data"/"part1.json").read_bytes()
        self.run_prepare()
        self.assertEqual((self.root/"data"/"part1.json").read_bytes(),before)

if __name__=="__main__":
    unittest.main()
