const { chromium } = require('playwright');
const PAGE = require('./_page');
// Cuba, the cube planet, shares this page with Tetra (Ruby, 2026-10-04: "it neends to be in the same file as tetra"). Checks: the page opens on Tetra;
// the Cuba button shows Cuba with its six sides in Ruby's arrangement; the Plus Continent and the Canyon are drawn where their markers sit; the star
// stays put and is not held in the frame (it is off screen when you face the lit Canon side, and on screen when you turn toward it); the world turns
// leftward; the 14-month calendar with Amberary reads right; the d5 moon eclipses on the 14th; the Far side carries the Canyon's other end; switching
// back shows Tetra; on a phone a tap on a side opens Cuba's Codex. A second run fakes the artifact's hot-reload hook: both worlds must start from one snapshot.
(async () => {
  const browser = await chromium.launch(PAGE.LAUNCH);
  const fails = [];
  const land = c => c && c[0] > 90 && c[1] > 90 && c[0] + c[1] > c[2] * 2.2, dark = c => c && c[0] + c[1] + c[2] < 150, purple = c => c && c[2] > 120 && c[2] >= c[1] && c[0] > 60;
  const settle = page => page.evaluate(() => new Promise(r => { let n = 0; const f = () => (++n >= 12 ? r() : requestAnimationFrame(f)); requestAnimationFrame(f); }));
  const run = async (width, height, phone) => {
    const ctx = await browser.newContext({ viewport: { width, height }, deviceScaleFactor: phone ? 2 : 1, isMobile: phone, hasTouch: phone });
    const page = await ctx.newPage(); const errors = [];
    page.on('pageerror', e => errors.push(String(e)));
    page.on('console', m => { if (m.type() === 'error' && !PAGE.isNetworkError(m.text())) errors.push('console: ' + m.text()); });
    await page.goto(PAGE.URL); await page.waitForTimeout(900);
    if ((await page.evaluate(() => dice.world)) !== 'tetra') fails.push(`${width}: the page did not open on Tetra`);
    await page.click('#diceWorlds [data-world="cuba"]'); await page.waitForTimeout(500);
    await page.evaluate(() => { cuba.setSpin(false); cuba.setDay(0); cuba.face('canon', false); }); await settle(page);
    const info = await page.evaluate(() => ({ world: dice.world, facing: cuba.facing(), nb: cuba.neighbours(), markers: cuba.markers(), island: cuba.sample('island'), hole: cuba.sample('hole'), star: cuba.starScreen(), starPx: cuba.starPixel(),
      tetraHidden: getComputedStyle(document.getElementById('app')).visibility, sides: [...document.querySelectorAll('#capp [data-face]')].map(b => b.dataset.face).join(','), date: document.getElementById('cdateOut').textContent + ' | ' + document.getElementById('cdateSub').textContent }));
    console.log(width, JSON.stringify(info));
    await page.screenshot({ path: PAGE.out(phone ? 'cuba_phone.png' : 'cuba_home.png') });
    if (info.world !== 'cuba' || info.tetraHidden !== 'hidden') fails.push(`${width}: the switch did not show Cuba`);
    if (info.sides !== 'canon,east,west,far,north,south') fails.push(`${width}: sides ${info.sides}`);
    if (info.facing !== 'canon') fails.push(`${width}: not facing canon`);
    const nb = info.nb; if (!(nb.left === 'east' && nb.right === 'west' && nb.up === 'north' && nb.down === 'south' && nb.behind === 'far')) fails.push(`${width}: arrangement ${JSON.stringify(nb)}`);
    if (!info.markers.includes('The Canyon · to the Far side') || !info.markers.includes('The Plus Continent')) fails.push(`${width}: markers ${JSON.stringify(info.markers)}`);
    if (!land(info.island && info.island.rgb)) fails.push(`${width}: the Plus Continent marker is not over land (${info.island && info.island.rgb})`);
    if (!dark(info.hole && info.hole.rgb)) fails.push(`${width}: the Canyon is not dark (${info.hole && info.hole.rgb})`);
    if (info.date !== '1 January | Rain season · day 1 of 393¼') fails.push(`${width}: first day reads "${info.date}"`);
    // the star: facing the lit Canon side it is behind the viewer and off the frame (Ruby: it must not be held in the frame); turned toward it, the glow is there and purple
    if (info.starPx) fails.push(`${width}: the star glow is on screen while facing the lit side (${JSON.stringify(info.star)})`);
    const starYaw = await page.evaluate(() => { const s = cuba.sunDir(); return Math.atan2(s[0], s[2]) + Math.PI; });   // the eye opposite the star looks straight at it
    await page.evaluate(y => cuba.setYaw(y + 0.1), starYaw); await settle(page);   // a small turn, so the glow is in the frame on a phone too
    const star2 = await page.evaluate(() => cuba.starPixel());
    if (!purple(star2 && star2.rgb)) fails.push(`${width}: no purple star glow when turned toward the star (${JSON.stringify(star2)})`);
    // the star does not move while the world turns and the view is not following
    const drift = await page.evaluate(() => { const a = cuba.starScreen(); cuba.setDay(0.3); return new Promise(r => requestAnimationFrame(() => requestAnimationFrame(() => { const b = cuba.starScreen(); r({ a, b }); }))); });
    if (!drift.a || !drift.b || Math.abs(drift.a.x - drift.b.x) > 0.5 || Math.abs(drift.a.y - drift.b.y) > 0.5) fails.push(`${width}: the star moved while the world turned (${JSON.stringify(drift)})`);
    await page.evaluate(() => { cuba.setDay(0); cuba.face('canon', false); }); await settle(page);
    // the turn: leftward like Tetra. Facing Canon, a point on the Canon side moves toward the viewer's left as the day advances
    const turn = await page.evaluate(() => { const a = cuba.sample('hole').x; cuba.setDay(0.04); const b = cuba.sample('hole').x; cuba.setDay(0); return { a, b }; });
    if (!(turn.b < turn.a)) fails.push(`${width}: the world does not turn leftward (${JSON.stringify(turn)})`);
    // the calendar: Amberary is the 14th month, before March, half rain and half between rain and spring; the Restart Day closes the year
    const cal = await page.evaluate(() => { const out = []; for (const d of [0, 27.5, 28, 56, 84, 98, 112, 391.5, 392.5, 393.3]) { cuba.setDay(d); const p = cuba.date(); out.push(`${d}:${p.mi < 0 ? 'Restart' : p.dom + ' ' + ['January','February','Tredesember','Amberary','March','April','May','June','July','August','September','October','November','December'][p.mi]}/${p.season.name}/${p.doy + 1}`); } cuba.setDay(0); return out.join(' '); });
    console.log(width, 'calendar', cal);
    const wantCal = '0:1 January/Rain season/1 27.5:28 January/Rain season/28 28:1 February/Spring/29 56:1 Tredesember/Spring/57 84:1 Amberary/Rain season/85 98:15 Amberary/Between rain and spring/99 112:1 March/Spring/113 391.5:28 December/Winter/392 392.5:Restart/Rain season/393 393.3:1 January/Rain season/1';
    if (cal !== wantCal) fails.push(`${width}: calendar reads wrong`);
    if (!phone) {
      await page.click('#ctabWorld'); await page.waitForTimeout(200);
      const strip = await page.evaluate(() => [...document.querySelectorAll('#cyearStrip .m')].map(e => e.textContent).join(' '));
      if (strip !== 'Mar Apr May Jun Jul Aug Sep Oct Nov Dec R Jan Feb Tre Amb') fails.push('Cuba strip order is ' + strip);
      const world = (await page.evaluate(() => document.getElementById('cpaneWorld').innerText)).toLowerCase();
      for (const need of ['still unwritten', 'north is the top', 'the plus continent', 'the canyon', 'amberary', 'd5', 'one magical and one magnetic', '8: far side', 'ammolite', 'chrysoberyl']) if (!world.includes(need)) fails.push(`Cuba's world tab lacks "${need}"`);
      await page.screenshot({ path: PAGE.out('cuba_world_tab.png') });
    }
    // the d5 moon: an eclipse at the deepest moment of the 14th of January, every place reading Eclipse, and none the day after
    const ecl = await page.evaluate(() => { let best = { e: 0, d: 13 }; for (let f = 0; f < 1; f += 1 / 120) { cuba.setDay(13 + f); const e = cuba.moon().eclipse; if (e > best.e) best = { e, d: 13 + f }; } cuba.setDay(best.d); const peak = ['canon', 'far', 'east', 'island', 'hole', 'hole-far'].map(id => cuba.phase(id).t); cuba.setDay(best.d + 1); const next = ['canon', 'island'].map(id => cuba.phase(id).t); cuba.setDay(0); return { best, peak, next }; });
    console.log(width, 'eclipse', JSON.stringify(ecl));
    if (ecl.best.e < 0.5 || ecl.peak.some(t => t !== 'Eclipse') || ecl.next.includes('Eclipse')) fails.push(`${width}: the moon's eclipse is wrong ${JSON.stringify(ecl)}`);
    if (!phone) { await page.evaluate(() => cuba.setDay(13.52)); await settle(page); await page.screenshot({ path: PAGE.out('cuba_eclipse.png') }); await page.evaluate(() => cuba.setDay(0)); }
    // the Far side
    await page.evaluate(() => cuba.face('far', false)); await settle(page);
    const far = await page.evaluate(() => ({ markers: cuba.markers(), px: cuba.sample('hole-far') }));
    if (!far.markers.includes('The other end of the Canyon') || far.markers.includes('The Plus Continent') || !dark(far.px && far.px.rgb)) fails.push(`${width}: far side ${JSON.stringify(far)}`);
    if (phone) {
      const closed = await page.evaluate(() => document.getElementById('ccodex').classList.contains('closed'));
      await page.tap('#capp [data-face="canon"]'); await page.waitForTimeout(1500);
      const open = await page.evaluate(() => !document.getElementById('ccodex').classList.contains('closed'));
      if (!closed || !open) fails.push('phone: Cuba\'s Codex did not open on a side tap');
      await page.screenshot({ path: PAGE.out('cuba_phone_card.png') });
    } else {
      await page.click('#capp [data-face="canon"]'); await page.waitForTimeout(1500);
      const card = await page.evaluate(() => document.getElementById('cplaceBody').innerText.replace(/\n+/g, ' | '));
      if (!/Canon Side/.test(card) || !/Follow this side/.test(card) || !/High sun|Morning|Afternoon|slow morning|Late light|First light|Dusk|Before dawn|Evening|Deep night/.test(card)) fails.push('the Canon card lacks its phase or follow button: ' + card.slice(0, 300));
      await page.evaluate(() => cuba.select('hole')); await page.waitForTimeout(600);
      const canyon = await page.evaluate(() => document.getElementById('cplaceBody').innerText.replace(/\n+/g, ' | ').slice(0, 120));
      if (!/The Canyon/.test(canyon)) fails.push('the Canyon card did not open: ' + canyon);
      await page.screenshot({ path: PAGE.out('cuba_canyon_card.png') });
    }
    // and back to Tetra
    await page.click('#diceWorlds [data-world="tetra"]'); await page.waitForTimeout(500);
    const back = await page.evaluate(() => ({ world: dice.world, date: document.getElementById('dateOut').textContent, cubaHidden: getComputedStyle(document.getElementById('capp')).visibility }));
    if (back.world !== 'tetra' || back.cubaHidden !== 'hidden' || !/January|February|Tredesember|March|April|May|June|July|August|September|October|November|December|Restart/.test(back.date)) fails.push(`${width}: switching back failed ${JSON.stringify(back)}`);
    console.log(width, 'errors', JSON.stringify(errors)); if (errors.length) fails.push(`${width}: page errors`);
    await ctx.close();
  };
  await run(1366, 820, false);
  await run(393, 852, true);
  // the hot-reload bridge: one hook, both worlds started from one snapshot, the world shown restored
  {
    const ctx = await browser.newContext({ viewport: { width: 1366, height: 820 } });
    await ctx.addInitScript(() => { window.claude = { hot: { data: null, ready(fn) { this._ready = fn; setTimeout(() => fn({ tetra: { day: 100, playing: false }, cuba: { day: 50, playing: false }, world: 'cuba' }), 60); }, snapshot(fn) { this._snap = fn; } } }; });
    const page = await ctx.newPage(); const errors = []; page.on('pageerror', e => errors.push(String(e)));
    await page.goto(PAGE.URL); await page.waitForTimeout(1200);
    const hot = await page.evaluate(() => ({ world: dice.world, tetraDay: window.tetra && tetra.state.day, cubaDay: window.cuba && cuba.state.day, cubaDate: document.getElementById('cdateOut').textContent, snap: window.claude.hot._snap ? Object.keys(window.claude.hot._snap()).sort().join(',') : null }));
    console.log('hot reload', JSON.stringify(hot));
    if (hot.world !== 'cuba' || Math.abs(hot.tetraDay - 100) > 0.5 || Math.abs(hot.cubaDay - 50) > 0.5 || !/February/.test(hot.cubaDate) || hot.snap !== 'cuba,tetra,world') fails.push('hot reload: ' + JSON.stringify(hot));
    await page.click('#diceWorlds [data-world="tetra"]'); await page.waitForTimeout(600);
    const tetraDate = await page.evaluate(() => document.getElementById('dateOut').textContent);   // Tetra's loop wakes when it is shown and draws its restored day
    console.log('tetra after hot reload', tetraDate, 'errors', JSON.stringify(errors));
    if (!/March/.test(tetraDate)) fails.push('hot reload: Tetra did not wake with its day (' + tetraDate + ')');
    if (errors.length) fails.push('hot reload: page errors ' + errors.join('; '));
    await ctx.close();
  }
  console.log(fails.length ? 'FAIL ' + fails.join('; ') : 'OK: Cuba shares the page with Tetra\'s mechanics: the fixed star, the leftward turn, the 14-month calendar with Amberary, the d5 moon and its eclipse, the switch and the hot-reload bridge');
  if (fails.length) process.exitCode = 1;
  await browser.close();
})();
