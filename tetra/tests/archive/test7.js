const { chromium } = require('playwright');
const PAGE = require('../_page');
(async () => {
  const browser = await chromium.launch(PAGE.LAUNCH);
  for (const vp of [{ width: 1366, height: 820 }, { width: 393, height: 852 }]) {
    const ctx = await browser.newContext({ viewport: vp, deviceScaleFactor: 1, hasTouch: vp.width < 800, isMobile: vp.width < 800 });
    const page = await ctx.newPage(); const errors = [];
    page.on('pageerror', e => errors.push(String(e)));
    page.on('console', m => { if (m.type() === 'error' && !/ERR_TUNNEL/.test(m.text())) errors.push('console: ' + m.text()); });
    await page.goto(PAGE.URL); await page.waitForTimeout(700);
    await page.evaluate(() => { tetra.state.playing = false; });
    await page.click('[data-face="south"]'); await page.waitForTimeout(1900); await page.screenshot({ path: PAGE.out(`s7_${vp.width}_south.png`) });
    await page.evaluate(() => tetra.select('continent-south')); await page.waitForTimeout(1500); await page.screenshot({ path: PAGE.out(`s7_${vp.width}_continent.png`) });
    if (vp.width > 800) { await page.click('#tabRegions'); await page.waitForTimeout(400); await page.screenshot({ path: PAGE.out('s7_regions.png') }); }
    console.log(vp.width, 'errors', JSON.stringify(errors), 'regions', await page.evaluate(() => JSON.parse(document.getElementById('worldJson').value).regions.length));
    await ctx.close();
  }
  await browser.close();
})();
