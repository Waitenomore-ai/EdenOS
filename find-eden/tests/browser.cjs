// Run with NODE_PATH pointing to Playwright and CHROMIUM_EXECUTABLE set.
// Uses authored source and deterministic full-dimension SVG fixtures, not native wallpaper pixels.
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const {chromium}=require('playwright');
(async()=>{
 const root=path.resolve(__dirname,'..'),read=f=>fs.readFileSync(path.join(root,'src',f),'utf8');
 const scenes=JSON.parse(read('scenes.json')).slice(0,3).map(s=>({...s,image:'data:image/svg+xml;base64,'+Buffer.from(`<svg xmlns="http://www.w3.org/2000/svg" width="${s.width}" height="${s.height}"><rect width="100%" height="100%" fill="#bcd9a9"/></svg>`).toString('base64')}));
 const html=read('index.html').replace('__CSP__',"default-src 'none'; img-src data:; style-src 'unsafe-inline'; script-src 'unsafe-inline'").replace('__STYLE__',read('style.css')).replace('__GAME__',read('game.js')).replace('__BOOT__',`FindEden.mount(${JSON.stringify(scenes)})`);
 const browser=await chromium.launch({headless:true,executablePath:process.env.CHROMIUM_EXECUTABLE});
 const page=await browser.newPage({viewport:{width:1280,height:1000}}),errors=[],requests=[];
 page.on('pageerror',e=>errors.push(e.message));page.on('request',r=>{if(/^https?:/.test(r.url()))requests.push(r.url())});
 try{
 await page.setContent(html);await page.locator('#picture').evaluate(i=>i.decode());
 const visible=async id=>page.locator(id).isVisible();
 const hit=async(s,x=(s.rect[0]+s.rect[2])/2,y=(s.rect[1]+s.rect[3])/2)=>{await page.locator('#scene').evaluate(e=>e.scrollIntoView());const r=await page.locator('#scene').boundingBox();await page.mouse.click(r.x+r.width*x,r.y+r.height*y)};
 for(let i=0;i<3;i++){
  assert.equal(await visible('#found-ring'),false);assert.equal(await visible('#search-ring'),false);
  await hit(scenes[i],.9,.1);assert.match(await page.locator('#feedback').innerText(),/Keep looking/);assert.equal(await visible('#next'),false);
  if(i===1){await page.locator('#hint').click();assert.equal(await visible('#found-ring'),false);assert.match(await page.locator('#hint-text').innerText(),/bridge/);await page.locator('#hint').click();assert.equal(await visible('#found-ring'),true);assert.equal(await visible('#next'),false)}
  await hit(scenes[i]);assert.equal(await visible('#next'),true);assert.equal(await page.locator('#hint').isDisabled(),true);await page.locator('#next').click();
 }
 assert.match(await page.locator('#scene-count').innerText(),/1 of 3/);assert.equal(await visible('#found-ring'),false);assert.equal(await visible('#choices'),false);assert.equal(await page.locator('#hint-text').innerText(),'');
 await page.locator('#scene').focus();for(let n=0;n<5;n++)await page.keyboard.press('ArrowLeft');for(let n=0;n<4;n++)await page.keyboard.press('ArrowDown');assert.equal(await visible('#search-ring'),true);await page.keyboard.press('Enter');assert.equal(await visible('#next'),true);await page.locator('#next').click();
 await page.locator('#choice-toggle').click();await page.locator('#choices button').nth(0).click();assert.match(await page.locator('#feedback').innerText(),/Try another/);await page.locator('#choices button').nth(1).click();assert.equal(await visible('#next'),true);await page.locator('#next').click();
 await page.setViewportSize({width:390,height:844});await page.locator('#zoom').selectOption('2');await hit(scenes[2]);assert.equal(await visible('#next'),true);await page.locator('#next').click();assert.equal(await page.locator('#zoom').inputValue(),'1');assert.equal(await visible('#found-ring'),false);
 assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),true);
 await page.locator('#picture').evaluate(i=>{i.src='data:image/png;base64,broken'});await page.waitForFunction(()=>document.getElementById('feedback').textContent.includes('could not load'));await page.locator('#choice-toggle').click();await page.locator('#choices button').nth(0).click();assert.equal(await visible('#next'),true);
 await page.locator('#picture').evaluate(i=>i.dispatchEvent(new Event('error')));assert.match(await page.locator('#feedback').innerText(),/You found Eden/);
 const many=Array.from({length:28},(_,i)=>({...scenes[i%3],name:'Synthetic Garden '+i}));
 await page.setContent(html.replace(/FindEden.mount\(.*\)<\/script>/,`FindEden.mount(${JSON.stringify(many)},()=>new Date(2026,10,27))</script>`));
 assert.equal(await page.locator('#scene-count').innerText(),'Garden 1 of 28');await page.locator('#hint').click();await page.locator('#zoom').selectOption('2');await page.locator('#today').click();
 assert.equal(await page.locator('#scene-count').innerText(),'Garden 28 of 28');assert.equal(await visible('#found-ring'),false);assert.equal(await page.locator('#hint-text').innerText(),'');assert.equal(await page.locator('#zoom').inputValue(),'1');
 await page.locator('#choice-toggle').click();await page.locator('#choices button').nth(many[27].answer).click();assert.equal(await page.locator('#feedback').innerText(),'You found Eden! She was playing hide-and-seek.');await page.locator('#next').click();assert.equal(await page.locator('#scene-count').innerText(),'Garden 1 of 28');
 assert.deepEqual(errors,[]);assert.deepEqual(requests,[]);console.log('PASS: all three maps, wrong taps, hint/reveal, keyboard, choices, zoom/mobile, replay, image decoding and zero network');
 }finally{await browser.close()}
})().catch(e=>{console.error(e);process.exitCode=1});
