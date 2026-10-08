// Überwachung und Fristen.
//   ohne Parameter (täglich): Erreichbarkeit + Antwortzeit aller Websites, Terminbuchung (buchung_url), montags PageSpeed (Handy), Domain-Ablauf,
//                             Vertragslaufzeiten (F3), Erinnerung Inhalte-Formular (E1), Löschfristen (Ü3).
//   ?art=erreichbar (alle 10 Min.): nur Erreichbarkeit, speichert nur Ausfälle, meldet jeden Ausfall einmal pro Tag.
//   ?art=datenschutz (monatlich): Cookies und Drittanbieter beim ersten Aufruf ohne Einwilligung.
// Fehler → Aufgabe (ohne Dubletten) + Push.
import { db, einfuegen, erlaubt, push, laden, pagespeed, json, aufgabe, tag } from "./db.ts";

const plusMonate = (d: string, m: number) => { const x = new Date(d + "T00:00:00Z"); x.setUTCMonth(x.getUTCMonth() + m); return tag(x); };
const de = (d: string) => d.split("-").reverse().join(".");

async function websites() { return await db("websites?select=id,domain,status,kunde_id,domain_ablauf,buchung_url,buchung_anbieter&status=in.(live,vorschau)&domain=not.is.null"); }

async function erreichbarkeit(nurFehler: boolean, mitPsi: boolean) {
  const heute = tag(), probleme: string[] = [], ergebnis: any[] = [];
  for (const w of await websites()) {
    const url = `https://${w.domain}/`;
    const r = await laden(url);
    if (!nurFehler || !r.ok) await einfuegen("checks", { website_id: w.id, art: "uptime", ok: r.ok, wert: r.ms, details: { status: r.status, fehler: (r as any).fehler ?? null } });
    if (!r.ok && await aufgabe(`${w.domain} nicht erreichbar (Status ${r.status || "–"})`, `ausfall:${w.domain}:${heute}`, { website_id: w.id, kunde_id: w.kunde_id, prioritaet: 1 }))
      probleme.push(`${w.domain} nicht erreichbar (Status ${r.status || "–"})`);
    let psi = null;
    if (mitPsi && r.ok) {
      psi = await pagespeed(url);
      if (psi) {
        await einfuegen("checks", { website_id: w.id, art: "lighthouse", ok: psi.leistung >= 90 && psi.barrierefreiheit >= 90, wert: psi.leistung, details: psi });
        const mw = Object.entries({ psi_leistung: psi.leistung, psi_barrierefreiheit: psi.barrierefreiheit, psi_seo: psi.seo, lcp_s: psi.lcp_s })
          .map(([kennzahl, wert]) => ({ website_id: w.id, datum: heute, kennzahl, wert }));
        await db("messwerte?on_conflict=website_id,datum,kennzahl", { method: "POST", body: JSON.stringify(mw), headers: { Prefer: "resolution=merge-duplicates,return=minimal" } }).catch(() => {});
        if (psi.leistung < 80 && await aufgabe(`${w.domain}: PageSpeed Handy nur ${psi.leistung}/100`, `psi:${w.domain}:${heute}`, { website_id: w.id, kunde_id: w.kunde_id }))
          probleme.push(`${w.domain}: PageSpeed Handy nur ${psi.leistung}/100`);
      }
    }
    if (!nurFehler && w.domain_ablauf && w.domain_ablauf <= plusMonate(heute, 1) &&
        await aufgabe(`Domain ${w.domain} läuft am ${de(w.domain_ablauf)} ab – Verlängerung prüfen`, `domain:${w.domain}:${w.domain_ablauf}`, { website_id: w.id, kunde_id: w.kunde_id, prioritaet: 1, quelle: "frist" }))
      probleme.push(`Domain ${w.domain} läuft bald ab`);
    if (!nurFehler && w.buchung_url) {                                  // Terminbuchung des Betriebs erreichbar? (403/429 = Schutz gegen Bots, kein Ausfall)
      const bu = await laden(w.buchung_url);
      const ok = bu.ok || [401, 403, 405, 429].includes(bu.status);
      await einfuegen("checks", { website_id: w.id, art: "links", ok, wert: bu.ms, details: { typ: "buchung", status: bu.status, url: w.buchung_url } });
      if (!ok && await aufgabe(`${w.domain}: Terminbuchung (${w.buchung_anbieter || "Buchungsseite"}) nicht erreichbar (Status ${bu.status || "–"})`, `buchung:${w.domain}:${heute}`, { website_id: w.id, kunde_id: w.kunde_id, prioritaet: 1 }))
        probleme.push(`${w.domain}: Terminbuchung nicht erreichbar`);
    }
    ergebnis.push({ domain: w.domain, erreichbar: r.ok, ms: r.ms, psi });
  }
  return { probleme, ergebnis };
}

// F3: Laufzeit-Wächter – 4 Monate vor Ende der (verlängerten) Laufzeit eine Aufgabe, damit Verlängerung/Upgrade rechtzeitig besprochen wird
async function fristen() {
  const heute = tag(), meldungen: string[] = [];
  const vs = await db("vertraege?select=id,produkt,start,mindestlaufzeit_monate,verlaengerung_monate,kuendigungsfrist_monate,kunde_id,kunden(firma)&ende=is.null&mindestlaufzeit_monate=gt.0");
  for (const v of vs) {
    let ende = plusMonate(v.start, v.mindestlaufzeit_monate);
    while (ende <= heute && v.verlaengerung_monate > 0) ende = plusMonate(ende, v.verlaengerung_monate);
    if (ende <= heute || plusMonate(heute, 4) < ende) continue;
    const stichtag = plusMonate(ende, -(v.kuendigungsfrist_monate ?? 0));
    const t = `${v.kunden?.firma ?? "Kunde"}: ${v.produkt} – Laufzeit endet ${de(ende)}, Kündigungsfrist bis ${de(stichtag)}. Verlängerung oder Upgrade ansprechen.`;
    if (await aufgabe(t, `laufzeit:${v.id}:${ende}`, { kunde_id: v.kunde_id, quelle: "frist", faellig: stichtag })) meldungen.push(t);
  }
  return meldungen;
}

