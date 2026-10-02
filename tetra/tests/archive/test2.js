const { chromium } = require('playwright');
const PAGE = require('../_page');
(async () => {
  const browser = await chromium.launch(PAGE.LAUNCH);
  async function ctxPage(viewport) {
    const ctx = await browser.newContext({ viewport, deviceScaleFactor: 1, hasTouch: viewport.width < 800, isMobile: viewport.width < 800 });
    const page = await ctx.newPage();
    const errors = [];
    page.on('pageerror', e => errors.push(String(e)));
    page.on('console', m => { if (m.type() === 'error' && !/ERR_TUNNEL/.test(m.text())) errors.push('console: ' + m.text()); });
    await page.goto(PAGE.URL);
    return { ctx, page, errors };
  }
  // desktop: first frame, then a sweep through a day
  {
    const { ctx, page, errors } = await ctxPage({ width: 1366, height: 820 });
    await page.waitForTimeout(400);
    await page.screenshot({ path: PAGE.out('s2_first.png') });
    await page.evaluate(() => { tetra.state.playing = false; });
    for (const d of [0.0, 0.18, 0.36, 0.55, 0.75]) {
      await page.evaluate(d => tetra.setDay(d), d); await page.waitForTimeout(250);
      await page.screenshot({ path: PAGE.out(`s2_day_${d}.png`) });
    }
    // region select on the west face + phases
    await page.evaluate(() => tetra.select('evermere')); await page.waitForTimeout(1800);
    await page.screenshot({ path: PAGE.out('s2_evermere.png') });
    console.log('desktop errors', errors);
    await ctx.close();
  }
  {
    const { ctx, page, errors } = await ctxPage({ width: 393, height: 852 });
    await page.waitForTimeout(500);
    await page.screenshot({ path: PAGE.out('s2_phone.png') });
    await page.evaluate(() => { tetra.state.playing = false; tetra.select('headlands'); }); await page.waitForTimeout(1800);
    await page.screenshot({ path: PAGE.out('s2_phone_place.png') });
    await page.tap('#btnClose'); await page.waitForTimeout(600);
    await page.tap('[data-face="west"]'); await page.waitForTimeout(1800);
    await page.screenshot({ path: PAGE.out('s2_phone_west.png') });
    console.log('phone errors', errors);
    await ctx.close();
  }
  await browser.close();
})();
