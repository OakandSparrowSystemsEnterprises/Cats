const { chromium } = require('playwright');
const PAGE = require('../_page');
(async () => {
  const browser = await chromium.launch(PAGE.LAUNCH);
  const errors = [];
  const ctx = await browser.newContext({ viewport: { width: 1366, height: 820 }, deviceScaleFactor: 1 });
  const page = await ctx.newPage();
  page.on('pageerror', e => errors.push(String(e)));
  page.on('console', m => { if (m.type() === 'error' && !/ERR_TUNNEL/.test(m.text())) errors.push('console: ' + m.text()); });
  await page.goto(PAGE.URL); await page.waitForTimeout(700);
  await page.evaluate(() => { tetra.state.playing = false; });
  const dates = [];
  for (const d of [0, 27.5, 28, 56, 84, 111.9, 112, 200, 300, 363.9, 364, 364.9, 365, 500]) {
    await page.evaluate(d => tetra.setDay(d), d); await page.waitForTimeout(120);
    dates.push(d + ' => ' + await page.evaluate(() => document.getElementById('dateOut').textContent + ' | ' + document.getElementById('dateSub').textContent));
  }
  console.log(dates.join('\n'));
  await page.evaluate(() => tetra.setDay(5)); await page.waitForTimeout(900);
  await page.screenshot({ path: PAGE.out('s3_rain.png') });
  await page.evaluate(() => tetra.setDay(160)); await page.waitForTimeout(500);
  await page.screenshot({ path: PAGE.out('s3_summer.png') });
  await page.evaluate(() => tetra.setDay(330)); await page.waitForTimeout(500);
  await page.screenshot({ path: PAGE.out('s3_winter.png') });
  // world tab scrolled to the calendar / life sections
  await page.evaluate(() => { document.querySelector('#codex .body').scrollTop = 330; }); await page.waitForTimeout(300);
  await page.screenshot({ path: PAGE.out('s3_codex1.png') });
  await page.evaluate(() => { document.querySelector('#codex .body').scrollTop = 1100; }); await page.waitForTimeout(300);
  await page.screenshot({ path: PAGE.out('s3_codex2.png') });
  await page.click('#tabRegions'); await page.waitForTimeout(400);
  await page.screenshot({ path: PAGE.out('s3_regions.png') });
  await page.click('[data-face="west"]'); await page.waitForTimeout(1800);
  await page.screenshot({ path: PAGE.out('s3_west.png') });
  console.log('markers', await page.evaluate(() => [...document.querySelectorAll('.marker')].map(m => m.textContent.trim())));
  console.log('regions in json', await page.evaluate(() => JSON.parse(document.getElementById('worldJson').value).regions.length));
  console.log('errors', JSON.stringify(errors));
  await ctx.close();
  const ctx2 = await browser.newContext({ viewport: { width: 393, height: 852 }, deviceScaleFactor: 1, hasTouch: true, isMobile: true });
  const p2 = await ctx2.newPage(); const err2 = [];
  p2.on('pageerror', e => err2.push(String(e)));
  await p2.goto(PAGE.URL); await p2.waitForTimeout(600);
  await p2.evaluate(() => { tetra.state.playing = false; tetra.setDay(10); }); await p2.waitForTimeout(600);
  await p2.tap('#btnCodex'); await p2.waitForTimeout(500);
  await p2.evaluate(() => { document.querySelector('#codex .body').scrollTop = 300; }); await p2.waitForTimeout(300);
  await p2.screenshot({ path: PAGE.out('s3_phone.png') });
  console.log('phone errors', JSON.stringify(err2));
  await ctx2.close();
  await browser.close();
})();
