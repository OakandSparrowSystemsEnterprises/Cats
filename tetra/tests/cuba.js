const { chromium } = require('playwright');
const PAGE = require('./_page');
// Cuba, the cube planet, shares this page with Tetra (Ruby, 2026-10-04: "it neends to be in the same file as tetra"). The Cuba button under
// the title switches worlds. Checks: Tetra is shown first; switching shows Cuba with its six sides in Ruby's arrangement (facing Canon with
// North up: East on the left, West on the right, Far behind), the Plus Continent and the Canyon drawn where their markers sit, the star's glow
// on screen ("i cant see the star"), the world turning leftward like Tetra, the Far side with the Canyon's other end; switching back shows
// Tetra's HUD; on a phone a tap on a side opens Cuba's Codex.
(async () => {
  const browser = await chromium.launch(PAGE.LAUNCH);
  const fails = [];
  const land = c => c && c[0] > 90 && c[1] > 90 && c[0] + c[1] > c[2] * 2.2, dark = c => c && c[0] + c[1] + c[2] < 150, purple = c => c && c[2] > 120 && c[2] >= c[1] && c[0] > 60;   // the glow is white at its heart and purple around it
  const run = async (width, height, phone) => {
    const ctx = await browser.newContext({ viewport: { width, height }, deviceScaleFactor: phone ? 2 : 1, isMobile: phone, hasTouch: phone });
    const page = await ctx.newPage(); const errors = [];
    page.on('pageerror', e => errors.push(String(e)));
    page.on('console', m => { if (m.type() === 'error' && !PAGE.isNetworkError(m.text())) errors.push('console: ' + m.text()); });
    await page.goto(PAGE.URL); await page.waitForTimeout(900);
    const first = await page.evaluate(() => dice.world);
    if (first !== 'tetra') fails.push(`${width}: the page did not open on Tetra`);
    await page.click('#diceWorlds [data-world="cuba"]'); await page.waitForTimeout(700);
    await page.evaluate(() => { cuba.setSpin(false); cuba.face('canon', false); }); await page.waitForTimeout(500);
    const info = await page.evaluate(() => ({ world: dice.world, facing: cuba.facing(), nb: cuba.neighbours(), markers: cuba.markers(), island: cuba.sample('island'), hole: cuba.sample('hole'), star: cuba.starPixel(),
      tetraHidden: getComputedStyle(document.getElementById('app')).visibility, sides: [...document.querySelectorAll('#capp [data-face]')].map(b => b.dataset.face).join(',') }));
    console.log(width, JSON.stringify(info));
    await page.screenshot({ path: PAGE.out(phone ? 'cuba_phone.png' : 'cuba_home.png') });
    if (info.world !== 'cuba' || info.tetraHidden !== 'hidden') fails.push(`${width}: the switch did not show Cuba`);
    if (info.sides !== 'canon,east,west,far,north,south') fails.push(`${width}: sides ${info.sides}`);
    if (info.facing !== 'canon') fails.push(`${width}: not facing canon`);
    const nb = info.nb; if (!(nb.left === 'east' && nb.right === 'west' && nb.up === 'north' && nb.down === 'south' && nb.behind === 'far')) fails.push(`${width}: arrangement ${JSON.stringify(nb)}`);
    if (!info.markers.includes('The Canyon · to the Far side') || !info.markers.includes('The Plus Continent')) fails.push(`${width}: markers ${JSON.stringify(info.markers)}`);
    if (!land(info.island && info.island.rgb)) fails.push(`${width}: the Plus Continent marker is not over land (${info.island && info.island.rgb})`);
    if (!dark(info.hole && info.hole.rgb)) fails.push(`${width}: the Canyon is not dark (${info.hole && info.hole.rgb})`);
    if (!purple(info.star && info.star.rgb)) fails.push(`${width}: no purple star glow on screen (${JSON.stringify(info.star)})`);
    // the turn: leftward like Tetra. Facing Canon, a point on the Canon side moves toward the viewer's left as time runs (the spin angle falls)
    const turn = await page.evaluate(() => { const a = cuba.sample('hole').x; const s0 = cuba.state.spin; cuba.state.spin = s0 - 0.25; const b = cuba.sample('hole').x; cuba.state.spin = s0; return { a, b }; });
    if (!(turn.b < turn.a)) fails.push(`${width}: the world does not turn leftward (${JSON.stringify(turn)})`);
    await page.evaluate(() => cuba.face('far', false)); await page.waitForTimeout(500);
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
      const card = await page.evaluate(() => document.getElementById('cplaceBody').innerText.replace(/\n+/g, ' | ').slice(0, 200));
      if (!/Canon Side/.test(card)) fails.push('the Canon card did not open: ' + card);
      await page.evaluate(() => cuba.select('hole')); await page.waitForTimeout(600);
      const canyon = await page.evaluate(() => document.getElementById('cplaceBody').innerText.replace(/\n+/g, ' | ').slice(0, 120));
      if (!/The Canyon/.test(canyon)) fails.push('the Canyon card did not open: ' + canyon);
      await page.screenshot({ path: PAGE.out('cuba_canyon_card.png') });
      await page.click('#ctabWorld'); await page.waitForTimeout(300);
      const world = (await page.evaluate(() => document.getElementById('cpaneWorld').innerText)).toLowerCase();
      for (const need of ['still unwritten', 'north is the top', 'to the far side', 'connect to the north south east and west faces', 'dark purple star', 'the plus continent', 'the canyon', 'd5', 'one magical and one magnetic', '8: far side']) if (!world.includes(need)) fails.push(`Cuba's world tab lacks "${need}"`);
      await page.screenshot({ path: PAGE.out('cuba_world_tab.png') });
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
  console.log(fails.length ? 'FAIL ' + fails.join('; ') : 'OK: Cuba shares the page, six sides in Ruby\'s arrangement, the Plus Continent, the Canyon and the star are drawn, the world turns leftward, the switch works both ways');
  if (fails.length) process.exitCode = 1;
  await browser.close();
})();