// E1: Inhalte-Formular – Erinnerung, wenn die Frist abgelaufen ist (höchstens 2×)
async function inhalteErinnern() {
  const heute = tag(), meldungen: string[] = [];
  const offen = await db(`inhalte_formulare?select=id,titel,frist,erinnert,kunde_id&eingereicht_am=is.null&frist=lt.${heute}&erinnert=lt.2`);
  for (const f of offen) {
    await db(`inhalte_formulare?id=eq.${f.id}`, { method: "PATCH", body: JSON.stringify({ erinnert: f.erinnert + 1 }), headers: { Prefer: "return=minimal" } });
    const t = `Inhalte von ${f.titel || "Kunde"} fehlen noch (Frist ${de(f.frist)}) – beim Kunden nachfragen`;
    if (await aufgabe(t, `inhalte-frist:${f.id}:${f.erinnert + 1}`, { kunde_id: f.kunde_id, quelle: "frist", prioritaet: 1 })) meldungen.push(t);
  }
  return meldungen;
}

// Ü3: Löschfristen laut Datenschutz – Formularanfragen nach 90 Tagen, Prüfprotokolle nach 400 Tagen
async function loeschen() {
  const vor = (tage: number) => new Date(Date.now() - tage * 864e5).toISOString();
  await db(`anfragen?eingang=lt.${vor(90)}`, { method: "DELETE", headers: { Prefer: "return=minimal" } }).catch(() => {});
  await db(`checks?zeit=lt.${vor(400)}`, { method: "DELETE", headers: { Prefer: "return=minimal" } }).catch(() => {});
}

// Datenschutz-Check: Was passiert beim ersten Aufruf, bevor jemand zugestimmt hat?
async function datenschutz() {
  const probleme: string[] = [];
  for (const w of (await websites()).filter((x: any) => x.status === "live")) {
    const r = await laden(`https://${w.domain}/`);
    if (!r.ok) continue;
    const h = r.text.toLowerCase(), funde: string[] = [];
    if (r.headers.get("set-cookie")) funde.push("setzt beim ersten Aufruf ein Cookie");
    if (/fonts\.googleapis\.com|fonts\.gstatic\.com/.test(h)) funde.push("lädt Schriften von Google-Servern");
    if (/<script[^>]+src=["'][^"']*(googletagmanager|google-analytics|connect\.facebook\.net|hotjar|clarity\.ms)/.test(h) && !/lw_dienste|einwilligung\.js/.test(h)) funde.push("lädt Tracking ohne Einwilligungs-Baustein");
    if (/<iframe[^>]+src=["'][^"']*(google\.[a-z.]+\/maps|youtube\.com|player\.vimeo)/.test(h)) funde.push("bettet Karte/Video direkt ein (Zwei-Klick-Lösung fehlt)");
    if (!/href=["'][^"']*impressum/.test(h) || !/href=["'][^"']*datenschutz/.test(h)) funde.push("Link zu Impressum oder Datenschutz fehlt");
    await db("messwerte?on_conflict=website_id,datum,kennzahl", { method: "POST", body: JSON.stringify({ website_id: w.id, datum: tag(), kennzahl: "datenschutz_funde", wert: funde.length }),
      headers: { Prefer: "resolution=merge-duplicates,return=minimal" } }).catch(() => {});
    const monat = tag().slice(0, 7);
    if (funde.length && await aufgabe(`Datenschutz ${w.domain}: ${funde.join(", ")}`, `datenschutz:${w.domain}:${monat}`, { website_id: w.id, kunde_id: w.kunde_id, prioritaet: 1 }))
      probleme.push(`${w.domain}: ${funde.join(", ")}`);
  }
  return probleme;
}

Deno.serve(async (req) => {
  if (!(await erlaubt(req))) return json({ fehler: "nicht erlaubt" }, 401);
  const p = new URL(req.url).searchParams, art = p.get("art");
  if (art === "erreichbar") {
    const { probleme } = await erreichbarkeit(true, false);
    if (probleme.length) await push("Website nicht erreichbar", probleme.join("\n"), "urgent");
    return json({ probleme });
  }
  if (art === "datenschutz") {
    const probleme = await datenschutz();
    if (probleme.length) await push("Datenschutz-Check", probleme.join("\n"), "high");
    return json({ probleme });
  }
  const mitPsi = p.get("psi") === "1" || new Date().getUTCDay() === 1;
  const { probleme, ergebnis } = await erreichbarkeit(false, mitPsi);
  const f = await fristen(), i = await inhalteErinnern();
  await loeschen();
  if (probleme.length) await push("Website-Problem", probleme.join("\n"), "high");
  if (f.length || i.length) await push("Fristen", [...f, ...i].join("\n"));
  return json({ geprueft: ergebnis.length, probleme, fristen: f, inhalte: i, ergebnis });
});
