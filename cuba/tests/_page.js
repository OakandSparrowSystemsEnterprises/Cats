// Shared by the Cuba tests: where the built page is, where screenshots go, how to launch Chromium.
// Playwright comes from this folder's node_modules if present, else from Tetra's install (npm install in ../tetra).
const path = require('path'), fs = require('fs');
const DIST = path.resolve(__dirname, '..', 'dist', 'cuba_world.html');
const OUT = path.resolve(__dirname, 'out');
fs.mkdirSync(OUT, { recursive: true });
if (!fs.existsSync(DIST)) { console.error('dist/cuba_world.html is missing: run `python3 pipeline/build.py` first'); process.exit(2); }
const pw = require(require.resolve('playwright', { paths: [path.resolve(__dirname, '..'), path.resolve(__dirname, '..', '..', 'tetra')] }));
module.exports = {
  chromium: pw.chromium,
  URL: 'file://' + DIST,
  out: name => path.join(OUT, name),
  LAUNCH: { args: ['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist', '--enable-unsafe-swiftshader'] },
  isNetworkError: text => /net::ERR_/.test(text) && !/ERR_INVALID_URL|ERR_FILE_NOT_FOUND/.test(text),
};
