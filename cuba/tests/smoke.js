const PAGE = require('./_page');
// Loads the page at computer and phone widths, checks for script errors, the six sides and Ruby's arrangement of them
// (looking at Canon with North up: East on the left, West on the right, Far behind), the island and the hole, and the phone Codex.
(async () => {
  const browser = await PAGE.chromium.launch(PAGE.LAUNCH);
  const fails = [];
  const run = async (width, height, phone) => {
    const ctx = await browser.newContext({ viewport: { width, height }, deviceScaleFactor: phone ? 2 : 1, isMobile: phone, hasTouch: phone });
    const page = await ctx.newPage(); const errors = [];
    page.on('pageerror', e => errors.push(String(e)));
    page.on('console', m => { if (m.type() === 'error' && !PAGE.isNetworkError(m.text())) errors.push('console: ' + m.text()); });
    await page.goto(PAGE.URL); await page.waitForTimeout(900);
    const title = await page.title();
    const sides = await page.evaluate(() => [...document.querySelectorAll('[data-face]')].map(b => b.dataset.face).join(','));
    await page.evaluate(() => { cuba.setSpin(false); cuba.face('canon', false); }); await page.waitForTimeout(400);
    const facing = await page.evaluate(() => cuba.facing());
    const nb = await page.evaluate(() => cuba.neighbours());
    const markers = await page.evaluate(() => cuba.markers());
    await page.screenshot({ path: PAGE.out(`${phone ? 'phone' : 'home'}_${width}.png`) });
    console.log(width, 'title', title, '| sides', sides, '| facing', facing, '| neighbours', JSON.stringify(nb), '| markers', JSON.stringify(markers));
    if (title !== 'Cuba') fails.push(`${width}: title ${title}`);
    if (sides !== 'canon,east,west,far,north,south') fails.push(`${width}: sides ${sides}`);
    if (facing !== 'canon') fails.push(`${width}: not facing canon after face()`);
    if (!(nb.left === 'east' && nb.right === 'west' && nb.up === 'north' && nb.down === 'south' && nb.behind === 'far')) fails.push(`${width}: arrangement ${JSON.stringify(nb)}`);
    if (!markers.includes('The hole · to the Far side') || !markers.includes('The central island')) fails.push(`${width}: markers ${JSON.stringify(markers)}`);
    // the drawn pixels: the island is land-coloured where its marker sits, the hole is dark, the sea beside the island is blue (the box once drew inside out and no test noticed)
    await page.waitForTimeout(300);
    const px = await page.evaluate(() => ({ island: cuba.sample('island'), hole: cuba.sample('hole') }));
    console.log(width, 'pixels', JSON.stringify(px));
    const land = c => c && c[0] > 90 && c[1] > 90 && c[0] + c[1] > c[2] * 2.2, dark = c => c && c[0] + c[1] + c[2] < 150;
    if (!land(px.island && px.island.rgb)) fails.push(`${width}: the island marker is not over land (${px.island && px.island.rgb})`);
    if (!dark(px.hole && px.hole.rgb)) fails.push(`${width}: the hole is not dark (${px.hole && px.hole.rgb})`);
    // the Far side shows the hole's other end and not the island
    await page.evaluate(() => cuba.face('far', false)); await page.waitForTimeout(400);
    const farMarkers = await page.evaluate(() => cuba.markers());
    if (!farMarkers.includes('The other end of the hole') || farMarkers.includes('The central island')) fails.push(`${width}: far markers ${JSON.stringify(farMarkers)}`);
    await page.waitForTimeout(300);
    const farPx = await page.evaluate(() => cuba.sample('hole-far'));
    if (!dark(farPx && farPx.rgb)) fails.push(`${width}: the hole's other end is not dark (${farPx && farPx.rgb})`);
    if (!phone) await page.screenshot({ path: PAGE.out('far_side.png') });
    if (!phone) {
      await page.click('[data-face="canon"]'); await page.waitForTimeout(1600);
      const card = await page.evaluate(() => document.getElementById('placeBody').innerText.replace(/\n+/g, ' | ').slice(0, 400));
      console.log('canon card', card);
      if (!/Canon Side/.test(card)) fails.push('the Canon card did not open');
      await page.screenshot({ path: PAGE.out('canon_card.png') });
      await page.click('#tabWorld'); await page.waitForTimeout(300);
      await page.screenshot({ path: PAGE.out('world_tab.png') });
      const world = (await page.evaluate(() => document.getElementById('paneWorld').innerText)).toLowerCase();   // eyebrows render in capitals
      for (const need of ['still unwritten', 'north is the top', 'to the far side', 'connect to the north south east and west faces']) if (!world.includes(need)) fails.push(`world tab lacks "${need}"`);
    } else {
      const closed = await page.evaluate(() => document.getElementById('codex').classList.contains('closed'));
      await page.tap('[data-face="canon"]'); await page.waitForTimeout(1600);
      const open = await page.evaluate(() => !document.getElementById('codex').classList.contains('closed'));
      console.log('phone codex closed before', closed, 'open after tap', open);
      if (!closed || !open) fails.push('phone: the Codex did not open on a side tap');
      await page.screenshot({ path: PAGE.out('phone_card.png') });
    }
    console.log(width, 'errors', JSON.stringify(errors)); if (errors.length) fails.push(`${width}: page errors`);
    await ctx.close();
  };
  await run(1366, 820, false);
  await run(393, 852, true);
  console.log(fails.length ? 'FAIL ' + fails.join('; ') : 'OK: Cuba loads clean, six sides in Ruby\'s arrangement, the island and the hole are there, the phone Codex opens');
  if (fails.length) process.exitCode = 1;
  await browser.close();
})();
