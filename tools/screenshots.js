// Erzeugt Screenshots der Vorschau-Websites.
// Aufruf (dist/ muss auf localhost:8765 laufen):
//   node tools/screenshots.js <ausgabeordner> [check|thumb]
// check = ganze Seiten zur Kontrolle, thumb = Ausschnitt für die Agentur-Website
const { chromium } = require('playwright');
(async () => {
  const [out, mode] = [process.argv[2], process.argv[3] || 'check'];
  const slugs = ['friseur', 'barber', 'dachdecker-solar', 'steuerberater', 'pflegedienst', 'bestatter', 'tierarzt'];
  const b = await chromium.launch();
  const errs = [];
  for (const s of slugs) {
    for (const [vw, vh, tag] of [[1440, 900, 'd'], [390, 780, 'm']]) {
      const ctx = await b.newContext({ viewport: { width: vw, height: vh }, deviceScaleFactor: tag === 'm' ? 2 : 1 });
      const p = await ctx.newPage();
      p.on('console', m => { if (m.type() === 'error') errs.push(s + ': ' + m.text()); });
      await p.goto(`http://localhost:8765/vorschau/${s}/`);
      await p.waitForTimeout(400);
      const sw = await p.evaluate(() => document.documentElement.scrollWidth);
      if (sw > vw) errs.push(`Überlauf ${s} bei ${vw}px: ${sw}px`);
      if (mode === 'thumb') {
        await p.evaluate(() => document.querySelector('.demo-bar')?.remove());
        await p.screenshot({ path: `${out}/${s}-${tag}.png` });
      } else {
        await p.screenshot({ path: `${out}/${s}-${tag}-full.png`, fullPage: true });
      }
      await ctx.close();
    }
  }
  console.log(errs.join('\n') || 'keine Fehler');
  await b.close();
})();
