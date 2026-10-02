const { chromium } = require('playwright');
const PAGE = require('./_page');
// Phone width: a real touch tap on the world must open the Codex on the tapped face (Ruby: 'the faces should be touchable').
(async () => {
  const browser = await chromium.launch(PAGE.LAUNCH);
  const ctx2 = await browser.newContext({ viewport: { width: 393, height: 852 }, deviceScaleFactor: 1, hasTouch: true, isMobile: true });
  const p2 = await ctx2.newPage(); const err2 = [];
  p2.on('pageerror', e => err2.push(String(e)));
  await p2.goto(PAGE.URL); await p2.waitForTimeout(800);
  await p2.evaluate(() => { tetra.state.playing = false; });
  const closedBefore = await p2.evaluate(() => document.getElementById('codex').classList.contains('closed'));
  await p2.touchscreen.tap(140, 300); await p2.waitForTimeout(1500);
  const after = await p2.evaluate(() => ({ closed: document.getElementById('codex').classList.contains('closed'), face: tetra.state.selectedFace, title: (document.getElementById('placeBody').innerText || '').split('\n').slice(0, 3).join(' | ') }));
  console.log('phone: codex closed before tap?', closedBefore, 'after tap:', JSON.stringify(after));
  await p2.screenshot({ path: PAGE.out('s13_phone_tap.png') });
  console.log('phone errors', JSON.stringify(err2));
  if (after.closed || !after.face || err2.length) { console.log('FAIL: the tap did not open the Codex on a face'); process.exitCode = 1; } else console.log('OK: tap opened the ' + after.face + ' face card');
  await ctx2.close(); await browser.close();
})();
