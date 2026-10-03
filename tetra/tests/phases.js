const { chromium } = require('playwright');
const PAGE = require('./_page');
// Sweeps a whole year, every half hour, through the debug hook and tallies the light phase each place reports.
// Canon checks: the Far Face never reaches High sun or Deep night; Mount Celestial is always twilight; the Canon Face still gets both;
// at the middle of a new-moon day every place that can see the star reads Eclipse, and the day after none does.
(async () => {
  const browser = await chromium.launch(PAGE.LAUNCH);
  const ctx = await browser.newContext({ viewport: { width: 1366, height: 820 } });
  const page = await ctx.newPage(); const errors = []; page.on('pageerror', e => errors.push(String(e)));
  await page.goto(PAGE.URL); await page.waitForTimeout(900);
  const { phases, eclipse } = await page.evaluate(() => {
    const ids = ['warmia', 'ehia', 'treeland', 'celestial', 'delta-far', 'hotland', 'spike', 'whiteland', 'delta', 'beria', 'tropicia'];
    const out = {}; for (const id of ids) out[id] = {};
    for (let d = 0; d < 365; d += 7) for (let h = 0; h < 24; h += 0.5) { tetra.setDay(d + h / 24); for (const id of ids) { const t = tetra.phase(id).t; out[id][t] = (out[id][t] || 0) + 1; } }
    // Ruby (2026-10-03): "Eclipse" is a time description too. The new moon is the 14th of each month and the die covers the star halfway through that day.
    // The die drifts a little about its swing, so the deepest moment is found by scanning the day (tetra.phase refreshes the moon for the day set).
    const ecl = { peak: {}, noon: {}, at: 13, peakAmount: 0 };
    for (let f = 0; f < 1; f += 1 / 240) { tetra.setDay(13 + f); tetra.phase('spike'); const e = tetra.moon().eclipse; if (e > ecl.peakAmount) { ecl.peakAmount = e; ecl.at = 13 + f; } }
    tetra.setDay(ecl.at); for (const id of ids) ecl.peak[id] = tetra.phase(id).t;
    tetra.setDay(ecl.at + 1); for (const id of ids) ecl.noon[id] = tetra.phase(id).t; ecl.noonAmount = tetra.moon().eclipse;
    return { phases: out, eclipse: ecl };
  });
  for (const k in phases) console.log(k.padEnd(14), JSON.stringify(phases[k]));
  console.log('eclipse peak at day', eclipse.at.toFixed(3), 'amount', eclipse.peakAmount.toFixed(2), JSON.stringify(eclipse.peak));
  console.log('next day    ', eclipse.noonAmount.toFixed(2), JSON.stringify(eclipse.noon));
  console.log('errors', JSON.stringify(errors));
  const far = ['warmia', 'ehia', 'treeland', 'delta-far'];
  const banned = ['High sun', 'Deep night', 'Morning', 'Afternoon', 'Evening', 'Before dawn'];
  const fails = [];
  for (const id of far) for (const b of banned) if (phases[id][b]) fails.push(`${id} reached ${b}`);
  const celestialKinds = Object.keys(phases.celestial).filter(t => t !== 'Eclipse');
  if (celestialKinds.join() !== 'Twilight, always') fails.push('Mount Celestial is not always twilight: ' + JSON.stringify(phases.celestial));
  if (!phases.whiteland['High sun'] || !phases.whiteland['Deep night']) fails.push('the Canon Face lost its high sun or deep night');
  if (eclipse.peakAmount < 0.5) fails.push('no eclipse on the 14th of March');
  const lit = Object.values(eclipse.peak).filter(t => t === 'Eclipse').length;
  if (lit < 3) fails.push('too few places read Eclipse at the eclipse peak: ' + JSON.stringify(eclipse.peak));
  if (eclipse.peak.celestial !== 'Eclipse') fails.push('Mount Celestial does not read Eclipse at the eclipse peak');
  if (Object.values(eclipse.noon).includes('Eclipse') || eclipse.noonAmount > 0) fails.push('Eclipse still showing the day after the new moon');
  if (errors.length) fails.push('page errors');
  console.log(fails.length ? 'FAIL ' + fails.join('; ') : 'OK: far face clamped, Mount Celestial always twilight (Eclipse aside), Canon face unchanged, Eclipse read at the new moon');
  if (fails.length) process.exitCode = 1;
  await browser.close();
})();
