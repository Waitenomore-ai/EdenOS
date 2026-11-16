const fs = require('node:fs');
const path = require('node:path');

const root = path.resolve(__dirname, '..');
const build = path.join(root, 'build');
const required = [
  'eden-original-approved.png',
  'icon.png',
  'icon.ico',
  'icon.icns',
  'installer-header.bmp',
  'installer-sidebar.bmp',
  'dmg-background.png',
  'eden-installer.nsh',
  'installer-information.txt',
];
for (const name of required) {
  const file = path.join(build, name);
  if (!fs.existsSync(file) || !fs.statSync(file).isFile() || fs.statSync(file).size === 0) {
    throw new Error(`Required installer resource missing or empty: build/${name}`);
  }
}

function pngSize(file) {
  const data = fs.readFileSync(file);
  if (data.subarray(0, 8).toString('hex') !== '89504e470d0a1a0a') throw new Error(`${file} is not PNG`);
  return [data.readUInt32BE(16), data.readUInt32BE(20)];
}
function bmpSize(file) {
  const data = fs.readFileSync(file);
  if (data.toString('ascii', 0, 2) !== 'BM') throw new Error(`${file} is not BMP`);
  return [Math.abs(data.readInt32LE(18)), Math.abs(data.readInt32LE(22))];
}
function expectSize(file, actual, expected) {
  if (actual[0] !== expected[0] || actual[1] !== expected[1]) {
    throw new Error(`${file} dimensions ${actual.join('x')} do not match ${expected.join('x')}`);
  }
  console.log(`OK ${file}: ${actual.join('x')}`);
}
expectSize('eden-original-approved.png', pngSize(path.join(build, 'eden-original-approved.png')), [1024, 1536]);
expectSize('dmg-background.png', pngSize(path.join(build, 'dmg-background.png')), [640, 430]);
expectSize('installer-header.bmp', bmpSize(path.join(build, 'installer-header.bmp')), [150, 57]);
expectSize('installer-sidebar.bmp', bmpSize(path.join(build, 'installer-sidebar.bmp')), [164, 314]);

const nsis = fs.readFileSync(path.join(build, 'eden-installer.nsh'), 'utf8');
for (const marker of ['customWelcomePage', 'customFinishPage', 'MUI_WELCOMEPAGE_TITLE', 'MUI_FINISHPAGE_TITLE']) {
  if (!nsis.includes(marker)) throw new Error(`NSIS branding marker missing: ${marker}`);
}
console.log('EDEN_INSTALLER_ASSETS_CHECK_PASS');
