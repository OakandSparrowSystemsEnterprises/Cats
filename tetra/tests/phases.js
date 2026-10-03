const { chromium } = require('playwright');
const PAGE = require('./_page');
// Sweeps a whole year, every half hour, through the debug hook and tallies the light phase each place reports.
// Canon checks: the Far Face never reaches High sun or Deep night; Mount Celestial is always twilight; the Canon Face still gets both.
(async () => {
  const browser = await chromium.launch(PAGE.LAUNCH);
  const ctx = await browser.newContext({ viewport: { width: 1366, height: 820 } });
  const page = await ctx.newPage(); const errors = []; page.on('pageerror', e => errors.push(String(e)));
  await page.goto(PAGE.URL); await page.waitForTimeout(900);
  const phases = await page.evaluate(() => {
    const ids = ['warmia', 'ehia', 'treeland', 'celestial', 'delta-far', 'hotland', 'spike', 'whiteland', 'delta', 'beria', 'tropicia'];
    const out = {}; for (const id of ids) out[id] = {};
    for (let d = 0; d < 365; d += 7) for (let h = 0; h < 24; h += 0.5) { tetra.setDay(d + h / 24); for (const id of ids) { const t = tetra.phase(id).t; out[id][t] = (out[id][t] || 0) + 1; } }
    return out;
  });
  for (const k in phases) console.log(k.padEnd(14), JSON.stringify(phases[k]));
  console.log('errors', JSON.stringify(errors));
  const far = ['warmia', 'ehia', 'treeland', 'delta-far'];
  const banned = ['High sun', 'Deep night', 'Morning', 'Afternoon', 'Evening', 'Before dawn'];
  const fails = [];
  for (const id of far) for (const b of banned) if (phases[id][b]) fails.push(`${id} reached ${b}`);
  if (Object.keys(phases.celestial).join() !== 'Twilight, always') fails.push('Mount Celestial is not always twilight: ' + JSON.stringify(phases.celestial));
  if (!phases.whiteland['High sun'] || !phases.whiteland['Deep night']) fails.push('the Canon Face lost its high sun or deep night');
  if (errors.length) fails.push('page errors');
  console.log(fails.length ? 'FAIL ' + fails.join('; ') : 'OK: far face clamped, Mount Celestial always twilight, Canon face unchanged');
  if (fails.length) process.exitCode = 1;
  await browser.close();
})();
