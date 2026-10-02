const { chromium } = require('playwright');
const PAGE = require('./_page');
(async () => {
  const browser = await chromium.launch(PAGE.LAUNCH);
  const ctx = await browser.newContext({ viewport: { width: 800, height: 700 }, deviceScaleFactor: 1 });
  const page = await ctx.newPage(); const errors = [];
  page.on('pageerror', e => errors.push(String(e)));
  await page.goto(PAGE.URL); await page.waitForTimeout(800);
  await page.evaluate(() => { tetra.state.playing = false; tetra.setDay(0.42); tetra.face('canon', true); });
  await page.waitForTimeout(2500);
  await page.evaluate(() => { tetra.state.dist = 3.6; document.getElementById('markers').style.display = 'none'; });
  const views = { 'canon-west': [-1.047, 0.12], 'canon-south': [1.047, 0.12], 'west-south': [3.1416, 0.12], 'canon-far': [0, -0.62], 'west-far': [-2.094, -0.62], 'south-far': [2.094, -0.62] };
  for (const [name, [yaw, pitch]] of Object.entries(views)) {
    await page.evaluate(([y, p]) => { tetra.state.fly = null; tetra.state.baseYaw = y; tetra.state.pitch = p; }, [yaw, pitch]);
    await page.waitForTimeout(500);
    await page.screenshot({ path: PAGE.out(`seam_${name}.png`), clip: { x: 100, y: 40, width: 600, height: 560 } });
  }
  console.log('errors', JSON.stringify(errors));
  await ctx.close(); await browser.close();
})();
