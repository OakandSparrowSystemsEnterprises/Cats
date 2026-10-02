const { chromium } = require('playwright');
const PAGE = require('../_page');
(async () => {
  const browser = await chromium.launch(PAGE.LAUNCH);
  const ctx = await browser.newContext({ viewport: { width: 393, height: 852 }, deviceScaleFactor: 2, hasTouch: true, isMobile: true });
  const page = await ctx.newPage(); const errors = [];
  page.on('pageerror', e => errors.push(String(e)));
  await page.goto(PAGE.URL); await page.waitForTimeout(800);
  await page.evaluate(() => { tetra.state.playing = false; });
  for (const f of ['canon', 'west', 'south', 'far']) {
    await page.tap(`[data-face="${f}"]`); await page.waitForTimeout(2200);
    await page.screenshot({ path: PAGE.out(`s9_phone_${f}.png`), clip: { x: 0, y: 200, width: 393, height: 470 } });
  }
  console.log('errors', JSON.stringify(errors));
  await ctx.close(); await browser.close();
})();
