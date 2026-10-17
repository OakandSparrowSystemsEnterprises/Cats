const { chromium } = require('playwright');
const PAGE = require('./_page');
// Octa, the eight-sided planet (Ruby, 2026-10-17: "cool now lets add octa (or octo ...)"), is the third world in this page. Checks: the Octa button shows Octa
// and hides Tetra and Hexa; the die has eight numbered sides, opposite sides adding up to 9; side 1 faces the viewer at the start; the sides are drawn (a slate
// pixel at each visible side's centre, not the sky); the eight side buttons fly to their sides; the Codex carries the vote, the directions question and Ruby's
// words about the first side; the shared clock runs here too; switching back shows Tetra; no page errors at desktop and phone widths.
(async () => {
  const browser = await chromium.launch(PAGE.LAUNCH);
  const fails = [];
  const settle = page => page.evaluate(() => new Promise(r => { let n = 0; const f = () => (++n >= 12 ? r() : requestAnimationFrame(f)); requestAnimationFrame(f); }));
  // a drawn side: the GL canvas is clear where there is only sky, so any opaque pixel that is not black is the die (slate, its dashed edge or its gold numeral)
  const slate = c => c && c[3] > 0 && c[0] + c[1] + c[2] > 45;
  const run = async (width, height, phone) => {
    const ctx = await browser.newContext({ viewport: { width, height }, deviceScaleFactor: phone ? 2 : 1, isMobile: phone, hasTouch: phone });
    const page = await ctx.newPage(); const errors = [];
    page.on('pageerror', e => errors.push(String(e)));
    page.on('console', m => { if (m.type() === 'error' && !PAGE.isNetworkError(m.text())) errors.push('console: ' + m.text()); });
    await page.goto(PAGE.URL); await page.waitForTimeout(900);
    await page.click('#diceWorlds [data-world="octa"]'); await page.waitForTimeout(400);
    await page.evaluate(() => { octa.setSpin(false); }); await settle(page);
    const info = await page.evaluate(() => ({ world: dice.world, facing: octa.facing(), sides: octa.sides().join(','), opposites: octa.sides().map(s => s + ':' + octa.opposite(s)).join(' '),
      tetraHidden: getComputedStyle(document.getElementById('app')).visibility, hexaHidden: getComputedStyle(document.getElementById('capp')).visibility,
      buttons: [...document.querySelectorAll('#oapp [data-face]')].map(b => b.dataset.face).join(','), facingText: document.getElementById('ofacing').textContent,
      centre: octa.sample('1'), date: document.getElementById('odateOut').textContent }));
    console.log(width, JSON.stringify(info));
    await page.screenshot({ path: PAGE.out(phone ? 'octa_phone.png' : 'octa_home.png') });
    if (info.world !== 'octa' || info.tetraHidden !== 'hidden' || info.hexaHidden !== 'hidden') fails.push(`${width}: the switch did not show Octa alone`);
    if (info.sides !== '1,2,3,4,5,6,7,8' || info.buttons !== '1,2,3,4,5,6,7,8') fails.push(`${width}: sides ${info.sides} buttons ${info.buttons}`);
    if (info.opposites !== '1:8 2:7 3:6 4:5 5:4 6:3 7:2 8:1') fails.push(`${width}: opposites ${info.opposites}`);
    if (info.facing !== '1' || !/Side 1/.test(info.facingText)) fails.push(`${width}: not facing side 1 (${info.facing}, ${info.facingText})`);
    if (!slate(info.centre)) fails.push(`${width}: side 1 is not drawn at its centre (${JSON.stringify(info.centre)})`);
    if (!/Shared clock · day \d+/.test(info.date)) fails.push(`${width}: the dock does not count the shared clock (${info.date})`);
    // every side button flies to its side, and the side's centre pixel is slate once it faces the viewer
    for (const id of ['8', '4', '5', '2']) {
      // on a phone the open Codex covers the dock (as on Hexa), so the side is chosen through the hook there and by the button on a desktop
      if (phone) await page.evaluate(id => octa.face(id), id); else await page.click(`#oapp [data-face="${id}"]`);
      await page.waitForTimeout(1600); await settle(page);
      const r = await page.evaluate(id => ({ facing: octa.facing(), px: octa.sample(id), card: document.getElementById('oplaceBody').textContent }), id);
      if (r.facing !== id) fails.push(`${width}: button ${id} did not fly to side ${id} (facing ${r.facing})`);
      if (!slate(r.px)) fails.push(`${width}: side ${id} is not drawn (${JSON.stringify(r.px)})`);
      if (!r.card.includes('Side ' + id) || !r.card.includes('Opposite it is side ' + (9 - Number(id)))) fails.push(`${width}: the card for side ${id} reads ${r.card.slice(0, 120)}`);
    }
    if (!phone) await page.screenshot({ path: PAGE.out('octa_side2.png') });
    // the Codex: the World tab phrases, in Ruby's spelling where they are hers
    await page.click('#otabWorld'); await page.waitForTimeout(200);
    const world = (await page.evaluate(() => document.getElementById('opaneWorld').textContent)).toLowerCase();
    for (const need of ['the first side hasent been discoverd or drawn yet', 'named by the number on the dice', 'daddy votes octa, i vote octo', 'two votes to one', 'dawn and dusk', 'zenith and nadir', 'windward and leeward', 'add up to 9', 'still unwritten', 'shared clock'])
      if (!world.includes(need)) fails.push(`${width}: Octa's world tab lacks "${need}"`);
    const sidesTab = await page.evaluate(() => { document.getElementById('otabSides').click(); return document.querySelectorAll('#osideList button').length; });
    if (sidesTab !== 8) fails.push(`${width}: the Sides tab lists ${sidesTab} sides`);
    if (!phone) await page.screenshot({ path: PAGE.out('octa_world_tab.png') });
    // the shared clock keeps running on Octa, and the switch back shows Tetra
    const clock = await page.evaluate(async () => { octa.setSpin(true); const d0 = dice.time.day; await new Promise(r => setTimeout(r, 700)); octa.setSpin(false); return dice.time.day - d0; });
    if (!(clock > 0.005)) fails.push(`${width}: the shared clock did not advance on Octa (${clock})`);
    await page.click('#diceWorlds [data-world="tetra"]'); await page.waitForTimeout(300);
    const back = await page.evaluate(() => ({ world: dice.world, octaHidden: getComputedStyle(document.getElementById('oapp')).visibility }));
    if (back.world !== 'tetra' || back.octaHidden !== 'hidden') fails.push(`${width}: the switch back did not show Tetra (${JSON.stringify(back)})`);
    console.log(width, 'errors', JSON.stringify(errors));
    if (errors.length) fails.push(`${width}: page errors ${errors.join('; ')}`);
    await ctx.close();
  };
  await run(1366, 820, false);
  await run(393, 760, true);
  // the hot-reload bridge restores Octa as the shown world
  {
    const ctx = await browser.newContext({ viewport: { width: 1366, height: 820 } });
    await ctx.addInitScript(() => { window.claude = { hot: { data: null, ready(fn) { this._ready = fn; setTimeout(() => fn({ tetra: { day: 3 }, cuba: { day: 7 }, octa: { baseYaw: 1.2, pitch: 0.3, dist: 5.5, selectedSide: '3' }, time: { day: 40, playing: false, speed: 1 }, world: 'octa' }), 60); }, snapshot(fn) { this._snap = fn; } } }; });
    const page = await ctx.newPage(); const errors = [];
    page.on('pageerror', e => errors.push(String(e)));
    await page.goto(PAGE.URL); await page.waitForTimeout(1200);
    const hot = await page.evaluate(() => ({ world: dice.world, yaw: octa.state.baseYaw, dist: octa.state.dist, side: octa.state.selectedSide, snap: Object.keys(window.claude.hot._snap()).sort().join(',') }));
    console.log('hot reload', JSON.stringify(hot));
    if (hot.world !== 'octa' || Math.abs(hot.yaw - 1.2) > 1e-6 || Math.abs(hot.dist - 5.5) > 1e-6 || hot.side !== '3' || hot.snap !== 'cuba,octa,tetra,time,world') fails.push('hot reload: Octa was not restored from the snapshot (' + JSON.stringify(hot) + ')');
    if (errors.length) fails.push('hot reload: page errors ' + errors.join('; '));
    await ctx.close();
  }
  await browser.close();
  if (fails.length) { console.log('FAIL\n' + fails.join('\n')); process.exit(1); }
  console.log('OK: Octa shares the page: eight blank numbered sides, opposite sides adding up to 9, the vote and the directions in the Codex, the shared clock, the switch and the hot-reload bridge');
})();
