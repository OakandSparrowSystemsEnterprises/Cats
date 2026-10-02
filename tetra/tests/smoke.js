const { chromium } = require('playwright');
const PAGE = require('./_page');
// Loads the page at desktop and phone width, opens a card, and fails on any script or console error.
(async () => {
  const browser = await chromium.launch(PAGE.LAUNCH);
  for (const vp of [{ width: 1366, height: 820 }, { width: 393, height: 852 }]) {
    const ctx = await browser.newContext({ viewport: vp, deviceScaleFactor: 1, hasTouch: vp.width < 800, isMobile: vp.width < 800 });
    const page = await ctx.newPage(); const errors = [];
    page.on('pageerror', e => errors.push(String(e)));
    page.on('console', m => { if (m.type() === 'error' && !PAGE.isNetworkError(m.text())) errors.push('console: ' + m.text()); });
    await page.goto(PAGE.URL); await page.waitForTimeout(600);
    await page.screenshot({ path: PAGE.out(`final_${vp.width}.png`) });
    await page.evaluate(() => tetra.select('islandia')); await page.waitForTimeout(1500);
    await page.keyboard.press('Escape'); await page.waitForTimeout(300);
    console.log(vp.width, 'errors:', JSON.stringify(errors), 'title:', await page.title());
    if (errors.length) process.exitCode = 1;
    await ctx.close();
  }
  await browser.close();
})();
