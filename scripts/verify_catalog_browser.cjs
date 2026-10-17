const {chromium}=require('playwright');
const fs=require('node:fs'),assert=require('node:assert/strict');
(async()=>{
 const expected=[1,2,3,4].flatMap(n=>JSON.parse(fs.readFileSync(`catalog/data/part${n}.json`,'utf8')));
 const browser=await chromium.launch({headless:true});
 try{
  for(const width of [1280,390]){
   const page=await browser.newPage({viewport:{width,height:900},isMobile:width===390,hasTouch:width===390});
   const errors=[];page.on('pageerror',e=>errors.push(e.message));
   // If every standalone JSON request fails, the page must still show the complete published catalog.
   await page.route('**/catalog/data/part*.json',route=>route.abort());
   await page.goto('https://mne2.ru/catalog/?verify_snapshot='+Date.now(),{waitUntil:'domcontentloaded',timeout:60000});
   await page.locator('.product').first().waitFor({timeout:12000});
   assert.equal(await page.locator('.product').count(),Math.min(24,expected.length));
   assert((await page.locator('#resultMeta').innerText()).includes(`из ${expected.length}`));
   await page.locator('#query').fill('CEHPPRO4050MDLB');
   assert.equal(await page.locator('.product').count(),1);
   await page.locator('.product img').click();
   assert.equal(await page.locator('#photoZoomCount').innerText(),'1 / 19');
   await page.locator('#photoZoomNext').click();
   assert.equal(await page.locator('#photoZoomCount').innerText(),'2 / 19');
   assert.deepEqual(errors,[]);
   await page.screenshot({path:`catalog-snapshot-${width}.png`});
   console.log('BROWSER_VERIFIED',width,expected.length,'products; JSON unavailable; search and gallery work');
   await page.close();
  }
 }finally{await browser.close()}
})().catch(e=>{console.error(e);process.exit(1)});
