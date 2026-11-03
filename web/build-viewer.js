// demo.html (Artifact sayfası, iskeletsiz) -> viewer.html (tam iskeletli ayrı sayfa; iframe ile gömülür)
// Kullanım: node build-viewer.js
const fs = require('fs'), path = require('path');
const src = fs.readFileSync(path.join(__dirname, 'demo.html'), 'utf8');
const title = (src.match(/<title>([^<]*)<\/title>/) || [, 'Koltuk Görünümü'])[1];
const body = src.replace(/<title>[^<]*<\/title>\s*/, '').replace(/<meta name="claude:viewport-fit-sides"[^>]*>\s*/, '');
const out = `<!doctype html>
<html lang="tr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>${title}</title>
</head>
<body>
${body}
</body>
</html>
`;
fs.writeFileSync(path.join(__dirname, 'viewer.html'), out);
console.log('viewer.html yazıldı', out.length, 'bayt');
