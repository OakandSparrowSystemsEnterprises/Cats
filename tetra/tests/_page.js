// Shared by every test: where the built page is, where screenshots go, how to launch Chromium.
const path = require('path'), fs = require('fs');
const DIST = path.resolve(__dirname, '..', 'dist', 'tetra_world.html');
const OUT = path.resolve(__dirname, 'out');
fs.mkdirSync(OUT, { recursive: true });
if (!fs.existsSync(DIST)) { console.error('dist/tetra_world.html is missing: run `python3 pipeline/build.py` first'); process.exit(2); }
module.exports = {
  URL: 'file://' + DIST,
  out: name => path.join(OUT, name),
  // software GL so the WebGL page renders on a headless box with no GPU
  LAUNCH: { args: ['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist', '--enable-unsafe-swiftshader'] },
  // The page's only external fetch is the Google Fonts stylesheet. When it fails (offline, a proxy, an untrusted
  // certificate) Chromium logs a net:: error; that is the network, not the page, so the tests do not count it.
  isNetworkError: text => /net::ERR_/.test(text) && !/ERR_INVALID_URL|ERR_FILE_NOT_FOUND/.test(text),
};
