const { chromium } = require('playwright');
const PAGE = require('./_page');
// Octa, the eight-sided planet (Ruby, 2026-10-17: "cool now lets add octa (or octo ...)"), is the third world in this page. Checks: the Octa button shows Octa
// and hides Tetra and Hexa; the die has eight numbered sides, opposite sides adding up to 9; side 1 faces the viewer at the start; the sides are drawn (a slate
// pixel at each visible side's centre, not the sky); the eight side buttons fly to their sides; the Codex carries the vote, the directions question and Ruby's
// words about the first side; the shared clock runs here too; switching back shows Tetra; no page errors at desktop and phone widths.
// Since Ruby's second message of 2026-10-17 ("give octa the same star, a d7 moon, a turn, a calender with one more month than hexa and a restart day that is
// one and three fourths of a day"): the die turns with the day, the star is drawn where it stands, the d7 moon is a seven-faced prism that eclipses on the 14th,
// and the year is 15 months of 28 days plus a Restart Day of 1.75 days, the fifteenth month unnamed, between March and April, half spring and half between spring and summer; the years count from 0, with -0 before it.
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
    await page.evaluate(() => { octa.setSpin(false); octa.setDay(0); octa.home(); }); await settle(page);
    const info = await page.evaluate(() => ({ world: dice.world, facing: octa.facing(), sides: octa.sides().join(','), opposites: octa.sides().map(s => s + ':' + octa.opposite(s)).join(' '),
      tetraHidden: getComputedStyle(document.getElementById('app')).visibility, hexaHidden: getComputedStyle(document.getElementById('capp')).visibility,
      buttons: [...document.querySelectorAll('#oapp [data-face]')].map(b => b.dataset.face).join(','), facingText: document.getElementById('ofacing').textContent,
      centre: octa.sample('1'), date: document.getElementById('odateOut').textContent, sub: document.getElementById('odateSub').textContent }));
    console.log(width, JSON.stringify(info));
    await page.screenshot({ path: PAGE.out(phone ? 'octa_phone.png' : 'octa_home.png') });
    if (info.world !== 'octa' || info.tetraHidden !== 'hidden' || info.hexaHidden !== 'hidden') fails.push(`${width}: the switch did not show Octa alone`);
    const codexOpen = await page.evaluate(() => document.getElementById('ocodex').classList.contains('open'));
    if (phone && codexOpen) fails.push(`${width}: the Codex starts open on a phone and hides the dock`);
    if (!phone && !codexOpen) fails.push(`${width}: the Codex starts closed on a desktop`);
    if (info.sides !== '1,2,3,4,5,6,7,8' || info.buttons !== '1,2,3,4,5,6,7,8') fails.push(`${width}: sides ${info.sides} buttons ${info.buttons}`);
    if (info.opposites !== '1:8 2:7 3:6 4:5 5:4 6:3 7:2 8:1') fails.push(`${width}: opposites ${info.opposites}`);
    if (info.facing !== '1' || !/Home/.test(info.facingText)) fails.push(`${width}: not facing side 1 (${info.facing}, ${info.facingText})`);
    if (!slate(info.centre)) fails.push(`${width}: side 1 is not drawn at its centre (${JSON.stringify(info.centre)})`);
    if (info.date !== 'Starday · 1 January' || info.sub !== 'Year 0 of Octa · Rain season · day 1 of 421¾') fails.push(`${width}: the dock date reads ${info.date} / ${info.sub}`);
    // the calendar: 15 months, the unnamed one between March and April, a Restart Day of a day and three quarters, 421¾ days a year
    const cal = await page.evaluate(() => { const out = []; for (const d of [0, 27.5, 28, 56, 84, 112, 140, 154, 168, 419.5, 420.2, 421.7, 421.75]) { octa.setDay(d); const p = octa.date(); out.push(`${d}:${p.wd}/${p.month}/${p.dom}/y${p.y}/${p.season}`); } octa.setDay(-1); const before = octa.date(); octa.setDay(0); return { months: octa.months().length, year: octa.yearDays(), out: out.join(' '), before: `${before.yl}/${before.y}` }; });
    console.log(width, 'calendar', JSON.stringify(cal));
    if (cal.months !== 15 || Math.abs(cal.year - 421.75) > 1e-9) fails.push(`${width}: the year is ${cal.months} months and ${cal.year} days`);
    for (const need of ['0:Starday/January/1/y0/Rain season', '27.5:Twilightday/January/28/y0/Rain season', '28:Starday/Amberary/1/y0/Rain season', '56:Starday/February/1/y0/Spring', '84:Starday/Tredesember/1/y0/Spring', '112:Starday/March/1/y0/Spring', '140:Starday/the fifteenth month/1/y0/Spring', '154:Starday/the fifteenth month/15/y0/Between spring and summer', '168:Starday/April/1/y0/Summer', '419.5:Twilightday/December/28/y0/Winter', '420.2:null/Restart Day/0/y0/Rain season', '421.7:null/Restart Day/0/y0/Rain season', '421.75:Starday/January/1/y1/Rain season'])
      if (!cal.out.includes(need)) fails.push(`${width}: calendar lacks ${need} (${cal.out})`);
    if (cal.before !== '-0/-1') fails.push(`${width}: the year before year 0 reads ${cal.before}, not -0`);
    // the d7 moon: seven faces, an eclipse at midday on the 14th and none on the 15th; the die turns with the day; the star stands in the world
    // the deepest moment of the eclipse is near midday on the 14th (the moon's small daily drift moves it a little off 13.5), so the day is scanned, as in tests/cuba.js
    const moon = await page.evaluate(() => { const die = octa.moonDie(); let e1 = 0, at = 0; for (let d = 13.2; d <= 13.8; d += 0.004) { octa.setDay(d); const e = octa.moon().eclipse; if (e > e1) { e1 = e; at = d; } } octa.setDay(14.5); const e2 = octa.moon().eclipse; octa.setDay(0.5); const f = octa.facing(); octa.setDay(0); return { die, e1, at, e2, halfTurnFacing: f, facing0: octa.facing(), sun: octa.sunDir() }; });
    console.log(width, 'moon', JSON.stringify(moon));
    if (!moon.die || moon.die.sides !== 7 || moon.die.count !== 60 || !(moon.die.tip >= moon.die.flat)) fails.push(`${width}: the moon is not the seven-faced prism (${JSON.stringify(moon.die)})`);
    if (!(moon.e1 >= 0.9) || !(moon.e2 < 0.1)) fails.push(`${width}: eclipse ${moon.e1} at day ${moon.at} on the 14th, ${moon.e2} on the 15th`);
    if (moon.halfTurnFacing === '1' || moon.facing0 !== '1') fails.push(`${width}: the die does not turn with the day (${moon.halfTurnFacing} at half a day, ${moon.facing0} at the start)`);
    // the star: with the camera on the far side of the die from the star, looking back through it, the star's glow is on screen
    const star = await page.evaluate(() => { const s = octa.sunDir(); octa.setYaw(Math.atan2(-s[0], -s[2]), 0.05); return new Promise(r => requestAnimationFrame(() => requestAnimationFrame(() => { const sp = octa.starScreen(); r({ sp }); }))); });
    if (!star.sp || star.sp.x < 0 || star.sp.x > width) fails.push(`${width}: the star is not on screen when facing it (${JSON.stringify(star.sp)})`);
    await page.evaluate(() => { octa.home(); }); await settle(page);
    // the other planets in the sky: seven of them at fixed places along the star's line through the die, and Tetra on screen at some turn of the view when zoomed out; the ship's landing marked on side 1 (Home)
    const sky = await page.evaluate(async () => { octa.state.pitch = 0.05; octa.state.dist = 9.5; octa.state.fly = null; const frames = () => new Promise(r => requestAnimationFrame(() => requestAnimationFrame(r))); let found = null;
      for (let k = 0; k < 36 && !found; k++) { octa.setYaw(k * Math.PI / 18, 0.05); await frames(); const b = octa.skyBodies(); if (b.tetra && b.tetra.x > 40 && b.tetra.x < innerWidth - 400 && b.tetra.y > 40 && b.tetra.y < innerHeight - 200) found = b.tetra; }
      const keys = Object.keys(octa.skyBodies()).sort().join(','); octa.home(); await frames(); octa.setDay(0); await frames(); return { found, keys, markers: octa.markers() }; });
    console.log(width, 'sky', JSON.stringify(sky));
    if (sky.keys !== 'cuba,deca,dodeca,icosa,icositetra,tetra,triaconta') fails.push(`${width}: the sky lists ${sky.keys}`);
    if (!phone && !sky.found) fails.push(`${width}: Tetra is not in Octa's sky when turned toward it`);
    if (!sky.markers.includes('The ship’s landing')) fails.push(`${width}: the landing marker is not shown on side 1 (${JSON.stringify(sky.markers)})`);
    // every side button flies to its side, and the side's centre pixel is slate once it faces the viewer
    for (const id of ['8', '4', '5', '2']) {
      // on a phone a chosen side opens the Codex sheet over the dock (as on Hexa), so Close is tapped before the next button
      if (phone) { const open = await page.evaluate(() => document.getElementById('ocodex').classList.contains('open')); if (open) { await page.click('#obtnClose'); await page.waitForTimeout(500); } }
      await page.click(`#oapp [data-face="${id}"]`);
      await page.waitForTimeout(1600); await settle(page);
      const r = await page.evaluate(id => ({ facing: octa.facing(), px: octa.sample(id), card: document.getElementById('oplaceBody').textContent }), id);
      if (r.facing !== id) fails.push(`${width}: button ${id} did not fly to side ${id} (facing ${r.facing})`);
      if (!slate(r.px)) fails.push(`${width}: side ${id} is not drawn (${JSON.stringify(r.px)})`);
      const names = { 1: 'Home', 2: 'Canon', 3: 'West', 4: 'South', 5: 'North', 6: 'East', 7: 'Far', 8: 'Away' };
      if (!r.card.includes('Side ' + id) || !r.card.includes(names[id]) || !r.card.includes('Opposite it is ' + names[9 - Number(id)] + ' (side ' + (9 - Number(id)) + ')')) fails.push(`${width}: the card for side ${id} reads ${r.card.slice(0, 120)}`);
    }
    if (!phone) await page.screenshot({ path: PAGE.out('octa_side2.png') });
    // the Codex: the World tab phrases, in Ruby's spelling where they are hers
    await page.click('#otabWorld'); await page.waitForTimeout(200);
    const world = (await page.evaluate(() => document.getElementById('opaneWorld').textContent)).toLowerCase();
    for (const need of ['the first side hasent been discoverd or drawn yet', 'named by the number on the dice', 'daddy votes octa, i vote octo', 'two votes to one', 'another 5 so they arent confusing', 'hedron name minus', 'add up to 9', 'still unwritten', 'give octa the same star', 'a d7 moon', 'one more month than hexa', 'one and three fourths of a day', '421¾', 'icosa', 'icositetra', 'between march and april', 'everything is similar to the first two', 'a ship as landed on side one of octa', 'all of the other planets', 'nay face could be seen', 'zenith and nadir', 'crown and keel', 'between spring and summer', 'year 0 of octa', 'curved line from te sun', 'it shuld be stronger', '5 more pairs', 'hither and yon', 'bow and stern', 'including the planet you are on', 'side names, not directions', 'heads and tails', 'home and away', 'maps are being drawn', 'pair three fits', '1 is home', 'home (1)', 'fixed pint in space'])
      if (!world.includes(need)) fails.push(`${width}: Octa's world tab lacks "${need}"`);
    const sidesTab = await page.evaluate(() => { document.getElementById('otabSides').click(); return document.querySelectorAll('#osideList button').length; });
    if (sidesTab !== 8) fails.push(`${width}: the Sides tab lists ${sidesTab} sides`);
    if (!phone) await page.screenshot({ path: PAGE.out('octa_world_tab.png') });
    // the shared clock keeps running on Octa, and the switch back shows Tetra
    const clock = await page.evaluate(async () => { octa.setSpin(true); const d0 = dice.time.day; await new Promise(r => setTimeout(r, 700)); octa.setSpin(false); const moved = dice.time.day - d0; octa.setDay(0); return moved; });
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
  console.log('OK: Octa shares the page: eight blank numbered sides turning under the star, opposite sides adding up to 9, the d7 moon and its eclipse, the 15-month year with its 1¾-day Restart Day, the vote and the directions in the Codex, the shared clock, the switch and the hot-reload bridge');
})();
