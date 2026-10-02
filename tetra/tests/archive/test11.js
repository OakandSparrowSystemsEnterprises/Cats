const { chromium } = require('playwright');
const PAGE = require('../_page');
(async () => {
  const browser = await chromium.launch(PAGE.LAUNCH);
  const ctx = await browser.newContext({ viewport: { width: 800, height: 700 }, deviceScaleFactor: 1 });
  const page = await ctx.newPage();
  await page.goto(PAGE.URL); await page.waitForTimeout(800);
  await page.evaluate(() => { tetra.state.playing = false; tetra.setDay(0.42); tetra.face('canon', true); });
  await page.waitForTimeout(2500);
  await page.evaluate(() => { tetra.state.dist = 3.6; tetra.state.fly = null; tetra.state.baseYaw = 0; tetra.state.pitch = -0.62; });
  await page.waitForTimeout(500);
  await page.screenshot({ path: PAGE.out('seam_canon-far_labels.png'), clip: { x: 60, y: 40, width: 680, height: 600 } });
  await ctx.close(); await browser.close();
})();
