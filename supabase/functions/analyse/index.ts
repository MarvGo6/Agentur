// Schnell-Analyse einer Betriebs-Website für den Vertrieb.
// POST {url, name?, branche?, ort?}  → legt den Interessenten an (oder aktualisiert ihn) und liefert den Befund sofort.
// Ohne Body (Zeitplan)               → analysiert bis zu 3 Interessenten mit Website, die noch keinen Befund haben.
// Ergebnis: pagespeed_mobil, potenzial (0–100, je höher desto größer der Hebel) und ein Befund in Klartext.
import { db, einfuegen, aendern, erlaubt, laden, pagespeed, json } from "./db.ts";

const hat = (h: string, re: RegExp) => re.test(h);
function pruefen(html: string, finalUrl: string, ms: number) {
  const h = html.slice(0, 600000), lower = h.toLowerCase();
  const jahr = new Date().getFullYear();
  const jahre = [...h.matchAll(/(?:©|&copy;|copyright)\s*(?:\d{4}\s*[-–]\s*)?(20\d\d)/gi)].map(m => +m[1]);
  const imgs = [...h.matchAll(/<img\b[^>]*>/gi)].map(m => m[0]);
  return {
    https: finalUrl.startsWith("https://"),
    handy_ansicht: hat(h, /<meta[^>]+name=["']viewport/i),
    titel: (h.match(/<title[^>]*>([^<]{0,140})/i)?.[1] || "").trim(),
    beschreibung: hat(h, /<meta[^>]+name=["']description["'][^>]+content=["'][^"']{30,}/i),
    h1: (h.match(/<h1\b/gi) || []).length,
    telefon_link: hat(h, /href=["']tel:/i),
    mail_link: hat(h, /href=["']mailto:/i),
    formular: hat(h, /<form\b/i),
    strukturierte_daten: hat(h, /"@type"\s*:\s*"(LocalBusiness|[A-Za-z]*(Store|Business|Service|Contractor|Clinic|Practice|Salon|Organization|Dentist|Physician|Attorney|AccountingService|HomeAndConstructionBusiness))"/),
    online_termin: hat(lower, /termin\s*(buchen|online|vereinbaren)|booking|treatwell|shore\.com|studiobookr|doctolib|calendly/),
    bewertungen_sichtbar: hat(lower, /bewertung|rezension|google-review|sterne|★/),
    cookie_banner: hat(lower, /cookiebot|usercentrics|borlabs|consentmanager|klaro|cookie-?consent|onetrust|complianz/),
    cookie_banner_eigen: hat(lower, /cookie[^<]{0,80}(akzeptieren|zustimmen|einverstanden|ablehnen)|(akzeptieren|zustimmen)[^<]{0,80}cookie/),
    tracking: hat(lower, /googletagmanager|gtag\(|google-analytics|fbq\(|connect\.facebook\.net|hotjar|clarity\.ms|matomo|linkedin\.com\/insight|tiktok\.com\/i18n\/pixel/),
    einbettung_extern: hat(lower, /<iframe[^>]+src=["'][^"']*(google\.[a-z.]+\/maps|maps\.google|youtube\.com|youtube-nocookie\.com|player\.vimeo)/),
    impressum_link: hat(lower, /href=["'][^"']*impressum|>\s*impressum\s*</),
    datenschutz_link: hat(lower, /href=["'][^"']*(datenschutz|privacy)|>\s*datenschutz/),
    google_fonts_extern: hat(lower, /fonts\.googleapis\.com|fonts\.gstatic\.com/),
    baukasten: (h.match(/<meta[^>]+name=["']generator["'][^>]+content=["']([^"']{0,60})/i)?.[1] || (lower.includes("wix.com") ? "Wix" : lower.includes("jimdo") ? "Jimdo" : "")).trim(),
    copyright_jahr: jahre.length ? Math.max(...jahre) : null,
    veraltet: jahre.length ? Math.max(...jahre) < jahr - 1 : null,
    bilder: imgs.length, bilder_ohne_alt: imgs.filter(i => !/\balt=["'][^"']+/i.test(i)).length,
    groesse_kb: Math.round(html.length / 1024), antwort_ms: ms,
  };
}
function bewerten(b: any, psi: any) {
  const punkte: [number, string][] = [];
  if (!b.erreichbar) return { potenzial: 90, befund: ["Website war bei der Prüfung nicht erreichbar."] };
  if (!b.https) punkte.push([20, "Keine verschlüsselte Verbindung (https) – Browser warnen Besucher."]);
  if (!b.handy_ansicht) punkte.push([20, "Nicht für Handys gebaut – die meisten lokalen Suchen kommen vom Handy."]);
  if (psi && psi.leistung < 50) punkte.push([20, `Sehr langsam auf dem Handy (Google PageSpeed ${psi.leistung}/100).`]);
  else if (psi && psi.leistung < 80) punkte.push([10, `Ladezeit auf dem Handy ausbaufähig (Google PageSpeed ${psi.leistung}/100).`]);
  if (!b.telefon_link) punkte.push([10, "Telefonnummer nicht antippbar – Anrufe vom Handy gehen verloren."]);
  if (!b.formular && !b.online_termin) punkte.push([10, "Kein Formular und keine Online-Buchung – Anfragen nur zu Öffnungszeiten."]);
  if (!b.beschreibung) punkte.push([5, "Keine Seitenbeschreibung für Google – das Suchergebnis wirkt zufällig."]);
  if (!b.strukturierte_daten) punkte.push([10, "Keine strukturierten Daten – Google und KI-Assistenten erkennen Ort und Leistungen schlechter."]);
  if (b.h1 !== 1) punkte.push([5, b.h1 === 0 ? "Keine Hauptüberschrift (H1)." : `${b.h1} Hauptüberschriften statt einer.`]);
  if (b.veraltet) punkte.push([10, `Letzte sichtbare Pflege ${b.copyright_jahr} – die Seite wirkt veraltet.`]);
  if (!b.bewertungen_sichtbar) punkte.push([5, "Bewertungen sind auf der Website nicht sichtbar."]);
  const einwilligung = b.cookie_banner || b.cookie_banner_eigen;
  if (b.tracking && !einwilligung) punkte.push([10, "Tracking (z. B. Google Analytics/Meta) ohne erkennbare Einwilligungsabfrage – rechtliches Risiko."]);
  if (b.einbettung_extern && !einwilligung) punkte.push([5, "Karte oder Video wird direkt eingebettet und überträgt Daten ohne Einwilligung – besser per Klick laden."]);
  if (!b.impressum_link || !b.datenschutz_link) punkte.push([10, `Kein erkennbarer Link zu${!b.impressum_link ? "m Impressum" : ""}${!b.impressum_link && !b.datenschutz_link ? " und zur" : !b.datenschutz_link ? "r" : ""}${!b.datenschutz_link ? " Datenschutzerklärung" : ""} auf der Startseite.`]);
  if (b.google_fonts_extern) punkte.push([5, "Schriften werden von Google-Servern geladen – Datenschutzrisiko (Abmahnungen bekannt)."]);
  if (b.bilder_ohne_alt > 3) punkte.push([3, `${b.bilder_ohne_alt} Bilder ohne Beschreibung (Alt-Text).`]);
  return { potenzial: Math.min(100, punkte.reduce((s, p) => s + p[0], 0)), befund: punkte.sort((a, z) => z[0] - a[0]).map(p => p[1]) };
}
async function analysieren(url: string) {
  if (!/^https?:\/\//i.test(url)) url = "https://" + url;
  let r = await laden(url);
  if (!r.ok && url.startsWith("https://")) r = await laden(url.replace("https://", "http://"));
  const b: any = { erreichbar: r.ok, status: r.status, ...(r.ok ? pruefen(r.text, r.url, r.ms) : {}) };
  const psi = r.ok ? await pagespeed(r.url) : null;
  const w = bewerten(b, psi);
  return { url: r.url, pruefung: b, pagespeed: psi, ...w };
}

Deno.serve(async (req) => {
  if (!(await erlaubt(req))) return json({ fehler: "nicht erlaubt" }, 401);
  let body: any = null;
  if (req.method === "POST") body = await req.json().catch(() => null);
  if (body?.url) {
    const a = await analysieren(body.url);
    const daten = { name: body.name || new URL(a.url || ("https://" + body.url)).hostname, branche: body.branche ?? null, ort: body.ort ?? null,
      website_alt: body.url, pagespeed_mobil: a.pagespeed?.leistung ?? null, potenzial: a.potenzial, befund: a, analysiert_am: new Date().toISOString(), quelle: body.quelle || "analyse" };
    const vorh = await db(`interessenten?select=id&website_alt=eq.${encodeURIComponent(body.url)}`);
    if (vorh.length) await aendern("interessenten", `id=eq.${vorh[0].id}`, daten); else await einfuegen("interessenten", daten);
    return json(a);
  }
  const offen = await db("interessenten?select=id,website_alt&website_alt=not.is.null&analysiert_am=is.null&limit=3");
  const fertig = [];
  for (const i of offen) {
    const a = await analysieren(i.website_alt);
    await aendern("interessenten", `id=eq.${i.id}`, { pagespeed_mobil: a.pagespeed?.leistung ?? null, potenzial: a.potenzial, befund: a, analysiert_am: new Date().toISOString() });
    fertig.push({ url: i.website_alt, potenzial: a.potenzial });
  }
  return json({ analysiert: fertig });
});
