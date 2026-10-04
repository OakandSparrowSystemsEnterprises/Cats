const { chromium } = require('playwright');
const PAGE = require('./_page');
// The calendar from Ruby's lines of 2026-10-03 and 2026-10-04 (the year begins on 1 January, the Restart Day closes it, the strip runs in her order
// from March) with the build's readings (1 January a Starday, the Restart Day outside the week), and the strip in the World tab follows the day without any click
// (it did not until 2026-10-04: "in march it says its july on the seosons calender untill you reload it").
(async () => {
  const browser = await chromium.launch(PAGE.LAUNCH);
  const fails = [], errors = [];
  const ctx = await browser.newContext({ viewport: { width: 1366, height: 820 } });
  const page = await ctx.newPage(); page.on('pageerror', e => errors.push(String(e)));
  await page.goto(PAGE.URL); await page.waitForTimeout(900);
  await page.evaluate(() => { tetra.state.playing = false; });
  // the World tab's strip and the phases refresh every 12th frame, so wait for 14 frames rather than a fixed time (software GL frames are slow)
  const settle = () => page.evaluate(() => new Promise(r => { let n = 0; const f = () => (++n >= 14 ? r() : requestAnimationFrame(f)); requestAnimationFrame(f); }));
  const hud = () => page.evaluate(() => [document.getElementById('dateOut').textContent, document.getElementById('dateSub').textContent]);
  const strip = () => page.evaluate(() => {
    const m = document.querySelector('#yearStrip .m.now'), sn = document.querySelector('#seasonList li.now');
    return { month: m ? m.title.split(' · ')[0] : null, season: sn ? sn.querySelector('b').textContent : null };
  });
  const expect = [
    [0, 'Starday · 1 January', 'Rain season · day 1 of', 'January', 'Rain season'],
    [6.5, 'Twilightday · 7 January', 'day 7 of', 'January', 'Rain season'],
    [7.2, 'Starday · 8 January', 'day 8 of', 'January', 'Rain season'],
    [27.9, 'Twilightday · 28 January', 'day 28 of', 'January', 'Rain season'],
    [28.0, 'Starday · 1 February', 'Spring · day 29 of', 'February', 'Spring'],
    [56.5, 'Starday · 1 Tredesember', 'Spring · day 57 of', 'Tredesember', 'Spring'],
    [84.5, 'Starday · 1 March', 'Spring · day 85 of', 'March', 'Spring'],
    [112.5, 'Starday · 1 April', 'Summer · day 113 of', 'April', 'Summer'],
    [252.5, 'Starday · 1 September', 'Fall · day 253 of', 'September', 'Fall'],
    [363.5, 'Twilightday · 28 December', 'Winter · day 364 of', 'December', 'Winter'],
    [364.5, 'Restart Day · 1¼ days', 'Rain season · day 365 of', 'The Restart Day, which closes the year', 'Rain season'],
    [365.2, 'Restart Day · 1¼ days', 'Year 1700 · Rain season · day 365 of', 'The Restart Day, which closes the year', 'Rain season'],
    [365.3, 'Starday · 1 January', 'Year 1701 · Rain season · day 1 of', 'January', 'Rain season'],
    [-0.5, 'Restart Day · 1¼ days', 'Year 1699 · Rain season · day 365 of', 'The Restart Day, which closes the year', 'Rain season'],
  ];
  for (const [day, date, sub, month, season] of expect) {
    await page.evaluate(d => tetra.setDay(d), day); await settle();   // the frame tick updates the HUD and, on the World tab, the strip
    const [d, s] = await hud(); const st = await strip();
    const line = `day ${day}: ${d} | ${s} | strip ${st.month} / ${st.season}`; console.log(line);
    if (d !== date) fails.push(`day ${day} date "${d}" (wanted "${date}")`);
    if (!s.includes(sub)) fails.push(`day ${day} sub "${s}" (wanted "${sub}")`);
    if (st.month !== month) fails.push(`day ${day} strip on ${st.month} (wanted ${month})`);
    if (st.season !== season) fails.push(`day ${day} season ${st.season} (wanted ${season})`);
  }
  // the Reset button and the year buttons move the strip too
  await page.evaluate(() => tetra.setDay(130)); await settle();
  await page.click('#btnReset'); await settle();
  const afterReset = await strip(); if (afterReset.month !== 'January') fails.push('after Reset the strip shows ' + afterReset.month);
  await page.click('#btnYear'); await settle();
  const [d1] = await hud(); if (!/1 January/.test(d1)) fails.push('after +1 year the date is ' + d1);
  // Ruby's order on the strip: from March, the Restart Day before January, January, February and Tredesember at the end
  const cells = await page.evaluate(() => [...document.querySelectorAll('#yearStrip .m')].map(e => e.textContent + '=' + e.title));
  const labels = cells.map(c => c.split('=')[0]).join(' ');
  if (labels !== 'Mar Apr May Jun Jul Aug Sep Oct Nov Dec R Jan Feb Tre') fails.push('strip order is ' + labels);
  if (!/September · the 7th month/.test(cells[6]) || !/Tredesember · the 13th month/.test(cells[13]) || !/December · the 10th month/.test(cells[9])) fails.push('strip numbering: ' + cells.join(', '));
  // the day slider lands on the start of the chosen day (doyStart; its quarter-day shift applies only to a month after the Restart Day, and there is none today)
  for (const [v, want] of [[1, 0], [200, 199], [364, 363], [365, 364]]) {
    const got = await page.evaluate(v => { tetra.setDay(0); const r = document.getElementById('rngDay'); r.value = String(v); r.dispatchEvent(new Event('input', { bubbles: true })); return tetra.state.day; }, v);
    if (Math.abs(got - want) > 1e-6) fails.push(`slider ${v} set day ${got} (wanted ${want})`);
  }
  // the dock keeps room for the sliders with the weekday on the date line, on a computer and on a phone
  const widths = {};
  for (const w of [1366, 1024, 860, 393]) {
    await page.setViewportSize({ width: w, height: 820 }); await page.evaluate(() => tetra.setDay(364.5)); await page.waitForTimeout(400);
    widths[w] = await page.evaluate(() => ({ day: document.getElementById('rngDay').getBoundingClientRect().width, spin: document.getElementById('rngSpin').getBoundingClientRect().width, scroll: document.documentElement.scrollWidth }));
    if (widths[w].day < 60 || widths[w].spin < 60) fails.push(`at ${w}px the sliders are ${widths[w].day.toFixed(0)} and ${widths[w].spin.toFixed(0)} px wide`);
    if (widths[w].scroll > w) fails.push(`at ${w}px the page scrolls sideways (${widths[w].scroll})`);
  }
  console.log('slider widths', JSON.stringify(widths));
  console.log('errors', JSON.stringify(errors)); if (errors.length) fails.push('page errors');
  console.log(fails.length ? 'FAIL ' + fails.join('; ') : 'OK: the calendar reads right from Starday 1 January to the Restart Day, the strip runs from March and follows the day, the sliders keep their room');
  if (fails.length) process.exitCode = 1;
  await browser.close();
})();
