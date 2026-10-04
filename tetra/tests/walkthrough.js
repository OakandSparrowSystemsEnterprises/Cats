const { chromium } = require('playwright');
const PAGE = require('./_page');
// Walks every face and a few cards on desktop, then checks that a face tap opens the Codex on a phone. Prints the card text it saw.
(async () => {
  const browser = await chromium.launch(PAGE.LAUNCH);
  const errors = [];
  const ctx = await browser.newContext({ viewport: { width: 1366, height: 820 }, deviceScaleFactor: 1 });
  const page = await ctx.newPage();
  page.on('pageerror', e => errors.push(String(e)));
  page.on('console', m => { if (m.type() === 'error' && !PAGE.isNetworkError(m.text())) errors.push('console: ' + m.text()); });
  await page.goto(PAGE.URL); await page.waitForTimeout(900);
  await page.evaluate(() => { tetra.state.playing = false; });
  await page.screenshot({ path: PAGE.out('s12_home.png') });
  // Far face: Mount Celestial card + phase across a whole day
  await page.click('#app [data-face="far"]'); await page.waitForTimeout(2200); await page.screenshot({ path: PAGE.out('s12_far.png') });
  await page.evaluate(() => tetra.select('celestial')); await page.waitForTimeout(1500); await page.screenshot({ path: PAGE.out('s12_celestial.png') });
  console.log('celestial card', (await page.evaluate(() => document.getElementById('placeBody').innerText)).slice(0, 400).replace(/\n+/g, ' | '));
  // (the year-long phase sweep lives in phases.js)
  await page.evaluate(() => tetra.setDay(120.3));
  await page.evaluate(() => tetra.select('ehia')); await page.waitForTimeout(1200);
  console.log('ehia card', (await page.evaluate(() => document.getElementById('placeBody').innerText)).slice(0, 300).replace(/\n+/g, ' | '));
  await page.click('#app [data-face="west"]'); await page.waitForTimeout(2200); await page.screenshot({ path: PAGE.out('s12_west.png') });
  await page.evaluate(() => tetra.select('delta')); await page.waitForTimeout(1200);
  console.log('wetia card', (await page.evaluate(() => document.getElementById('placeBody').innerText)).slice(0, 300).replace(/\n+/g, ' | '));
  await page.click('#app [data-face="south"]'); await page.waitForTimeout(2200); await page.screenshot({ path: PAGE.out('s12_south.png') });
  await page.click('#app [data-face="canon"]'); await page.waitForTimeout(2200); await page.screenshot({ path: PAGE.out('s12_canon.png') });
  await page.click('#tabWorld'); await page.evaluate(() => { document.querySelector('#codex .body').scrollTop = 0; }); await page.waitForTimeout(300);
  await page.screenshot({ path: PAGE.out('s12_world_tab.png') });
  console.log('world tab text', (await page.evaluate(() => document.getElementById('paneWorld').innerText)).replace(/\n+/g, ' | ').slice(0, 2500));
  console.log('markers', await page.evaluate(() => [...document.querySelectorAll('.marker')].map(m => m.textContent.trim()).join(', ')));
  console.log('json', await page.evaluate(() => { const j = JSON.parse(document.getElementById('worldJson').value); return j.regions.length + ' regions; ' + j.regions.filter(r => /Wetia/.test(r.name)).length + ' Wetia; fields=' + JSON.stringify(j.fields) + '; star=' + JSON.stringify(j.star); }));
  console.log('errors', JSON.stringify(errors));
  if (errors.length) process.exitCode = 1;
  await ctx.close();
  // phone: tap a face, expect the card to open
  const ctx2 = await browser.newContext({ viewport: { width: 393, height: 852 }, deviceScaleFactor: 1, hasTouch: true, isMobile: true });
  const p2 = await ctx2.newPage(); const err2 = [];
  p2.on('pageerror', e => err2.push(String(e)));
  await p2.goto(PAGE.URL); await p2.waitForTimeout(800);
  await p2.evaluate(() => { tetra.state.playing = false; });
  await p2.screenshot({ path: PAGE.out('s12_phone_home.png') });
  await p2.evaluate(() => { tetra.face('far', true); }); await p2.waitForTimeout(2200);
  console.log('phone codex open after face tap?', await p2.evaluate(() => document.body.classList.contains('codex-open') || document.getElementById('codex').classList.contains('open') || getComputedStyle(document.getElementById('codex')).transform));
  await p2.screenshot({ path: PAGE.out('s12_phone_far.png') });
  await p2.evaluate(() => { tetra.select('celestial'); }); await p2.waitForTimeout(1500);
  await p2.screenshot({ path: PAGE.out('s12_phone_celestial.png') });
  console.log('phone errors', JSON.stringify(err2));
  if (err2.length) process.exitCode = 1;
  await ctx2.close(); await browser.close();
})();
