const { chromium } = require('playwright');
const PAGE = require('../_page');
(async () => {
  const browser = await chromium.launch({ args: ['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'] });
  const results = [];
  async function run(name, viewport, actions) {
    const ctx = await browser.newContext({ viewport, deviceScaleFactor: 1, hasTouch: viewport.width < 800, isMobile: viewport.width < 800 });
    const page = await ctx.newPage();
    const errors = [], logs = [];
    page.on('console', m => { if (m.type() === 'error' || m.type() === 'warning') logs.push(m.type() + ': ' + m.text()); });
    page.on('pageerror', e => errors.push(String(e)));
    await page.goto(PAGE.URL);
    await page.waitForTimeout(2500);
    await actions(page);
    results.push({ name, errors, logs: logs.slice(0, 10) });
    await ctx.close();
  }
  await run('desktop', { width: 1366, height: 820 }, async page => {
    await page.screenshot({ path: PAGE.out('shot_desktop_0.png') });
    const st = await page.evaluate(() => ({ date: document.getElementById('dateOut').textContent, facing: document.getElementById('facing').textContent, markers: [...document.querySelectorAll('.marker')].map(m => [m.textContent.trim(), m.style.opacity, m.style.transform]).filter(x => x[1] !== '0') }));
    console.log('desktop state', JSON.stringify(st, null, 1));
    // click a marker (Yolkia)
    const m = page.locator('.marker[data-id="yolkia"]');
    await m.click({ force: true });
    await page.waitForTimeout(1800);
    await page.screenshot({ path: PAGE.out('shot_desktop_yolkia.png') });
    console.log('place html', (await page.evaluate(() => document.getElementById('placeBody').innerText)).slice(0, 400));
    // drag rotate
    await page.mouse.move(500, 400); await page.mouse.down(); await page.mouse.move(700, 350, { steps: 12 }); await page.mouse.up();
    await page.waitForTimeout(600);
    // face button: south
    await page.click('[data-face="south"]'); await page.waitForTimeout(1800);
    await page.screenshot({ path: PAGE.out('shot_desktop_south.png') });
    await page.click('[data-face="far"]'); await page.waitForTimeout(1800);
    await page.screenshot({ path: PAGE.out('shot_desktop_far.png') });
    // regions tab
    await page.click('#tabRegions'); await page.waitForTimeout(700);
    await page.screenshot({ path: PAGE.out('shot_desktop_regions.png') });
    // +1 month, pause
    await page.click('#btnMonth'); await page.click('#btnPlay'); await page.waitForTimeout(300);
    console.log('after month', await page.evaluate(() => document.getElementById('dateOut').textContent + ' | ' + document.getElementById('dateSub').textContent + ' | ' + document.getElementById('btnPlay').textContent));
    // scrub day
    await page.evaluate(() => { const r = document.getElementById('rngDay'); r.value = '200'; r.dispatchEvent(new Event('input', { bubbles: true })); });
    await page.waitForTimeout(200);
    console.log('after scrub', await page.evaluate(() => document.getElementById('dateOut').textContent + ' | ' + document.getElementById('dateSub').textContent));
    // edit lore
    await page.evaluate(() => tetra.select('footia')); await page.waitForTimeout(500);
    await page.click('.btnEdit'); await page.fill('#loreEdit', 'Test lore for Footia.'); await page.click('.btnSave'); await page.waitForTimeout(300);
    console.log('lore after save', await page.evaluate(() => document.querySelector('#placeBody .text').textContent + ' | chip=' + document.querySelector('#placeBody .chiptext').textContent + ' | ls=' + localStorage.getItem('tetra.lore.v1')));
    await page.click('.btnRestore'); await page.waitForTimeout(200);
    console.log('lore after restore', await page.evaluate(() => document.querySelector('#placeBody .text').textContent.slice(0, 40) + ' | ls=' + localStorage.getItem('tetra.lore.v1')));
    // frame time
    const fps = await page.evaluate(() => new Promise(res => { let n = 0; const t0 = performance.now(); function f() { n++; if (performance.now() - t0 < 2000) requestAnimationFrame(f); else res(n / 2); } requestAnimationFrame(f); }));
    console.log('fps ~', fps);
  });
  await run('phone', { width: 393, height: 852 }, async page => {
    await page.screenshot({ path: PAGE.out('shot_phone_0.png') });
    await page.tap('#btnCodex'); await page.waitForTimeout(600);
    await page.screenshot({ path: PAGE.out('shot_phone_codex.png') });
    await page.tap('#btnClose'); await page.waitForTimeout(500);
    await page.tap('[data-face="west"]'); await page.waitForTimeout(1800);
    await page.screenshot({ path: PAGE.out('shot_phone_west.png') });
    const scrollW = await page.evaluate(() => [document.documentElement.scrollWidth, innerWidth, document.documentElement.scrollHeight, innerHeight]);
    console.log('phone scroll', scrollW);
  });
  console.log(JSON.stringify(results, null, 1));
  await browser.close();
})();
